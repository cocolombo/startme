from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from .models import Page, Widget, Link
import psutil
import subprocess
import os
import shutil
import socket
import requests

import zipfile
import io
import logging
from datetime import datetime
from django.conf import settings
from django.http import FileResponse

logger = logging.getLogger(__name__)

def index(request, slug=None):
    """Affiche la page principale du tableau de bord.

    Cette vue récupère toutes les pages pour la navigation et détermine
    la page active en se basant sur le 'slug' fourni dans l'URL. Si aucun
    slug n'est fourni, la première page est affichée par défaut.

    Args:
        request (HttpRequest): L'objet de requête Django.
        slug (str, optional): Le slug de la page à afficher. Defaults to None.

    Returns:
        HttpResponse: La page HTML du tableau de bord rendue avec le contexte.
    """
    pages = Page.objects.all()
    if not slug:
        active_page = pages.first()
    else:
        active_page = get_object_or_404(Page, slug=slug)

    context = {
        'pages': pages,
        'active_page': active_page,
        'weather_city': settings.WEATHER_CITY,
        'weather_lat': settings.WEATHER_LAT,
        'weather_lon': settings.WEATHER_LON,
        'weather_timezone': settings.WEATHER_TIMEZONE,
        'clock_timezones': settings.CLOCK_TIMEZONES,
    }
    return render(request, 'dashboard/index.html', context)


@csrf_exempt
@require_POST
def update_link_order(request):
    """Met à jour l'ordre et l'appartenance des liens après un glisser-déposer.

    Cette API est appelée par HTMX/SortableJS. Elle met à jour l'attribut 'order'
    de chaque lien et peut changer le widget parent si un lien est déplacé
    vers une autre catégorie.

    Args:
        request (HttpRequest): La requête POST doit contenir :
            - 'widget_id' (int): L'ID du widget de destination.
            - 'link' (list[int]): Une liste des IDs des liens dans leur nouvel ordre.

    Returns:
        HttpResponse: Un statut 200 OK si la mise à jour réussit.
    """
    # 1. On récupère l'ID du widget dans lequel le lien a atterri
    widget_id = request.POST.get('widget_id')
    # 2. On récupère la liste des liens dans leur nouvel ordre
    link_ids = request.POST.getlist('link')

    # Si on a un widget_id (donc un déplacement ou réarrangement)
    if widget_id:
        target_widget = get_object_or_404(Widget, id=widget_id)

        for index, link_id in enumerate(link_ids):
            try:
                link = Link.objects.get(id=link_id)

                # On change le parent du lien pour le nouveau widget
                link.widget = target_widget

                # On met à jour sa position
                link.order = index
                link.save()
            except Link.DoesNotExist:
                continue

    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def update_widget_order(request):
    """Met à jour l'ordre des widgets (catégories) sur une page.

    Appelée par SortableJS lors du déplacement d'un bloc widget entier.

    Args:
        request (HttpRequest): La requête POST doit contenir :
            - 'widget' (list[int]): Liste ordonnée des IDs des widgets.

    Returns:
        HttpResponse: Statut 200 si succès.
    """
    widget_ids = request.POST.getlist('widget')

    for index, widget_id in enumerate(widget_ids):
        try:
            widget = get_object_or_404(Widget, id=widget_id)
            widget.order = index
            widget.save()
        except Exception:
            continue

    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def move_link_to_page(request, link_id):
    """Déplace un lien vers un widget ou une page via le menu contextuel.

    Args:
        request (HttpRequest): La requête POST doit contenir soit
            'target_widget_id' (widget précis) soit 'target_page_id'
            (premier widget de la page).
        link_id (int): L'ID du lien à déplacer.

    Returns:
        HttpResponse: Statut 200 si succès, 400 si aucun widget trouvé.
    """
    link = get_object_or_404(Link, id=link_id)
    target_widget_id = request.POST.get('target_widget_id')
    target_page_id = request.POST.get('target_page_id')

    if target_widget_id:
        target_widget = get_object_or_404(Widget, id=target_widget_id)
    elif target_page_id:
        target_page = get_object_or_404(Page, id=target_page_id)
        target_widget = target_page.widgets.first()
        if not target_widget:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)

    link.widget = target_widget
    link.save()
    return HttpResponse(status=200)


