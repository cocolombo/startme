#!/usr/bin/env bash
# Sauvegarde d'un projet vers Google Drive, Proton Drive et un hôte SSH local.
# L'archive est créée une seule fois puis uploadée en parallèle vers les trois destinations.
#
# Prérequis : rclone installé et configuré (rclone config)
#   - remote "gdrive"       : type Google Drive
#   - remote "protondrive"  : type Proton Drive
#
# Usage :
#   ./scripts/backup_cloud.sh                          # sauvegarde startme (défaut)
#   ./scripts/backup_cloud.sh /chemin/vers/projet      # sauvegarde un autre projet
#   ./scripts/backup_cloud.sh [PROJET] --local         # archive locale uniquement
#   ./scripts/backup_cloud.sh [PROJET] --dry-run       # liste les fichiers sans archiver
#
# Exclusions par projet :
#   Créer un fichier .backup_exclude à la racine du projet pour des exclusions spécifiques.
#   Les chemins sont relatifs à la racine du projet (ex: node_modules, dist/, secret.json).

set -euo pipefail

# ── Parsing des arguments ──────────────────────────────────────────────────────
MODE="upload"
ARG_DIR=""
for arg in "$@"; do
  case "$arg" in
    --local)   MODE="local" ;;
    --dry-run) MODE="dryrun" ;;
    *)         ARG_DIR="$arg" ;;
  esac
done

# ── Configuration ──────────────────────────────────────────────────────────────
if [[ -n "${ARG_DIR}" ]]; then
  PROJECT_DIR="$(realpath "${ARG_DIR}")"
else
  PROJECT_DIR="/media/120gb/python/startme"
fi

PROJECT_NAME="$(basename "${PROJECT_DIR}")"
DATE=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="${PROJECT_NAME}_${DATE}.tar.gz"
ARCHIVE_PATH="/tmp/${ARCHIVE_NAME}"

# Destinations rclone — adapter selon votre config (rclone listremotes)
GDRIVE_DEST="gdrive:BU_${PROJECT_NAME}"
PROTON_DEST="protondrive:BU_${PROJECT_NAME}"

# Sauvegarde SSH locale (ignorée si l'hôte est hors ligne)
SSH_HOST="10.0.0.29"
SSH_USER="nimzo"
SSH_DEST_DIR="~/BU_${PROJECT_NAME}"
# ───────────────────────────────────────────────────────────────────────────────

if [[ ! -d "${PROJECT_DIR}" ]]; then
  echo "ERREUR : répertoire introuvable : ${PROJECT_DIR}"
  exit 1
fi

echo "==> Projet : ${PROJECT_NAME} (${PROJECT_DIR})"

# ── Fichiers temporaires ────────────────────────────────────────────────────────
EXCLUDE_FILE=$(mktemp)
GDRIVE_LOG=$(mktemp)
PROTON_LOG=$(mktemp)
SSH_LOG=$(mktemp)
trap 'rm -f "${EXCLUDE_FILE}" "${GDRIVE_LOG}" "${PROTON_LOG}" "${SSH_LOG}"' EXIT

# ── Fichiers d'exclusions ──────────────────────────────────────────────────────
# Exclusions génériques (tout projet Python/Django)
cat > "${EXCLUDE_FILE}" << EXCLUDES
# Secrets et données sensibles
${PROJECT_NAME}/.env

# Environnement virtuel (regen : pip install -r requirements.txt)
${PROJECT_NAME}/venv
${PROJECT_NAME}/.venv

# Historique Git — supprimer cette ligne si pas de dépôt distant
${PROJECT_NAME}/.git

# Config IDE locale
${PROJECT_NAME}/.idea
${PROJECT_NAME}/.vscode

# Base de données SQLite
# ${PROJECT_NAME}/db.sqlite3

# Fichiers statiques Django collectés (regen : collectstatic)
# ${PROJECT_NAME}/static

# Bytecode Python
*/__pycache__
*.pyc
*.pyo

# Artefacts ML lourds (régénérables par ré-entraînement)
# Poids, checkpoints et états d'optimiseur — souvent plusieurs Go par fichier.
*.pt
*.pth
*.ckpt
*.safetensors
*.bin
*.onnx
*.gguf
*.h5

# Archives (évite les doublons)
*.tar.gz
*.zip

# Images de debug/test
*.png
*.jpg
*.jpeg

# Logs
*.log
EXCLUDES

