# CLAUDE.md — Spécifications locales du projet

## 1. Rappel des règles globales
Applique strictement les directives globales : plan d'action sous forme de liste
avant tout code, pas d'accents graves dans les blocs de code, validation pas-à-pas,
et proposition d'un message de commit à chaque étape.

## 2. Couche 1 — Spec (contexte et objectif)
- Nom du projet : startme
- But réel (pas la tâche) : disposer d'un tableau de bord personnel auto-hébergé
  (signets organisés en Pages > Widgets > Liens, + widgets spéciaux météo, horloges,
  monitoring système, etc.) qui remplace un service externe type Start.me et reste
  pilotable à la souris (drag & drop).
- Stack spécifique : Django 5.2 + django-htmx + SQLite (db.sqlite3) ;
  psutil pour le monitoring, requests pour l'IP publique, python-dotenv pour .env.
- Méthode : reste agile (specs petits et compartimentés). Si le but d'une tâche est
  flou, interviewe-moi avant de coder. Fais-moi valider les décisions clés.

## 3. Couche 3 — Architecture et base de connaissances
Carte des dossiers de ce projet :
- /startme : configuration du projet Django (settings.py, urls.py, wsgi/asgi).
- /dashboard : application principale (models.py, views.py, urls.py, templates,
  templatetags, migrations).
- /templates et /static/js : gabarits HTML (partials, registration) et JS front.
- /scripts et /tools : utilitaires (backup, installation, ajout de liens).
- db.sqlite3 : base de données locale. .env : secrets et configuration.
- Docs internes : README.md, STRUCTURE.md, DEVELOPMENT.md, CHEATSHEET.md, AI_CONTEXT.md.
- Skills du projet : aucun pour l'instant.

## 4. Couche 2 — Protocole de vérification (The Verifier)
Avant de considérer une tâche terminée :
1. Critère de succès : la page de dashboard se charge sans erreur 500, les liens et
   widgets s'affichent, et le drag & drop persiste bien la nouvelle position en base.
2. Commande de vérification locale : "python manage.py test" (tests dans
   dashboard/tests.py) ; pour un essai manuel, "./run.sh" puis ouvrir
   http://127.0.0.1:8800.
3. Signal externe : ne présume pas qu'une vue fonctionne — lis startup.log et la
   sortie du runserver, et vérifie l'état réel en base après une action.
4. Revue croisée (si build complexe) : confronter la sortie à un second modèle / Codex.

## 5. Couche 3 — Guardrails spécifiques (sécurité des outils)
- JAMAIS (Never do) : ne pas éditer à la main les fichiers de dashboard/migrations,
  ni écraser db.sqlite3 ou .env, sans confirmation écrite explicite de ma part.
  (Idéalement, doubler d'un hook pre-tool-use sur ces chemins.)
- DEMANDER D'ABORD (Ask first) : toute nouvelle dépendance dans requirements.txt,
  toute migration de schéma, et toute commande qui touche la base.
- AUTOPILOT (Always do) : lire, analyser, chercher dans le code et les templates.
