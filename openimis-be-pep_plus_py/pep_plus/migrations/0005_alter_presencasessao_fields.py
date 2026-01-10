# Generated migration for PresencaSessao field changes
# - Update estado choices (add ENCA, update AUSE to FALT)
# - Add nome_instituicao field
# - Make nome_familia optional

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0004_alter_sessaopep_fields'),
    ]

    operations = [
        # Update estado choices
        migrations.AlterField(
            model_name='presencasessao',
            name='estado',
            field=models.CharField(
                db_column='Estado',
                max_length=4,
                choices=[
                    ('PRES', 'Presente'),
                    ('FALT', 'Faltou'),
                    ('ENCA', 'Encaminhado'),
                ],
                default='PRES'
            ),
        ),

        # Add nome_instituicao field
        migrations.AddField(
            model_name='presencasessao',
            name='nome_instituicao',
            field=models.CharField(
                db_column='NomeInstituicao',
                max_length=255,
                null=True,
                blank=True,
                help_text='Nome da instituição quando estado=ENCA'
            ),
        ),

        # Make nome_familia optional
        migrations.AlterField(
            model_name='presencasessao',
            name='nome_familia',
            field=models.CharField(
                db_column='NomeFamilia',
                max_length=255,
                null=True,
                blank=True
            ),
        ),

        # Update codigo_encaminhamento help text
        migrations.AlterField(
            model_name='presencasessao',
            name='codigo_encaminhamento',
            field=models.CharField(
                db_column='CodigoEncaminhamento',
                max_length=50,
                null=True,
                blank=True,
                help_text='Código de encaminhamento quando estado=ENCA'
            ),
        ),
    ]
