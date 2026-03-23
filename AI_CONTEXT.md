Voici le contexte de mon projet actuel.

Contexte Technique du Projet Dashboard

1. Stack Technique

    Backend : Python 3.12, Django 5.2.
    Frontend : HTML5, Tailwind CSS (Local), HTMX (AJAX), SortableJS.
    Base de données : SQLite.
    Système : psutil (monitoring serveur), python-dotenv (configuration).
    Design : Dark Mode par défaut.

2. Models (dashboard/models.py)

Structure hiérarchique : Page > Widget > Link.

class Page(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class Widget(models.Model):
    TYPE_CHOICES = [
        ('list', 'Liste de liens'),
        ('note', 'Bloc-notes'),
        ('command', 'Lanceur de scripts'),
        ('snippet', 'Bloc de commandes'),
    ]

    title = models.CharField(max_length=100)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='widgets')
    order = models.IntegerField(default=0)
    widget_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='list')
    content = models.TextField(blank=True, null=True)   # utilisé par le type 'note'
    is_wide = models.BooleanField(default=False)         # largeur 2 colonnes

    class Meta:
        ordering = ['order']

class Link(models.Model):
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=500, blank=True, null=True)  # URL, chemin local ou commande shell
    widget = models.ForeignKey(Widget, on_delete=models.CASCADE, related_name='links')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

3. URLs (dashboard/urls.py)

    # Vues principales
    path('', views.index, name='index_root')
    path('page/<slug:slug>/', views.index, name='index')

    # Pages
    path('page/create/', views.create_page, name='create_page')
    path('page/rename/<int:page_id>/', views.rename_page, name='rename_page')
    path('page/delete/<int:page_id>/', views.delete_page, name='delete_page')

    # Widgets
    path('widget/add/<int:page_id>/', views.add_widget, name='add_widget')
    path('widget/delete/<int:widget_id>/', views.delete_widget, name='delete_widget')
    path('widget/<int:pk>/rename/', views.rename_widget, name='rename_widget')
    path('widget/move/<int:widget_id>/', views.move_widget_to_page, name='move_widget')
    path('widget/toggle-width/<int:widget_id>/', views.toggle_widget_width, name='toggle_widget_width')

    # Liens
    path('link/add/<int:widget_id>/', views.add_link, name='add_link')
    path('link/delete/<int:link_id>/', views.delete_link, name='delete_link')
    path('link/<int:pk>/edit/', views.edit_link, name='edit_link')
    path('link/<int:pk>/cancel/', views.cancel_edit_link, name='cancel_edit_link')
    path('link/run/<int:link_id>/', views.run_command, name='run_command')
    path('link/open-local/<int:link_id>/', views.open_local_file, name='open_local_file')

    # API (HTMX / JS)
    path('api/update-page-order/', views.update_page_order, name='update_page_order')
    path('api/update-widget-order/', views.update_widget_order, name='update_widget_order')
    path('api/update-order/', views.update_link_order, name='update_order')
    path('api/move-link/<int:link_id>/', views.move_link_to_page, name='move_link')
    path('api/save-note/<int:widget_id>/', views.save_note_content, name='save_note')

    # Utilitaires / Page Infos
    path('api/system-monitor/', views.system_monitor, name='system_monitor')
    path('api/network-info/', views.get_network_info, name='get_network_info')
    path('api/backup/', views.download_backup, name='download_backup')

4. Règles UI & Frontend

    Templates : Un seul template principal index.html situé dans startme/templates/dashboard/.
    Partials : Les fragments HTML pour HTMX sont dans startme/templates/partials/.

    Interactions :
        Drag & Drop : SortableJS, sauvegarde via API fetch.
        Édition : Inline via HTMX (hx-swap="outerHTML").
        Widgets Infos : La page avec le slug 'infos' charge un layout spécifique (widgets_infos.html)
        Widgets Spéciaux : Météo (API JS), Calendrier (JS Frontend), Marchés (Iframe TradingView), Système (HTMX Polling), Réseau (HTMX), Calculatrice (JS), Minuteur Pomodoro (JS avec Web Audio API).

5. Types de widgets

    list     : Liste de liens cliquables (défaut). Partial : link_item.html
    note     : Bloc-notes auto-sauvegardé (textarea). Contenu stocké dans Widget.content.
    command  : Lanceur de scripts — exécute un Link.url via run_command. Partial : command_item.html
    snippet  : Bloc de commandes à copier (pas d'exécution). Partial : snippet_item.html
               Supporte is_wide pour affichage en 2 colonnes.
    infos    : Widgets système hardcodés (Météo, Horloges, Réseau, etc.) exclusifs à la page 'infos'.
