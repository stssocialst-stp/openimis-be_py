# Generated migration for adding resumo_da_agenda field to RoteiroReuniaoBimestral

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0011_update_relatorio_supervisao_bimestral'),
    ]

    operations = [
        migrations.AddField(
            model_name='roteiroreuniaobimestral',
            name='resumo_da_agenda',
            field=models.JSONField(
                db_column='ResumoDaAgenda',
                default=list,
                blank=True,
                help_text='Array de objetos: [{ aberturaEBoasVindas, relatoDesafiosSolucoes, compartilhamentoOportunidades, apreciacaoRelatorios, definicaoAcoesEncaminhamentos, encerramentoProximaReuniao }]'
            ),
        ),
    ]
