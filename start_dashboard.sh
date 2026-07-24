#!/bin/bash

# Le serveur startme est desormais gere par le service systemd (startme.service).
# Ce script ne fait plus qu'ouvrir le navigateur au login.

# Petit delai pour laisser le service ecouter le port apres le boot
sleep 3

xdg-open http://127.0.0.1:8800
