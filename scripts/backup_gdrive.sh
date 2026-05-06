#!/usr/bin/env bash
# Sauvegarde du projet startme vers Google Drive via rclone.
# Prérequis : rclone installé et configuré (rclone config)
#
# Usage :
#   ./scripts/backup_gdrive.sh              # archive + upload vers Drive
#   ./scripts/backup_gdrive.sh --local      # archive locale uniquement (dans /tmp)
#   ./scripts/backup_gdrive.sh --dry-run    # liste les fichiers sans créer d'archive

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────────
PROJECT_DIR="/media/120gb/python/startme"
PROJECT_NAME="startme"
DATE=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="${PROJECT_NAME}_${DATE}.tar.gz"
ARCHIVE_PATH="/tmp/${ARCHIVE_NAME}"

# Destination rclone — adapter selon votre config (rclone listremotes)
GDRIVE_DEST="gdrive:backups/${PROJECT_NAME}"
# ───────────────────────────────────────────────────────────────────────────────

MODE="upload"
case "${1:-}" in
  --local)    MODE="local" ;;
  --dry-run)  MODE="dryrun" ;;
esac

# ── Fichiers d'exclusions ──────────────────────────────────────────────────────
EXCLUDE_FILE=$(mktemp)
trap 'rm -f "${EXCLUDE_FILE}"' EXIT

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
    echo "ERREUR : rclone n'est pas installé."
    echo "  sudo apt install rclone"
    echo "  rclone config   # suivre l'assistant pour configurer Google Drive"
    echo ""
    echo "Archive conservée localement : ${ARCHIVE_PATH}"
    exit 1
  fi

  echo "==> Upload vers ${GDRIVE_DEST}..."
  rclone copy "${ARCHIVE_PATH}" "${GDRIVE_DEST}" --progress

  rm -f "${ARCHIVE_PATH}"
  echo "==> Terminé. Archive disponible : ${GDRIVE_DEST}/${ARCHIVE_NAME}"

else
  # --local : on déplace l'archive dans le répertoire courant
  FINAL_PATH="${PROJECT_DIR}/${ARCHIVE_NAME}"
  mv "${ARCHIVE_PATH}" "${FINAL_PATH}"
  echo "==> Archive locale : ${FINAL_PATH}"
fi
