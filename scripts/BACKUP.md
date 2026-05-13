# Documentation — backup_cloud.sh

Script de sauvegarde universel pour projets Python/Django.
Crée une archive `.tar.gz` et l'envoie en parallèle vers trois destinations.

---

## Destinations

| Destination | Type | Condition |
|---|---|---|
| Google Drive | rclone remote `gdrive` | Toujours tentée |
| Proton Drive | rclone remote `protondrive` | Toujours tentée |
| `nimzo@10.0.0.29` | rsync via SSH | Ignorée si hors ligne |

---

## Prérequis

### 1. rclone installé et configuré

```bash
sudo apt install rclone
rclone config
```

Deux remotes requis (noms exacts) :
- `gdrive` — type Google Drive
- `protondrive` — type Proton Drive

Vérifier : `rclone listremotes`

### 2. Clé SSH autorisée sur la machine de destination

```bash
ssh-copy-id nimzo@10.0.0.29
```

Tester : `ssh nimzo@10.0.0.29 echo ok`

---

## Usage

```bash
# Sauvegarder startme (projet par défaut)
./scripts/backup_cloud.sh

# Sauvegarder un autre projet
./scripts/backup_cloud.sh /media/120gb/python/redico-ai

# Vérifier les fichiers qui seraient archivés (sans créer d'archive)
./scripts/backup_cloud.sh /media/120gb/python/redico-ai --dry-run

# Créer une archive locale uniquement (sans upload)
./scripts/backup_cloud.sh /media/120gb/python/redico-ai --local
```

Les arguments `--dry-run` et `--local` peuvent être placés avant ou après le chemin du projet.

---

## Exclusions

### Exclusions génériques (tous les projets)

Appliquées automatiquement par le script :

| Exclusion | Raison |
|---|---|
| `venv/`, `.venv/` | Environnement virtuel (regen : `pip install -r requirements.txt`) |
| `.git/` | Historique Git |
| `.env` | Secrets |
| `.idea/`, `.vscode/` | Config IDE |
| `__pycache__/`, `*.pyc` | Bytecode Python |
| `*.tar.gz`, `*.zip` | Archives existantes |
| `*.log` | Logs transitoires |

### Exclusions spécifiques par projet

Créer un fichier `.backup_exclude` à la racine du projet.
Les chemins sont **relatifs à la racine du projet**.

```
# Exemple : redico-ai/.backup_exclude

# Base de données
redico-ai.sqlite3

# Dumps SQL
backup.sql
dump_local.sql

# Fichiers statiques collectés
staticfiles

# Dépendances JS
theme/static_src/node_modules
```

Règles de syntaxe :
- Lignes commençant par `#` → commentaires ignorés
- Chemins relatifs → préfixés automatiquement avec le nom du projet
- Patterns globaux (`*.ext`, `**/dossier`) → passés tels quels

---

## Ajouter un nouveau projet

1. Copier le template d'exclusions à la racine du projet :
   ```bash
   cp startme/scripts/backup_exclude.template /chemin/vers/projet/.backup_exclude
   ```
2. Éditer `.backup_exclude` — décommenter ce qui s'applique, supprimer le reste
3. Vérifier le contenu qui sera archivé :
   ```bash
   ./scripts/backup_cloud.sh /chemin/vers/projet --dry-run
   ```
4. Lancer la sauvegarde :
   ```bash
   ./scripts/backup_cloud.sh /chemin/vers/projet
   ```

Aucune modification du script n'est nécessaire.

---

## Structure des sauvegardes

Les archives sont nommées `{projet}_{YYYYMMDD_HHMMSS}.tar.gz` et déposées dans :

| Destination | Dossier |
|---|---|
| Google Drive | `BU_{projet}/` |
| Proton Drive | `BU_{projet}/` |
| `nimzo@10.0.0.29` | `~/BU_{projet}/` |

---

## Exemple de sortie

```
==> Projet : redico-ai (/media/120gb/python/redico-ai)
    Exclusions projet : /media/120gb/python/redico-ai/.backup_exclude
==> Création de l'archive : redico-ai_20260512_143022.tar.gz
    Taille : 8.2M
==> Upload en parallele vers les destinations...
    -> Google Drive : gdrive:BU_redico-ai
    -> Proton Drive : protondrive:BU_redico-ai
    -> SSH  nimzo@10.0.0.29:~/BU_redico-ai

==> Resultats :
    [OK]    Google Drive : gdrive:BU_redico-ai/redico-ai_20260512_143022.tar.gz
    [OK]    Proton Drive : protondrive:BU_redico-ai/redico-ai_20260512_143022.tar.gz
    [OK]    SSH nimzo@10.0.0.29:~/BU_redico-ai/redico-ai_20260512_143022.tar.gz

==> Termine. Archive locale supprimee.
```

Si la machine SSH est hors ligne :
```
    -> SSH  10.0.0.29 : hors ligne, ignoré
    ...
    [IGNORE] SSH 10.0.0.29 : hors ligne
```