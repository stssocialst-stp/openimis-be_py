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
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(self.name, DEFAULT_CONFIG)
