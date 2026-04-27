from django.db import migrations


class Migration(migrations.Migration):
    """
    Fixes PolicyRenewal.MultipleObjectsReturned raised by the renewal scheduler job.

    Root cause: get_or_create(policy=policy, validity_to=None) finds multiple rows
    because the partial unique index is missing from the database even though it is
    declared in the Policy model's Meta.constraints.

    Steps:
      1. Remove duplicate active renewals, keeping the row with the highest RenewalID.
      2. Create the partial unique index (idempotent — skipped if it already exists).
    """

    dependencies = [
        ('pep_plus', '0022_add_participantes_manuais_roteiro_reuniao'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- Identify duplicate active renewal IDs (all except the highest per policy)
                -- Step 1: delete child details that belong to duplicate renewals first (FK safety)
                DELETE FROM "tblPolicyRenewalDetails"
                WHERE "RenewalID" IN (
                    SELECT "RenewalID"
                    FROM "tblPolicyRenewals"
                    WHERE "ValidityTo" IS NULL
                      AND "RenewalID" NOT IN (
                          SELECT MAX("RenewalID")
                          FROM "tblPolicyRenewals"
                          WHERE "ValidityTo" IS NULL
                          GROUP BY "PolicyID"
                      )
                );

                -- Step 2: now safe to delete the duplicate parent renewals
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
