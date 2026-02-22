# Migration: Adicionar tabela Aluno e FK aluno em ModuloEducacional
#
# Cria:
#   - tblAluno: perfil centralizado de aluno, com FK para Individual (openIMIS)
#     Todo aluno é um indivíduo, mas nem todo indivíduo é um aluno.
#     Inclui dados de localização (FK Distrito/Localidade) e dados escolares
#     (FK Escola/Classe) equivalentes aos de ModuloEducacional.
#
# Altera:
#   - tblModuloEducacional: adiciona coluna AlunoID (FK para tblAluno, nullable)
#     para ligar registos de assiduidade ao perfil do aluno

import uuid
import core.fields
import core.utils
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0017_add_coordenacao_distrital'),
        ('individual', '0001_initial'),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aluno',
            fields=[
                ('id', models.AutoField(db_column='AlunoID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='AlunoUUID', default=uuid.uuid4, max_length=36, unique=True)),
                # VersionedModel audit fields
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom', default=core.utils.TimeUtils.now)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(blank=True, db_column='AuditUserID', null=True)),
                # Individual FK (Individual usa UUID como PK)
                ('individual', models.ForeignKey(
                    db_column='IndividualUUID',
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='alunos',
                    to='individual.individual',
                )),
                # Integration IDs
                ('id_membro_crianca', models.CharField(blank=True, db_column='IdMembroCrianca', max_length=100, null=True)),
                ('id_da_crianca', models.CharField(blank=True, db_column='IdDaCrianca', max_length=100, null=True)),
                ('nome_encarregado', models.CharField(blank=True, db_column='NomeEncarregado', max_length=255, null=True)),
                # Personal
                ('sexo', models.CharField(
                    blank=True, db_column='Sexo', max_length=20, null=True,
                    choices=[('M', 'Masculino'), ('F', 'Feminino'), ('I', 'Indeterminado')],
                )),
                # Location
                ('distrito', models.ForeignKey(
                    blank=True, db_column='DistritoID', null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='alunos_distrito', to='location.location',
                )),
                ('localidade', models.ForeignKey(
                    blank=True, db_column='LocalidadeID', null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='alunos_localidade', to='location.location',
                )),
                ('ponto_referencia', models.TextField(blank=True, db_column='PontoReferencia', null=True)),
                ('meio_residencia', models.CharField(blank=True, db_column='MeioResidencia', max_length=100, null=True)),
                # School
                ('escola', models.ForeignKey(
                    blank=True, db_column='EscolaID', null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='alunos_escola', to='pep_plus.escola',
                )),
                ('escola_actual', models.ForeignKey(
                    blank=True, db_column='EscolaActualID', null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='alunos_escola_actual', to='pep_plus.escola',
                )),
                ('escolaridade_actual', models.CharField(
                    blank=True, db_column='EscolaridadeActual', max_length=100, null=True,
                    choices=[
                        ('EP1', 'EP1'), ('EP2', 'EP2'), ('ESG1', 'ESG1'), ('ESG2', 'ESG2'),
                        ('ENSINO_SUPERIOR', 'Ensino Superior'), ('OUTRO', 'Outro'),
                    ],
                )),
                ('classe', models.ForeignKey(
                    blank=True, db_column='ClasseID', null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='alunos_classe', to='pep_plus.classe',
                )),
                ('classe_que_frequenta', models.ForeignKey(
                    blank=True, db_column='ClasseQueFrequentaID', null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='alunos_classe_frequenta', to='pep_plus.classe',
                )),
                ('dados_escolares_correctos', models.BooleanField(blank=True, db_column='DadosEscolaresCorrectos', null=True)),
                ('ativo', models.BooleanField(db_column='Ativo', default=True)),
            ],
            options={
                'db_table': 'tblAluno',
                'ordering': ['individual__first_name', 'individual__last_name'],
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='aluno',
            field=models.ForeignKey(
                blank=True,
                db_column='AlunoID',
                help_text='Perfil centralizado do aluno (criado em Registar Indivíduo)',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='assiduidades',
                to='pep_plus.aluno',
            ),
        ),
    ]
