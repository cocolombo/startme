# 🛠️ Dépannage (Troubleshooting)

Ce document liste les problèmes courants que vous pourriez rencontrer lors de l'utilisation ou de l'installation du Dashboard, ainsi que leurs solutions.

---

## 🖥️ 1. Widget "Système" (Monitoring)

### Le widget affiche `0%` ou "Chargement sys..." en boucle
*   **Cause possible 1 :** Le module `psutil` n'est pas installé ou rencontre une erreur de permission.
    *   *Solution :* Vérifiez que vous avez bien exécuté `pip install -r requirements.txt`. Sous certains OS, lire les stats système nécessite des droits spécifiques.
*   **Cause possible 2 :** Les chemins des disques durs à surveiller sont incorrects.
    *   *Solution :* Vérifiez la variable `MONITOR_DISKS` dans votre fichier `.env`. Si un chemin n'existe pas sur votre OS (ex: `/media/nimzo/3tb` n'existe pas), le widget peut ignorer silencieusement le disque ou planter. Utilisez la commande `df -h` (sous Linux/Mac) pour trouver les bons points de montage.

### Le GPU (Nvidia) ne s'affiche pas
*   **Cause possible :** La commande `nvidia-smi` n'est pas disponible sur le système, ou vous n'avez pas de carte Nvidia.
    *   *Solution :* Le dashboard masque automatiquement la section GPU si `nvidia-smi` échoue. Ce n'est pas un bug. Si vous avez une carte AMD/Radeon, il faudra adapter le code dans `dashboard/views.py` (`get_gpu_stats()`).

---

## 📂 2. Liens Locaux et Commandes Shell

### Les liens `file:///...` ne s'ouvrent pas quand je clique dessus
*   **Cause :** Tous les navigateurs modernes (Chrome, Firefox, Safari) bloquent par sécurité l'ouverture de liens locaux (`file://`) depuis une page web hébergée sur un serveur (`http://`).
*   **Solution :** N'utilisez pas le clic gauche direct sur le texte du lien. Cliquez sur le **bouton bleu en forme de dossier** affiché à droite du lien. Ce bouton demande au serveur Python d'ouvrir le fichier via le système d'exploitation (`xdg-open` sous Linux).

### Le widget "Commandes Shell" ne lance aucun terminal
*   **Cause :** Le script cherche des terminaux spécifiques (`mate-terminal`, `gnome-terminal`, `xterm`, `konsole`). S'il n'en trouve aucun, l'action échoue.
*   **Solution :** 
    1. Regardez la console où tourne Django, vous devriez voir "ERREUR: Aucun terminal compatible trouvé".
    2. Installez un terminal supporté (ex: `sudo apt install gnome-terminal`) ou modifiez la liste des terminaux détectés dans `dashboard/views.py` (fonction `run_command`).

---

## 🌐 3. Widgets Réseau, Météo et Bourse

### L'adresse IP publique affiche "Indisponible"
*   **Cause :** Le serveur n'arrive pas à joindre l'API `https://api.ipify.org`. Cela peut être dû à une coupure internet, ou l'API vous a temporairement bloqué (rate limit).
*   **Solution :** Attendez quelques minutes. Si le problème persiste, vérifiez la connexion internet du serveur hébergeant le dashboard.

### La Météo affiche des tirets `--°` ou des erreurs
*   **Cause :** Problème avec l'API Open-Meteo ou coordonnées géographiques invalides.
*   **Solution :** Vérifiez vos variables d'environnement dans `.env` (`WEATHER_LAT` et `WEATHER_LON`). Assurez-vous que ce sont bien des nombres décimaux valides (ex: `45.5088`).

### Le widget TradingView (Marchés) est vide ou bloque
*   **Cause :** Les bloqueurs de publicités (uBlock Origin, AdGuard) ou la protection contre le pistage de Firefox (Strict) bloquent parfois les iframes de TradingView.
*   **Solution :** Désactivez le bloqueur de pubs pour `localhost` ou l'IP de votre serveur.

---

## ⚙️ 4. Serveur et Base de données

### Erreur `KeyError: 'SECRET_KEY'` au lancement
*   **Cause :** Le fichier de configuration `.env` est manquant ou mal formaté.
*   **Solution :** Copiez le fichier d'exemple (`cp .env.example .env`) et relancez le serveur.

### Erreur `no such table: dashboard_page` ou similaire
*   **Cause :** La base de données SQLite n'est pas initialisée.
*   **Solution :** Arrêtez le serveur et lancez `python manage.py migrate`.

### Les modifications de glisser-déposer (grille principale) ne sont pas sauvegardées
*   **Cause :** La requête HTMX échoue, potentiellement à cause d'un problème de jeton CSRF.
*   **Solution :** Vérifiez la console navigateur (F12). Assurez-vous que la balise `<body>` contient bien `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` dans `index.html`.

### Le glisser-déposer dans la sidebar ne fonctionne pas (pages ou widgets)
*   **Cause possible 1 :** Erreur JavaScript au démarrage de SortableJS (élément DOM manquant).
    *   *Solution :* Ouvrez F12 → Onglet **Console**. Une erreur JS bloquante empêche l'initialisation. Rechargez la page et reproduisez le problème.
*   **Cause possible 2 :** La requête `fetch()` vers l'API échoue (erreur réseau ou réponse 4xx/5xx).
    *   *Solution :* Ouvrez F12 → Onglet **Réseau** (Network). Filtrez par `update-page-order` ou `widget/move`. Vérifiez le code de réponse et le corps de l'erreur côté serveur (console Django).

---

## 🆘 Obtenir plus d'aide
Si un problème n'est pas listé ici :
1. Regardez la **console de votre terminal** où tourne `python manage.py runserver`, les erreurs Python y sont détaillées.
2. Regardez la **console du navigateur** (Touche F12 -> Onglet Console) pour les erreurs JavaScript ou HTMX.
