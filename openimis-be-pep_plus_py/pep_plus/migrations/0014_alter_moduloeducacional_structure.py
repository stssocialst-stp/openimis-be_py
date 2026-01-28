# Generated migration for ModuloEducacional restructure to Assiduidade Escolar

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0013_seed_test_data'),
    ]

    operations = [
        # Remove old fields
        migrations.RemoveField(
            model_name='moduloeducacional',
            name='codigo',
        ),
        migrations.RemoveField(
            model_name='moduloeducacional',
            name='descricao',
        ),
        migrations.RemoveField(
            model_name='moduloeducacional',
            name='ordem',
        ),
        migrations.RemoveField(
            model_name='moduloeducacional',
            name='duracao_semanas',
        ),
        migrations.RemoveField(
            model_name='moduloeducacional',
            name='ativo',
        ),

        # Add new fields for Assiduidade Escolar
        migrations.AddField(
            model_name='moduloeducacional',
            name='id_membro_crianca',
            field=models.CharField(blank=True, db_column='IdMembroCrianca', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='nome_encarregado',
            field=models.CharField(blank=True, db_column='NomeEncarregado', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='escola',
            field=models.CharField(blank=True, db_column='Escola', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='escolaridade_actual',
            field=models.CharField(blank=True, db_column='EscolaridadeActual', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='data_nascimento',
            field=models.DateField(blank=True, db_column='DataNascimento', null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='id_da_crianca',
            field=models.CharField(blank=True, db_column='IdDaCrianca', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='sexo',
            field=models.CharField(blank=True, db_column='Sexo', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='dados_escolar_correctos',
            field=models.BooleanField(blank=True, db_column='DadosEscolarCorrectos', null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='escola_actual',
            field=models.CharField(blank=True, db_column='EscolaActual', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='classe',
            field=models.CharField(blank=True, db_column='Classe', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='idade',
            field=models.IntegerField(blank=True, db_column='Idade', null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='dados_escolares_correctos',
            field=models.BooleanField(blank=True, db_column='DadosEscolaresCorrectos', null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='informacoes_localizacao',
            field=models.JSONField(blank=True, db_column='InformacoesLocalizacao', default=dict, help_text='Objeto: { nomeDaRegiao, distritoId, Localidade, nomeEscola, pontoReferencia, meioResidencia }'),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='classe_que_frequenta',
            field=models.CharField(blank=True, db_column='ClasseQueFrequenta', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='aproveitamento_primeiro_trimestre',
            field=models.CharField(blank=True, choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('+10', '+10')], db_column='AproveitamentoPrimeiroTrimestre', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='faixa_de_faltas',
            field=models.CharField(blank=True, choices=[('1-3', '1-3'), ('4-6', '4-6'), ('7-10', '7-10'), ('+10', '+10')], db_column='FaixaDeFaltas', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='disciplinas_basicas',
            field=models.TextField(blank=True, db_column='DisciplinasBasicas', null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='disciplinas_avancadas',
            field=models.TextField(blank=True, db_column='DisciplinasAvancadas', null=True),
        ),
        migrations.AddField(
            model_name='moduloeducacional',
            name='observacoes',
            field=models.TextField(blank=True, db_column='Observacoes', null=True),
        ),
    ]
