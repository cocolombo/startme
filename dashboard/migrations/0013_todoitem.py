from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_commandlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widget',
            name='widget_type',
            field=models.CharField(
                choices=[
                    ('list', 'Liste de liens'),
                    ('note', 'Bloc-notes'),
                    ('command', 'Lanceur de scripts'),
                    ('snippet', 'Bloc de commandes'),
                    ('todo', 'Liste de tâches'),
                ],
                default='list',
                max_length=10,
            ),
        ),
        migrations.CreateModel(
            name='TodoItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('done', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('widget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todos', to='dashboard.widget')),
            ],
            options={
                'ordering': ['done', 'order', 'created_at'],
            },
        ),
    ]