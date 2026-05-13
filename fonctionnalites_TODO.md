# Fonctionnalités TODO

## Rapides (1-2h)
- [ ] Favoris / épingler un lien — marquer des liens importants qui remontent en haut du widget
- [ ] Compteur de clics — afficher combien de fois un lien a été ouvert
- [ ] Duplication de widget — copier un widget existant (avec ses liens) vers une page
- [ ] Raccourcis clavier — `Alt+N` nouvelle page, `Alt+W` nouveau widget, etc.

## Moyennes (demi-journée)
- [x] Recherche globale — barre de recherche qui filtre liens et widgets sur toutes les pages en temps réel
- [ ] Tags sur les liens — étiquettes colorées filtrables
- [ ] Import/export JSON — sauvegarder et restaurer la configuration complète (pages + widgets + liens)
- [x] Widget météo amélioré — prévisions sur 3 jours au lieu d'un snapshot

## Plus ambitieuses
- [ ] Widget RSS/Atom — agrégateur de flux pour suivre des sites
- [x] Widget TODO/checklist — liste de tâches avec cases à cocher et persistance
- [x] Historique des commandes — log des scripts lancés avec timestamp et résultat
- [ ] Multi-utilisateur — chaque utilisateur a son propre dashboard (auth Django déjà en place)

## Outils (tools/)
- [x] Coffre chiffré — `tools/coffre.html` standalone, AES-GCM 256-bit côté navigateur, export/import .vault

## Scripts (scripts/)
- [x] Sauvegarde cloud — `scripts/backup_cloud.sh` vers Google Drive, Proton Drive et SSH `nimzo@10.0.0.29` en parallèle
- [x] Sauvegarde multi-projets — argument optionnel `[PROJECT_DIR]`, exclusions par projet via `.backup_exclude`
- [x] Template `.backup_exclude` — `scripts/backup_exclude.template` pour standardiser les exclusions par projet
- [x] Documentation sauvegarde — `scripts/BACKUP.md` (prérequis, usage, exclusions, procédure nouveau projet)