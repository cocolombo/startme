import json
import os
from django.core.management.base import BaseCommand
from dashboard.models import Page, Widget, Link
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Importe les liens depuis un fichier data_export.json'

    def handle(self, *args, **kwargs):
        # Chemin du fichier
        file_path = 'data_export.json'

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Fichier {file_path} introuvable !"))
            return

        # Lecture du JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stdout.write("Début de l'importation...")

        # On parcourt les pages (dans votre JSON, il n'y en a surement qu'une "Extracted Page")
        for page_name, widgets_data in data.items():
            # 1. Créer ou Récupérer la Page
            page, created = Page.objects.get_or_create(
                slug=slugify(page_name),
                defaults={'name': page_name}
            )
            if created:
                self.stdout.write(f"Page créée : {page_name}")

            # Gestion de l'ordre des widgets
            widget_order = 0

            # On parcourt les widgets (Catégories)
            for widget_title, links_list in widgets_data.items():
                # 2. Créer le Widget
                widget, w_created = Widget.objects.get_or_create(
                    title=widget_title,
                    page=page,
                    defaults={'order': widget_order}
                )
                widget_order += 1

                link_order = 0
                # On parcourt les liens
                for link_data in links_list:
                    # link_data est une liste : [Titre, URL, IconURL]
                    title = link_data[0]
                    url = link_data[1]

                    # 3. Créer le Lien (éviter doublons basés sur l'URL)
                    Link.objects.get_or_create(
                        url=url,
                        widget=widget,
                        defaults={
                            'title': title,
                            'order': link_order
                        }
                    )
                    link_order += 1

                self.stdout.write(f" - Widget traité : {widget_title} ({len(links_list)} liens)")

        self.stdout.write(self.style.SUCCESS("Importation terminée avec succès !"))
