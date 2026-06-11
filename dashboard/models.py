from django.db import models
from django.utils import timezone


def next_order(objects) -> int:
    """Calcule la position suivante dans une liste ordonnée (Max('order') + 1).

    Remplace l'ancien hack `order=999` : deux ajouts successifs recevaient
    la même position, rendant l'ordre final imprévisible.

    Args:
        objects: Un queryset ou un manager d'objets possédant un champ 'order'
            (Page, Widget, Link, TodoItem).

    Returns:
        int: 0 si la liste est vide, sinon max(order) + 1.
    """
    max_order = objects.aggregate(max_order=models.Max('order'))['max_order']
    return 0 if max_order is None else max_order + 1


class Page(models.Model):
    """Représente un onglet (une page) du tableau de bord.

    Chaque page a un nom, un slug unique pour l'URL, et un ordre
    d'affichage. Elle contient plusieurs widgets.

    Attributes:
        name (CharField): Le nom de la page affiché à l'utilisateur.
        slug (SlugField): L'identifiant unique utilisé dans l'URL.
        order (IntegerField): La position de la page dans la barre d'onglets.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class Widget(models.Model):
    """Représente une catégorie ou un "widget" sur une page.

    Un widget peut être de plusieurs types (liste de liens, bloc-notes,
    lanceur de scripts), déterminé par le champ 'widget_type'. Il est
    associé à une page et contient des liens ou du contenu textuel.

    Attributes:
        title (CharField): Le titre du widget.
        page (ForeignKey): La page parente à laquelle ce widget appartient.
        order (IntegerField): La position du widget sur la page.
        widget_type (CharField): Le type de widget (ex: 'list', 'note').
        content (TextField): Le contenu textuel, utilisé principalement
                             pour les widgets de type 'note'.
    """
    # Choix du type de widget
    TYPE_CHOICES = [
        ('list', 'Liste de liens'),
        ('note', 'Bloc-notes'),
        ('command', 'Lanceur de scripts'),
        ('snippet', 'Bloc de commandes'),
        ('todo', 'Liste de tâches'),
    ]

    title = models.CharField(max_length=100)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='widgets')
    order = models.IntegerField(default=0)

    # Nouveaux champs
    widget_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='list')
    content = models.TextField(blank=True, null=True)
    is_wide = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Link(models.Model):
    """Représente un lien hypertexte ou une commande dans un widget.

    Chaque lien a un titre, une URL (qui peut être une adresse web, un chemin
    de fichier local ou une commande shell), et est associé à un widget.

    Attributes:
        title (CharField): Le texte affiché pour le lien.
        url (CharField): L'URL cible, le chemin du fichier local, ou la commande shell.
        widget (ForeignKey): Le widget parent auquel ce lien appartient.
        order (IntegerField): La position du lien dans la liste du widget.
    """
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=500, blank=True, null=True)
    widget = models.ForeignKey(Widget, on_delete=models.CASCADE, related_name='links')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class TodoItem(models.Model):
    """Un item d'une liste de tâches associée à un widget de type 'todo'."""
    widget = models.ForeignKey(Widget, on_delete=models.CASCADE, related_name='todos')
    text = models.CharField(max_length=500)
    done = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['done', 'order', 'created_at']

    def __str__(self) -> str:
        return self.text


class CommandLog(models.Model):
    """Enregistre chaque exécution d'une commande depuis un widget lanceur."""
    link = models.ForeignKey(
        'Link', on_delete=models.SET_NULL, null=True, blank=True, related_name='logs'
    )
    widget = models.ForeignKey(
        'Widget', on_delete=models.SET_NULL, null=True, blank=True, related_name='command_logs'
    )
    command_title = models.CharField(max_length=200)
    command = models.CharField(max_length=500)
    executed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-executed_at']

    def __str__(self):
        return f"{self.command_title} — {self.executed_at:%Y-%m-%d %H:%M}"
