# Generated migration for SupervisaoSessao - Add avaliacao_execucao_metodologia field
# - Add avaliacao_execucao_metodologia JSONField with specific confirmacao options

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0007_alter_supervisaosessao_fields'),
    ]

    operations = [
        # Add avaliacao_execucao_metodologia JSONField
        migrations.AddField(
            model_name='supervisaosessao',
            name='avaliacao_execucao_metodologia',
            field=models.JSONField(
                db_column='AvaliacaoExecucaoMetodologia',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ descricao, confirmacao: Não fez/Não adequado/Adequado/Excelente/N/A }]'
            ),
        ),
    ]