@require_POST
def add_link(request, widget_id):
    """Ajoute un nouveau lien dans un widget spécifique.

    Args:
        request (HttpRequest): La requête POST doit contenir 'title' et 'url'.
        widget_id (int): L'ID du widget parent.

    Returns:
        HttpResponse: Le fragment HTML du nouveau lien (pour insertion HTMX).
    """
    widget = get_object_or_404(Widget, id=widget_id)
    title = request.POST.get('title', '')
    url = request.POST.get('url', '')

    link = None
    if widget.widget_type == 'snippet':
        if url:
            link = Link.objects.create(title=title, url=url, widget=widget, order=999)
    elif title:
        link = Link.objects.create(title=title, url=url, widget=widget, order=999)

    if link is None:
        return HttpResponse(status=400)

    if widget.widget_type == 'command':
        return render(request, 'partials/command_item.html', {'link': link})
    elif widget.widget_type == 'snippet':
        return render(request, 'partials/snippet_item.html', {'link': link})
    else:
        return render(request, 'partials/link_item.html', {'link': link})

def delete_link(request, link_id):
    """Supprime un lien spécifique.

    Args:
        request (HttpRequest): L'objet de requête.
        link_id (int): L'ID du lien à supprimer.

    Returns:
        HttpResponse: Réponse vide 200 (HTMX retire l'élément du DOM côté client).
    """
    link = get_object_or_404(Link, id=link_id)
    link.delete()
    return HttpResponse(status=200)


@require_POST
def create_page(request):
    """Crée une nouvelle page (onglet) dans le tableau de bord.

    Gère la création automatique d'un slug unique basé sur le nom.

    Args:
        request (HttpRequest): La requête POST doit contenir 'name'.

    Returns:
        HttpResponseRedirect: Redirige vers la nouvelle page créée.
    """
    name = request.POST.get('name')
    if name:
        # On génère un slug unique (ex: "Ma Page" -> "ma-page")
        base_slug = slugify(name)
        slug = base_slug
        counter = 1

        # Gestion des doublons de slug
        while Page.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # On crée la page (à la fin de la liste par défaut)
        Page.objects.create(name=name, slug=slug, order=999)

        # On redirige immédiatement vers la nouvelle page
        return redirect('index', slug=slug)

    return redirect('index_root')


