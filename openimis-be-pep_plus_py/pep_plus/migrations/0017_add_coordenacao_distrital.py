# Migration: Adicionar tabelas de Coordenação Distrital
#
# Cria:
#   - tblCoordenacaoDistrital   (1 coordenador + 1 técnico administrativo por distrito)
#   - tblCoordenacaoDistritalTecnico  (M2M técnicos operacionais)
#
# Regras de negócio:
#   - 1 coordenador por distrito (FK → User)
#   - 1 técnico administrativo por distrito (FK → User, nullable)
#   - N técnicos operacionais (M2M via tabela intermediária)
#   - Apenas 1 registo activo por distrito (enforced no service)

import uuid
import core.fields
import core.utils
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0016_add_classe_table'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoordenacaoDistrital',
            fields=[
                ('id', models.AutoField(db_column='CoordenacaoDistritalID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='CoordenacaoDistritalUUID', default=uuid.uuid4, max_length=36, unique=True)),
                # VersionedModel audit fields
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom', default=core.utils.TimeUtils.now)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(blank=True, db_column='AuditUserID', null=True)),
                # Business fields
                ('ativo', models.BooleanField(db_column='Ativo', default=True)),
                ('observacoes', models.TextField(blank=True, db_column='Observacoes', null=True)),
                ('distrito', models.ForeignKey(
                    db_column='DistritoID',
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='coordenacoes_distritais',
                    to='location.location',
                )),
                ('coordenador', models.ForeignKey(
                    db_column='CoordenadorID',
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='coordenacoes_como_coordenador',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('tecnico_administrativo', models.ForeignKey(
                    blank=True,
                    db_column='TecnicoAdministrativoID',
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='coordenacoes_como_tecnico_admin',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'tblCoordenacaoDistrital',
                'ordering': ['distrito'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CoordenacaoDistritalTecnico',
            fields=[
                ('id', models.AutoField(db_column='CoordenacaoDistritalTecnicoID', primary_key=True, serialize=False)),
                ('coordenacao', models.ForeignKey(
                    db_column='CoordenacaoDistritalID',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tecnicos_operacionais',
                    to='pep_plus.coordenacaodistrital',
                )),
                ('tecnico', models.ForeignKey(
                    db_column='TecnicoID',
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='coordenacoes_como_tecnico_operacional',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'tblCoordenacaoDistritalTecnico',
                'managed': True,
                'unique_together': {('coordenacao', 'tecnico')},
            },
        ),
    ]
