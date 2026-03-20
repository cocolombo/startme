import os

# 1. Définition des contenus des fichiers
# ---------------------------------------

models_content = """from django.db import models

class Page(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class Widget(models.Model):
    title = models.CharField(max_length=100)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='widgets')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Link(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    icon_url = models.URLField(blank=True, null=True)
    widget = models.ForeignKey(Widget, on_delete=models.CASCADE, related_name='links')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
"""

views_content = """from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import Page, Link
from django.views.decorators.csrf import csrf_exempt # Simplification pour le dev local

def index(request, slug=None):
    pages = Page.objects.all()
    if not slug:
        active_page = pages.first()
    else:
        active_page = get_object_or_404(Page, slug=slug)
    
    context = {
        'pages': pages,
        'active_page': active_page,
    }
    return render(request, 'dashboard/index.html', context)

@csrf_exempt 
@require_POST
def update_link_order(request):
    # Note: Dans un vrai projet prod, il faut gérer le CSRF token via JS
    link_ids = request.POST.getlist('link')
    for index, link_id in enumerate(link_ids):
        try:
            link = Link.objects.get(id=link_id)
            link.order = index
            link.save()
        except Link.DoesNotExist:
            continue
    return HttpResponse(status=200)

@csrf_exempt
@require_POST
def move_link_to_page(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    target_page_id = request.POST.get('target_page_id')
    target_page = get_object_or_404(Page, id=target_page_id)
    
    # On déplace vers le premier widget de la page cible par défaut
    target_widget = target_page.widgets.first() 
    
    if target_widget:
        link.widget = target_widget
        link.save()
        return HttpResponse(status=200)
    return HttpResponse(status=400)
"""

urls_content = """from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index_root'),
    path('page/<slug:slug>/', views.index, name='index'),
    path('api/update-order/', views.update_link_order, name='update_order'),
    path('api/move-link/<int:link_id>/', views.move_link_to_page, name='move_link'),
]
"""

admin_content = """from django.contrib import admin
from .models import Page, Widget, Link

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'page', 'order')
    list_filter = ('page',)

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'widget', 'order')
    list_filter = ('widget__page', 'widget')
"""

html_content = """<!DOCTYPE html>
<html lang="fr" class="dark">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Perso</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@1.9.6"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Sortable/1.14.0/Sortable.min.js"></script>
    <style>
        #context-menu { display: none; position: absolute; z-index: 50; }
        .sortable-ghost { opacity: 0.4; background-color: #4B5563; }
    </style>
</head>
<body class="bg-gray-900 text-gray-200 font-sans min-h-screen select-none">

    <nav class="flex items-center space-x-2 p-3 bg-black border-b border-gray-800 overflow-x-auto">
        <div class="font-bold text-xl mr-4 text-white">≡ Pages</div>
        {% for page in pages %}
            <a href="{% url 'index' page.slug %}" 
               class="px-4 py-2 rounded transition-colors duration-200 whitespace-nowrap 
               {% if page == active_page %}bg-blue-600 text-white font-bold shadow-md{% else %}bg-gray-800 hover:bg-gray-700 text-gray-300{% endif %}">
                {{ page.name }}
            </a>
        {% endfor %}
    </nav>

    <div class="p-6">
        {% if active_page %}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {% for widget in active_page.widgets.all %}
            <div class="bg-gray-800 rounded-lg p-4 shadow-lg border border-gray-700 flex flex-col">
                <h3 class="font-bold text-orange-400 mb-3 border-b border-gray-600 pb-2 flex justify-between">
                    {{ widget.title }}
                </h3>
                <ul class="sortable-list space-y-2 flex-1 min-h-[50px]" data-widget-id="{{ widget.id }}">
                    {% for link in widget.links.all %}
                    <li class="flex items-center space-x-2 p-2 hover:bg-gray-700 rounded cursor-grab active:cursor-grabbing group relative bg-gray-800" 
                        data-id="{{ link.id }}">
                        <img src="{{ link.icon_url|default:'https://www.google.com/s2/favicons?domain='|add:link.url }}" 
                             class="w-4 h-4 rounded-sm opacity-70 group-hover:opacity-100">
                        <a href="{{ link.url }}" target="_blank" class="truncate text-sm text-blue-300 hover:text-blue-100 flex-1">
                            {{ link.title }}
                        </a>
                        <div class="absolute inset-0 z-10" oncontextmenu="showContextMenu(event, '{{ link.id }}')"></div>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="text-center text-gray-500 mt-10">Aucune page configurée. Lancez la commande seed_db !</div>
        {% endif %}
    </div>

    <div id="context-menu" class="bg-gray-800 border border-gray-600 text-gray-200 rounded shadow-xl w-56 py-1 text-sm">
        <div class="px-4 py-2 font-bold border-b border-gray-700 text-gray-400 text-xs uppercase">Actions</div>
        <div class="relative group">
            <button class="w-full text-left px-4 py-2 hover:bg-blue-600 flex justify-between items-center">
                Déplacer vers... <span>▶</span>
            </button>
            <div class="absolute left-full top-0 w-48 bg-gray-800 border border-gray-600 shadow-lg hidden group-hover:block rounded-r">
                {% for page in pages %}
                    {% if page != active_page %}
                    <form hx-post="{% url 'move_link' 0 %}" hx-trigger="click" hx-swap="none">
                        <input type="hidden" name="target_page_id" value="{{ page.id }}">
                        <button type="submit" class="w-full text-left px-4 py-2 hover:bg-blue-600 border-b border-gray-700 last:border-0">
                            {{ page.name }}
                        </button>
                    </form>
                    {% endif %}
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        // Drag & Drop
        document.querySelectorAll('.sortable-list').forEach(function(list) {
            new Sortable(list, {
                group: 'shared',
                animation: 150,
                ghostClass: 'sortable-ghost',
                onEnd: function (evt) {
                    // Récupérer l'ordre
                    var itemEl = evt.item;
                    var newIndex = evt.newIndex;
                    var listItems = evt.to.querySelectorAll('li');
                    var linkIds = Array.from(listItems).map(li => li.getAttribute('data-id'));
                    
                    // Envoi AJAX (vanilla JS pour éviter complexité HTMX ici)
                    var formData = new FormData();
                    linkIds.forEach(id => formData.append('link', id));
                    
                    fetch('/api/update-order/', {
                        method: 'POST',
                        body: formData
                    });
                }
            });
        });

        // Menu Contextuel
        const menu = document.getElementById('context-menu');
        function showContextMenu(e, linkId) {
            e.preventDefault();
            menu.style.left = e.pageX + 'px';
            menu.style.top = e.pageY + 'px';
            menu.style.display = 'block';
            
            // Mise à jour des formulaires HTMX avec le bon ID de lien
            document.querySelectorAll('form[hx-post]').forEach(form => {
                let url = form.getAttribute('hx-post').replace(/\d+$/, linkId);
                form.setAttribute('hx-post', url);
                htmx.process(form);
            });
        }
        document.addEventListener('click', () => menu.style.display = 'none');
    </script>
</body>
</html>
"""

