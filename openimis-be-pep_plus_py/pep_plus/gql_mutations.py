"""
PEP+ GraphQL Mutations
Implements CREATE, UPDATE, DELETE operations for all PEP+ entities
"""
import graphene
from core.schema import OpenIMISMutation
from .models import (
    ModuloEducacional, GrupoFamiliar, SessaoPEP, PresencaSessao,
    ExecucaoSessao, SupervisaoSessao, RelatorioDistritalBimestral,
    EncaminhamentoSessao
)
from .gql_queries import (
    ModuloEducacionalGQLType, GrupoFamiliarGQLType, SessaoPEPGQLType,
    PresencaSessaoGQLType, ExecucaoSessaoGQLType, SupervisaoSessaoGQLType,
    RelatorioDistritalBimestralGQLType, EncaminhamentoSessaoGQLType
)
from .services import (
    ModuloEducacionalService, GrupoFamiliarService, SessaoPEPService,
    PresencaSessaoService, ExecucaoSessaoService, SupervisaoSessaoService,
    RelatorioDistritalService, EncaminhamentoService
)


# ========== EDUCATIONAL MODULE MUTATIONS ==========

class CreateModuloEducacionalInput(OpenIMISMutation.Input):
    """Input for creating an educational module"""
    codigo = graphene.String(required=True)
    nome = graphene.String(required=True)
    descricao = graphene.String(required=False)
    ordem = graphene.Int(required=False)
    duracao_semanas = graphene.Int(required=False)
    ativo = graphene.Boolean(required=False)


