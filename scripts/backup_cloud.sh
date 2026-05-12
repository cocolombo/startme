#!/usr/bin/env bash
# Sauvegarde du projet startme vers Google Drive ET Proton Drive via rclone.
# L'archive est créée une seule fois puis uploadée en parallèle vers les deux destinations.
#
# Prérequis : rclone installé et configuré pour les deux remotes (rclone config)
#   - remote "gdrive"       : type Google Drive
#   - remote "protondrive"  : type Proton Drive
#
# Usage :
#   ./scripts/backup_cloud.sh              # archive + upload vers les deux clouds
#   ./scripts/backup_cloud.sh --local      # archive locale uniquement (dans /tmp)
#   ./scripts/backup_cloud.sh --dry-run    # liste les fichiers sans créer d'archive

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────────
PROJECT_DIR="/media/120gb/python/startme"
PROJECT_NAME="startme"
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

MODE="upload"
case "${1:-}" in
  --local)    MODE="local" ;;
  --dry-run)  MODE="dryrun" ;;
esac

# ── Fichiers temporaires ────────────────────────────────────────────────────────
EXCLUDE_FILE=$(mktemp)
GDRIVE_LOG=$(mktemp)
PROTON_LOG=$(mktemp)
SSH_LOG=$(mktemp)
trap 'rm -f "${EXCLUDE_FILE}" "${GDRIVE_LOG}" "${PROTON_LOG}" "${SSH_LOG}"' EXIT

# ── Fichiers d'exclusions ──────────────────────────────────────────────────────
cat > "${EXCLUDE_FILE}" << 'EXCLUDES'
# Secrets et données sensibles
startme/.env

# Environnement virtuel (regen : pip install -r requirements.txt)
startme/venv

# Historique Git — supprimer cette ligne si pas de dépôt distant
startme/.git

# Config IDE locale (peut contenir des credentials DB)
startme/.idea

# Base de données SQLite — préférer un export JSON via :
#   python manage.py dumpdata --indent 2 > data_export.json
# Décommenter la ligne suivante pour exclure la BDD :
# startme/db.sqlite3

# Export de données statique (régénérable avec dumpdata)
startme/data_export.json

# Fichiers statiques Django collectés (regen : python manage.py collectstatic)
# Décommenter si static/ ne contient que des fichiers collectés :
# startme/static

# Bytecode Python (régénéré automatiquement)
*/__pycache__
*.pyc
*.pyo

# Archives (évite les doublons dans la sauvegarde)
*.tar.gz
*.zip

# Images de debug/test
*.png
*.jpg
*.jpeg

# Logs (transitoires, sans valeur de restauration)
*.log
startme/startup.log
EXCLUDES

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
  echo "Pour créer l'archive : $0"
  echo "Pour archive locale  : $0 --local"
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
    # Conserver l'archive si au moins un upload a echoue
    echo "AVERTISSEMENT : ${ERRORS} upload(s) en echec. Archive conservee : ${ARCHIVE_PATH}"
    exit 1
  fi

else
  # --local : on déplace l'archive dans le répertoire courant
  FINAL_PATH="${PROJECT_DIR}/${ARCHIVE_NAME}"
  mv "${ARCHIVE_PATH}" "${FINAL_PATH}"
  echo "==> Archive locale : ${FINAL_PATH}"
fi
