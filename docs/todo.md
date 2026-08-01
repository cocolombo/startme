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

- [-] **Route orpheline `toggle_widget_collapse`** (`urls.py:31`)
  Vérification faite : la route n'est pas présente dans `urls.py`. Fausse alerte.

- [x] **`requirements.txt` incomplet**
  Ajout de `psutil==7.2.1`, `requests==2.32.5`, `django-htmx==1.27.0` (versions installées dans le venv).

- [x] **`link_form.html` utilise `location.reload()`** (`link_form.html:23`)
  Remplacé par un `hx-get` vers la nouvelle vue `cancel_edit_link`. Retourne le bon partial selon le `widget_type` (link, command, snippet).

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

- [x] **Météo** : Ville et coordonnées configurables via `WEATHER_CITY`, `WEATHER_LAT`, `WEATHER_LON`, `WEATHER_TIMEZONE` dans `.env`.
- [x] **Horloges** : Fuseaux configurables via `CLOCK_TIMEZONES` dans `.env`. Le JS utilise `data-timezone` au lieu d'IDs fixes.
- [x] **Port** : Aligné sur `8800` dans les deux scripts. Documenté dans `.env.example`.

---

## ✨ Fonctionnalités à envisager

- [-] **Authentification** : Non nécessaire (usage local uniquement sur 127.0.0.1).
- [-] **Import de favoris** : Importer un fichier HTML d'export de navigateur (Chrome/Firefox) pour peupler les liens en masse.
- [x] **Choix du widget cible** lors d'un déplacement de lien vers une autre page (voir bug ci-dessus).
- [x] **Sidebar hamburger** : Arborescence hiérarchique Pages → Catégories pour navigation rapide. Ouverte via bouton ☰ dans la nav.
- [x] **Réordonner les pages via la sidebar** : Drag-and-drop sur la poignée `⠿` de chaque page. Appelle `POST /api/update-page-order/`.
- [x] **Déplacer un widget entre pages via la sidebar** : Drag-and-drop dans la sidebar hamburger (SortableJS `group: sidebar-widgets`). Appelle `POST /widget/move/<id>/` avec CSRF. Le `href` est mis à jour sans rechargement.
- [x] **Widget Disques** : Affichage style `df -h` avec point de montage abrégé et code couleur selon le taux de remplissage (>75% jaune, >90% rouge). Dans `system_monitor.html`.
- [x] **Bouton Annuler + touche Escape** : Les 3 formulaires d'ajout (liste, commande, snippet) ont un bouton Annuler et répondent à la touche Escape. Un handler global dans `scripts.html` ferme aussi les modales.
- [ ] **Mode Clair / Sombre** toggle (actuellement dark mode fixe).
- [x] **Favicon automatique** : Implémenté via `https://www.google.com/s2/favicons?domain=...` dans `link_item.html`. Fonctionne pour les URLs web ; sans effet sur les chemins locaux ou commandes (comportement attendu).
- [-] **Déploiement** : Non applicable (usage local uniquement).

---

## 🔍 Observations (passe du 2026-03-21)

- **Recherche live** (`scripts.html:338`) : Le sélecteur `.group\/widget` (avec antislash d'échappement JS) cible la classe Tailwind `group/widget`. À valider en situation réelle car les slashes dans les classes Tailwind peuvent causer des surprises selon la version utilisée.
- **Gestion d'erreur météo** (`scripts.html:254`) : En cas d'échec de l'API météo, l'interface affiche juste "Erreur" sans détail. Un message plus informatif (ex : clé manquante, ville inconnue) serait utile.
- **Page Infos et recherche** : Le filtre live search ne s'applique pas à la page "Infos" (widgets spéciaux hors grille normale). Comportement cohérent mais à documenter.
