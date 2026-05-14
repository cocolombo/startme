# 📝 Cheatsheet (Aide-mémoire)

Ce document rassemble les commandes utiles, les astuces d'utilisation et les syntaxes spécifiques pour administrer et utiliser le Dashboard au quotidien.

---

## 💻 1. Commandes d'Administration (Django)

Ces commandes sont à exécuter dans le terminal, à la racine du projet, avec l'environnement virtuel activé (`source venv/bin/activate`).

| Action | Commande |
| :--- | :--- |
| **Démarrer le serveur** | `python manage.py runserver` (ou `./run.sh`) |
| **Créer/Mettre à jour la base** | `python manage.py makemigrations`<br>`python manage.py migrate` |
| **Créer un administrateur** | `python manage.py createsuperuser` |
| **Accéder au shell interactif** | `python manage.py shell` |
| **Lancer un script externe** | `python scripts/add_ia_links.py` |

---

## 🔗 2. Syntaxe des Liens (Widget Type "Liste")

Le champ "URL" d'un lien accepte plusieurs formats qui déclencheront des comportements différents.

### A. Liens Web classiques
* **Format :** `https://www.google.com` ou `http://localhost:8080`
* **Comportement :** S'ouvre dans un nouvel onglet (`target="_blank"`). Le script tente de récupérer automatiquement le favicon du site via Google Favicons.

### B. Liens Locaux (Fichiers et Dossiers)
* **Format :** `/media/120gb/mondossier` ou `file:///home/user/document.pdf`
* **Comportement :** Pour des raisons de sécurité, les navigateurs bloquent les liens directs vers le disque local. 
* **L'Astuce :** Le Dashboard ajoute automatiquement un bouton spécial (icône de dossier bleu). Cliquer dessus envoie une requête au serveur Python qui exécute la commande système `xdg-open /media/120gb/mondossier` pour ouvrir le dossier dans l'explorateur de fichiers de votre OS.

---

## ⚡ 3. Syntaxe des Commandes (Widget Type "Lanceur")

Si vous créez un widget de type **"Lanceur de scripts"** (Command), les liens à l'intérieur ne sont pas des URLs mais des commandes Bash/Shell.

* **Comportement :** Le serveur Python va chercher un terminal disponible sur votre machine (`mate-terminal`, `gnome-terminal`, `xterm`, `konsole`), l'ouvrir, exécuter la commande, et garder la fenêtre ouverte pour afficher le résultat (succès/erreur).

**Exemples de commandes valides :**

*   **Lancer une application :**
    `code /media/120gb/python/mon_projet` (Ouvre VS Code)
*   **Lancer un modèle IA local :**
    `ollama run llama3`
*   **Mettre à jour le système (Ubuntu) :**
    `sudo apt update && sudo apt upgrade -y`
*   **Lancer un script sh complexe :**
    `bash /home/user/scripts/backup.sh`

*(Note : Évitez les commandes nécessitant une saisie utilisateur complexe avant leur lancement final, privilégiez les arguments directs).*

---

## 🛠️ 4. Les Variables d'Environnement (`.env`)

Le fichier `.env` (à la racine) contrôle la configuration sans toucher au code. S'il manque, copiez `.env.example`.

### Paramètres de base
*   `SECRET_KEY=votre_cle_tres_longue_ici` (À changer absolument en production)
*   `DEBUG=True` (Passer à `False` en production pour cacher les erreurs détaillées)

### Configuration des Widgets Spéciaux (Page Infos)
*   **Disques Surveillés :**
    `MONITOR_DISKS="Système:/|Data 3TB:/media/nimzo/3tb|Fast 120GB:/media/120gb"`
    *(Format: Nom1:Chemin1|Nom2:Chemin2)*
*   **Météo :**
    *   `WEATHER_CITY="Montréal, QC"` (Titre affiché)
    *   `WEATHER_LAT=45.5088` (Latitude pour l'API)
    *   `WEATHER_LON=-73.5878` (Longitude pour l'API)

---

## 🖱️ 5. Raccourcis UI (Interface)

*   **Renommer un widget :** Cliquez simplement sur son titre.
*   **Ouvrir tous les liens :** Le petit bouton `⇱` dans l'en-tête d'une liste ouvre tous ses liens dans de nouveaux onglets (décalés de 100ms pour ne pas surcharger le navigateur).
*   **Déplacer un widget (méthode 1 — menu contextuel) :** Clic droit sur le titre du widget ➔ Choisissez la page de destination.
*   **Déplacer un widget (méthode 2 — sidebar) :** Ouvrez la sidebar (☰), glissez le nom d'un widget vers la liste d'une autre page. La mise à jour est instantanée, sans rechargement.
*   **Réordonner les pages :** Ouvrez la sidebar (☰), saisissez la poignée `⠿` à gauche d'une page et glissez-la à la position souhaitée.
*   **Passer un widget en 2 colonnes :** Clic sur l'icône ⚙ (en-tête du widget) ➔ `↔ Largeur 2 colonnes`. Le widget occupe alors toute la largeur de la page. Recliquer pour revenir à 1 colonne.
*   **Éditer un lien existant :** Survolez la ligne du lien et cliquez sur l'icône de crayon `✎` qui apparaît.

---

## 💾 6. Sauvegardes

```bash
./scripts/backup_cloud.sh           # startme (projet par défaut)
./scripts/backup_cloud.sh /chemin   # autre projet
./scripts/backup_cloud.sh /chemin --dry-run  # vérifier sans archiver
```

Doc complète → `scripts/BACKUP.md`