seed_content = """from django.core.management.base import BaseCommand
from dashboard.models import Page, Widget, Link
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Remplit la DB'

    def handle(self, *args, **kwargs):
        Page.objects.all().delete()
        data = {
            "Start Page": {
                "Achats": [("Costco", "https://costco.ca"), ("Amazon", "https://amazon.ca")],
                "Maison": [("Thermostat", "#"), ("Caméras", "#")]
            },
            "Politique": {
                "News": [("La Presse", "https://lapresse.ca"), ("Le Devoir", "https://ledevoir.com")],
                "Partis": [("PQ", "https://pq.org"), ("Bloc", "https://blocquebecois.org")]
            },
            "Programmation": {
                "Dev": [("Github", "https://github.com"), ("StackOverflow", "https://stackoverflow.com")],
                "Django": [("Docs", "https://docs.djangoproject.com"), ("HTMX", "https://htmx.org")]
            }
        }
        
        for p_name, widgets in data.items():
            p = Page.objects.create(name=p_name, slug=slugify(p_name))
            for w_title, links in widgets.items():
                w = Widget.objects.create(title=w_title, page=p)
                for l_title, l_url in links:
                    Link.objects.create(title=l_title, url=l_url, widget=w)
        
        self.stdout.write(self.style.SUCCESS('Données créées!'))
"""

# 2. Création de l'arborescence et des fichiers
# ---------------------------------------------

# Nom de l'application (doit correspondre à votre INSTALLED_APPS)
app_name = 'dashboard'

# Liste des fichiers à créer
files_to_create = [
    (f'{app_name}/models.py', models_content),
    (f'{app_name}/views.py', views_content),
    (f'{app_name}/urls.py', urls_content),
    (f'{app_name}/admin.py', admin_content),
    (f'{app_name}/templates/{app_name}/index.html', html_content),
    (f'{app_name}/management/commands/seed_db.py', seed_content),
    # Initialiseurs vides pour que Python reconnaisse les dossiers comme modules
    (f'{app_name}/management/__init__.py', ''),
    (f'{app_name}/management/commands/__init__.py', ''),
]

print(f"🚀 Début de l'installation dans le dossier de l'app : {app_name}...")

for path, content in files_to_create:
    # Créer les répertoires parents si nécessaire
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Écrire le fichier
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Créé : {path}")

print("-" * 30)
print("Installation terminée !")
print("N'oubliez pas de faire :")
print("1. python manage.py makemigrations")
print("2. python manage.py migrate")
print("3. python manage.py seed_db")
print("4. python manage.py runserver")