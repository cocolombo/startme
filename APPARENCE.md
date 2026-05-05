# Personnalisation de l'Apparence

Le design est géré via **Tailwind CSS** (chargé localement depuis `static/js/tailwind.js`).
Les modifications se font dans les fichiers de templates — aucune compilation nécessaire.

---

## 1. Grille et Disposition (Colonnes)

**Fichier :** `dashboard/templates/dashboard/index.html`
**Chercher :** `id="widget-grid"`

Modifier la classe `lg:grid-cols-4` :

| Classe | Résultat |
| :--- | :--- |
| `lg:grid-cols-3` | Plus large (3 colonnes) |
| `lg:grid-cols-4` | Défaut (4 colonnes) |
| `lg:grid-cols-5` | Plus compact (5 colonnes) |
| `grid-cols-1` | Mobile (1 colonne) |

Un widget avec `is_wide=True` utilise `col-span-2` et occupe automatiquement 2 colonnes.

---

## 2. Thème et Couleurs

### Couleurs principales

| Élément | Classe Tailwind | Emplacement |
| :--- | :--- | :--- |
| Fond global | `bg-gray-900` (`#111827`) | `<body>` dans `index.html` |
| Fond des widgets | `bg-gray-800` (`#1f2937`) | `widget.html` |
| Bordures | `border-gray-700` (`#374151`) | partout |
| Texte principal | `text-gray-200` | `<body>` dans `index.html` |
| Texte secondaire | `text-gray-400` / `text-gray-500` | labels, compteurs |

### Couleurs d'accent

| Élément | Classe | Emplacement |
| :--- | :--- | :--- |
| Titres des widgets | `text-orange-400` | `widget_title.html` |
| En-têtes menus contextuels | `text-orange-400` | `menus.html` |
| Liens (hover) | `hover:text-blue-400` | `link_item.html`, `widget.html` |
| Page active (sidebar) | `bg-blue-600/20 text-blue-400` | `sidebar_menu.html` |
| Commandes/Snippets | `text-green-400` | `command_item.html`, `snippet_item.html` |

Pour changer la couleur d'accent des titres de widgets, remplacez `text-orange-400` par `text-blue-400`, `text-green-400`, `text-purple-400`, etc. dans `widget_title.html`.

---

## 3. Densité (Espacement des Liens)

**Fichier :** `templates/partials/link_item.html`

- Écart vertical entre liens : modifier `space-y-0.5` sur le `<ul>` parent (dans `widget.html`)
- Padding vertical des lignes : modifier `py-1` sur les `<li>`

---

## 4. Drag & Drop (Effet Visuel)

L'élément glissé affiche un fantôme semi-transparent. Configurable dans `index.html` :

```css
.sortable-ghost { opacity: 0.4; background-color: #4B5563; }
```

---

## 5. Widgets Spéciaux (Page "Infos")

### Widget Bourse (TradingView)

**Fichier :** `templates/partials/widgets_infos.html`
Cherchez le bloc `<script ... embed-widget-market-overview.js">`.
Modifiez la liste `"symbols"` dans le JSON :

```json
{ "s": "NASDAQ:AAPL", "d": "Apple" }
```

Format : `"s": "MARCHE:SYMBOLE"`, `"d": "Nom affiché"`

### Widget Météo (Open-Meteo)

La configuration se fait dans le fichier **`.env`** (pas dans le JS) :

```
WEATHER_CITY="Montréal, QC"
WEATHER_LAT=45.5088
WEATHER_LON=-73.5878
WEATHER_TIMEZONE=America/Toronto
```

Le JS dans `scripts.html` lit ces valeurs via les variables de contexte Django (`{{ weather_lat }}`, etc.).
