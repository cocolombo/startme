# 🧩 Guide de Création des Widgets (WIDGETS_API)

Ce document explique l'architecture des "Widgets Spéciaux" (ceux présents sur la page **Infos**) et détaille la marche à suivre pour en créer de nouveaux.

Contrairement aux widgets standards (Listes, Notes, Commandes) qui sont créés dynamiquement par l'utilisateur via l'interface et stockés en base de données, les **Widgets Spéciaux sont codés en dur** dans les templates pour accomplir des tâches spécifiques (Météo, Monitoring, Bourse).

---

## 🏗️ 1. Architecture Générale

Tous les widgets spéciaux sont rassemblés dans un seul fichier template :
👉 `templates/partials/widgets_infos.html`

Ce fichier est chargé uniquement si l'utilisateur se trouve sur la page dont le slug est exactement `infos` (défini dans `views.py -> index()`).

### La Grille (CSS Grid)
La page utilise Tailwind CSS pour créer une grille responsive :
*   `grid-cols-1` sur mobile.
*   `md:grid-cols-3` sur grand écran (3 colonnes).

Chaque widget est une `div` qui occupe une ou plusieurs colonnes (ex: `col-span-1`).

### Le Conteneur Standard (Boîte de base)
Pour qu'un nouveau widget s'intègre parfaitement au design existant, il doit utiliser les classes CSS suivantes :

```html
<div class="col-span-1 bg-gray-800 rounded-lg p-4 shadow-lg border border-gray-700 h-64 flex flex-col">
    <h3 class="font-bold text-orange-400 mb-2 text-lg">Mon Titre</h3>
    <!-- Contenu du widget ici -->
</div>
```
*(Note: La hauteur `h-56` ou `h-64` permet de standardiser la taille des blocs).*

---

## ⚙️ 2. Les 3 Méthodes de Création (avec exemples)

Il y a trois façons principales d'alimenter un widget en données.

### Méthode A : 100% Frontend (JavaScript Vanilla)
**Idéal pour :** Calculatrice, Minuteur, Horloges.
**Fonctionnement :** Le HTML et la logique JS sont entièrement contenus dans `widgets_infos.html`. Pas de requête au serveur.

*Exemple minimal :*
```html
<div class="col-span-1 bg-gray-800 rounded-lg p-4 h-64">
    <div id="mon-compteur" class="text-white text-2xl">0</div>
    <button onclick="document.getElementById('mon-compteur').innerText++">Click</button>
</div>
```

### Méthode B : Backend via HTMX (Polling ou Chargement Ajax)
**Idéal pour :** Monitoring système (psutil), Infos Réseau, lectures de fichiers locaux.
**Fonctionnement :** Le widget HTML est vide au départ. HTMX interroge une vue Django (`views.py`) qui renvoie un fragment HTML (un template partiel) pour remplir le widget.

*Étape 1 : Le Conteneur dans `widgets_infos.html`*
```html
<!-- hx-get appelle l'URL, hx-trigger="load" le fait au démarrage, "every 5s" le répète -->
<div class="col-span-1 bg-gray-800 rounded-lg p-4 h-64"
     hx-get="/api/mon-nouveau-widget/"
     hx-trigger="load, every 10s">
    <div class="text-gray-500 animate-pulse">Chargement...</div>
</div>
```

*Étape 2 : La Vue dans `views.py`*
```python
def get_mon_nouveau_widget(request):
    donnees = "Ceci vient de Python !"
    # Renvoie un fragment HTML, pas une page complète !
    return render(request, 'partials/mon_widget_partial.html', {'data': donnees})
```

*Étape 3 : Le routeur dans `urls.py`*
```python
path('api/mon-nouveau-widget/', views.get_mon_nouveau_widget, name='mon_widget'),
```

### Méthode C : API Externe via Frontend (Fetch / iFrame)
**Idéal pour :** Météo, Marchés boursiers (TradingView).
**Fonctionnement :** Le widget intègre un script fourni par un tiers, ou fait un appel `fetch()` en JS vers une API publique.

*Exemple avec l'API Météo (déjà implémentée) :*
*   L'appel se fait vers `api.open-meteo.com`.
*   Les coordonnées sont récupérées dynamiquement dans `scripts.html`.
*   Le DOM est mis à jour en JS (`document.getElementById('current-temp').textContent = ...`).

---

## 🔌 3. APIs Externes Utilisées Actuellement

Si un widget tombe en panne, voici les services externes dont dépend le dashboard actuel :

1.  **Météo :** Open-Meteo (Gratuit, sans clé API).
    *   *Endpoint :* `https://api.open-meteo.com/v1/forecast`
2.  **Marchés Financiers :** TradingView (Widget Embed).
    *   *Script :* `https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js`
3.  **Adresse IP Publique :** Ipify (Gratuit, sans clé API).
    *   *Endpoint :* `https://api.ipify.org`
4.  **Favicons (Images des liens) :** Google S2 (Non officiel mais très stable).
    *   *Endpoint :* `https://www.google.com/s2/favicons?domain=...`

---

## 🎨 4. Bonnes Pratiques

1.  **Ne surchargez pas `index.html`** : Gardez les scripts spécifiques aux widgets de la page Infos dans `widgets_infos.html` ou chargez-les via des fichiers externes si cela devient trop gros.
2.  **Gérez les erreurs gracieusement** : Si une API (comme Ipify ou Open-Meteo) ne répond pas, le widget ne doit pas faire planter la page. Affichez "Indisponible" en gris. (C'est ce qui est fait dans le bloc `try/except` de `views.py` pour le réseau).
3.  **Attention au Polling HTMX** : Un `hx-trigger="every 1s"` sur 5 widgets différents va bombarder votre serveur Django (et potentiellement votre CPU) de requêtes. Préférez des intervalles de `5s` ou `10s` pour le monitoring local, et n'utilisez **jamais** de polling HTMX rapide pour appeler des APIs externes payantes/limitées.
