from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adiciona a coluna LegacyID em tblCoordenacaoDistrital e tblAluno.

    Estas tabelas estendem VersionedModel mas as migrations anteriores (0017 e 0018)
    não incluíram o campo legacy_id (db_column='LegacyID'), causando o erro:
      column "LegacyID" of relation "tblCoordenacaoDistrital" does not exist
    """

    dependencies = [
        ('pep_plus', '0020_add_ano_registo_moduloeducacional'),
    ]

    operations = [
        migrations.AddField(
            model_name='coordenacaodistrital',
            name='legacy_id',
            field=models.IntegerField(
                blank=True, db_column='LegacyID', null=True
            ),
        ),
        migrations.AddField(
            model_name='aluno',
            name='legacy_id',
            field=models.IntegerField(
                blank=True, db_column='LegacyID', null=True
            ),
        ),
    ]
