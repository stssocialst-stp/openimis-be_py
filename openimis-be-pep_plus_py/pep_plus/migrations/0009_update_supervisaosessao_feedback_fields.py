# Generated migration for SupervisaoSessao feedback fields
# - Add metodologia_passos JSONField
# - Add feedback_pontos_fortes TextField
# - Add feedback_desafios TextField
# - Add compromisso_formador TextField
# - Remove perguntas_avaliacao (deprecated)
# - Remove pontos_positivos (deprecated)
# - Remove pontos_melhorar (deprecated)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0008_add_avaliacao_execucao_metodologia'),
    ]

    operations = [
        # Add new feedback fields
        migrations.AddField(
            model_name='supervisaosessao',
            name='metodologia_passos',
            field=models.JSONField(
                db_column='MetodologiaPassos',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ descricao, confirmacao: Adequado/N/A/etc }]'
            ),
        ),
        migrations.AddField(
            model_name='supervisaosessao',
            name='feedback_pontos_fortes',
            field=models.TextField(
                db_column='FeedbackPontosFortes',
                null=True,
                blank=True,
                help_text='Feedback sobre pontos fortes observados'
            ),
        ),
        migrations.AddField(
            model_name='supervisaosessao',
            name='feedback_desafios',
            field=models.TextField(
                db_column='FeedbackDesafios',
                null=True,
                blank=True,
                help_text='Feedback sobre desafios observados'
            ),
        ),
        migrations.AddField(
            model_name='supervisaosessao',
            name='compromisso_formador',
            field=models.TextField(
                db_column='CompromissoFormador',
                null=True,
                blank=True,
                help_text='Compromissos assumidos pelo formador'
            ),
        ),

        # Remove deprecated fields
        migrations.RemoveField(
            model_name='supervisaosessao',
            name='perguntas_avaliacao',
        ),
        migrations.RemoveField(
            model_name='supervisaosessao',
            name='pontos_positivos',
        ),
        migrations.RemoveField(
            model_name='supervisaosessao',
            name='pontos_melhorar',
        ),
    ]
