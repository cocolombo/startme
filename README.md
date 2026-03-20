# Django Personal Dashboard

Un tableau de bord (Dashboard) personnel, auto-hébergé et interactif, inspiré de services comme Start.me. Il permet de gérer ses signets, de les organiser par catégories (widgets) et par pages (onglets), avec une interface moderne et fluide entièrement pilotable à la souris.

## 🚀 Fonctionnalités

### Organisation
* **Structure Hiérarchique** : Pages (Onglets) > Widgets (Catégories) > Liens.
* **Barre de Recherche** : Recherche Google intégrée directement dans le dashboard.
* **Compteurs** : Visualisez rapidement le nombre de liens par catégorie directement dans le titre.
* **Page "Infos" Spéciale** : Si une page est nommée **"Infos"**, elle affiche automatiquement :
    * **Météo** : Météo locale dynamique (via Open-Meteo API).
    * **Horloges** : Heure locale et fuseaux horaires internationaux (Paris, SF, Pékin).
    * **Calendrier** : Calendrier mensuel interactif.
    * **Marchés** : Widget TradingView (Indices, Crypto, Forex, EH/NASDAQ).
    * **Moniteur Système** : Utilisation CPU, RAM, Disques et GPU (Nvidia) en temps réel.
    * **Calculatrice** : Calculatrice intégrée avec historique visuel.
    * **Minuteur** : Compte à rebours visuel (style Pomodoro) avec alarme sonore et presets (5-60 min).
    * **Réseau** : Affichage de l'IP Locale et de l'IP Publique (WAN).

### Widgets Spéciaux
* **Bloc-notes** : Un widget de type "Note" qui sauvegarde automatiquement votre texte pendant la frappe.
* **Commandes Shell** : Un widget spécial pour exécuter des scripts ou commandes système directement depuis le navigateur (ouvre un terminal local).

### Drag & Drop (Glisser-Déposer)
* **Liens** : Déplacez les liens d'une catégorie à une autre ou réorganisez-les au sein d'une liste.
* **Catégories** : Réorganisez l'ordre des catégories sur la page par simple glisser-déposer via l'en-tête.
* **Persistance** : Toutes les modifications de position sont sauvegardées instantanément en base de données.

### Gestion Complète
* **Pages** : Créer, Renommer, Supprimer.
* **Catégories (Widgets)** :
    * **Ouvrir Tout** : Bouton `⇱` pour ouvrir tous les liens d'une catégorie dans de nouveaux onglets (avec délai progressif).
    * **Renommer (Inline)** : Cliquez simplement sur le titre pour le modifier.
    * **Déplacer vers** : Envoyez une catégorie entière vers une autre page.
* **Liens** :
    * **Éditer (Inline)** : Modifiez le titre et l'URL directement dans la liste.
    * **Ouverture Locale** : Supporte l'ouverture de fichiers locaux (via `xdg-open`).

### Interface (UI/UX)
* **Design** : Mode sombre (Dark Mode) utilisant Tailwind CSS.
* **Interactivité** : HTMX pour les mises à jour sans rechargement.
* **Sécurité** : Gestion des variables d'environnement via `.env`.

## 🛠️ Stack Technique

* **Backend** : Python 3.12, Django 5.2.
* **Frontend** : HTML5, Tailwind CSS, HTMX, SortableJS.
* **Système** : `psutil` pour le monitoring, `python-dotenv` pour la config.
* **Base de données** : SQLite (par défaut).

## ⚙️ Installation & Démarrage

### 1. Pré-requis
Assurez-vous d'avoir **Python 3.12** installé sur votre machine.

### 2. Installation
```bash
# Cloner le projet
git clone [https://github.com/cocolombo/dashboard.git](https://github.com/cocolombo/dashboard.git)
cd dashboard

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# venv\Scripts\activate   # Sur Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# (Optionnel) Modifiez .env avec votre propre SECRET_KEY

# Initialiser la base de données
python manage.py migrate
```

### 3. Lancement
```bash
python manage.py runserver
```

## 📂 Structure du Projet
 - **startme/** : Configuration principale Django (settings.py, urls.py).
 - **dashboard/** : L'application principale.
   - `models.py` : Définition des données (Page, Widget, Link).
   - `views.py` : Logique métier (affichage, APIs de mise à jour).
   - `templates/dashboard/index.html` : Le frontend unique de l'application.
   - `templates/partials/` : Fragments HTML pour HTMX (widgets, formulaires).
 - **static/** : Fichiers JS/CSS locaux (Tailwind, HTMX, SortableJS).

## 💡 Utilisation
 - **Ajouter un lien** : Cliquez sur le `+` à droite du titre d'une catégorie.
 - **Déplacer un élément** : Cliquez et glissez un lien ou un titre de catégorie.
 - **Menu Contextuel** : Faites un clic-droit sur un lien ou un titre de catégorie pour voir les options avancées.
 - **Gérer les pages** : Utilisez les boutons `+`, `✎` (renommer) et `🗑` (supprimer) dans la barre de navigation supérieure.
 - **Backup** : Un bouton permet de télécharger une sauvegarde complète du projet (ZIP).
