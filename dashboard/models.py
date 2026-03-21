from django.db import models

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
