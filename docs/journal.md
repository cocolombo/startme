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