@require_POST
def rename_page(request, page_id):
    """Renomme une page existante.

    Met à jour le nom et régénère le slug pour garder l'URL cohérente.

    Args:
        request (HttpRequest): La requête POST doit contenir le nouveau 'name'.
        page_id (int): L'ID de la page à modifier.

    Returns:
        HttpResponseRedirect: Redirige vers la page avec son nouveau slug.
    """
    page = get_object_or_404(Page, id=page_id)
    new_name = request.POST.get('name')

    if new_name:
        page.name = new_name
        base_slug = slugify(new_name)
        slug = base_slug
        counter = 1
        while Page.objects.filter(slug=slug).exclude(id=page.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        page.slug = slug
        page.save()
        return redirect('index', slug=page.slug)

    return redirect('index', slug=page.slug)


def delete_page(request, page_id):
    """Supprime une page complète et tout son contenu (widgets/liens).

    Args:
        request (HttpRequest): L'objet de requête.
        page_id (int): L'ID de la page à supprimer.

    Returns:
        HttpResponseRedirect: Redirige vers la racine (index_root).
    """
    page = get_object_or_404(Page, id=page_id)
    page.delete()
    return redirect('index_root')


@require_POST
def move_widget_to_page(request, widget_id):
    """Déplace un widget (catégorie) entier vers une autre page.

    Args:
        request (HttpRequest): La requête POST doit contenir 'target_page_id'.
        widget_id (int): L'ID du widget à déplacer.

    Returns:
        HttpResponseRedirect: Redirige vers la page d'origine (HTTP_REFERER).
    """
    widget = get_object_or_404(Widget, id=widget_id)
    target_page_id = request.POST.get('target_page_id')

    if target_page_id:
        target_page = get_object_or_404(Page, id=target_page_id)
        widget.page = target_page
        # On place le widget à la fin de la nouvelle page
        widget.order = 999
        widget.save()

    # On recharge la page actuelle pour voir le widget disparaître
    return redirect(request.META.get('HTTP_REFERER', '/'))


def toggle_widget_width(request, widget_id):
    """Bascule le widget entre 1 colonne et 2 colonnes."""
    widget = get_object_or_404(Widget, id=widget_id)
    widget.is_wide = not widget.is_wide
    widget.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_widget(request, widget_id):
    """Supprime un widget (catégorie) et tous les liens ou notes qu'il contient.

    Args:
        request (HttpRequest): L'objet de requête.
        widget_id (int): L'ID du widget à supprimer.

    Returns:
        HttpResponseRedirect: Redirige vers la page précédente.
    """
    widget = get_object_or_404(Widget, id=widget_id)
    widget.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def add_widget(request, page_id):
    """Ajoute une nouvelle catégorie (Widget) sur une page spécifique.

    Prend en compte le type de widget sélectionné (Liste ou Bloc-notes).

    Args:
        request (HttpRequest): La requête POST doit contenir 'title' et 'widget_type'.
        page_id (int): L'ID de la page parente.

    Returns:
        HttpResponseRedirect: Redirige vers la page active (index).
    """
    page = get_object_or_404(Page, id=page_id)
    title = request.POST.get('title')
    # C'est la ligne magique qui manquait :
    # On récupère le choix fait dans la modale (ou 'list' par défaut)
    w_type = request.POST.get('widget_type', 'list')

    if title:
        Widget.objects.create(
            title=title,
            page=page,
            order=999,
            widget_type=w_type  # On enregistre le type en base de données
        )

    return redirect('index', slug=page.slug)


def rename_widget(request, pk):
    """Gère l'édition en ligne du titre d'un widget.

    Cette vue a un double comportement en fonction de la méthode HTTP :
    - GET : Renvoie un fragment HTML contenant un formulaire pour éditer le titre.
    - POST : Met à jour le titre du widget en base de données et renvoie
      le fragment HTML du titre mis à jour.

    Args:
        request (HttpRequest): La requête HTTP (GET ou POST).
        pk (int): La clé primaire du widget à modifier.

    Returns:
        HttpResponse: Un fragment HTML (soit le formulaire, soit le titre).
    """
    widget = get_object_or_404(Widget, pk=pk)

    # 1. Si on reçoit du POST, c'est que l'utilisateur a validé le formulaire
    if request.method == "POST":
        new_title = request.POST.get('title')
        if new_title:
            widget.title = new_title
            widget.save()
        # On renvoie le template d'affichage (le HTML normal)
        return render(request, 'partials/widget_title.html', {'widget': widget})

    # 2. Si on reçoit du GET, c'est que l'utilisateur a cliqué pour éditer
    # On renvoie le formulaire d'édition
    return render(request, 'partials/widget_title_form.html', {'widget': widget})


def edit_link(request, pk):
    """Gère l'édition d'un objet Link.

    Cette vue gère les requêtes GET et POST pour l'édition d'un objet Link.

    Args:
        request (HttpRequest): L'objet HttpRequest contenant les informations de la requête HTTP.
        pk (int): La clé primaire (primary key) de l'objet Link à éditer.

    Returns:
        HttpResponse: Un objet HttpResponse contenant le rendu d'une template HTML ou une redirection vers une autre URL.

    Raises:
        Http404: Si l'objet Link correspondant à la clé primaire ne peut pas être trouvé.

    Notes:
        - Si la requête est de type POST, les champs 'title' et 'url' de l'objet Link sont mis à jour avec les valeurs envoyées par le client.
        - En fonction du widget_type de l'objet Link, soit un bouton (command_item.html) soit une ligne de liste (link_item.html) sera rendu.
    """
    link = get_object_or_404(Link, pk=pk)

    if request.method == "POST":
        # Sauvegarde
        link.title = request.POST.get('title')
        link.url = request.POST.get('url')
        link.save()

        # INTELLIGENCE ICI :
        # Si le widget parent est de type 'command', on renvoie un BOUTON.
        # Sinon, on renvoie une LIGNE DE LISTE.
        if link.widget.widget_type == 'command':
            return render(request, 'partials/command_item.html', {'link': link})
        elif link.widget.widget_type == 'snippet':
            return render(request, 'partials/snippet_item.html', {'link': link})
        else:
            return render(request, 'partials/link_item.html', {'link': link})

    # Si GET, on renvoie le formulaire d'édition
    return render(request, 'partials/link_form.html', {'link': link})


def cancel_edit_link(request, pk):
    """Annulation de l'édition : retourne le link_item sans modification."""
    link = get_object_or_404(Link, pk=pk)
    if link.widget.widget_type == 'command':
        return render(request, 'partials/command_item.html', {'link': link})
    elif link.widget.widget_type == 'snippet':
        return render(request, 'partials/snippet_item.html', {'link': link})
    return render(request, 'partials/link_item.html', {'link': link})


# dashboard/views.py

def get_gpu_stats():
    """Récupère VRAM et Température via nvidia-smi sans librairie tierce.

    Returns:
        dict: Un dictionnaire contenant 'temp', 'used', 'total', 'percent' si succès.
        None: Si la commande échoue (pas de GPU Nvidia ou driver manquant).
    """
    try:
        # On demande : température, mémoire utilisée, mémoire totale
        cmd = "nvidia-smi --query-gpu=temperature.gpu,memory.used,memory.total --format=csv,noheader,nounits"
        output = subprocess.check_output(cmd.split(), encoding='utf-8')
        temp, used, total = map(int, output.strip().split(', '))
        return {
            'temp': temp,
            'used': used,
            'total': total,
            'percent': round((used / total) * 100, 1)
        }
    except Exception:
        return None  # Pas de GPU Nvidia ou erreur driver


def system_monitor(request):
    """Récupère les métriques du système (CPU, GPU, RAM, Disque) pour le widget de monitoring.

    Cette vue est appelée périodiquement par HTMX (Polling).

    Args:
        request (HttpRequest): L'objet de requête.

    Returns:
        HttpResponse: Le fragment HTML (Partial) avec les jauges et valeurs mises à jour.
    """
    # 1. CPU & RAM (Existant)
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()

    # 2. DISQUES — configurés via MONITOR_DISKS dans .env
    disks_to_check = settings.MONITOR_DISKS

    disks_info = []
    for d in disks_to_check:
        try:
            usage = psutil.disk_usage(d['path'])
            disks_info.append({
                'name': d['name'],
                'device': d['path'].rstrip('/').split('/')[-1],
                'percent': round(usage.percent, 1),
                'free_gb': round(usage.free / (1024 ** 3)),
                'used_gb': round(usage.used / (1024 ** 3)),
                'total_gb': round(usage.total / (1024 ** 3)),
            })
        except FileNotFoundError:
            continue

    # 3. GPU
    gpu = get_gpu_stats()

    context = {
        'cpu_usage': cpu,
        'ram_percent': ram.percent,
        'ram_used_gb': round(ram.used / (1024 ** 3), 1),
        'ram_total_gb': round(ram.total / (1024 ** 3), 1),
        'disks': disks_info,  # On envoie la liste des disques
        'gpu': gpu,
    }
    return render(request, 'partials/system_monitor.html', context)

@require_POST
def save_note_content(request, widget_id):
    """Sauvegarde automatiquement le contenu textuel d'un widget 'Bloc-notes'.

    Déclenché par HTMX lors de la frappe ou de la perte de focus.

    Args:
        request (HttpRequest): La requête POST doit contenir 'content'.
        widget_id (int): L'ID du widget.

    Returns:
        HttpResponse: Statut 200 OK (pas de rendu HTML nécessaire).
    """
    widget = get_object_or_404(Widget, id=widget_id)
    # On récupère le contenu envoyé par le champ texte
    new_content = request.POST.get('content', '')
    widget.content = new_content
    widget.save()
    # On ne renvoie rien (ou un petit statut 200 OK), HTMX n'a pas besoin de redessiner
    return HttpResponse(status=200)


def open_local_file(request, link_id):
    """Ouvre un fichier ou dossier local sur le serveur (l'ordinateur de l'utilisateur).

    Utilise la commande système `xdg-open` pour contourner les restrictions de sécurité
    des navigateurs concernant les liens `file://`.

    Args:
        request (HttpRequest): L'objet de requête.
        link_id (int): L'ID du lien contenant le chemin local.

    Returns:
        HttpResponse:
            - 204 (No Content) si succès (l'action est faite côté système).
            - 404 si le fichier n'existe pas sur le disque.
    """
    link = get_object_or_404(Link, id=link_id)
    path = link.url.strip()

    # Nettoyage si l'utilisateur a copié "file://"
    if path.startswith('file://'):
        path = path[7:]

    if os.path.exists(path):
        # xdg-open est la commande magique d'Ubuntu pour ouvrir n'importe quoi
        # avec le programme par défaut
        subprocess.Popen(['xdg-open', path], start_new_session=True)
        return HttpResponse(status=204) # 204 = Succès, ne fais rien sur la page
    else:
        logger.warning("Fichier introuvable : %s", path)
        return HttpResponse(status=404)


@csrf_exempt
@require_POST
def update_page_order(request):
    """API pour réorganiser les pages (onglets) via Drag & Drop.

    Args:
        request (HttpRequest): La requête POST doit contenir 'page' (liste d'IDs).

    Returns:
        HttpResponse: Statut 200 si succès.
    """
    page_ids = request.POST.getlist('page')

    for index, page_id in enumerate(page_ids):
        try:
            page = get_object_or_404(Page, id=page_id)
            page.order = index
            page.save()
        except Exception:
            continue

    return HttpResponse(status=200)


def download_backup(request):
    """Crée une archive ZIP du projet complet et la renvoie pour téléchargement.

    Exclut les dossiers lourds ou inutiles (.venv, .git, __pycache__, etc.).

    Args:
        request (HttpRequest): L'objet de requête.

    Returns:
        FileResponse: Le fichier ZIP en téléchargement (attachment).
    """

    # 1. Préparation du fichier en mémoire (pas d'écriture sur le disque du serveur)
    buffer = io.BytesIO()

    # 2. Nom du fichier avec la date (ex: backup_startme_2025-12-02_14h30.zip)
    timestamp = datetime.now().strftime('%Y-%m-%d_%Hh%M')
    filename = f"backup_startme_{timestamp}.zip"

    # 3. Dossiers à ignorer absolument
    # .venv / venv : L'environnement virtuel (très lourd et recréable)
    # .git : L'historique de version (lourd et déjà sur Github)
    # __pycache__ : Fichiers compilés python inutiles
    # .idea : Configuration PyCharm (optionnel, souvent perso)
    EXCLUDE_DIRS = {'.venv', 'venv', '.git', '__pycache__', '.idea'}

    # 4. Création du ZIP
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # On parcourt tout le dossier du projet (BASE_DIR)
        for root, dirs, files in os.walk(settings.BASE_DIR):
            # Filtrage des dossiers interdits (modification de la liste 'dirs' en place)
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                # On ignore aussi les fichiers compilés individuels et la db si elle est verrouillée (optionnel)
                if file.endswith(('.pyc', '.pyo', '.log')):
                    continue

                # Chemin complet sur le disque
                file_path = os.path.join(root, file)

                # Chemin relatif à l'intérieur du ZIP (pour garder la structure)
                # ex: /home/nimzo/.../startme/manage.py devient startme/manage.py
                archive_name = os.path.relpath(file_path, settings.BASE_DIR)

                try:
                    zip_file.write(file_path, archive_name)
                except PermissionError:
                    continue  # On saute les fichiers qu'on n'a pas le droit de lire

    # 5. Envoi du fichier
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=filename)


