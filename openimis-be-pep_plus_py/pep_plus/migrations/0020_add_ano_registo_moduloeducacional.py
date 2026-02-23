from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0019_relatorio_dist_encaminhamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='moduloeducacional',
            name='ano_registo',
            field=models.IntegerField(
                db_column='AnoRegisto',
                null=True,
                blank=True,
                help_text='Ano lectivo do registo (ex: 2026)',
            ),
        ),
    ]
