#!/bin/bash

# 1. Se déplacer dans le dossier du projet
cd /media/120gb/python/startme
# 2. Activer l'environnement virtuel
source venv/bin/activate

# 3. Lancer le serveur sur le port 8800
python manage.py runserver 8800 &

# 4. Attendre quelques secondes que le serveur soit prêt
sleep 5

# 5. Ouvrir le navigateur
xdg-open http://127.0.0.1:8800
