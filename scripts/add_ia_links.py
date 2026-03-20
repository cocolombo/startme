import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startme.settings')
django.setup()

from dashboard.models import Page, Widget, Link

page_ia, created = Page.objects.get_or_create(
    name="IA",
    defaults={'slug': 'ia', 'order': 999}
)
print(f"Page 'IA' {'créée' if created else 'existante trouvée'}.")

widget_yt, created = Widget.objects.get_or_create(
    title="Chaîne YT",
    page=page_ia,
    defaults={'order': 0, 'widget_type': 'list'}
)
print(f"Widget 'Chaîne YT' {'créé' if created else 'existant trouvé'}.")

links_data = [
    ("Andrej Karpathy", "https://www.youtube.com/@AndrejKarpathy"),
    ("3Blue1Brown", "https://www.youtube.com/@3blue1brown"),
    ("Andrew Ng", "https://www.youtube.com/@stanfordonline"),
    ("ML Street Talk", "https://www.youtube.com/@MachineLearningStreetTalk"),
    ("Josh Starmer", "https://www.youtube.com/@statquest"),
    ("Luis Serrano", "https://www.youtube.com/@SerranoAcademy"),
    ("Jeremy Howard", "https://www.youtube.com/@howardjeremyp"),
    ("Hamel Husain", "https://www.youtube.com/@hamelhusain7140"),
    ("Dave Ebbelaar", "https://www.youtube.com/@daveebbelaar"),
    ("Lex Fridman", "https://www.youtube.com/@lexfridman"),
    ("Zachary Huang (MS)", "https://www.youtube.com/@ZacharyLLM"),
]

count = 0
for title, url in links_data:
    obj, created = Link.objects.get_or_create(
        title=title,
        widget=widget_yt,
        defaults={'url': url, 'order': 999}
    )
    if created:
        count += 1

print(f"{count} liens ajoutés avec succès dans 'Chaîne YT'.")
