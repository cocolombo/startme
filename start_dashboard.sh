#!/bin/bash

# 1. Se déplacer dans le dossier du projet
cd /media/120gb/python/startme

# 2. Lancer le serveur avec le chemin ABSOLU vers le python du venv
# On redirige les erreurs (stderr) et la sortie (stdout) vers un fichier log pour déboguer
/media/120gb/python/startme/venv/bin/python manage.py runserver 8800 > startup.log 2>&1 &

# 3. Attendre que le serveur démarre
sleep 5

# 4. Ouvrir le navigateur
xdg-open http://127.0.0.1:8800