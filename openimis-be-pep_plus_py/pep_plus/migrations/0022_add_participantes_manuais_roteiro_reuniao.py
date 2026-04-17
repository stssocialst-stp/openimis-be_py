from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0021_add_legacy_id_coordenacao_aluno'),
    ]

    operations = [
        migrations.AddField(
            model_name='roteioreuniaobimestral',
            name='participantes_manuais',
            field=models.JSONField(blank=True, db_column='ParticipantesManuais', default=list, help_text='Array de nomes de participantes inseridos manualmente'),
        ),
    ]
