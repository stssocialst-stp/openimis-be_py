# Generated migration for SupervisaoSessao field changes (Ferramenta 4)
# - Add localidade ForeignKey
# - Add grupo ForeignKey
# - Add numero_participantes with choices
# - Add praticas_positivas_estrategias JSONField
# - Add desafios_transmissao JSONField
# - Add necessita_encaminhamento BooleanField
# - Add auto_avaliacao_pontos_fortes and auto_avaliacao_pontos_atencao JSONFields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0006_alter_execucaosessao_fields'),
        ('location', '__first__'),
    ]

    operations = [
        # Add localidade ForeignKey
        migrations.AddField(
            model_name='supervisaosessao',
            name='localidade',
            field=models.ForeignKey(
                db_column='LocalidadeID',
                on_delete=django.db.models.deletion.PROTECT,
                to='location.location',
                null=True,
                blank=True,
                related_name='supervisoes_sessao',
                help_text='Localidade onde ocorreu a supervisão'
            ),
        ),

        # Add grupo ForeignKey
        migrations.AddField(
            model_name='supervisaosessao',
            name='grupo',
            field=models.ForeignKey(
                db_column='GrupoID',
                on_delete=django.db.models.deletion.PROTECT,
                to='pep_plus.grupofamiliar',
                null=True,
                blank=True,
                related_name='supervisoes',
                help_text='Grupo familiar supervisionado'
            ),
        ),

        # Add numero_participantes with choices
        migrations.AddField(
            model_name='supervisaosessao',
            name='numero_participantes',
            field=models.CharField(
                db_column='NumeroParticipantes',
                max_length=10,
                choices=[
                    ('0', '0 participantes'),
                    ('1-5', '1 a 5 participantes'),
                    ('6-10', '6 a 10 participantes'),
                    ('15+', 'Mais de 15 participantes'),
                ],
                default='0',
                help_text='Número de participantes presentes na supervisão'
            ),
        ),

        # Add praticas_positivas_estrategias JSONField
        migrations.AddField(
            model_name='supervisaosessao',
            name='praticas_positivas_estrategias',
            field=models.JSONField(
                db_column='PraticasPositivasEstrategias',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ descricao, confirmacao: Sim/Não/N/A }]'
            ),
        ),

        # Add desafios_transmissao JSONField
        migrations.AddField(
            model_name='supervisaosessao',
            name='desafios_transmissao',
            field=models.JSONField(
                db_column='DesafiosTransmissao',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ descricao, confirmacao: Sim/Não/N/A }]'
            ),
        ),

        # Add necessita_encaminhamento BooleanField
        migrations.AddField(
            model_name='supervisaosessao',
            name='necessita_encaminhamento',
            field=models.BooleanField(
                db_column='NecessitaEncaminhamento',
                default=False,
                help_text='Indica se há necessidade de encaminhamento'
            ),
        ),

        # Add auto_avaliacao_pontos_fortes JSONField (with boolean confirmacao)
        migrations.AddField(
            model_name='supervisaosessao',
            name='auto_avaliacao_pontos_fortes',
            field=models.JSONField(
                db_column='AutoAvaliacaoPontosFortes',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ descricao, confirmacao: boolean }]'
            ),
        ),

        # Add auto_avaliacao_pontos_atencao JSONField (with boolean confirmacao)
        migrations.AddField(
            model_name='supervisaosessao',
            name='auto_avaliacao_pontos_atencao',
            field=models.JSONField(
                db_column='AutoAvaliacaoPontosAtencao',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ descricao, confirmacao: boolean }]'
            ),
        ),

        # Add data_modulo_anterior DateField
        migrations.AddField(
            model_name='supervisaosessao',
            name='data_modulo_anterior',
            field=models.DateField(
                db_column='DataModuloAnterior',
                null=True,
                blank=True,
                help_text='Data do módulo anterior'
            ),
        ),
    ]
