# Migration: Adicionar tabelas de parametrização PEP+
#
# Cria 4 novas tabelas de referência (lookup tables):
#   - tblModuloPEP        (substitui nome_modulo CharField em SessaoPEP)
#   - tblEscola           (substitui escola/escola_actual CharField em ModuloEducacional)
#   - tblDisciplina       (substitui disciplinas_basicas/avancadas TextField em ModuloEducacional)
#   - tblTipoEncaminhamento (substitui nome_instituicao CharField em PresencaSessao; adicionado em EncaminhamentoSessao)
#
# Cria 1 tabela M2M intermediária:
#   - tblModuloEducacionalDisciplina
#
# Altera modelos existentes:
#   - SessaoPEP: remove nome_modulo, adiciona modulo (FK → ModuloPEP)
#   - ModuloEducacional: remove escola/escola_actual/disciplinas_basicas/disciplinas_avancadas,
#                        adiciona escola/escola_actual (FK → Escola), AlterField choices para sexo/classe/escolaridade
#   - PresencaSessao: remove nome_instituicao, adiciona tipo_encaminhamento (FK → TipoEncaminhamento)
#   - EncaminhamentoSessao: adiciona tipo_encaminhamento (FK → TipoEncaminhamento)

import core.fields
import core.utils
import datetime
import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0014_alter_moduloeducacional_structure'),
        ('location', '0018_auto_20230925_2243'),
    ]

    operations = [

        # =====================================================================
        # 1. Criar tabelas de parametrização (VersionedModel)
        # =====================================================================

        migrations.CreateModel(
            name='ModuloPEP',
            fields=[
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom', default=datetime.datetime.now)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('id', models.AutoField(db_column='ModuloPEPID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='ModuloPEPUUID', default=uuid.uuid4, max_length=36, unique=True)),
                ('codigo', models.CharField(db_column='Codigo', max_length=50, unique=True)),
                ('nome', models.CharField(db_column='Nome', max_length=255)),
                ('descricao', models.TextField(blank=True, db_column='Descricao', null=True)),
                ('ordem', models.IntegerField(blank=True, db_column='Ordem', null=True)),
                ('duracao_semanas', models.IntegerField(blank=True, db_column='DuracaoSemanas', null=True)),
                ('ativo', models.BooleanField(db_column='Ativo', default=True)),
            ],
            options={
                'db_table': 'tblModuloPEP',
                'managed': True,
                'ordering': ['ordem', 'codigo'],
            },
            bases=(core.utils.CachedModelMixin, models.Model),
        ),

        migrations.CreateModel(
            name='Escola',
            fields=[
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom', default=datetime.datetime.now)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('id', models.AutoField(db_column='EscolaID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='EscolaUUID', default=uuid.uuid4, max_length=36, unique=True)),
                ('nome', models.CharField(db_column='Nome', max_length=255)),
                ('codigo', models.CharField(blank=True, db_column='Codigo', max_length=50, null=True)),
                ('nivel', models.CharField(
                    blank=True,
                    choices=[
                        ('EP1', 'EP1 (Ensino Primário 1)'),
                        ('EP2', 'EP2 (Ensino Primário 2)'),
                        ('ESG1', 'ESG1 (Ensino Secundário Geral 1)'),
                        ('ESG2', 'ESG2 (Ensino Secundário Geral 2)'),
                        ('OUTRO', 'Outro'),
                    ],
                    db_column='Nivel',
                    max_length=50,
                    null=True,
                )),
                ('ativo', models.BooleanField(db_column='Ativo', default=True)),
                ('distrito', models.ForeignKey(
                    blank=True,
                    db_column='DistritoID',
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='escolas_distrito',
                    to='location.location',
                )),
                ('localidade', models.ForeignKey(
                    blank=True,
                    db_column='LocalidadeID',
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='escolas_localidade',
                    to='location.location',
                )),
            ],
            options={
                'db_table': 'tblEscola',
                'managed': True,
                'ordering': ['nome'],
            },
            bases=(core.utils.CachedModelMixin, models.Model),
        ),

        migrations.CreateModel(
            name='Disciplina',
            fields=[
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom', default=datetime.datetime.now)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('id', models.AutoField(db_column='DisciplinaID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='DisciplinaUUID', default=uuid.uuid4, max_length=36, unique=True)),
                ('nome', models.CharField(db_column='Nome', max_length=255)),
                ('nivel', models.CharField(
                    choices=[('BASICA', 'Básica'), ('AVANCADA', 'Avançada')],
                    db_column='Nivel',
                    max_length=20,
                )),
                ('ativo', models.BooleanField(db_column='Ativo', default=True)),
            ],
            options={
                'db_table': 'tblDisciplina',
                'managed': True,
                'ordering': ['nivel', 'nome'],
            },
            bases=(core.utils.CachedModelMixin, models.Model),
        ),

        migrations.CreateModel(
            name='TipoEncaminhamento',
            fields=[
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom', default=datetime.datetime.now)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('id', models.AutoField(db_column='TipoEncaminhamentoID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='TipoEncaminhamentoUUID', default=uuid.uuid4, max_length=36, unique=True)),
                ('codigo', models.CharField(db_column='Codigo', max_length=50, unique=True)),
                ('nome', models.CharField(db_column='Nome', max_length=255)),
                ('descricao', models.TextField(blank=True, db_column='Descricao', null=True)),
                ('ativo', models.BooleanField(db_column='Ativo', default=True)),
            ],
            options={
                'db_table': 'tblTipoEncaminhamento',
                'managed': True,
                'ordering': ['codigo'],
            },
            bases=(core.utils.CachedModelMixin, models.Model),
        ),

        # =====================================================================
        # 2. Criar tabela M2M intermediária (plain Model, não VersionedModel)
        # =====================================================================

        migrations.CreateModel(
            name='ModuloEducacionalDisciplina',
            fields=[
                ('id', models.AutoField(db_column='ModuloEducacionalDisciplinaID', primary_key=True, serialize=False)),
                ('tipo', models.CharField(
                    choices=[('BASICA', 'Básica'), ('AVANCADA', 'Avançada')],
                    db_column='Tipo',
                    max_length=20,
                )),
                ('modulo', models.ForeignKey(
                    db_column='ModuloEducacionalID',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='disciplinas_associadas',
                    to='pep_plus.moduloeducacional',
                )),
                ('disciplina', models.ForeignKey(
                    db_column='DisciplinaID',
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='modulos_associados',
                    to='pep_plus.disciplina',
                )),
            ],
            options={
                'db_table': 'tblModuloEducacionalDisciplina',
                'managed': True,
            },
        ),
        migrations.AlterUniqueTogether(
            name='moduloeducacionaldisciplina',
            unique_together={('modulo', 'disciplina')},
        ),

        # =====================================================================
        # 3. SessaoPEP: remover nome_modulo, adicionar modulo FK → ModuloPEP
        # =====================================================================

        migrations.RemoveField(
            model_name='sessaopep',
            name='nome_modulo',
        ),
        migrations.AddField(
            model_name='sessaopep',
            name='modulo',
            field=models.ForeignKey(
                blank=True,
                db_column='ModuloID',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='sessoes',
                to='pep_plus.modulopep',
            ),
        ),

        # =====================================================================
        # 4. ModuloEducacional: remover CharField escola/escola_actual/disciplinas,
        #    adicionar FK escola/escola_actual → Escola, AlterField choices
        # =====================================================================

        # Remove os campos CharField/TextField antigos
        migrations.RemoveField(
            model_name='moduloeducacional',
            name='escola',
        ),
        migrations.RemoveField(
            model_name='moduloeducacional',
            name='escola_actual',
        ),
        migrations.RemoveField(
            model_name='moduloeducacional',
            name='disciplinas_basicas',
        ),
        migrations.RemoveField(
            model_name='moduloeducacional',
            name='disciplinas_avancadas',
        ),

        # Adiciona novos FK campos (com db_column diferente)
        migrations.AddField(
            model_name='moduloeducacional',
            name='escola',
            field=models.ForeignKey(
                blank=True,
                db_column='EscolaID',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='modulos_escola',
                to='pep_plus.escola',
            ),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='escola_actual',
            field=models.ForeignKey(
                blank=True,
                db_column='EscolaActualID',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='modulos_escola_actual',
                to='pep_plus.escola',
            ),
        ),

        # Adicionar choices a campos existentes (sem alterar schema DB)
        migrations.AlterField(
            model_name='moduloeducacional',
            name='sexo',
            field=models.CharField(
                blank=True,
                choices=[('M', 'Masculino'), ('F', 'Feminino'), ('I', 'Indeterminado')],
                db_column='Sexo',
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='moduloeducacional',
            name='classe',
            field=models.CharField(
                blank=True,
                choices=[
                    ('1', '1ª Classe'), ('2', '2ª Classe'), ('3', '3ª Classe'),
                    ('4', '4ª Classe'), ('5', '5ª Classe'), ('6', '6ª Classe'),
                    ('7', '7ª Classe'), ('8', '8ª Classe'), ('9', '9ª Classe'),
                    ('10', '10ª Classe'), ('11', '11ª Classe'), ('12', '12ª Classe'),
                    ('OUTRO', 'Outro'),
                ],
                db_column='Classe',
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='moduloeducacional',
            name='classe_que_frequenta',
            field=models.CharField(
                blank=True,
                choices=[
                    ('1', '1ª Classe'), ('2', '2ª Classe'), ('3', '3ª Classe'),
                    ('4', '4ª Classe'), ('5', '5ª Classe'), ('6', '6ª Classe'),
                    ('7', '7ª Classe'), ('8', '8ª Classe'), ('9', '9ª Classe'),
                    ('10', '10ª Classe'), ('11', '11ª Classe'), ('12', '12ª Classe'),
                    ('OUTRO', 'Outro'),
                ],
                db_column='ClasseQueFrequenta',
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='moduloeducacional',
            name='escolaridade_actual',
            field=models.CharField(
                blank=True,
                choices=[
                    ('EP1', 'EP1'), ('EP2', 'EP2'),
                    ('ESG1', 'ESG1'), ('ESG2', 'ESG2'),
                    ('ENSINO_SUPERIOR', 'Ensino Superior'),
                    ('OUTRO', 'Outro'),
                ],
                db_column='EscolaridadeActual',
                max_length=100,
                null=True,
            ),
        ),

        # =====================================================================
        # 5. PresencaSessao: remover nome_instituicao, adicionar tipo_encaminhamento FK
        # =====================================================================

        migrations.RemoveField(
            model_name='presencasessao',
            name='nome_instituicao',
        ),
        migrations.AddField(
            model_name='presencasessao',
            name='tipo_encaminhamento',
            field=models.ForeignKey(
                blank=True,
                db_column='TipoEncaminhamentoID',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='presencas',
                to='pep_plus.tipoencaminhamento',
            ),
        ),

        # =====================================================================
        # 6. EncaminhamentoSessao: adicionar tipo_encaminhamento FK
        # =====================================================================

        migrations.AddField(
            model_name='encaminhamentosessao',
            name='tipo_encaminhamento',
            field=models.ForeignKey(
                blank=True,
                db_column='TipoEncaminhamentoID',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='encaminhamentos',
                to='pep_plus.tipoencaminhamento',
            ),
        ),
    ]
