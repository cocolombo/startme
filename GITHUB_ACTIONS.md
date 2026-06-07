# GitHub Actions — comment fonctionne la CI du projet

Document d'information expliquant ce qui se passe sur GitHub à chaque push.
Le workflow concerné est `.github/workflows/tests.yml`.

## L'idée générale

GitHub Actions est un **automate** hébergé par GitHub : on décrit dans un
fichier YAML « quand » et « quoi » exécuter, et à chaque événement
correspondant, GitHub **loue une machine jetable**, y fait tourner les
instructions, puis la détruit. Aucun serveur à gérer.

## Le déroulé, étape par étape

Quand on fait `git push` :

1. **Événement** — GitHub reçoit le push et regarde tous les fichiers
   `.github/workflows/*.yml` présents sur la branche poussée.
2. **Correspondance** — pour chacun, il lit la clé `on:`. Notre fichier dit
   `on: push` (branche `main`) + `pull_request`. Le push sur `main`
   correspond → le workflow est **déclenché**.
3. **Provisionnement du runner** — GitHub démarre une **machine virtuelle
   neuve** (`runs-on: ubuntu-latest` = un Ubuntu propre, rien d'installé à part
   les outils de base). C'est le **runner**.
4. **Exécution du job** — sur cette VM, il déroule les `steps` dans l'ordre :
   - `checkout` → clone le dépôt sur la VM
   - `setup-python` → installe Python 3.12
   - `pip install -r requirements.txt` → installe les 5 dépendances
   - `python manage.py test` → lance les 13 tests
5. **Verdict** — si **toutes** les étapes renvoient un code de sortie 0, le job
   est ✅. Dès qu'une échoue (ex. un test rouge → `manage.py test` renvoie un
   code ≠ 0), le job s'arrête en ❌.
6. **Destruction** — la VM est **détruite** immédiatement après. Rien ne
   persiste (sauf ce qu'on choisit de garder, voir plus bas).

> C'est pour ça que la CI est un juge impartial : elle repart **toujours de
> zéro**, sans le venv local ni le `.env`. Si ça marche là, ça marche
> « proprement ».

## Le vocabulaire (avec notre fichier)

| Terme | Dans `tests.yml` | Rôle |
|-------|------------------|------|
| **Workflow** | tout le fichier (`name: Tests`) | L'unité déclenchée par un événement |
| **Événement** | `on: push / pull_request` | Le « quand » |
| **Job** | `test:` | Un ensemble d'étapes sur **une** VM |
| **Runner** | `runs-on: ubuntu-latest` | La VM jetable |
| **Step** | chaque `- ` sous `steps:` | Une instruction |
| **Action** | `uses: actions/checkout@v5` | Une brique **réutilisable** publiée par un tiers |
| **Commande** | `run: python manage.py test` | Une ligne shell écrite par nous |

## Deux types de steps : `uses` vs `run`

- **`run:`** = on exécute sa propre commande shell (comme dans le terminal).
- **`uses:`** = on réutilise une **action** packagée, partagée via le
  **Marketplace**. `actions/checkout` et `actions/setup-python` sont
  officielles. Le `@v5` est une **version épinglée**, exactement comme une
  dépendance pip.

## L'avertissement Node.js

Les actions `uses:` sont elles-mêmes des programmes ; beaucoup tournent sur un
**runtime Node.js** fourni par le runner. GitHub déprécie Node 20 → les vieilles
versions d'actions génèrent un *warning*. En passant à `checkout@v5` /
`setup-python@v6` (qui ciblent Node 24), l'avertissement disparaît. Aucun
rapport avec le code Python — c'est purement l'outillage de la CI.

## Notions utiles pour la suite

- **Logs & historique** : chaque run est archivé dans l'onglet *Actions*. On
  peut rouvrir un vieux run et lire ses logs (utile pour une régression).
- **Badge de statut** : on peut afficher une pastille ✅/❌ dans le `README`
  (`![Tests](…/actions/workflows/tests.yml/badge.svg)`).
- **Protection de branche** : on peut exiger que la CI soit verte **avant** de
  merger une PR (Settings → Branches). C'est là que la CI prend toute sa valeur
  en équipe.
- **Secrets** : pour de vraies clés (API, déploiement), ne **jamais** les mettre
  dans le YAML ; les stocker dans *Settings → Secrets* et les lire via
  `${{ secrets.NOM }}`. Ici la `SECRET_KEY` est factice et en clair, car elle
  n'a aucune valeur de sécurité pour des tests.
- **Coût** : gratuit et illimité pour les dépôts **publics**. Pour les dépôts
  **privés**, quota de minutes mensuel gratuit (large pour un petit projet).
- **Artefacts & cache** : on peut garder des fichiers produits par un run
  (rapport de couverture, build) ou mettre en cache des dossiers — c'est ce que
  fait `cache: pip`, qui réutilise les paquets téléchargés d'un run à l'autre
  pour accélérer.

---

**En résumé :** on décrit l'intention en YAML, GitHub loue une machine propre,
exécute, juge, et nettoie. Le dépôt a maintenant ce réflexe automatique à
chaque modification.
