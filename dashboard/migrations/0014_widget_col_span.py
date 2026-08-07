from django.db import migrations, models


def is_wide_to_col_span(apps, schema_editor):
    """Convertit l'ancien booleen is_wide en largeur numerique.

    is_wide=True (2 colonnes) -> col_span=2 ; sinon col_span reste a 1.
    """
    Widget = apps.get_model('dashboard', 'Widget')
    Widget.objects.filter(is_wide=True).update(col_span=2)


def col_span_to_is_wide(apps, schema_editor):
    """Retour arriere : col_span >= 2 redevient is_wide=True."""
    Widget = apps.get_model('dashboard', 'Widget')
    Widget.objects.filter(col_span__gte=2).update(is_wide=True)


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_todoitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='widget',
            name='col_span',
            field=models.IntegerField(
                default=1,
                choices=[(1, '1 colonne'), (2, '2 colonnes'), (4, 'Pleine largeur')],
            ),
        ),
        migrations.RunPython(is_wide_to_col_span, col_span_to_is_wide),
        migrations.RemoveField(
            model_name='widget',
            name='is_wide',
        ),
    ]
