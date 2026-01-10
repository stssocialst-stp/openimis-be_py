# Generated migration for ExecucaoSessao field changes (Ferramenta 3)
# - Change numero_participantes_compromissos to numero_cuidadores with choices
# - Add outras_praticas_positivas field
# - Add outros_desafios field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0005_alter_presencasessao_fields'),
    ]

    operations = [
        # Remove old field numero_participantes_compromissos
        migrations.RemoveField(
            model_name='execucaosessao',
            name='numero_participantes_compromissos',
        ),

        # Add new field numero_cuidadores with choices
        migrations.AddField(
            model_name='execucaosessao',
            name='numero_cuidadores',
            field=models.CharField(
                db_column='NumeroCuidadores',
                max_length=10,
                choices=[
                    ('0', '0 cuidadores'),
                    ('1-5', '1 a 5 cuidadores'),
                    ('6-10', '6 a 10 cuidadores'),
                    ('15+', 'Mais de 15 cuidadores'),
                ],
                default='0',
                help_text='Número de cuidadores presentes'
            ),
        ),

        # Add outras_praticas_positivas field
        migrations.AddField(
            model_name='execucaosessao',
            name='outras_praticas_positivas',
            field=models.TextField(
                db_column='OutrasPraticasPositivas',
                null=True,
                blank=True,
                help_text='Outras práticas positivas observadas'
            ),
        ),

        # Add outros_desafios field
        migrations.AddField(
            model_name='execucaosessao',
            name='outros_desafios',
            field=models.TextField(
                db_column='OutrosDesafios',
                null=True,
                blank=True,
                help_text='Outros desafios identificados'
            ),
        ),

        # Update help texts for existing JSON fields
        migrations.AlterField(
            model_name='execucaosessao',
            name='praticas_positivas',
            field=models.JSONField(
                db_column='PraticasPositivas',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ descricao, confirmacao: Sim/Não/N/A }]'
            ),
        ),

        migrations.AlterField(
            model_name='execucaosessao',
            name='desafios_transmissao',
            field=models.JSONField(
                db_column='DesafiosTransmissao',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ descricao, confirmacao: Sim/Não/N/A }]'
            ),
        ),

        migrations.AlterField(
            model_name='execucaosessao',
            name='necessita_encaminhamento',
            field=models.BooleanField(
                db_column='NecessitaEncaminhamento',
                default=False,
                help_text='Indica se há necessidade de encaminhamento'
            ),
        ),

        migrations.AlterField(
            model_name='execucaosessao',
            name='auto_avaliacao_pontos_fortes',
            field=models.JSONField(
                db_column='AutoAvaliacaoPontosFortes',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ descricao, avaliacao: 1-5 }]'
            ),
        ),

        migrations.AlterField(
            model_name='execucaosessao',
            name='auto_avaliacao_pontos_atencao',
            field=models.JSONField(
                db_column='AutoAvaliacaoPontosAtencao',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ descricao, avaliacao: 1-5 }]'
            ),
        ),

        migrations.AlterField(
            model_name='execucaosessao',
            name='avaliacao_metodologia',
            field=models.JSONField(
                db_column='AvaliacaoMetodologia',
                default=dict,
                blank=True,
                help_text='Avaliação da metodologia utilizada'
            ),
        ),
    ]
