# TODO — Dashboard Perso

## 🐛 Bugs & Qualité du code

- [x] **`Link.url` mauvais type de champ** (`models.py:74`)
  Migré de `URLField` vers `CharField(max_length=500)` — migration `0009_link_url_charfield`.

- [ ] **`icon_url` inutilisé** (`models.py:75`)
  Le champ existe dans le modèle mais n'est jamais utilisé côté frontend. Supprimer ou implémenter.

- [ ] **`rename_page` ne gère pas les slugs dupliqués** (`views.py:233`)
  `create_page` a une logique de déduplication de slug (`ma-page`, `ma-page-2`, etc.) mais `rename_page` ne l'a pas — risque de collision.

- [ ] **`bare except:` dans 4 vues** (`views.py:110, 541, 703, 710`)
  Les blocs `except:` sans type capturent tous les cas (y compris `KeyboardInterrupt`). Remplacer par `except Exception`.

- [ ] **`print()` de debug en production** (`views.py:519, 625`)
  Deux `print()` actifs dans `open_local_file` et `run_command`. Remplacer par un logger Django.

- [ ] **Chemins de disques hardcodés** (`views.py:437-440`)
  Les chemins `/media/nimzo/3tb` et `/media/120gb` sont en dur dans `system_monitor()`. Les déplacer dans `.env` ou `settings.py`.

- [ ] **`move_link_to_page` cible toujours le 1er widget** (`views.py:135`)
  Quand on déplace un lien vers une autre page, il atterrit dans `widgets.first()` sans que l'utilisateur puisse choisir le widget cible.

---

## 🧹 Nettoyage du dépôt

- [ ] Supprimer `templates/partials/widgets_infos.html.bak` (fichier de sauvegarde commité)
- [ ] Supprimer ou archiver `startme_20260210.tar.gz` de la racine du projet (archive volumineuse)
- [ ] Archiver les scripts one-shot (`add_ia_links.py`, `install_dashboard.py`) dans un dossier `scripts/`
- [ ] Mettre à jour le `changelog` (widget Réseau, chaînes YT IA, changement de port non documentés)
- [ ] Corriger le README : référence à `.venv` alors que le projet utilise `venv/`
- [ ] Ajouter `venv/`, `*.tar.gz`, `startup.log`, `data_export.json` dans `.gitignore`

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
