# Generated migration for SessaoPEP field changes
# - Add data_planejamento field
# - Change modulo FK to nome_modulo CharField

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def copy_modulo_to_nome_modulo(apps, schema_editor):
    """Copy modulo.nome to nome_modulo field"""
    SessaoPEP = apps.get_model('pep_plus', 'SessaoPEP')
    ModuloEducacional = apps.get_model('pep_plus', 'ModuloEducacional')

    for sessao in SessaoPEP.objects.all():
        if sessao.modulo_id:
            try:
                modulo = ModuloEducacional.objects.get(id=sessao.modulo_id)
                sessao.nome_modulo = modulo.nome
                # Set data_planejamento to data_sessao as default
                if not sessao.data_planejamento:
                    sessao.data_planejamento = sessao.data_sessao
                sessao.save()
            except ModuloEducacional.DoesNotExist:
                # If module doesn't exist, use a default value
                sessao.nome_modulo = f"Módulo {sessao.modulo_id}"
                if not sessao.data_planejamento:
                    sessao.data_planejamento = sessao.data_sessao
                sessao.save()


def reverse_copy(apps, schema_editor):
    """Reverse migration - cannot restore FK relationship"""
    # Cannot reverse this migration as we lose the FK relationship
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0003_relatoriosupervisaobimestral'),
    ]

    operations = [
        # Step 1: Add data_planejamento field (nullable first)
        migrations.AddField(
            model_name='sessaopep',
            name='data_planejamento',
            field=models.DateField(db_column='DataPlanejamento', help_text='Data do planejamento', null=True, blank=True),
        ),

        # Step 2: Add nome_modulo field (nullable first)
        migrations.AddField(
            model_name='sessaopep',
            name='nome_modulo',
            field=models.CharField(db_column='NomeModulo', max_length=255, help_text='Nome do módulo educacional', null=True, blank=True),
        ),

        # Step 3: Copy data from modulo FK to nome_modulo
        migrations.RunPython(copy_modulo_to_nome_modulo, reverse_copy),

        # Step 4: Remove the modulo FK field
        migrations.RemoveField(
            model_name='sessaopep',
            name='modulo',
        ),

        # Step 5: Make nome_modulo and data_planejamento NOT NULL
        migrations.AlterField(
            model_name='sessaopep',
            name='nome_modulo',
            field=models.CharField(db_column='NomeModulo', max_length=255, help_text='Nome do módulo educacional'),
        ),
        migrations.AlterField(
            model_name='sessaopep',
            name='data_planejamento',
            field=models.DateField(db_column='DataPlanejamento', help_text='Data do planejamento'),
        ),
    ]
