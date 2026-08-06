"""Migration one-shot : regroupement du dashboard 15 pages -> 8.

Plan valide : docs/plans/plan-regroupement-liens.md (2026-08-06).
Execution : venv/bin/python scripts/migrate_regroupement.py
Principe : tout deplacement de lien passe par move_link(), qui supprime le
lien (journalise) si son URL exacte existe deja dans le widget cible.
Transaction atomique : la moindre erreur annule tout.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startme.settings')

import django

django.setup()

from django.db import transaction

from dashboard.models import Link, Page, Widget, next_order

journal = []          # operations effectuees
doublons_supprimes = []  # (titre, url, emplacement de l'exemplaire conserve)


def log(msg):
    journal.append(msg)
    print(msg)


def page(name):
    return Page.objects.get(name=name)


def W(page_name, title, wtype=None, starts=False):
    """Resout un widget de facon stricte (echoue si 0 ou 2+ resultats)."""
    qs = Widget.objects.filter(page__name=page_name)
    qs = qs.filter(title__startswith=title) if starts else qs.filter(title=title)
    if wtype:
        qs = qs.filter(widget_type=wtype)
    return qs.get()


def move_link(link, cible):
    """Deplace un lien vers un widget cible, avec dedup par URL exacte."""
    if link.url and cible.links.filter(url=link.url).exists():
        doublons_supprimes.append((link.title, link.url,
                                   f"{cible.page.name} > {cible.title}"))
        log(f"  doublon supprime : '{link.title}' (garde dans "
            f"{cible.page.name} > {cible.title})")
        link.delete()
        return
    link.widget = cible
    link.order = next_order(cible.links)
    link.save()
    log(f"  lien deplace : '{link.title}' -> {cible.page.name} > {cible.title}")


def move_links(source, cible, titres=None, starts=None):
    """Deplace des liens d'un widget vers un autre (tous si titres=None)."""
    qs = source.links.all()
    if titres is not None:
        qs = qs.filter(title__in=titres)
    if starts is not None:
        qs = qs.filter(title__startswith=starts)
    for link in list(qs.order_by('order', 'id')):
        move_link(link, cible)


def move_widget(w, page_cible, nouveau_titre=None):
    w.page = page_cible
    w.order = next_order(page_cible.widgets)
    if nouveau_titre:
        w.title = nouveau_titre
    w.save()
    log(f"widget deplace : '{w.title}' -> page {page_cible.name}")


def rename_widget(w, titre):
    log(f"widget renomme : '{w.title}' -> '{titre}' (page {w.page.name})")
    w.title = titre
    w.save()


def delete_empty_widget(w):
    assert w.links.count() == 0, f"widget non vide : {w.page.name} > {w.title}"
    log(f"widget dissous (vide) : {w.page.name} > {w.title}")
    w.delete()


def dedup_pair(perdant, gagnant):
    """Supprime du widget perdant les liens dont l'URL existe chez le gagnant."""
    for link in list(perdant.links.all()):
        if link.url and gagnant.links.filter(url=link.url).exists():
            doublons_supprimes.append((link.title, link.url,
                                       f"{gagnant.page.name} > {gagnant.title}"))
            log(f"  doublon supprime : '{link.title}' de {perdant.page.name} > "
                f"{perdant.title} (garde dans {gagnant.page.name} > {gagnant.title})")
            link.delete()


