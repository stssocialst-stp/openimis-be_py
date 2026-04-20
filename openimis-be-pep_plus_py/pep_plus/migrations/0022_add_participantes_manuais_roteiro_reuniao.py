from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0021_add_legacy_id_coordenacao_aluno'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
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
            ],
            state_operations=[
                migrations.AddField(
                    model_name='roteiroreuniaobimestral',
                    name='participantes_manuais',
                    field=models.JSONField(
                        blank=True,
                        db_column='ParticipantesManuais',
                        default=list,
                        help_text='Array de nomes de participantes inseridos manualmente',
                    ),
                ),
            ],
        ),
    ]
