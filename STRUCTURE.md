startme/
├── startme/                    # Configuration principale Django
│   ├── settings.py             # Paramètres (DB, apps, static files, variables .env)
│   ├── urls.py                 # Routes racine
│   ├── asgi.py
│   └── wsgi.py
├── dashboard/                  # Application principale
│   ├── models.py               # Modèles de données (Page, Widget, Link)
│   ├── views.py                # Logique métier et endpoints HTMX
│   ├── urls.py                 # Routes de l'application
│   ├── admin.py                # Enregistrement des modèles dans l'admin Django
│   ├── migrations/             # Migrations Django (auto-générées)
│   ├── templates/
│   │   └── dashboard/
│   │       └── index.html      # Template principal du tableau de bord
│   ├── templatetags/
│   │   └── dashboard_extras.py # Filtres et tags Django personnalisés
│   └── management/
│       └── commands/
│           ├── seed_db.py      # Peuple la DB avec des données initiales
│           └── import_json.py  # Importe des données depuis un fichier JSON
├── templates/
│   └── partials/               # Fragments HTML pour HTMX
│       ├── widget.html         # Rendu d'un widget (dispatch selon widget_type)
│       ├── widget_title.html   # Titre d'un widget (lecture)
│       ├── widget_title_form.html # Titre d'un widget (édition)
│       ├── link_item.html      # Item de lien (widget type 'list')
│       ├── link_form.html      # Formulaire d'ajout/édition de lien
│       ├── command_item.html   # Item de commande shell (widget type 'command')
│       ├── snippet_item.html   # Item de snippet à copier (widget type 'snippet')
│       ├── nav_header.html     # En-tête de navigation
│       ├── menus.html          # Menus contextuels
│       ├── modals.html         # Fenêtres modales
│       ├── scripts.html        # Inclusion des scripts JS
│       ├── network_info.html   # Widget IP locale et publique
│       ├── system_monitor.html # Widget monitoring système
│       └── widgets_infos.html  # Informations globales des widgets
├── static/
│   └── js/
│       ├── htmx.js             # Librairie HTMX
│       ├── sortable.js         # Drag & drop des widgets
│       └── tailwind.js         # Framework CSS Tailwind (CDN local)
├── scripts/                    # Scripts utilitaires one-shot
│   ├── add_ia_links.py         # Ajout de liens IA en masse
│   └── install_dashboard.py   # Script d'installation automatique
├── .env                        # Variables d'environnement (secret, port…)
├── .env.example                # Template de configuration .env
├── requirements.txt            # Dépendances Python
├── manage.py                   # Point d'entrée Django
├── run.sh                      # Script de lancement rapide
├── start_dashboard.sh          # Script de démarrage complet
├── export_project.py           # Export du projet en archive ZIP
├── get_static_files.py         # Récupération des fichiers statiques
├── data_export.json            # Données exportées (backup)
├── db.sqlite3                  # Base de données locale
├── changelog                   # Journal des changements
├── README.md                   # Documentation utilisateur
├── AI_CONTEXT.md               # Contexte du projet pour l'IA
├── DEVELOPMENT.md              # Notes de développement
├── APPARENCE.md                # Documentation sur le thème/apparence
└── STRUCTURE.md                # Ce fichier
