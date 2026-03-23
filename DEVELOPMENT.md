# Guide de Développement

Ce document est destiné aux développeurs souhaitant modifier le code source, personnaliser l'apparence ou comprendre l'architecture du Dashboard.

## 🛠️ Stack Technique

* **Backend** : Python 3.12+, Django 5.2.
* **Frontend** :
    * **HTML5/CSS3** : Structure.
    * **Tailwind CSS** : Framework utilitaire (chargé localement via `static/js/tailwind.js`).
    * **HTMX** : Pour les interactions dynamiques (AJAX, édition inline, polling).
    * **SortableJS** : Pour le Drag & Drop.
* **Base de données** : SQLite (par défaut).
* **Système** : `psutil` pour le monitoring système (CPU, RAM, Disque).
* **Configuration** : `python-dotenv` pour la gestion des variables d'environnement (`.env`).

---

## ⚙️ Installation (Environnement de Dév)

### 1. Pré-requis
* Python 3.12+
* Git

### 2. Setup du projet
```bash
# Cloner le dépôt
git clone https://github.com/cocolombo/dashboard.git
cd dashboard

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Linux/Mac :
source venv/bin/activate
# Windows :
# venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement local
cp .env.example .env
# Éditez le fichier .env selon vos besoins (SECRET_KEY, DEBUG, ALLOWED_HOSTS)

# Migrer la base de données
python manage.py migrate

# (Optionnel) Peupler la base avec des données de test
# python manage.py seed_db
```

### 3. Lancement
```bash
python manage.py runserver
# Ou utiliser le script fourni : ./run.sh
```

---

## 🏗️ Architecture du Code

L'application suit le pattern MVC (MVT dans l'écosystème Django) :

* **Models** (`dashboard/models.py`) : Gère la hiérarchie `Page` > `Widget` > `Link`.
* **Views** (`dashboard/views.py`) : Traite la logique métier, retourne soit des templates complets (`index.html`) soit des fragments HTML (partials) pour HTMX.
* **Templates** (`templates/`) : 
    * `dashboard/index.html` : Template principal.
    * `partials/` : Contient tous les fragments réutilisables (widgets, formulaires, menus) mis à jour dynamiquement par HTMX.

Pour une vue détaillée des fichiers, consultez [STRUCTURE.md](STRUCTURE.md).
Pour le contexte IA global du projet, consultez [AI_CONTEXT.md](AI_CONTEXT.md).

---

## 🎨 Personnalisation (UI/UX)

L'apparence est principalement gérée par Tailwind CSS. La configuration est centralisée dans le script intégré dans le `<head>` de `index.html`.

Pour modifier le thème de couleurs ou d'autres aspects visuels, consultez le fichier [APPARENCE.md](APPARENCE.md) (si disponible) ou ajustez directement les classes Tailwind dans les templates partiels.
