from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrate_tecnicos_to_m2m(apps, schema_editor):
    SessaoPEP = apps.get_model('pep_plus', 'SessaoPEP')
    SessaoPEPTecnico = apps.get_model('pep_plus', 'SessaoPEPTecnico')
    for sessao in SessaoPEP.objects.filter(validity_to__isnull=True, tecnico_social__isnull=False):
        SessaoPEPTecnico.objects.get_or_create(sessao=sessao, tecnico_id=sessao.tecnico_social_id)


def reverse_migrate(apps, schema_editor):
    # Nothing needed — tecnico_social FK is still populated
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pep_plus', '0026_seed_mrr_roles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessaopep',
            name='tecnico_social',
            field=models.ForeignKey(
                blank=True,
                db_column='TecnicoSocialID',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='sessoes_tecnico',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name='SessaoPEPTecnico',
            fields=[
                ('id', models.AutoField(db_column='SessaoPEPTecnicoID', primary_key=True, serialize=False)),
                ('sessao', models.ForeignKey(
                    db_column='SessaoPEPID',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tecnicos_formadores',
                    to='pep_plus.SessaoPEP',
                )),
                ('tecnico', models.ForeignKey(
                    db_column='TecnicoID',
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='sessoes_como_tecnico_formador',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'tblSessaoPEPTecnico',
                'managed': True,
            },
        ),
        migrations.AlterUniqueTogether(
            name='sessaopeptecnico',
            unique_together={('sessao', 'tecnico')},
        ),
        migrations.RunPython(migrate_tecnicos_to_m2m, reverse_migrate),
    ]
