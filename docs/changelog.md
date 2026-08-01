# Historique des modifications (Changelog)

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [2026-03-20] - Corrections et améliorations
### Corrigé
- `Link.url` migré de `URLField` vers `CharField(max_length=500)` pour supporter les chemins locaux et commandes shell.
- Champ `icon_url` inutilisé supprimé du modèle `Link`.
- `rename_page` : ajout de la déduplication de slug (évite les collisions).
- `bare except:` remplacés par `except Exception` dans 4 vues.
- `print()` de debug remplacés par un logger Django (`logging.getLogger(__name__)`).
- Sous-menu "Déplacer vers..." : choix du widget cible (au lieu du premier widget par défaut).

### Configuration
- Chemins de disques surveillés déplacés dans `.env` via `MONITOR_DISKS`.
- Changement de port : `8888` → `8800`.

## [2026-02] - Nouvelles fonctionnalités
### Ajouté
- Widget **Réseau** : affichage de l'IP locale et de l'IP publique (WAN).
- Widget **Minuteur** : compte à rebours avec alarme sonore et presets (5-60 min).
- Widget **Calculatrice** : calculatrice intégrée avec historique.
- Chaînes YouTube IA ajoutées via script `scripts/add_ia_links.py`.

## [Non publié] - En cours de développement
### Ajouté
- Fichier `CHANGELOG.md` pour le suivi de l'historique.
- Séparation de la documentation technique vers `DEVELOPMENT.md` (recommandé).

## [2025-11-26] - Mise à jour UI & Fonctionnalités dynamiques
### Fonctionnalités
- **Météo Dynamique** : Remplacement de l'image statique `wttr.in` par un widget interactif utilisant l'API Open-Meteo (JS). Affiche la météo actuelle et prévisions J+3.
- **Édition Inline (Widgets)** : Possibilité de renommer les catégories directement en cliquant sur le titre (remplacement de la modale).
- **Édition Inline (Liens)** : Possibilité de modifier le titre et l'URL d'un lien directement dans la liste via un bouton "crayon".

### Technique
- **Refactoring HTMX** : Extraction du code HTML des widgets et des liens vers des templates partiels (`templates/partials/`) pour supporter les mises à jour dynamiques `hx-swap`.
- **Optimisation** : Suppression du champ `icon_url` inutile dans le modèle Link (logique déplacée vers le frontend ou calculée si nécessaire).

## [2025-11-26] - Matin
### Ajouté
- Implémentation initiale de l'édition "Inline" avec HTMX.

## [Archives] - Pushs précédents
- Création de la structure initiale Django.
- Intégration de Tailwind CSS en local.
- Mise en place du Drag & Drop avec SortableJS.
- Système de Pages et Widgets.
- Page "Infos" avec widget TradingView et Horloge.