@require_POST
def run_command(request, link_id):
    """Exécute une commande shell dans une nouvelle fenêtre de terminal.

    Récupère une commande depuis un objet Link et la lance dans un terminal
    graphique (gnome-terminal, xterm, etc.). Un script wrapper est utilisé
    pour afficher un message de succès ou d'erreur et pour garder la
    fenêtre ouverte jusqu'à ce que l'utilisateur appuie sur Entrée.

    Args:
        request (HttpRequest): L'objet de requête Django.
        link_id (int): L'ID du lien contenant la commande à exécuter.

    Returns:
        HttpResponse:
            - 204 No Content: Si la commande est lancée avec succès.
            - 400 Bad Request: Si la commande est vide.
            - 500 Internal Server Error: Si aucun terminal n'est trouvé ou
              si une autre exception se produit.
    """
    link = get_object_or_404(Link, id=link_id)
    command = link.url.strip()

    logger.debug("Tentative d'exécution : %s", command)

    if not command:
        return HttpResponse(status=400)

    # 1. Détection du terminal (Mate > Gnome > Xterm > Konsole)
    terminal_path = shutil.which('mate-terminal') or shutil.which('gnome-terminal') or shutil.which('xterm') or shutil.which('konsole')

    if not terminal_path:
        logger.error("Aucun terminal compatible trouvé")
        return HttpResponse(status=500)

    try:
        # 2. Construction du script Bash robuste
        # - On exécute la commande de l'utilisateur.
        # - On capture le code de retour ($?).
        # - Si échec (code != 0), on affiche un message ROUGE.
        # - Si succès, on affiche un message VERT.
        # - Le 'read' final garantit que la fenêtre reste ouverte.

        script_bash = f"""
        echo ">>> Exécution de : {command}"
        echo ""
        {command}
        EXIT_CODE=$?
        echo ""
        if [ $EXIT_CODE -ne 0 ]; then
            echo -e "\\033[1;31m⚠️  ERREUR CRITIQUE : La commande a échoué (Code $EXIT_CODE)\\033[0m"
            echo -e "\\033[1;31m    Vérifiez la syntaxe ou les logs ci-dessus.\\033[0m"
        else
            echo -e "\\033[1;32m✅  SUCCÈS : Commande terminée.\\033[0m"
        fi
        echo ""
        echo "---------------------------------------------------"
        echo "Terminal interactif activé."
        echo "Tapez vos prochaines commandes ci-dessous (ex: ollama run ...)"
        echo "Tapez 'exit' pour fermer la fenêtre."
        echo "---------------------------------------------------"
        exec bash
        """

        # 3. Adaptation selon le terminal (Syntaxe d'appel)
        if 'mate-terminal' in terminal_path or 'gnome-terminal' in terminal_path:
            # Note : On passe le script comme un seul argument à bash -c
            full_cmd = [terminal_path, '--', 'bash', '-c', script_bash]

        elif 'xterm' in terminal_path:
            full_cmd = [terminal_path, '-fa', 'Monospace', '-fs', '11', '-geometry', '130x40', '-e', 'bash', '-c',
                        script_bash]

        elif 'konsole' in terminal_path:
            full_cmd = [terminal_path, '-e', 'bash', '-c', script_bash]

        else:
            full_cmd = [terminal_path, '-e', 'bash', '-c', script_bash]

        # 4. Exécution sécurisée
        # L'utilisation d'une liste pour full_cmd empêche l'injection de commande au niveau du système hôte (Python).
        subprocess.Popen(full_cmd)

        return HttpResponse(status=204)

    except Exception as e:
        logger.exception("Erreur lors du lancement du terminal")
        return HttpResponse(status=500)

def get_network_info(request):
    """Récupère les informations réseau (IP locale et publique).

    Returns:
        HttpResponse: Fragment HTML avec les IPs.
    """
    # 1. IP Locale
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    # 2. IP Publique (via API externe rapide)
    try:
        public_ip = requests.get('https://api.ipify.org', timeout=2).text
    except Exception:
        public_ip = "Indisponible"

    return render(request, 'partials/network_info.html', {
        'local_ip': local_ip,
        'public_ip': public_ip
    })
