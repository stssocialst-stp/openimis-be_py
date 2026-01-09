# Generated migration for RoteiroReuniaoBimestral updates (Ferramenta 6)
# - Change coordenador_nacional from CharField to ForeignKey
# - Change participantes from TextField to JSONField
# - Add principais_desafios, oportunidades_melhoria, apreciacao_relatorios, plano_acao, proxima_reuniao
# - Remove old fields: resumo_agenda, desafios_solucoes, oportunidades_praticas, analise_dados_tendencias, acoes_definidas, observacoes_proxima_reuniao

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pep_plus', '0009_update_supervisaosessao_feedback_fields'),
    ]

    operations = [
        # Remove old fields first
        migrations.RemoveField(
            model_name='roteiroreuniaobimestral',
            name='resumo_agenda',
        ),
        migrations.RemoveField(
            model_name='roteiroreuniaobimestral',
            name='desafios_solucoes',
        ),
        migrations.RemoveField(
            model_name='roteiroreuniaobimestral',
            name='oportunidades_praticas',
        ),
        migrations.RemoveField(
            model_name='roteiroreuniaobimestral',
            name='analise_dados_tendencias',
        ),
        migrations.RemoveField(
            model_name='roteiroreuniaobimestral',
            name='acoes_definidas',
        ),
        migrations.RemoveField(
            model_name='roteiroreuniaobimestral',
            name='observacoes_proxima_reuniao',
        ),

        # Change coordenador_nacional from CharField to ForeignKey
        # First, we need to use RunSQL to handle the column type change
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    -- Rename old column if it exists
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='CoordenadorNacional'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral"
                        RENAME COLUMN "CoordenadorNacional" TO "CoordenadorNacional_old";
                    END IF;

                    -- Add new column if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='CoordenadorNacionalID'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral"
                        ADD COLUMN "CoordenadorNacionalID" integer NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='CoordenadorNacionalID'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral"
                        DROP COLUMN "CoordenadorNacionalID";
                    END IF;

                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='CoordenadorNacional_old'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral"
                        RENAME COLUMN "CoordenadorNacional_old" TO "CoordenadorNacional";
                    END IF;
                END $$;
            """
        ),

        # Add ForeignKey constraint
        migrations.AddField(
            model_name='roteiroreuniaobimestral',
            name='coordenador_nacional',
            field=models.ForeignKey(
                db_column='CoordenadorNacionalID',
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
                related_name='reunioes_coordenadas',
                help_text='Coordenador nacional responsável pela reunião',
                null=True
            ),
        ),

        # Drop old coordenador_nacional column
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='CoordenadorNacional_old'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral" DROP COLUMN "CoordenadorNacional_old";
                    END IF;
                END $$;
            """,
            reverse_sql='-- No reverse'
        ),

        # Change participantes from TextField to JSONField
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    -- Rename old column if it exists and new doesn't exist yet
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='Participantes'
                        AND data_type != 'jsonb'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='Participantes_old'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral"
                        RENAME COLUMN "Participantes" TO "Participantes_old";
                    END IF;

                    -- Add new column as JSONB if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='Participantes'
                        AND data_type = 'jsonb'
                    ) THEN
                        -- Drop Participantes if it exists and is not jsonb
                        IF EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name='tblRoteiroReuniaoBimestral'
                            AND column_name='Participantes'
                        ) THEN
                            ALTER TABLE "tblRoteiroReuniaoBimestral" DROP COLUMN "Participantes";
                        END IF;

                        ALTER TABLE "tblRoteiroReuniaoBimestral"
                        ADD COLUMN "Participantes" jsonb DEFAULT '[]'::jsonb NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='Participantes'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral"
                        DROP COLUMN "Participantes";
                    END IF;

                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='Participantes_old'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral"
                        RENAME COLUMN "Participantes_old" TO "Participantes";
                    END IF;
                END $$;
            """
        ),

        # Drop old participantes column
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='tblRoteiroReuniaoBimestral'
                        AND column_name='Participantes_old'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral" DROP COLUMN "Participantes_old";
                    END IF;
                END $$;
            """,
            reverse_sql='-- No reverse'
        ),

        # Add new content fields
        migrations.AddField(
            model_name='roteiroreuniaobimestral',
            name='principais_desafios',
            field=models.TextField(
                db_column='PrincipaisDesafios',
                null=True,
                blank=True,
                help_text='Principais desafios discutidos na reunião'
            ),
        ),
        migrations.AddField(
            model_name='roteiroreuniaobimestral',
            name='oportunidades_melhoria',
            field=models.TextField(
                db_column='OportunidadesMelhoria',
                null=True,
                blank=True,
                help_text='Oportunidades de melhoria identificadas'
            ),
        ),
        migrations.AddField(
            model_name='roteiroreuniaobimestral',
            name='apreciacao_relatorios',
            field=models.TextField(
                db_column='ApreciacaoRelatorios',
                null=True,
                blank=True,
                help_text='Apreciação e análise dos relatórios apresentados'
            ),
        ),
        migrations.AddField(
            model_name='roteiroreuniaobimestral',
            name='plano_acao',
            field=models.TextField(
                db_column='PlanoAcao',
                null=True,
                blank=True,
                help_text='Plano de ação definido com responsáveis e prazos'
            ),
        ),
        migrations.AddField(
            model_name='roteiroreuniaobimestral',
            name='proxima_reuniao',
            field=models.TextField(
                db_column='ProximaReuniao',
                null=True,
                blank=True,
                help_text='Informações sobre a próxima reunião (data, horário, local)'
            ),
        ),
    ]
