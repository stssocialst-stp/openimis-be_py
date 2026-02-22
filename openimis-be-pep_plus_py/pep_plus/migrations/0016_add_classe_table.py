# Migration: Adicionar tabela Classe e campos de faltas em Disciplina
#
# Cria nova tabela de referência:
#   - tblClasse  (substitui choices 'classe' e 'classe_que_frequenta' em ModuloEducacional)
#
# Cria tabela M2M intermediária:
#   - tblClasseDisciplina  (relação Classe ↔ Disciplina)
#
# Adiciona campos a Disciplina:
#   - faixa_faltas_aceitaveis  (CharField com choices)
#   - quantidade_faltas_aceitaveis  (IntegerField)
#
# Altera ModuloEducacional:
#   - Remove classe (CharField choices) → adiciona classe (FK → Classe, db_column='ClasseID')
#   - Remove classe_que_frequenta (CharField choices) → adiciona classe_que_frequenta (FK → Classe, db_column='ClasseQueFrequentaID')

import core.fields
import core.utils
import datetime
import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0015_add_parametrizacao_tables'),
    ]

    operations = [

        # =====================================================================
        # 1. Criar tabela Classe (VersionedModel)
        # =====================================================================

        migrations.CreateModel(
            name='Classe',
            fields=[
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom', default=datetime.datetime.now)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('id', models.AutoField(db_column='ClasseID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='ClasseUUID', default=uuid.uuid4, max_length=36, unique=True)),
                ('nome', models.CharField(db_column='Nome', max_length=100)),
                ('codigo', models.CharField(db_column='Codigo', max_length=10, unique=True)),
                ('nivel', models.CharField(
                    blank=True,
                    choices=[
                        ('EP1', 'EP1 (Ensino Primário 1 — 1ª a 4ª Classe)'),
                        ('EP2', 'EP2 (Ensino Primário 2 — 5ª e 6ª Classe)'),
                        ('ESG1', 'ESG1 (Ensino Secundário Geral 1 — 7ª a 9ª Classe)'),
                        ('ESG2', 'ESG2 (Ensino Secundário Geral 2 — 10ª a 12ª Classe)'),
                        ('OUTRO', 'Outro'),
                    ],
                    db_column='Nivel',
                    max_length=50,
                    null=True,
                )),
                ('ordem', models.IntegerField(blank=True, db_column='Ordem', null=True)),
                ('ativo', models.BooleanField(db_column='Ativo', default=True)),
            ],
            options={
                'db_table': 'tblClasse',
                'managed': True,
                'ordering': ['ordem', 'codigo'],
            },
            bases=(core.utils.CachedModelMixin, models.Model),
        ),

        # =====================================================================
        # 2. Adicionar campos faixa/quantidade de faltas em Disciplina
        # =====================================================================

        migrations.AddField(
            model_name='disciplina',
            name='faixa_faltas_aceitaveis',
            field=models.CharField(
                blank=True,
                choices=[
                    ('1-3', '1 a 3 faltas'),
                    ('4-6', '4 a 6 faltas'),
                    ('7-10', '7 a 10 faltas'),
                    ('+10', 'Mais de 10 faltas'),
                ],
                db_column='FaixaFaltasAceitaveis',
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='disciplina',
            name='quantidade_faltas_aceitaveis',
            field=models.IntegerField(blank=True, db_column='QuantidadeFaltasAceitaveis', null=True),
        ),

        # =====================================================================
        # 3. Criar tabela M2M ClasseDisciplina (plain Model)
        # =====================================================================

        migrations.CreateModel(
            name='ClasseDisciplina',
            fields=[
                ('id', models.AutoField(db_column='ClasseDisciplinaID', primary_key=True, serialize=False)),
                ('classe', models.ForeignKey(
                    db_column='ClasseID',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='disciplinas_associadas',
                    to='pep_plus.classe',
                )),
                ('disciplina', models.ForeignKey(
                    db_column='DisciplinaID',
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='classes_associadas',
                    to='pep_plus.disciplina',
                )),
            ],
            options={
                'db_table': 'tblClasseDisciplina',
                'managed': True,
            },
        ),
        migrations.AlterUniqueTogether(
            name='classedisciplina',
            unique_together={('classe', 'disciplina')},
        ),

        # =====================================================================
        # 4. ModuloEducacional.classe: remover CharField → adicionar FK → Classe
        # =====================================================================

        migrations.RemoveField(
            model_name='moduloeducacional',
            name='classe',
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='classe',
            field=models.ForeignKey(
                blank=True,
                db_column='ClasseID',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='modulos_classe',
                to='pep_plus.classe',
            ),
        ),

        # =====================================================================
        # 5. ModuloEducacional.classe_que_frequenta: remover CharField → FK → Classe
        # =====================================================================

        migrations.RemoveField(
            model_name='moduloeducacional',
            name='classe_que_frequenta',
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='classe_que_frequenta',
            field=models.ForeignKey(
                blank=True,
                db_column='ClasseQueFrequentaID',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='modulos_classe_que_frequenta',
                to='pep_plus.classe',
            ),
        ),
    ]
