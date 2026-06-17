#!/usr/bin/env bash
# Installe le hook pre-commit versionne (scripts/git-hooks/pre-commit)
# dans le repertoire .git/hooks d'un depot.
#
# Usage :
#   ./scripts/install-git-hooks.sh                      # depot courant
#   ./scripts/install-git-hooks.sh /chemin/vers/projet  # autre depot
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/git-hooks" && pwd)"
HOOK_SRC="${SOURCE_DIR}/pre-commit"

if [[ ! -f "$HOOK_SRC" ]]; then
  echo "ERREUR : hook source introuvable : ${HOOK_SRC}" >&2
  exit 1
fi

TARGET="${1:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
if [[ -z "$TARGET" ]]; then
  echo "ERREUR : preciser un depot : $0 /chemin/vers/projet" >&2
  exit 1
fi

GIT_DIR="$(git -C "$TARGET" rev-parse --git-dir 2>/dev/null || true)"
if [[ -z "$GIT_DIR" ]]; then
  echo "ERREUR : ${TARGET} n'est pas un depot git." >&2
  exit 1
fi
# git-dir peut etre relatif au depot cible : le rendre absolu.
case "$GIT_DIR" in
  /*) : ;;
  *)  GIT_DIR="${TARGET%/}/${GIT_DIR}" ;;
esac

DEST="${GIT_DIR}/hooks/pre-commit"
mkdir -p "$(dirname "$DEST")"

# Sauvegarder un hook preexistant different avant de l'ecraser.
if [[ -f "$DEST" ]] && ! cmp -s "$HOOK_SRC" "$DEST"; then
  BACKUP="${DEST}.bak.$(date +%Y%m%d_%H%M%S)"
  cp "$DEST" "$BACKUP"
  echo "    Hook existant sauvegarde : ${BACKUP}"
fi

cp "$HOOK_SRC" "$DEST"
chmod +x "$DEST"
echo "[OK] pre-commit installe dans ${TARGET}"
echo "     -> ${DEST}"