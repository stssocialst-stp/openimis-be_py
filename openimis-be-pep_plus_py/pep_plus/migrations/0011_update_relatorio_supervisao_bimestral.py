# Generated migration for RelatorioSupervisaoBimestral updates (Ferramenta 7)
# - Change nome_supervisores from TextField to supervisores JSONField
# - Rename num_sessoes_supervisionadas to numero_sessoes
# - Rename num_tecnicos_supervisionados to numero_tecnicos_formadores
# - Change periodo from IntegerField to CharField
# - Remove periodo_inicio and periodo_fim
# - Update avaliacoes_tecnicos structure
# - Rename notas_sessoes_pep to sessoes_pep and change structure
# - Change modulo_maior_dificuldade from ForeignKey to modulos_dificuldade JSONField
# - Rename observacoes_adicionais to observacoes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0010_update_roteiro_reuniao_bimestral'),
    ]

    operations = [
        # Remove old fields
        migrations.RemoveField(
            model_name='relatoriosupervisaobimestral',
            name='nome_supervisores',
        ),
        migrations.RemoveField(
            model_name='relatoriosupervisaobimestral',
            name='periodo_inicio',
        ),
        migrations.RemoveField(
            model_name='relatoriosupervisaobimestral',
            name='periodo_fim',
        ),
        migrations.RemoveField(
            model_name='relatoriosupervisaobimestral',
            name='modulo_maior_dificuldade',
        ),

        # Add new supervisores JSONField
        migrations.AddField(
            model_name='relatoriosupervisaobimestral',
            name='supervisores',
            field=models.JSONField(
                db_column='Supervisores',
                default=list,
                blank=True,
                help_text='Array de IDs dos supervisores responsáveis pelo relatório'
            ),
        ),

        # Rename num_sessoes_supervisionadas to numero_sessoes
        migrations.RenameField(
            model_name='relatoriosupervisaobimestral',
            old_name='num_sessoes_supervisionadas',
            new_name='numero_sessoes',
        ),
        migrations.AlterField(
            model_name='relatoriosupervisaobimestral',
            name='numero_sessoes',
            field=models.IntegerField(
                db_column='NumeroSessoes',
                default=0,
                help_text='Quantidade total de sessões supervisionadas no bimestre'
            ),
        ),

        # Rename num_tecnicos_supervisionados to numero_tecnicos_formadores
        migrations.RenameField(
            model_name='relatoriosupervisaobimestral',
            old_name='num_tecnicos_supervisionados',
            new_name='numero_tecnicos_formadores',
        ),
        migrations.AlterField(
            model_name='relatoriosupervisaobimestral',
            name='numero_tecnicos_formadores',
            field=models.IntegerField(
                db_column='NumeroTecnicosFormadores',
                default=0,
                help_text='Total de técnicos formadores supervisionados'
            ),
        ),

        # Change periodo from IntegerField to CharField
        migrations.AlterField(
            model_name='relatoriosupervisaobimestral',
            name='periodo',
            field=models.CharField(
                db_column='Periodo',
                max_length=10,
                choices=[
                    ('JAN_FEV', 'Janeiro e Fevereiro'),
                    ('MAR_ABR', 'Março e Abril'),
                    ('MAI_JUN', 'Maio e Junho'),
                    ('JUL_AGO', 'Julho e Agosto'),
                    ('SET_OUT', 'Setembro e Outubro'),
                    ('NOV_DEZ', 'Novembro e Dezembro'),
                ],
                help_text='Período bimestral do relatório'
            ),
        ),

        # Update distrito ForeignKey (change on_delete)
        migrations.AlterField(
            model_name='relatoriosupervisaobimestral',
            name='distrito',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                db_column='DistritoID',
                to='location.location',
                related_name='relatorios_supervisao',
                help_text='Distrito do relatório'
            ),
        ),

        # Rename notas_sessoes_pep to sessoes_pep
        migrations.RenameField(
            model_name='relatoriosupervisaobimestral',
            old_name='notas_sessoes_pep',
            new_name='sessoes_pep',
        ),
        migrations.AlterField(
            model_name='relatoriosupervisaobimestral',
            name='sessoes_pep',
            field=models.JSONField(
                db_column='SessoesPep',
                default=list,
                blank=True,
                help_text='Array de objetos: [{passo, nota}]'
            ),
        ),

        # Add new modulos_dificuldade JSONField
        migrations.AddField(
            model_name='relatoriosupervisaobimestral',
            name='modulos_dificuldade',
            field=models.JSONField(
                db_column='ModulosDificuldade',
                default=list,
                blank=True,
                help_text='Array de objetos: [{modulo, selected}]'
            ),
        ),

        # Rename observacoes_adicionais to observacoes
        migrations.RenameField(
            model_name='relatoriosupervisaobimestral',
            old_name='observacoes_adicionais',
            new_name='observacoes',
        ),
        migrations.AlterField(
            model_name='relatoriosupervisaobimestral',
            name='observacoes',
            field=models.TextField(
                db_column='Observacoes',
                null=True,
                blank=True,
                help_text='Observações adicionais do relatório'
            ),
        ),
    ]
