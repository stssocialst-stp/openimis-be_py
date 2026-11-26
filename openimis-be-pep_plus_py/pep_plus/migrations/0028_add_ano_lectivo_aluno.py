from django.db import migrations, models


class Migration(migrations.Migration):
    """Adiciona AnoLectivo a tblAluno (ano lectivo da escola/classe registadas, ex.: 2025-2026)."""

    dependencies = [
        ('pep_plus', '0027_add_sessao_pep_tecnicos'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='ano_lectivo',
            field=models.CharField(
                blank=True, db_column='AnoLectivo', max_length=9, null=True,
                help_text='Ano lectivo dos dados escolares (ex: 2025-2026)',
            ),
        ),
    ]