with transaction.atomic():
    nb_pages_avant = Page.objects.count()
    nb_widgets_avant = Widget.objects.count()
    nb_liens_avant = Link.objects.count()

    # ---- Phase 1 : pages (renommages, ordres) --------------------------------
    p_depart, p_perso, p_ia = page('Départ'), page('Perso'), page('IA')
    p_dev = page('Projet')
    p_dev.name, p_dev.slug = 'Dev', 'dev'
    p_dev.save()
    log("page renommee : Projet -> Dev")
    p_savoirs = page('Science')
    p_savoirs.name, p_savoirs.slug = 'Savoirs', 'savoirs'
    p_savoirs.save()
    log("page renommee : Science -> Savoirs")
    p_commandes, p_medias, p_politique = (page('Commandes'), page('Médias'),
                                          page('Politique'))
    for i, p in enumerate([p_depart, p_perso, p_ia, p_dev, p_commandes,
                           p_medias, p_politique, p_savoirs]):
        p.order = i
        p.save()

    # ---- Phase 2 : Depart ----------------------------------------------------
    quotidien = W('Départ', 'Récurrent')
    rename_widget(quotidien, 'Quotidien')
    souvent = W('Départ', 'Souvent')
    move_links(souvent, quotidien)              # fusion, dedup URL integree
    delete_empty_widget(souvent)
    meteo = W('Départ', 'Météo')
    move_links(quotidien, meteo, titres=['Radar météo', 'Windy.com'])
    rename_widget(W('Départ', 'Drive'), 'Courriel & Drives')
    rename_widget(W('Départ', 'Divers'), 'Loto')

    # Les 3 todo de la page TODO -> Depart
    move_widget(W('TODO', 'Tâches', 'todo'), p_depart)
    move_widget(W('TODO', 'IA', 'todo'), p_depart, 'Tâches IA')
    move_widget(W('TODO', 'Perso', 'todo'), p_depart, 'Tâches perso')

    # Forums/Blogues -> Savoirs
    forums = W('Départ', 'Forums/Blogues')
    move_widget(forums, p_savoirs)

    # ---- Phase 3 : Dev (avant la dissolution de Travail) ---------------------
    github_dev = W('Dev', 'Github')
    redico = W('Dev', 'Redico-ai')
    turing = W('Dev', 'Turing Machine')
    outils_dev = Widget.objects.create(page=p_dev, title='Outils dev',
                                       widget_type='list',
                                       order=next_order(p_dev.widgets))
    log("widget cree : Dev > Outils dev")

    docs_dev = W('Programmation', 'Django')
    rename_widget(docs_dev, 'Docs')
    move_widget(docs_dev, p_dev)
    prog_dev = W('Programmation', 'Dev')
    move_links(prog_dev, github_dev, titres=['Github'])
    move_links(prog_dev, docs_dev, titres=['StackOverflow'])
    delete_empty_widget(prog_dev)

    scripts_w = W('Outils', 'Scripts', 'command')
    move_widget(scripts_w, p_dev)
    fichiers = W('Outils', 'Fichiers')
    for link in list(fichiers.links.all()):     # Alim : dedup avec Quotidien
        if link.url and quotidien.links.filter(url=link.url).exists():
            doublons_supprimes.append((link.title, link.url, 'Départ > Quotidien'))
            log(f"  doublon supprime : '{link.title}' (garde dans Départ > Quotidien)")
            link.delete()
        else:
            move_link(link, scripts_w)
    delete_empty_widget(fichiers)

    # Dissolution de Depart > Travail
    travail = W('Départ', 'Travail')
    move_links(travail, github_dev, titres=['Github Repo', 'GitHub Gist'])
    move_links(travail, redico, titres=['administration'])
    move_links(travail, forums, titres=['Le Redico'])
    move_links(travail, outils_dev,
               titres=['Streamlit', 'https://www.cursor.com/en',
                       'Authenticator.cursor.sh', 'fill out this form.',
                       'OpenHands README'])
    # (Desmos, OpenAI playground, Bluesky : deplaces plus bas, cibles creees apres)

    # ---- Phase 4 : Perso -----------------------------------------------------
    dashboard_w = W('Dev', 'Dashboard')
    move_links(dashboard_w, W('Perso', 'Épicerie'))
    delete_empty_widget(dashboard_w)

    maison = W('Perso', 'Maison', 'list')
    maison_projet = W('Dev', 'Maison')
    move_links(maison_projet, maison)
    delete_empty_widget(maison_projet)
    divers_perso = W('Perso', 'Divers')
    move_links(divers_perso, maison, titres=['HQ', 'HQ pannes',
                                             'Helix admin 10.0.0.1'])

    finances = W('Perso', 'Impots')
    rename_widget(finances, 'Finances')
    actions = W('Divers', 'Cours des actions')
    move_links(actions, finances)
    delete_empty_widget(actions)

    transport = W('Perso', 'Autobus')
    rename_widget(transport, 'Transport')
    dedup_pair(quotidien, transport)            # Communauto

    abonnements = W('Perso', 'Abonnements', 'list')
    ia_w = W('IA', 'IA')
    move_links(ia_w, abonnements,
               titres=['Anthropic Billing', 'Claude usage',
                       'Claude abonnement mensuel'])
    move_links(ia_w, abonnements, starts='https://console.x.ai/')
    move_links(redico, abonnements,
               titres=['Claude usage', 'Clause cost', 'Anthropic Billing 5.57',
                       'Gemini API coûts'])
    move_links(W('Départ', 'Google'), abonnements, starts='Facturation GoogleCloud')

    recettes = W('Perso', 'Recettes')
    recettes.is_wide = True
    recettes.save()
    log("widget Recettes : is_wide = True")

    # ---- Phase 5 : IA --------------------------------------------------------
    dedup_pair(ia_w, W('IA', 'Chat'))           # les 5 chats en double
    rename_widget(ia_w, 'Plateformes & consoles')
    move_links(travail, ia_w, starts='https://platform.openai.com/')

    cours_ia = W('Programmation', 'Cours IA')
    rename_widget(cours_ia, 'Cours & docs IA')
    move_widget(cours_ia, p_ia)
    kaggle = W('Dev', 'Cours Kaggle', starts=True)
    move_links(kaggle, cours_ia)
    delete_empty_widget(kaggle)

    docu = W('Divers', 'Docu importante')
    dedup_pair(docu, W('Départ', 'Google'))
    rename_widget(docu, 'Docs & références')
    move_widget(docu, p_ia)

    # ---- Phase 6 : Commandes -------------------------------------------------
    ffmpef_note = W('Médias', 'ffmpef', 'note')
    rename_widget(ffmpef_note, 'ffmpeg')
    move_widget(ffmpef_note, p_commandes)
    ffmpeg_list = W('Médias', 'ffmpeg', 'list')
    move_widget(ffmpeg_list, p_commandes)
    move_links(W('Médias', 'Twitter'), ffmpeg_list, titres=['Commandes ffmpeg'])
    move_links(W('Médias', 'Visu'), ffmpeg_list, titres=['ffmpeg'])

    programmes_note = W('Programmes', 'Programmes installée', starts=True)
    rename_widget(programmes_note, 'Programmes installés')
    move_widget(programmes_note, p_commandes)

    # ---- Phase 7 : Medias ----------------------------------------------------
    x_reseaux = W('Médias', 'Twitter')
    rename_widget(x_reseaux, 'X / Réseaux')
    move_links(travail, x_reseaux, titres=['Bluesky Social'])
    for titre_w in ['Politique', 'Code Source']:
        wsrc = W('Twitter', titre_w)
        move_links(wsrc, x_reseaux)
        delete_empty_widget(wsrc)

    audio = W('Médias', 'Audio/Journaux')
    radio = Widget.objects.create(page=p_medias, title='Radio',
                                  widget_type='list',
                                  order=next_order(p_medias.widgets))
    log("widget cree : Médias > Radio")
    move_links(audio, radio, titres=['98.5 FM', '995.fm', 'CBC Music',
                                     'Direct.radiovm.com'])
    rename_widget(audio, 'Journaux')
    dedup_pair(quotidien, audio)                # Le Figaro

    # ---- Phase 8 : Politique -------------------------------------------------
    autres_ref = Widget.objects.create(page=p_politique, title='Autres références',
                                       widget_type='list',
                                       order=next_order(p_politique.widgets))
    log("widget cree : Politique > Autres références")
    for titre_w in ['Géopolitique', 'Données ouvertes', 'Québec Fier']:
        wsrc = W('Politique', titre_w)
        move_links(wsrc, autres_ref)
        delete_empty_widget(wsrc)
    move_links(divers_perso, autres_ref, titres=['Données ouvertes'])

    # ---- Phase 9 : Savoirs ---------------------------------------------------
    sciences = W('Savoirs', 'Sciences')
    rename_widget(sciences, 'Sciences & maths')
    move_links(sciences, turing, titres=['The Busy Beaver Challenge'])
    for titre_w in ['Lectures', 'Grandient, Divergence, Curl']:
        wsrc = W('Savoirs', titre_w)
        move_links(wsrc, sciences)
        delete_empty_widget(wsrc)
    move_links(travail, sciences, titres=['Desmos'])
    move_widget(W('Divers', 'Langue'), p_savoirs)
    move_widget(W('Divers', 'Citations', 'note'), p_savoirs)

    # Travail doit maintenant etre vide
    delete_empty_widget(travail)

    # ---- Phase 10 : suppression des pages videes ------------------------------
    for nom in ['Programmation', 'Infos', 'Divers', 'Outils', 'Programmes',
                'Twitter', 'TODO']:
        p = page(nom)
        assert p.widgets.count() == 0, f"page non vide : {nom}"
        log(f"page supprimee (vide) : {nom}")
        p.delete()

    # ---- Phase 11 : renumerotation des orders ---------------------------------
    for p in Page.objects.all():
        for i, w in enumerate(p.widgets.order_by('order', 'id')):
            if w.order != i:
                w.order = i
                w.save(update_fields=['order'])
            for j, l in enumerate(w.links.order_by('order', 'id')):
                if l.order != j:
                    l.order = j
                    l.save(update_fields=['order'])

    # ---- Bilan -----------------------------------------------------------------
    nb_pages = Page.objects.count()
    nb_widgets = Widget.objects.count()
    nb_liens = Link.objects.count()
    print("\n===== BILAN =====")
    print(f"Pages   : {nb_pages_avant} -> {nb_pages}")
    print(f"Widgets : {nb_widgets_avant} -> {nb_widgets}")
    print(f"Liens   : {nb_liens_avant} -> {nb_liens} "
          f"({len(doublons_supprimes)} doublon(s) supprime(s))")
    assert nb_liens + len(doublons_supprimes) == nb_liens_avant, \
        "des liens ont disparu hors dedup !"
    assert nb_pages == 8, f"attendu 8 pages, obtenu {nb_pages}"
    print("\nDoublons supprimes (exemplaire conserve entre parentheses) :")
    for titre, url, garde in doublons_supprimes:
        print(f"  - {titre} ({garde}) [{url[:60]}]")
    print("\nMigration terminee avec succes.")
