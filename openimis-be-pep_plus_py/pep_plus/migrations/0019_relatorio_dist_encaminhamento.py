# Migration: Ligação estruturada Relatório Distrital ↔ PresencaSessao (ENCA)
#
# Problema resolvido:
#   O campo JSON 'dados_encaminhamentos' em tblRelatorioDistritalBimestral
#   continha dados livres sem ligação real às presenças encaminhadas.
#
# Solução:
#   Nova tabela tblRelatorioDistEncaminhamento que liga cada relatório
#   directamente às PresencaSessao com estado='ENCA', mantendo o código
#   e tipo de encaminhamento referenciados da presença original.
#
# O campo dados_encaminhamentos (JSON) permanece para notas livres auxiliares.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0018_add_aluno'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatorioDistEncaminhamento',
            fields=[
                ('id', models.AutoField(
                    db_column='RelatorioDistEncaminhamentoID',
                    primary_key=True,
                    serialize=False,
                )),
                ('relatorio', models.ForeignKey(
                    db_column='RelatorioDistritalID',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='encaminhamentos_estruturados',
                    to='pep_plus.relatoriodistritalbimestral',
                )),
                ('presenca', models.ForeignKey(
                    db_column='PresencaSessaoID',
                    help_text='Registo de presença encaminhada (estado obrigatoriamente ENCA)',
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='relatorios_distritais',
                    to='pep_plus.presencasessao',
                )),
                ('observacoes', models.TextField(
                    blank=True,
                    db_column='Observacoes',
                    null=True,
                )),
            ],
            options={
                'db_table': 'tblRelatorioDistEncaminhamento',
                'managed': True,
                'unique_together': {('relatorio', 'presenca')},
            },
        ),
    ]
