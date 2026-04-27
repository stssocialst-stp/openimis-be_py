from django.db import migrations


class Migration(migrations.Migration):
    """
    Fixes PolicyRenewal.MultipleObjectsReturned raised by the renewal scheduler job.

    Root cause: get_or_create(policy=policy, validity_to=None) finds multiple rows
    because the partial unique index is missing from the database.

    Steps:
      1. Discover the FK column name in tblPolicyRenewalDetails at runtime (it may
         differ from "RenewalID") using information_schema, then delete child rows
         that belong to duplicate renewals.
      2. Delete the duplicate parent renewals (now safe — no child FK violations).
      3. Create the partial unique index to prevent recurrence (idempotent).
    """

    dependencies = [
        ('pep_plus', '0022_add_participantes_manuais_roteiro_reuniao'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                DECLARE
                    v_fk_col text;
                BEGIN
                    -- Discover the FK column name in tblPolicyRenewalDetails that
                    -- references tblPolicyRenewals, so we can delete the right rows.
                    SELECT kcu.column_name INTO v_fk_col
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON kcu.constraint_name = tc.constraint_name
                       AND kcu.table_name      = tc.table_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_name      = 'tblPolicyRenewalDetails'
                      AND tc.constraint_name = 'FK_tblPolicyRenewalDetails_tblPolicyRenewals'
                    LIMIT 1;

                    -- Fall back to the most common legacy column name if lookup fails
                    IF v_fk_col IS NULL THEN
                        v_fk_col := 'RenewalID';
                    END IF;

                    -- Step 1: delete child rows for all duplicate active renewals
                    EXECUTE format(
                        'DELETE FROM "tblPolicyRenewalDetails"
                         WHERE %I IN (
                             SELECT "RenewalID"
                             FROM "tblPolicyRenewals"
                             WHERE "ValidityTo" IS NULL
                               AND "RenewalID" NOT IN (
                                   SELECT MAX("RenewalID")
                                   FROM "tblPolicyRenewals"
                                   WHERE "ValidityTo" IS NULL
                                   GROUP BY "PolicyID"
                               )
                         )',
                        v_fk_col
                    );
                END $$;

                -- Step 2: delete duplicate parent renewals (children already removed above)
                DELETE FROM "tblPolicyRenewals"
                WHERE "ValidityTo" IS NULL
                  AND "RenewalID" NOT IN (
                      SELECT MAX("RenewalID")
                      FROM "tblPolicyRenewals"
                      WHERE "ValidityTo" IS NULL
                      GROUP BY "PolicyID"
                  );

                -- Step 3: create partial unique index if it does not exist
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes
                        WHERE indexname = 'unique_policy_validity_to_null'
                    ) THEN
                        CREATE UNIQUE INDEX unique_policy_validity_to_null
                        ON "tblPolicyRenewals" ("PolicyID")
                        WHERE "ValidityTo" IS NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS unique_policy_validity_to_null;
            """,
        ),
    ]
