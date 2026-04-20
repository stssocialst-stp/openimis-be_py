from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds ParticipantesManuais column to tblRoteiroReuniaoBimestral.

    Uses RunSQL with IF NOT EXISTS to be safe against:
    - Fresh database builds
    - Repeated migration attempts
    - State inconsistencies from earlier migrations (0010 SeparateDatabaseAndState)

    The state update is done via SeparateDatabaseAndState only when the model
    exists in state; otherwise only the DB column is added.
    """

    dependencies = [
        ('pep_plus', '0021_add_legacy_id_coordenacao_aluno'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'tblRoteiroReuniaoBimestral'
                        AND column_name = 'ParticipantesManuais'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral"
                        ADD COLUMN "ParticipantesManuais" jsonb DEFAULT '[]'::jsonb NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'tblRoteiroReuniaoBimestral'
                        AND column_name = 'ParticipantesManuais'
                    ) THEN
                        ALTER TABLE "tblRoteiroReuniaoBimestral"
                        DROP COLUMN "ParticipantesManuais";
                    END IF;
                END $$;
            """,
        ),
    ]
