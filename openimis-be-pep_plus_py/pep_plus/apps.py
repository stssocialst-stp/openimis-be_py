from django.apps import AppConfig

MODULE_NAME = "pep_plus"

DEFAULT_CONFIG = {
    "gql_query_pep_perms":                            ["159001"],
    "gql_mutation_manage_modulo_pep_perms":            ["159011"],
    "gql_mutation_manage_escola_perms":                ["159012"],
    "gql_mutation_manage_disciplina_perms":            ["159013"],
    "gql_mutation_manage_tipo_encaminhamento_perms":   ["159014"],
    "gql_mutation_create_sessao_pep_perms":            ["159021"],
    "gql_mutation_update_sessao_pep_perms":            ["159022"],
    "gql_mutation_delete_sessao_pep_perms":            ["159023"],
    "gql_mutation_manage_presenca_sessao_perms":       ["159031"],
    "gql_mutation_delete_presenca_sessao_perms":       ["159032"],
    "gql_mutation_manage_execucao_sessao_perms":       ["159041"],
    "gql_mutation_manage_supervisao_sessao_perms":     ["159051"],
    "gql_mutation_manage_modulo_educacional_perms":    ["159061"],
    "gql_mutation_delete_modulo_educacional_perms":    ["159062"],
    "gql_mutation_manage_grupo_familiar_perms":        ["159071"],
    "gql_mutation_delete_grupo_familiar_perms":        ["159072"],
    "gql_mutation_manage_relatorio_distrital_perms":   ["159081"],
    "gql_mutation_delete_relatorio_distrital_perms":   ["159082"],
    "gql_mutation_manage_roteiro_reuniao_perms":       ["159091"],
    "gql_mutation_delete_roteiro_reuniao_perms":       ["159092"],
    "gql_mutation_manage_relatorio_supervisao_perms":  ["159101"],
    "gql_mutation_delete_relatorio_supervisao_perms":  ["159102"],
    "gql_mutation_manage_encaminhamento_perms":        ["159111"],
    "gql_mutation_manage_coordenacao_distrital_perms": ["159121"],
    "gql_mutation_delete_coordenacao_distrital_perms": ["159122"],
}


class PepPlusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = MODULE_NAME

    # Right IDs — padrão openIMIS, usados em services.py e registados em modulesPermissions
    gql_query_pep_perms                            = ["159001"]
    gql_mutation_manage_modulo_pep_perms           = ["159011"]
    gql_mutation_manage_escola_perms               = ["159012"]
    gql_mutation_manage_disciplina_perms           = ["159013"]
    gql_mutation_manage_tipo_encaminhamento_perms  = ["159014"]
    gql_mutation_create_sessao_pep_perms           = ["159021"]
    gql_mutation_update_sessao_pep_perms           = ["159022"]
    gql_mutation_delete_sessao_pep_perms           = ["159023"]
    gql_mutation_manage_presenca_sessao_perms      = ["159031"]
    gql_mutation_delete_presenca_sessao_perms      = ["159032"]
    gql_mutation_manage_execucao_sessao_perms      = ["159041"]
    gql_mutation_manage_supervisao_sessao_perms    = ["159051"]
    gql_mutation_manage_modulo_educacional_perms   = ["159061"]
    gql_mutation_delete_modulo_educacional_perms   = ["159062"]
    gql_mutation_manage_grupo_familiar_perms       = ["159071"]
    gql_mutation_delete_grupo_familiar_perms       = ["159072"]
    gql_mutation_manage_relatorio_distrital_perms  = ["159081"]
    gql_mutation_delete_relatorio_distrital_perms  = ["159082"]
    gql_mutation_manage_roteiro_reuniao_perms      = ["159091"]
    gql_mutation_delete_roteiro_reuniao_perms      = ["159092"]
    gql_mutation_manage_relatorio_supervisao_perms = ["159101"]
    gql_mutation_delete_relatorio_supervisao_perms = ["159102"]
    gql_mutation_manage_encaminhamento_perms       = ["159111"]
    gql_mutation_manage_coordenacao_distrital_perms= ["159121"]
    gql_mutation_delete_coordenacao_distrital_perms= ["159122"]

    def ready(self):
        from django.db import connection
        from django.db.utils import OperationalError, ProgrammingError

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM information_schema.tables WHERE table_name = 'core_ModuleConfiguration' LIMIT 1"
                )
                table_exists = cursor.fetchone() is not None

            if table_exists:
                from core.models import ModuleConfiguration
                ModuleConfiguration.get_or_default(self.name, DEFAULT_CONFIG)
        except (OperationalError, ProgrammingError):
            pass

        self._connect_rights_cache_invalidation()

    @staticmethod
    def _connect_rights_cache_invalidation():
        """
        Invalidates the cached user rights when a UserRole or RoleRight is saved.
        core.models.InteractiveUser.rights uses cache.set(..., timeout=None) so
        the cache never expires on its own — new role assignments would be invisible
        until the cache is cleared or the backend restarted without this hook.
        """
        try:
            from django.core.cache import cache
            from django.db.models.signals import post_save
            from core.models import UserRole, RoleRight

            def _on_user_role_save(sender, instance, **kwargs):
                cache.delete('rights_' + str(instance.user_id))

            def _on_role_right_save(sender, instance, **kwargs):
                # A right was added/changed on a role — clear cache for every user with that role
                user_ids = UserRole.filter_queryset().filter(
                    role_id=instance.role_id
                ).values_list('user_id', flat=True)
                for uid in user_ids:
                    cache.delete('rights_' + str(uid))

            post_save.connect(_on_user_role_save, sender=UserRole, weak=False)
            post_save.connect(_on_role_right_save, sender=RoleRight, weak=False)
        except Exception:
            pass
