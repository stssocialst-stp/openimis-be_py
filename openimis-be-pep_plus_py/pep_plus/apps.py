from django.apps import AppConfig

MODULE_NAME = "pep_plus"

DEFAULT_CONFIG = {
    "gql_query_pep_sessions_perms": ["159001"],
    "gql_mutation_create_pep_session_perms": ["159002"],
    "gql_mutation_update_pep_session_perms": ["159003"],
    "gql_mutation_delete_pep_session_perms": ["159004"],
}


class PepPlusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = MODULE_NAME

    def ready(self):
        # Only load configuration after migrations are complete
        # Avoid database access during initial migrations
        from django.db import connection
        from django.db.utils import OperationalError, ProgrammingError

        try:
            # Check if tables exist before trying to access ModuleConfiguration
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM information_schema.tables WHERE table_name = 'core_ModuleConfiguration' LIMIT 1"
                )
                table_exists = cursor.fetchone() is not None

            if table_exists:
                from core.models import ModuleConfiguration
                cfg = ModuleConfiguration.get_or_default(self.name, DEFAULT_CONFIG)
        except (OperationalError, ProgrammingError):
            # Tables don't exist yet, skip configuration loading
            pass
