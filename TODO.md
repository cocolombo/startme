# TODO — Dashboard Perso

## 🐛 Bugs & Qualité du code

- [x] **`Link.url` mauvais type de champ** (`models.py:74`)
  Migré de `URLField` vers `CharField(max_length=500)` — migration `0009_link_url_charfield`.

- [x] **`icon_url` inutilisé** (`models.py:75`)
  Champ supprimé du modèle, de `link_item.html` et de `import_json.py` — migration `0010_remove_link_icon_url`.

- [x] **`rename_page` ne gère pas les slugs dupliqués** (`views.py:233`)
  Logique de déduplication ajoutée (identique à `create_page`, avec `.exclude(id=page.id)` pour ignorer la page elle-même).

- [x] **`bare except:` dans 4 vues** (`views.py:110, 541, 703, 710`)
  Remplacés par `except Exception` dans `update_widget_order`, `update_page_order` et `get_network_info`.

- [x] **`print()` de debug en production** (`views.py:519, 625`)
  4 `print()` remplacés par `logger = logging.getLogger(__name__)` avec les niveaux appropriés (`warning`, `debug`, `error`, `exception`).

- [x] **Chemins de disques hardcodés** (`views.py:437-440`)
  Déplacés dans `.env` via `MONITOR_DISKS="Nom:/chemin|Nom:/chemin"`, parsé dans `settings.py`.

- [x] **`move_link_to_page` cible toujours le 1er widget** (`views.py:135`)
  Sous-menu à deux niveaux (Page → Widgets). La vue utilise `target_widget_id` directement.

---

## 🧹 Nettoyage du dépôt

- [x] Supprimer `templates/partials/widgets_infos.html.bak` (fichier de sauvegarde commité)
- [x] Supprimer ou archiver `startme_20260210.tar.gz` de la racine du projet (archive volumineuse)
- [x] Archiver les scripts one-shot (`add_ia_links.py`, `install_dashboard.py`) dans un dossier `scripts/`
- [x] Mettre à jour le `changelog` (widget Réseau, chaînes YT IA, changement de port non documentés)
- [x] Corriger le README : référence à `.venv` → `venv/`
- [x] Ajouter `*.tar.gz`, `startup.log`, `data_export.json` dans `.gitignore`

---

## ⚙️ Configuration

- [ ] **Météo** : Ville codée en dur dans `widgets_infos.html` (`Montréal, QC`). Rendre configurable via `.env`.
- [ ] **Horloges** : Fuseaux (Paris, SF, Pékin) hardcodés dans le HTML. Rendre configurables.
- [ ] **Port** : Actuellement `8800` dans les scripts de lancement, documenter clairement dans `.env.example`.

---

## ✨ Fonctionnalités à envisager

- [ ] **Authentification** : Le dashboard est accessible sans mot de passe. Ajouter une protection basique (`LOGIN_REQUIRED` ou `.env` avec token).
- [ ] **Import de favoris** : Importer un fichier HTML d'export de navigateur (Chrome/Firefox) pour peupler les liens en masse.
- [ ] **Choix du widget cible** lors d'un déplacement de lien vers une autre page (voir bug ci-dessus).
- [ ] **Mode Clair / Sombre** toggle (actuellement dark mode fixe).
- [ ] **Favicon automatique** : Récupérer et afficher le favicon de chaque lien (`https://www.google.com/s2/favicons?domain=...`).
- [ ] **Déploiement** : Documenter la mise en production (systemd service ou Docker Compose).
