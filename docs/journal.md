# Journal de développement — startme

Journal chronologique des décisions et étapes. À chaque étape validée : ce qui a
été fait, pourquoi, et « **État : N tests verts** ». Entrées récentes en bas.

<!-- Voir aussi changelog.md pour les changements notables orientés versions. -->

## 2026-08-06 — Regroupement des pages : 15 → 8

- **Élagage préalable** : 7 widgets vides ou obsolètes supprimés (dont les 2
  Unsloth et un snippet Linux vide en doublon), après validation de la liste A.
- **Migration** (plan validé : `plans/plan-regroupement-liens.md`, script :
  `scripts/migrate_regroupement.py`) : 15 pages → 8 (Départ, Perso, IA, Dev,
  Commandes, Médias, Politique, Savoirs), 85 widgets → 73, 420 liens → 401.
- **Pourquoi** : trop de pages squelettes (Infos, Programmes, Twitter…), thèmes
  éclatés sur 3-4 pages (Google, Github, facturation IA, ffmpeg), trois widgets
  « Divers ». Les 19 liens supprimés sont tous des doublons à URL strictement
  identique, journalisés un à un ; tout le reste a été déplacé, jamais perdu.
- **Garde-fous appliqués** : dumpdata avant chaque écriture
  (`dump_avant_elagage_…` et `dump_avant_migration_2026-08-06.json`),
  transaction atomique, bilan de comptes assert-é, vérification HTTP 200.
- Bonus : les vieux `order=999` (hack pré-`next_order()`) ont été renumérotés.
- Reste à la main de l'utilisateur : nettoyage de la liste B (liens périmés,
  « - YouTube » à renommer) et sort de `data_export.json` (suivi par git).
- **État : 23 tests verts.**

## 2026-08-06 — Correctif : page « Infos » (widgets système) disparue

- **Symptôme** : après le regroupement, plus d'accès aux widgets météo,
  calculatrice, espaces disques, horloge et monitoring système.
- **Cause** : ces widgets ne sont **pas** des enregistrements `Widget` en base ;
  ils sont codés en dur dans `templates/partials/widgets_infos.html`, affichés
  uniquement par la condition `{% if active_page.slug == 'infos' %}`
  (`dashboard/templates/dashboard/index.html:84`). La Phase 10 de
  `migrate_regroupement.py` a supprimé la page « Infos » car elle jugeait toute
  page « vide » sur `widgets.count() == 0` — or « Infos » n'a jamais eu de
  `Widget` en base, sa seule utilité étant de porter le slug `infos`.
- **Correction** : recréation de la page en base via `manage.py shell`
  (`Page.objects.get_or_create(slug='infos', defaults={'name': 'Infos',
  'order': 8})`). Aucun changement de code, aucune migration de schéma :
  le template réaffiche les widgets dès que le slug existe.
- **Vérification** : `Client` de test authentifié → `GET /page/infos/` renvoie
  **HTTP 200** et le rendu contient bien météo, calculatrice, system-monitor et
  horloge.
- **Point de vigilance** (non corrigé, laissé au choix de l'utilisateur) : le
  slug `infos` est une page « fantôme » sans widget en base ; tout futur script
  qui supprime les pages « vides » la re-supprimera. Protéger le slug ou
  garantir sa présence au démarrage si le cas se représente.
- **État : correctif de données, pas de test ajouté (comportement front inchangé).**

## 2026-08-07 — Largeur des catégories réglable à 1, 2 ou 4 colonnes

- **But** : pouvoir afficher une catégorie (widget) sur 1 colonne, 2 colonnes,
  ou pleine largeur (4 colonnes), là où seul un mode « 2 colonnes » existait.
- **Décision de modèle** : le booléen `Widget.is_wide` (2 états) ne suffisait
  plus. Remplacé par un entier `col_span` avec choix `1 / 2 / 4`
  (`dashboard/models.py`). Migration `0014_widget_col_span` réversible : ajout
  du champ, conversion `is_wide=True → col_span=2`, puis suppression de
  `is_wide`.
- **Vue** : `toggle_widget_width` (bascule booléenne) devient
  `set_widget_width(widget_id, span)` avec validation `span ∈ {1, 2, 4}`
  (toute autre valeur retombe à 1). Route :
  `widget/set-width/<id>/<span>/`.
- **Front** :
  - `templates/partials/widget.html` mappe `col_span` vers les classes Tailwind
    `lg:col-span-2` (2 col) et `md:col-span-2 lg:col-span-4` (pleine largeur,
    en tenant compte des points de rupture md/lg).
  - `templates/partials/menus.html` : le bouton unique « ↔ Largeur 2 colonnes »
    devient une section **Largeur** à trois boutons (`▮` / `▮▮` / `▮▮▮▮`),
    accessible via l'icône engrenage `⚙` de l'en-tête du widget (clic gauche,
    `showWidgetMenu`), **pas** le clic droit.
  - `templates/partials/scripts.html` : le regex qui injecte l'ID du widget dans
    l'action des formulaires vise désormais le **premier** segment numérique
    (l'ID), pour ne pas écraser le segment de largeur qui le suit.
- **Point de vigilance** : la grille utilise `grid-flow-dense`, qui comble les
  trous en réordonnant visuellement les tuiles ; un widget pleine largeur peut
  donc laisser de petites tuiles « remonter » au-dessus de lui. Comportement
  jugé acceptable après test manuel de l'utilisateur.
- **Vérification** : deux tests adaptés à la nouvelle route ; migration
  appliquée ; service systemd rechargé sans erreur ; validation visuelle par
  l'utilisateur (« ça semble bien fonctionner »). Commit `fb493b4`.
- **État : 23 tests verts.**