# Plan — Regroupement des pages du dashboard (15 → 8)

Date : 2026-08-06. Validé le : (en attente).
Préalable fait : élagage de la liste A le 2026-08-06 (7 widgets vides/obsolètes
supprimés, sauvegarde dump_avant_elagage_2026-08-06.json).

## Objectif

Passer de 15 pages / 85 widgets à 8 pages / ~55 widgets, sans perte de donnée :
la migration DÉPLACE et RENOMME ; elle ne SUPPRIME que les doublons stricts.

## Principes (règles du script)

1. Suppression uniquement pour les doublons à URL exactement identique ;
   en cas de doublon inter-pages, on garde l'exemplaire du widget thématique
   (ex. Communauto reste dans Transport, pas dans Quotidien).
2. Fusion de widgets uniquement entre widgets de même type (une note ne
   fusionne pas avec une liste ; elles restent adjacentes).
3. Tout se fait dans une transaction atomique : la moindre erreur annule tout.
4. Les champs order sont renumérotés proprement (0..n) — corrige les vieux 999.
5. Sauvegarde dumpdata immédiatement avant l'exécution.

## Pages cibles (ordre des onglets)

0. Départ — 1. Perso — 2. IA — 3. Dev (= Projet renommée) — 4. Commandes —
5. Médias — 6. Politique — 7. Savoirs (= Science renommée).

Pages supprimées après vidage : Programmation, Infos, Divers, Outils,
Programmes, Twitter, TODO.

## Mapping détaillé

### Départ
| Widget cible | Provenance |
|---|---|
| Quotidien (= Récurrent renommé) | + liens de Souvent (dédup URL). Sortants : Radar météo et Windy.com vers Météo ; Communauto (doublon de Transport) ; Le Figaro (doublon de Journaux) |
| Courriel & Drives (= Drive renommé) | inchangé |
| Google | inchangé (les doublons de « Docu importante » sont supprimés côté Docu) |
| Météo | + Radar météo, Windy.com |
| Loto (= Divers renommé) | inchangé |
| Tâches / Tâches IA / Tâches perso | les 3 todo de la page TODO, renommés |

Widget dissous : Travail — Github Repo et Gist vers Dev>Github (dédup) ;
Le Redico (doublon Forums/Blogues) ; administration vers Dev>Redico-ai ;
Desmos vers Savoirs>Sciences & maths ; OpenAI playground vers IA>Plateformes ;
Bluesky vers Médias>X / Réseaux ; Streamlit, cursor.com, Authenticator.cursor.sh,
OpenHands README, « fill out this form. » vers Dev>Outils dev (nouveau widget).
Widget sortant : Forums/Blogues vers Savoirs.

### Perso
| Widget cible | Provenance |
|---|---|
| Achats | inchangé |
| Épicerie | + Metro Favoris et SuperC Favoris (de Projet>Dashboard, widget dissous) |
| Maison | + les 4 liens de Projet>Maison (widget dissous) + HQ, HQ pannes, Helix admin (de Perso>Divers) ; note Maison dimensions adjacente |
| Finances (= Impots renommé) | + les 4 liens de Divers>Cours des actions |
| Santé (liste + 2 notes) | inchangé |
| Transport (= Autobus renommé) | Communauto déjà présent (doublon de Quotidien supprimé) ; note Communauto adjacente |
| Abonnements (liste + note + todo adjacents) | + liens facturation centralisés : Claude usage, Anthropic Billing (dédup IA/Redico-ai), Clause cost, Gemini API coûts, Facturation GoogleCloud, console.x.ai billing |
| Recettes | passe en is_wide=True |
| Divers | reste : TinEye, Bibliomontreal, quebecmunicipal, Board Editor ; Données ouvertes vers Politique si doublon |
| Notes Médicaments, Matériel, Idées | inchangées |

### IA
| Widget cible | Provenance |
|---|---|
| Chat | inchangé |
| Plateformes & consoles (= IA renommé) | dédup des 5 chats déjà dans Chat ; billing sorti vers Perso>Abonnements ; + OpenAI playground |
| Cours & docs IA (= Cours IA de Programmation) | + les 3 liens de Projet>Cours Kaggle (widget dissous) |
| Docs & références (= Divers>Docu importante déplacé) | après dédup des doublons Google (supprimés au profit de Départ>Google) |
| Chaîne YT, notes Ollama/OpenwenUI et Claude | inchangés |

### Dev (= page Projet renommée)
| Widget cible | Provenance |
|---|---|
| Redico-ai | - liens billing (vers Abonnements) ; + administration (de Travail) |
| Turing Machine | + The Busy Beaver Challenge (de Science>Sciences) ; note Busy-Beaver adjacente |
| Github | + dédup Github Repo/Gist (de Travail) et Github (de Programmation>Dev) |
| Docs (= Programmation>Django renommé) | Django Docs, HTMX + StackOverflow (de Programmation>Dev, widget dissous) |
| Scripts (lanceur, de Outils) | déplacé tel quel ; Outils>Fichiers (Alim) : dédup avec Quotidien>Alim si URL identique, sinon versé dans Scripts |
| Outils dev (nouveau) | Streamlit, cursor.com, Authenticator.cursor.sh, OpenHands README, « fill out this form. » (de Travail) |
| Hymne, note Sauvegardes | inchangés |

### Commandes
Inchangée, plus : note ffmpeg (= « ffmpef » renommée, de Médias) ; liste ffmpeg
(de Médias) qui reçoit « Commandes ffmpeg » (de Médias>Twitter) et « ffmpeg »
(de Médias>Visu) ; note « Programmes installés » (= page Programmes dissoute,
coquille corrigée).

### Médias
| Widget cible | Provenance |
|---|---|
| Musique YT | inchangé |
| Visu | - lien ffmpeg (vers Commandes) |
| Radio (scission d'Audio/Journaux) | 98,5 FM, 995.fm, CBC Music, Direct.radiovm.com |
| Journaux (scission d'Audio/Journaux) | Richard Martineau, Le Devoir, La Presse, NYT, WaPo, Globe and Mail, JdM, Le Figaro (absorbe le doublon de Quotidien) |
| X / Réseaux (= Twitter renommé) | - Commandes ffmpeg ; + les 3 liens de la page Twitter (dissoute) + Bluesky (de Travail) |

### Politique
Inchangée, plus : Autres références (nouveau) = fusion de Géopolitique (1),
Données ouvertes (1) et Québec Fier (2), widgets sources dissous.

### Savoirs (= page Science renommée)
| Widget cible | Provenance |
|---|---|
| Climat | inchangé |
| Sciences & maths | fusion de Sciences (- Busy Beaver vers Dev), Lectures et « Grandient, Divergence, Curl » + Desmos (de Travail) |
| Forums/Blogues | déplacé de Départ |
| Langue | déplacé de Divers |
| Citations (note) | déplacée de Divers |

## Exécution

1. Sauvegarde : dumpdata dashboard vers dump_avant_migration_2026-08-06.json.
2. Script scripts/migrate_regroupement.py exécuté via manage.py shell,
   transaction atomique, journalisation de chaque opération.
3. Vérifications : bilan des comptes (liens avant = liens après + doublons
   supprimés, listés un à un), 8 pages restantes, aucun widget/lien orphelin,
   dashboard répond 200.

## Critères de succès (Verifier)

- Aucun lien perdu hors doublons stricts (chaque suppression journalisée avec
  son URL et l'emplacement de l'exemplaire conservé).
- 8 pages, ~55 widgets, orders séquentiels sans 999.
- La page se charge sans erreur 500 ; drag & drop toujours fonctionnel.
