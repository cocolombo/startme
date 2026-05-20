from django.core.management.base import BaseCommand
from dashboard.models import Page, Widget, Link
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Remplit la DB'

    def handle(self, *args, **kwargs):
        """Vide la base de données et la remplit avec des données de démonstration."""
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