class CreateModuloEducacionalMutation(OpenIMISMutation):
    """Create a new educational module"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateModuloEducacionalMutation"

    class Input(CreateModuloEducacionalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            modulo = ModuloEducacionalService.create(data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdateModuloEducacionalInput(OpenIMISMutation.Input):
    """Input for updating an educational module"""
    id = graphene.Int(required=True)
    codigo = graphene.String(required=False)
    nome = graphene.String(required=False)
    descricao = graphene.String(required=False)
    ordem = graphene.Int(required=False)
    duracao_semanas = graphene.Int(required=False)
    ativo = graphene.Boolean(required=False)


class UpdateModuloEducacionalMutation(OpenIMISMutation):
    """Update an educational module"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateModuloEducacionalMutation"

    class Input(UpdateModuloEducacionalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            modulo_id = data.pop('id')
            modulo = ModuloEducacionalService.update(modulo_id, data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class DeleteModuloEducacionalMutation(OpenIMISMutation):
    """Delete an educational module"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteModuloEducacionalMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.Int(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            ModuloEducacionalService.delete(data['id'], user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== FAMILY GROUP MUTATIONS ==========

class CreateGrupoFamiliarInput(OpenIMISMutation.Input):
    """Input for creating a family group"""
    codigo = graphene.String(required=True)
    nome = graphene.String(required=True)
    distrito_id = graphene.Int(required=True)
    localidade_id = graphene.Int(required=False)
    numero_familias = graphene.Int(required=False)
    ativo = graphene.Boolean(required=False)


class CreateGrupoFamiliarMutation(OpenIMISMutation):
    """Create a new family group"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateGrupoFamiliarMutation"

    class Input(CreateGrupoFamiliarInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            grupo = GrupoFamiliarService.create(data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdateGrupoFamiliarInput(OpenIMISMutation.Input):
    """Input for updating a family group"""
    id = graphene.Int(required=True)
    codigo = graphene.String(required=False)
    nome = graphene.String(required=False)
    distrito_id = graphene.Int(required=False)
    localidade_id = graphene.Int(required=False)
    numero_familias = graphene.Int(required=False)
    ativo = graphene.Boolean(required=False)


class UpdateGrupoFamiliarMutation(OpenIMISMutation):
    """Update a family group"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateGrupoFamiliarMutation"

    class Input(UpdateGrupoFamiliarInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            grupo_id = data.pop('id')
            grupo = GrupoFamiliarService.update(grupo_id, data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class DeleteGrupoFamiliarMutation(OpenIMISMutation):
    """Delete a family group"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteGrupoFamiliarMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.Int(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            GrupoFamiliarService.delete(data['id'], user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== PEP SESSION MUTATIONS (Ferramenta 1) ==========

class CreateSessaoPEPInput(OpenIMISMutation.Input):
    """Input for creating a PEP session"""
    codigo_sessao = graphene.String(required=True)
    coordenador_distrital_id = graphene.Int(required=True)
    tecnico_social_id = graphene.Int(required=True)
    distrito_id = graphene.Int(required=True)
    modulo_id = graphene.Int(required=True)
    mes_modulo_anterior = graphene.String(required=False)
    dia_semana = graphene.String(required=True)
    data_sessao = graphene.Date(required=True)
    hora_sessao = graphene.Time(required=True)
    zona = graphene.String(required=True)
    numero_familias = graphene.Int(required=True)
    grupo_familia_id = graphene.Int(required=True)
    tempo_deslocamento = graphene.Int(required=False)
    feedback_documentacao = graphene.String(required=True)
    tem_supervisao = graphene.Boolean(required=False)
    observacoes = graphene.String(required=False)
    status = graphene.String(required=False)


class CreateSessaoPEPMutation(OpenIMISMutation):
    """Create a new PEP session"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateSessaoPEPMutation"

    class Input(CreateSessaoPEPInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            sessao = SessaoPEPService.create(data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdateSessaoPEPInput(OpenIMISMutation.Input):
    """Input for updating a PEP session"""
    id = graphene.Int(required=True)
    coordenador_distrital_id = graphene.Int(required=False)
    tecnico_social_id = graphene.Int(required=False)
    distrito_id = graphene.Int(required=False)
    modulo_id = graphene.Int(required=False)
    mes_modulo_anterior = graphene.String(required=False)
    dia_semana = graphene.String(required=False)
    data_sessao = graphene.Date(required=False)
    hora_sessao = graphene.Time(required=False)
    zona = graphene.String(required=False)
    numero_familias = graphene.Int(required=False)
    grupo_familia_id = graphene.Int(required=False)
    tempo_deslocamento = graphene.Int(required=False)
    feedback_documentacao = graphene.String(required=False)
    tem_supervisao = graphene.Boolean(required=False)
    observacoes = graphene.String(required=False)
    status = graphene.String(required=False)


class UpdateSessaoPEPMutation(OpenIMISMutation):
    """Update a PEP session"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateSessaoPEPMutation"

    class Input(UpdateSessaoPEPInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            sessao_id = data.pop('id')
            sessao = SessaoPEPService.update(sessao_id, data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class DeleteSessaoPEPMutation(OpenIMISMutation):
    """Delete a PEP session"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteSessaoPEPMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.Int(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            SessaoPEPService.delete(data['id'], user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== SESSION ATTENDANCE MUTATIONS (Ferramenta 2) ==========

class CreatePresencaSessaoInput(OpenIMISMutation.Input):
    """Input for creating an attendance record"""
    sessao_id = graphene.Int(required=True)
    familia_id = graphene.String(required=True)
    nome_familia = graphene.String(required=True)
    grupo_id = graphene.String(required=False)
    estado = graphene.String(required=False)
    codigo_encaminhamento = graphene.String(required=False)
    observacoes = graphene.String(required=False)


class CreatePresencaSessaoMutation(OpenIMISMutation):
    """Create a new attendance record"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreatePresencaSessaoMutation"

    class Input(CreatePresencaSessaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            presenca = PresencaSessaoService.create(data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdatePresencaSessaoInput(OpenIMISMutation.Input):
    """Input for updating an attendance record"""
    id = graphene.Int(required=True)
    estado = graphene.String(required=False)
    codigo_encaminhamento = graphene.String(required=False)
    observacoes = graphene.String(required=False)


class UpdatePresencaSessaoMutation(OpenIMISMutation):
    """Update an attendance record"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdatePresencaSessaoMutation"

    class Input(UpdatePresencaSessaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            presenca_id = data.pop('id')
            presenca = PresencaSessaoService.update(presenca_id, data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class DeletePresencaSessaoMutation(OpenIMISMutation):
    """Delete an attendance record"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeletePresencaSessaoMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.Int(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            PresencaSessaoService.delete(data['id'], user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== SESSION EXECUTION MUTATIONS (Ferramenta 3) ==========

class CreateExecucaoSessaoInput(OpenIMISMutation.Input):
    """Input for creating a session execution record"""
    sessao_id = graphene.Int(required=True)
    formador_id = graphene.Int(required=True)
    supervisor_id = graphene.Int(required=False)
    localidade_id = graphene.Int(required=False)
    numero_participantes_compromissos = graphene.Int(required=False)
    praticas_positivas = graphene.JSONString(required=False)
    desafios_transmissao = graphene.JSONString(required=False)
    necessita_encaminhamento = graphene.Boolean(required=False)
    auto_avaliacao_pontos_fortes = graphene.JSONString(required=False)
    auto_avaliacao_pontos_atencao = graphene.JSONString(required=False)
    avaliacao_metodologia = graphene.JSONString(required=False)
    observacoes = graphene.String(required=False)


class CreateExecucaoSessaoMutation(OpenIMISMutation):
    """Create a new session execution record"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateExecucaoSessaoMutation"

    class Input(CreateExecucaoSessaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            execucao = ExecucaoSessaoService.create(data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdateExecucaoSessaoInput(OpenIMISMutation.Input):
    """Input for updating a session execution record"""
    id = graphene.Int(required=True)
    numero_participantes_compromissos = graphene.Int(required=False)
    praticas_positivas = graphene.JSONString(required=False)
    desafios_transmissao = graphene.JSONString(required=False)
    necessita_encaminhamento = graphene.Boolean(required=False)
    auto_avaliacao_pontos_fortes = graphene.JSONString(required=False)
    auto_avaliacao_pontos_atencao = graphene.JSONString(required=False)
    avaliacao_metodologia = graphene.JSONString(required=False)
    observacoes = graphene.String(required=False)


class UpdateExecucaoSessaoMutation(OpenIMISMutation):
    """Update a session execution record"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateExecucaoSessaoMutation"

    class Input(UpdateExecucaoSessaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            execucao_id = data.pop('id')
            execucao = ExecucaoSessaoService.update(execucao_id, data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== SESSION SUPERVISION MUTATIONS (Ferramenta 4) ==========

class CreateSupervisaoSessaoInput(OpenIMISMutation.Input):
    """Input for creating a supervision record"""
    sessao_id = graphene.Int(required=True)
    supervisor_id = graphene.Int(required=True)
    formador_id = graphene.Int(required=True)
    data_supervisao = graphene.Date(required=True)
    data_modulo_anterior = graphene.Date(required=False)
    identificador_grupo = graphene.String(required=True)
    perguntas_avaliacao = graphene.JSONString(required=False)
    pontos_positivos = graphene.String(required=False)
    pontos_melhorar = graphene.String(required=False)
    observacoes = graphene.String(required=False)


class CreateSupervisaoSessaoMutation(OpenIMISMutation):
    """Create a new supervision record"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateSupervisaoSessaoMutation"

    class Input(CreateSupervisaoSessaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            supervisao = SupervisaoSessaoService.create(data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdateSupervisaoSessaoInput(OpenIMISMutation.Input):
    """Input for updating a supervision record"""
    id = graphene.Int(required=True)
    perguntas_avaliacao = graphene.JSONString(required=False)
    pontos_positivos = graphene.String(required=False)
    pontos_melhorar = graphene.String(required=False)
    observacoes = graphene.String(required=False)


class UpdateSupervisaoSessaoMutation(OpenIMISMutation):
    """Update a supervision record"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateSupervisaoSessaoMutation"

    class Input(UpdateSupervisaoSessaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            supervisao_id = data.pop('id')
            supervisao = SupervisaoSessaoService.update(supervisao_id, data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== ENCAMINHAMENTO MUTATIONS ==========

class CreateEncaminhamentoInput(OpenIMISMutation.Input):
    """Input for creating a referral"""
    sessao_id = graphene.Int(required=True)
    familia_id = graphene.String(required=True)
    nome_familia = graphene.String(required=True)
    codigo_encaminhamento = graphene.String(required=True)
    descricao = graphene.String(required=True)
    status = graphene.String(required=False)
    tecnico_responsavel_id = graphene.Int(required=False)
    observacoes = graphene.String(required=False)


class CreateEncaminhamentoMutation(OpenIMISMutation):
    """Create a new referral"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateEncaminhamentoMutation"

    class Input(CreateEncaminhamentoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            encaminhamento = EncaminhamentoService.create(data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdateEncaminhamentoInput(OpenIMISMutation.Input):
    """Input for updating a referral"""
    id = graphene.Int(required=True)
    status = graphene.String(required=False)
    tecnico_responsavel_id = graphene.Int(required=False)
    observacoes = graphene.String(required=False)


class UpdateEncaminhamentoMutation(OpenIMISMutation):
    """Update a referral"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateEncaminhamentoMutation"

    class Input(UpdateEncaminhamentoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            encaminhamento_id = data.pop('id')
            encaminhamento = EncaminhamentoService.update(encaminhamento_id, data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== ROOT MUTATION ==========

class Mutation(graphene.ObjectType):
    """Root Mutation for PEP+ module"""

    # Educational Module mutations
    create_modulo_educacional = CreateModuloEducacionalMutation.Field()
    update_modulo_educacional = UpdateModuloEducacionalMutation.Field()
    delete_modulo_educacional = DeleteModuloEducacionalMutation.Field()

    # Family Group mutations
    create_grupo_familiar = CreateGrupoFamiliarMutation.Field()
    update_grupo_familiar = UpdateGrupoFamiliarMutation.Field()
    delete_grupo_familiar = DeleteGrupoFamiliarMutation.Field()

    # PEP Session mutations (Ferramenta 1)
    create_sessao_pep = CreateSessaoPEPMutation.Field()
    update_sessao_pep = UpdateSessaoPEPMutation.Field()
    delete_sessao_pep = DeleteSessaoPEPMutation.Field()

    # Session Attendance mutations (Ferramenta 2)
    create_presenca_sessao = CreatePresencaSessaoMutation.Field()
    update_presenca_sessao = UpdatePresencaSessaoMutation.Field()
    delete_presenca_sessao = DeletePresencaSessaoMutation.Field()

    # Session Execution mutations (Ferramenta 3)
    create_execucao_sessao = CreateExecucaoSessaoMutation.Field()
    update_execucao_sessao = UpdateExecucaoSessaoMutation.Field()

    # Session Supervision mutations (Ferramenta 4)
    create_supervisao_sessao = CreateSupervisaoSessaoMutation.Field()
    update_supervisao_sessao = UpdateSupervisaoSessaoMutation.Field()

    # Referral mutations
    create_encaminhamento = CreateEncaminhamentoMutation.Field()
    update_encaminhamento = UpdateEncaminhamentoMutation.Field()
