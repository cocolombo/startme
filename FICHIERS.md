# Index des fichiers du projet

Tous les fichiers du projet listés par ordre alphabétique, hors `venv/`, `migrations/`, `.git/` et `.idea/`.

| Fichier | Description |
|---|---|
| `.backup_exclude` | Liste des chemins exclus lors des sauvegardes cloud (via `backup_cloud.sh`) |
| `.env` | Variables d'environnement locales (non versionnées) — voir `.env.example` |
| `.env.example` | Modèle documenté des variables d'environnement nécessaires au projet |
| `.gitignore` | Fichiers et dossiers ignorés par Git |
| `AI_CONTEXT.md` | Résumé du contexte technique du projet à destination des assistants IA |
| `APPARENCE.md` | Guide de personnalisation de l'interface (Tailwind CSS, templates) |
| `CHEATSHEET.md` | Aide-mémoire des commandes et opérations courantes du projet |
| `CLAUDE.md` | Instructions de comportement pour Claude Code (style, raisonnement, commits) |
| `changelog` | Historique des modifications notables du projet |
| `dashboard/admin.py` | Configuration de l'interface d'administration Django pour les modèles |
| `dashboard/management/__init__.py` | Marqueur de package Python pour le module `management` |
| `dashboard/management/commands/__init__.py` | Marqueur de package Python pour les commandes de management |
| `dashboard/management/commands/import_json.py` | Commande Django pour importer des données depuis un fichier JSON |
| `dashboard/management/commands/seed_db.py` | Commande Django pour peupler la base de données avec des données initiales |
| `dashboard/models.py` | Modèles de données Django (Page, Widget, Link, Snippet, TodoItem, CommandLog…) |
| `dashboard/templates/dashboard/index.html` | Template principal de la page dashboard |
| `dashboard/templatetags/__init__.py` | Marqueur de package Python pour les template tags |
| `dashboard/templatetags/dashboard_extras.py` | Filtres et tags Jinja/Django personnalisés (ex. `get_item`) |
| `dashboard/urls.py` | Routes URL de l'application `dashboard` |
| `dashboard/views.py` | Vues Django : rendu des pages, gestion HTMX, CRUD des widgets/liens/todos |
| `DEVELOPMENT.md` | Guide du développeur : stack, architecture, conventions, workflow |
| `export_project.py` | Script utilitaire qui concatène les fichiers source du projet pour partage IA |
| `fonctionnalites_TODO.md` | Liste des fonctionnalités envisagées ou en cours de réflexion |
| `get_static_files.py` | Script de téléchargement des librairies JS statiques (HTMX, Sortable, Tailwind) |
| `goal.png` | Capture d'écran de référence de l'interface cible |
| `grilleAcces.png` | Diagramme ou maquette de la grille d'accès rapide |
| `manage.py` | Point d'entrée CLI Django (migrations, serveur, commandes custom) |
| `README.md` | Présentation du projet, installation rapide, utilisation |
| `requirements.txt` | Dépendances Python du projet |
| `run.sh` | Script shell de lancement rapide du serveur de développement |
| `scripts/add_ia_links.py` | Script one-shot pour peupler la page IA avec des liens prédéfinis en base |
| `scripts/BACKUP.md` | Documentation du système de sauvegarde cloud |
| `scripts/backup_cloud.sh` | Script de sauvegarde multi-destinations (GDrive, Proton Drive, SSH) |
| `scripts/backup_exclude.template` | Modèle de fichier `.backup_exclude` à copier par projet |
| `scripts/install_dashboard.py` | Script d'installation automatisée du projet (structure, fichiers initiaux) |
| `start_dashboard.sh` | Script shell alternatif de démarrage (active le venv et lance le serveur) |
| `startme/__init__.py` | Marqueur de package Python pour le module de configuration Django |
| `startme/asgi.py` | Point d'entrée ASGI (déploiement async) |
| `startme/settings.py` | Configuration Django centrale (DB, apps installées, static files, variables .env) |
| `startme/urls.py` | Routes URL racine du projet Django |
| `startme/wsgi.py` | Point d'entrée WSGI (déploiement serveur classique) |
| `static/js/htmx.js` | Librairie HTMX (interactions AJAX sans JavaScript custom) |
| `static/js/sortable.js` | Librairie SortableJS (drag-and-drop des widgets et liens) |
| `static/js/tailwind.js` | Librairie Tailwind CSS (styles utilitaires, chargé localement) |
| `STRUCTURE.md` | Arborescence commentée du projet |
| `templates/partials/command_history.html` | Fragment HTMX : liste de l'historique des commandes shell |
| `templates/partials/command_item.html` | Fragment HTMX : rendu d'un item de l'historique des commandes |
| `templates/partials/link_form.html` | Fragment HTMX : formulaire d'ajout/édition d'un lien |
| `templates/partials/link_item.html` | Fragment HTMX : rendu d'un lien dans un widget |
| `templates/partials/menus.html` | Fragment : menus contextuels (page, widget) |
| `templates/partials/modals.html` | Fragment : boîtes de dialogue modales (confirmation, saisie) |
| `templates/partials/nav_header.html` | Fragment : en-tête de navigation et onglets de pages |
| `templates/partials/network_info.html` | Fragment : widget d'affichage des informations réseau |
| `templates/partials/scripts.html` | Fragment : inclusion des scripts JS globaux |
| `templates/partials/search_results.html` | Fragment HTMX : résultats de la barre de recherche |
| `templates/partials/sidebar_menu.html` | Fragment : menu latéral de navigation entre pages |
| `templates/partials/snippet_item.html` | Fragment HTMX : rendu d'un snippet de code ou texte |
| `templates/partials/system_monitor.html` | Fragment : widget de monitoring système (CPU, RAM, disque) |
| `templates/partials/todo_item.html` | Fragment HTMX : rendu d'un item de la liste TODO |
| `templates/partials/todo_items_fragment.html` | Fragment HTMX : liste complète des items TODO (rechargée dynamiquement) |
| `templates/partials/widget.html` | Fragment HTMX : rendu générique d'un widget (conteneur, titre, contenu) |
| `templates/partials/widget_title.html` | Fragment HTMX : affichage du titre d'un widget |
| `templates/partials/widget_title_form.html` | Fragment HTMX : formulaire d'édition du titre d'un widget |
| `templates/partials/widgets_infos.html` | Fragment : section "Infos" avec les widgets spéciaux (météo, bourse…) |
| `TODO.md` | Tâches immédiates et bugs connus à traiter |
| `tools/coffre.html` | Page HTML autonome (hors Django) : coffre-fort de notes chiffrées local |
| `TROUBLESHOOTING.md` | Guide de dépannage : problèmes courants et solutions |
| `WIDGETS_API.md` | Guide de création de nouveaux widgets spéciaux (architecture et conventions) |