# Exclusions spécifiques au projet (optionnel)
PROJECT_EXCLUDE="${PROJECT_DIR}/.backup_exclude"
if [[ -f "${PROJECT_EXCLUDE}" ]]; then
  echo "    Exclusions projet : ${PROJECT_EXCLUDE}"
  # Préfixer les chemins relatifs avec le nom du projet
  while IFS= read -r line || [[ -n "${line}" ]]; do
    [[ "${line}" =~ ^#.*$ || -z "${line}" ]] && echo "${line}" >> "${EXCLUDE_FILE}" && continue
    # Si la ligne ne commence pas par * ou /, préfixer avec le nom du projet
    if [[ "${line}" != /* && "${line}" != \** ]]; then
      echo "${PROJECT_NAME}/${line}" >> "${EXCLUDE_FILE}"
    else
      echo "${line}" >> "${EXCLUDE_FILE}"
    fi
  done < "${PROJECT_EXCLUDE}"
fi

# ── Mode dry-run ───────────────────────────────────────────────────────────────
if [[ "${MODE}" == "dryrun" ]]; then
  echo "=== DRY RUN — fichiers qui seraient archivés ==="
  tar -czf /dev/null \
    -C "$(dirname "${PROJECT_DIR}")" \
    --exclude-from="${EXCLUDE_FILE}" \
    --wildcards \
    --verbose \
    "${PROJECT_NAME}" 2>&1 | grep -v "^tar:" || true
  echo ""
  echo "Pour créer l'archive : $0 ${PROJECT_DIR}"
  echo "Pour archive locale  : $0 ${PROJECT_DIR} --local"
  exit 0
fi

# ── Création de l'archive ──────────────────────────────────────────────────────
echo "==> Création de l'archive : ${ARCHIVE_NAME}"

tar -czf "${ARCHIVE_PATH}" \
  -C "$(dirname "${PROJECT_DIR}")" \
  --exclude-from="${EXCLUDE_FILE}" \
  --wildcards \
  "${PROJECT_NAME}"

SIZE=$(du -sh "${ARCHIVE_PATH}" | cut -f1)
echo "    Taille : ${SIZE}"

# ── Upload ou conservation locale ─────────────────────────────────────────────
if [[ "${MODE}" == "upload" ]]; then
  if ! command -v rclone &>/dev/null; then
    echo ""
    echo "ERREUR : rclone n'est pas installe."
    echo "  sudo apt install rclone"
    echo "  rclone config   # configurer gdrive et protondrive"
    echo ""
    echo "Archive conservee localement : ${ARCHIVE_PATH}"
    exit 1
  fi

  echo "==> Upload en parallele vers les destinations..."
  echo "    -> Google Drive : ${GDRIVE_DEST}"
  echo "    -> Proton Drive : ${PROTON_DEST}"

  rclone copy "${ARCHIVE_PATH}" "${GDRIVE_DEST}" \
    --log-file="${GDRIVE_LOG}" --log-level INFO &
  PID_GDRIVE=$!

  rclone copy "${ARCHIVE_PATH}" "${PROTON_DEST}" \
    --log-file="${PROTON_LOG}" --log-level INFO &
  PID_PROTON=$!

  # SSH : vérification connectivité (timeout 3s) puis rsync en parallèle
  SSH_AVAILABLE=false
  if ssh -o ConnectTimeout=3 -o BatchMode=yes \
         "${SSH_USER}@${SSH_HOST}" "mkdir -p ${SSH_DEST_DIR}" 2>/dev/null; then
    SSH_AVAILABLE=true
    echo "    -> SSH  ${SSH_USER}@${SSH_HOST}:${SSH_DEST_DIR}"
    rsync -az "${ARCHIVE_PATH}" \
      "${SSH_USER}@${SSH_HOST}:${SSH_DEST_DIR}/" >"${SSH_LOG}" 2>&1 &
    PID_SSH=$!
  else
    echo "    -> SSH  ${SSH_HOST} : hors ligne, ignoré"
  fi

  wait "${PID_GDRIVE}"; STATUS_GDRIVE=$?
  wait "${PID_PROTON}"; STATUS_PROTON=$?
  if [[ "${SSH_AVAILABLE}" == true ]]; then
    wait "${PID_SSH}"; STATUS_SSH=$?
  fi

  echo ""
  echo "==> Resultats :"
  ERRORS=0

  if [[ ${STATUS_GDRIVE} -eq 0 ]]; then
    echo "    [OK]    Google Drive : ${GDRIVE_DEST}/${ARCHIVE_NAME}"
  else
    echo "    [ECHEC] Google Drive :"
    cat "${GDRIVE_LOG}"
    ERRORS=$((ERRORS + 1))
  fi

  if [[ ${STATUS_PROTON} -eq 0 ]]; then
    echo "    [OK]    Proton Drive : ${PROTON_DEST}/${ARCHIVE_NAME}"
  else
    echo "    [ECHEC] Proton Drive :"
    cat "${PROTON_LOG}"
    ERRORS=$((ERRORS + 1))
  fi

  if [[ "${SSH_AVAILABLE}" == true ]]; then
    if [[ ${STATUS_SSH} -eq 0 ]]; then
      echo "    [OK]    SSH ${SSH_USER}@${SSH_HOST}:${SSH_DEST_DIR}/${ARCHIVE_NAME}"
    else
      echo "    [ECHEC] SSH ${SSH_USER}@${SSH_HOST} :"
      cat "${SSH_LOG}"
      ERRORS=$((ERRORS + 1))
    fi
  else
    echo "    [IGNORE] SSH ${SSH_HOST} : hors ligne"
  fi

  echo ""
  if [[ ${ERRORS} -eq 0 ]]; then
    rm -f "${ARCHIVE_PATH}"
    echo "==> Termine. Archive locale supprimee."
  else
    echo "AVERTISSEMENT : ${ERRORS} upload(s) en echec. Archive conservee : ${ARCHIVE_PATH}"
    exit 1
  fi

else
  # --local : on déplace l'archive dans le répertoire courant
  FINAL_PATH="${PROJECT_DIR}/${ARCHIVE_NAME}"
  mv "${ARCHIVE_PATH}" "${FINAL_PATH}"
  echo "==> Archive locale : ${FINAL_PATH}"
fi
