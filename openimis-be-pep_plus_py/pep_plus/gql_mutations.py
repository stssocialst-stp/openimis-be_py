"""
PEP+ GraphQL Mutations
Implements CREATE, UPDATE, DELETE operations for all PEP+ entities
"""
import graphene
from core.schema import OpenIMISMutation
from .models import (
    ModuloEducacional, GrupoFamiliar, SessaoPEP, PresencaSessao,
    ExecucaoSessao, SupervisaoSessao, RelatorioDistritalBimestral,
    EncaminhamentoSessao, RoteiroReuniaoBimestral
)
from .gql_queries import (
    ModuloEducacionalGQLType, GrupoFamiliarGQLType, SessaoPEPGQLType,
    PresencaSessaoGQLType, ExecucaoSessaoGQLType, SupervisaoSessaoGQLType,
    RelatorioDistritalBimestralGQLType, EncaminhamentoSessaoGQLType,
    RoteiroReuniaoBimestralGQLType
)
from .services import (
    ModuloEducacionalService, GrupoFamiliarService, SessaoPEPService,
    PresencaSessaoService, ExecucaoSessaoService, SupervisaoSessaoService,
    RelatorioDistritalService, EncaminhamentoService, RoteiroReuniaoService
)
from .utils import convert_ids_in_session_data, decode_id


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
    distrito_id = graphene.String(required=True)
    localidade_id = graphene.String(required=False)
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
            # Convert Relay IDs and UUIDs to database IDs
            converted_data = convert_ids_in_session_data(data)
            grupo = GrupoFamiliarService.create(converted_data, user)
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
    distrito_id = graphene.String(required=False)
    localidade_id = graphene.String(required=False)
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
            # Convert Relay IDs to database IDs
            converted_data = convert_ids_in_session_data(data)
            grupo = GrupoFamiliarService.update(grupo_id, converted_data, user)
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
    data_planejamento = graphene.Date(required=True)
    coordenador_distrital_id = graphene.String(required=True)
    tecnico_social_id = graphene.String(required=True)
    distrito_id = graphene.String(required=True)
    nome_modulo = graphene.String(required=True)
    mes_modulo_anterior = graphene.String(required=False)
    dia_semana = graphene.String(required=True)
    data_sessao = graphene.Date(required=True)
    hora_sessao = graphene.Time(required=True)
    zona = graphene.String(required=True)
    numero_familias = graphene.Int(required=True)
    grupo_familia_id = graphene.String(required=True)
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
            # Convert Relay IDs to database IDs
            converted_data = convert_ids_in_session_data(data)
            sessao = SessaoPEPService.create(converted_data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdateSessaoPEPInput(OpenIMISMutation.Input):
    """Input for updating a PEP session"""
    id = graphene.Int(required=True)
    data_planejamento = graphene.Date(required=False)
    coordenador_distrital_id = graphene.String(required=False)
    tecnico_social_id = graphene.String(required=False)
    distrito_id = graphene.String(required=False)
    nome_modulo = graphene.String(required=False)
    mes_modulo_anterior = graphene.String(required=False)
    dia_semana = graphene.String(required=False)
    data_sessao = graphene.Date(required=False)
    hora_sessao = graphene.Time(required=False)
    zona = graphene.String(required=False)
    numero_familias = graphene.Int(required=False)
    grupo_familia_id = graphene.String(required=False)
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
            # Convert Relay IDs to database IDs
            converted_data = convert_ids_in_session_data(data)
            sessao = SessaoPEPService.update(sessao_id, converted_data, user)
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


class SessaoPEPInputType(graphene.InputObjectType):
    """Input type for a single session in bulk creation"""
    codigo_sessao = graphene.String(required=True)
    data_planejamento = graphene.Date(required=True)
    coordenador_distrital_id = graphene.String(required=True)
    tecnico_social_id = graphene.String(required=True)
    distrito_id = graphene.String(required=True)
    nome_modulo = graphene.String(required=True)
    mes_modulo_anterior = graphene.String(required=False)
    dia_semana = graphene.String(required=True)
    data_sessao = graphene.Date(required=True)
    hora_sessao = graphene.Time(required=True)
    zona = graphene.String(required=True)
    numero_familias = graphene.Int(required=True)
    grupo_familia_id = graphene.String(required=True)
    tempo_deslocamento = graphene.Int(required=False)
    feedback_documentacao = graphene.String(required=True)
    tem_supervisao = graphene.Boolean(required=False)
    observacoes = graphene.String(required=False)
    status = graphene.String(required=False)


class CreateMultipleSessoesPEPMutation(OpenIMISMutation):
    """Create multiple PEP sessions at once"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateMultipleSessoesPEPMutation"

    class Input(OpenIMISMutation.Input):
        sessions = graphene.List(graphene.NonNull(SessaoPEPInputType), required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            sessions_list = [dict(session) for session in data.get('sessions', [])]
            # Convert Relay IDs to database IDs for each session
            converted_sessions = [convert_ids_in_session_data(session) for session in sessions_list]
            sessoes = SessaoPEPService.create_multiple(converted_sessions, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class SessaoPEPUpdateInputType(graphene.InputObjectType):
    """Input type for a single session in bulk update"""
    id = graphene.Int(required=True)
    codigo_sessao = graphene.String(required=False)
    data_planejamento = graphene.Date(required=False)
    coordenador_distrital_id = graphene.String(required=False)
    tecnico_social_id = graphene.String(required=False)
    distrito_id = graphene.String(required=False)
    nome_modulo = graphene.String(required=False)
    mes_modulo_anterior = graphene.String(required=False)
    dia_semana = graphene.String(required=False)
    data_sessao = graphene.Date(required=False)
    hora_sessao = graphene.Time(required=False)
    zona = graphene.String(required=False)
    numero_familias = graphene.Int(required=False)
    grupo_familia_id = graphene.String(required=False)
    tempo_deslocamento = graphene.Int(required=False)
    feedback_documentacao = graphene.String(required=False)
    tem_supervisao = graphene.Boolean(required=False)
    observacoes = graphene.String(required=False)
    status = graphene.String(required=False)


class UpdateMultipleSessoesPEPMutation(OpenIMISMutation):
    """Update multiple PEP sessions at once"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateMultipleSessoesPEPMutation"

    class Input(OpenIMISMutation.Input):
        sessions = graphene.List(graphene.NonNull(SessaoPEPUpdateInputType), required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            sessions_list = [dict(session) for session in data.get('sessions', [])]
            # Convert Relay IDs to database IDs for each session
            converted_sessions = [convert_ids_in_session_data(session) for session in sessions_list]
            sessoes = SessaoPEPService.update_multiple(converted_sessions, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== SESSION ATTENDANCE MUTATIONS (Ferramenta 2) ==========

class CreatePresencaSessaoInput(OpenIMISMutation.Input):
    """Input for creating an attendance record"""
    sessao_id = graphene.String(required=True)
    familia_id = graphene.String(required=True)
    nome_familia = graphene.String(required=False)
    grupo_id = graphene.String(required=False)
    estado = graphene.String(required=False)
    codigo_encaminhamento = graphene.String(required=False)
    nome_instituicao = graphene.String(required=False)
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
            # Convert Relay IDs and UUIDs to database IDs
            converted_data = convert_ids_in_session_data(data)
            presenca = PresencaSessaoService.create(converted_data, user)
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
    nome_instituicao = graphene.String(required=False)
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


# Batch mutation for registering attendance with session details
class PresencaItemInput(graphene.InputObjectType):
    """Input for a single family attendance record"""
    familia_id = graphene.String(required=True)
    estado = graphene.String(required=True)  # PRES, FALT, ENCA
    codigo_encaminhamento = graphene.String(required=False)
    nome_instituicao = graphene.String(required=False)


class RegistrarPresencasBatchInput(OpenIMISMutation.Input):
    """Input for batch attendance registration with session details (Ferramenta 2)"""
    # Detalhes da sessão
    sessao_id = graphene.String(required=True)
    data_sessao = graphene.Date(required=True)
    distrito_id = graphene.String(required=True)
    formador_id = graphene.String(required=True)
    localidade_id = graphene.String(required=False)
    nome_modulo = graphene.String(required=True)
    mes_modulo_anterior = graphene.String(required=False)
    codigo_sessao = graphene.String(required=True)
    grupo_familia_id = graphene.String(required=True)

    # Array de presenças
    presencas = graphene.List(PresencaItemInput, required=True)


class RegistrarPresencasBatchMutation(OpenIMISMutation):
    """Batch register attendance records with session details (Ferramenta 2)"""
    _mutation_module = "pep_plus"
    _mutation_class = "RegistrarPresencasBatchMutation"

    class Input(RegistrarPresencasBatchInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            from .services import PresencaSessaoService
            # Convert Relay IDs to database IDs
            converted_data = convert_ids_in_session_data(data)
            result = PresencaSessaoService.registrar_presencas_batch(converted_data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== SESSION EXECUTION MUTATIONS (Ferramenta 3) ==========

class CreateExecucaoSessaoInput(OpenIMISMutation.Input):
    """Input for creating a session execution record (Ferramenta 3)"""
    # Detalhes do planejamento da sessão
    sessao_id = graphene.String(required=True)
    formador_id = graphene.String(required=True)
    supervisor_id = graphene.String(required=False)
    localidade_id = graphene.String(required=False)

    # Detalhes da execução
    numero_cuidadores = graphene.String(required=False)  # Opções: "0", "1-5", "6-10", "15+"

    # Práticas positivas: [{ descricao: "...", confirmacao: "Sim/Não/N/A" }]
    praticas_positivas = graphene.JSONString(required=False)
    outras_praticas_positivas = graphene.String(required=False)

    # Desafios: [{ descricao: "...", confirmacao: "Sim/Não/N/A" }]
    desafios_transmissao = graphene.JSONString(required=False)
    outros_desafios = graphene.String(required=False)

    necessita_encaminhamento = graphene.Boolean(required=False)

    # Auto-avaliação: [{ descricao: "...", avaliacao: "1/2/3/4/5" }]
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
            # Convert Relay IDs
            data = convert_ids_in_session_data(data)
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

    # Detalhes da execução
    numero_cuidadores = graphene.String(required=False)  # Opções: "0", "1-5", "6-10", "15+"

    # Práticas positivas
    praticas_positivas = graphene.JSONString(required=False)
    outras_praticas_positivas = graphene.String(required=False)

    # Desafios
    desafios_transmissao = graphene.JSONString(required=False)
    outros_desafios = graphene.String(required=False)

    necessita_encaminhamento = graphene.Boolean(required=False)

    # Auto-avaliação
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
    """Input for creating a supervision record (Ferramenta 4)"""
    # Detalhes da sessão
    sessao_id = graphene.String(required=True)
    supervisor_id = graphene.String(required=True)
    formador_id = graphene.String(required=True)
    localidade_id = graphene.String(required=False)
    grupo_id = graphene.String(required=False)
    data_supervisao = graphene.Date(required=True)
    data_modulo_anterior = graphene.Date(required=False)
    identificador_grupo = graphene.String(required=True)

    # Detalhes da observação
    numero_participantes = graphene.String(required=False)  # Opções: "0", "1-5", "6-10", "15+"

    # Práticas positivas e estratégias: [{ descricao: "...", confirmacao: "Sim/Não/N/A" }]
    praticas_positivas_estrategias = graphene.JSONString(required=False)

    # Desafios: [{ descricao: "...", confirmacao: "Sim/Não/N/A" }]
    desafios_transmissao = graphene.JSONString(required=False)

    necessita_encaminhamento = graphene.Boolean(required=False)

    # Auto-avaliação: [{ descricao: "...", confirmacao: boolean }]
    auto_avaliacao_pontos_fortes = graphene.JSONString(required=False)
    auto_avaliacao_pontos_atencao = graphene.JSONString(required=False)

    # Avaliação da execução dos passos da metodologia: [{ descricao: "...", confirmacao: "Não fez/Não adequado/Adequado/Excelente/N/A" }]
    avaliacao_execucao_metodologia = graphene.JSONString(required=False)

    # Novos campos de feedback
    metodologia_passos = graphene.JSONString(required=False)
    feedback_pontos_fortes = graphene.String(required=False)
    feedback_desafios = graphene.String(required=False)
    compromisso_formador = graphene.String(required=False)

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
            # Convert Relay IDs
            data = convert_ids_in_session_data(data)
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

    # Detalhes da observação
    numero_participantes = graphene.String(required=False)  # Opções: "0", "1-5", "6-10", "15+"

    # Práticas positivas e estratégias
    praticas_positivas_estrategias = graphene.JSONString(required=False)

    # Desafios
    desafios_transmissao = graphene.JSONString(required=False)

    necessita_encaminhamento = graphene.Boolean(required=False)

    # Auto-avaliação
    auto_avaliacao_pontos_fortes = graphene.JSONString(required=False)
    auto_avaliacao_pontos_atencao = graphene.JSONString(required=False)

    # Avaliação da execução dos passos da metodologia
    avaliacao_execucao_metodologia = graphene.JSONString(required=False)

    # Novos campos de feedback
    metodologia_passos = graphene.JSONString(required=False)
    feedback_pontos_fortes = graphene.String(required=False)
    feedback_desafios = graphene.String(required=False)
    compromisso_formador = graphene.String(required=False)

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


# ========== RELATORIO DISTRITAL BIMESTRAL MUTATIONS (Ferramenta 5) ==========

class CreateRelatorioDistritalInput(OpenIMISMutation.Input):
    """Input for creating a district bimonthly report (Ferramenta 5)"""
    # Identificação
    distrito_id = graphene.String(required=True)
    coordenador_distrital_id = graphene.String(required=True)
    tecnico_administrativo_id = graphene.String(required=False)

    # Período
    periodo = graphene.String(required=True)  # BIM1, BIM2, BIM3, BIM4, BIM5, BIM6
    ano = graphene.Int(required=True)
    periodo_inicio = graphene.Date(required=True)
    periodo_fim = graphene.Date(required=True)

    # Estatísticas gerais
    numero_localidades_atendidas = graphene.Int(required=True)
    numero_familias_atendidas = graphene.Int(required=True)
    numero_tecnicos_formadores = graphene.Int(required=True)
    numero_sessoes_conduzidas = graphene.Int(required=True)
    numero_sessoes_esperadas = graphene.Int(required=True)
    numero_familias_presentes = graphene.Int(required=True)
    numero_familias_esperadas = graphene.Int(required=True)
    numero_familias_migraram = graphene.Int(required=True)
    numero_sessoes_perdidas = graphene.Int(required=True)

    # Percentuais calculados (opcionais)
    percentual_sessoes = graphene.Float(required=False)
    percentual_familias = graphene.Float(required=False)
    media_familia_presente = graphene.Float(required=False)
    media_familia_esperada = graphene.Float(required=False)

    # Tabela de dados por técnico
    # [{ tecnicoFormador, sessoesExecutadas, sessoesPerdidas, modulos,
    #    familiasPresentes, familiasMigraram, naoCompareceram2Sessoes, naoCompareceram1Sessao }]
    dados_tecnicos = graphene.JSONString(required=False)

    # Dados de encaminhamentos (opcional)
    dados_encaminhamentos = graphene.JSONString(required=False)

    # Observações
    observacoes = graphene.String(required=False)


class CreateRelatorioDistritalMutation(OpenIMISMutation):
    """Create a new district bimonthly report"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateRelatorioDistritalMutation"

    class Input(CreateRelatorioDistritalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Convert Relay IDs
            data = convert_ids_in_session_data(data)
            relatorio = RelatorioDistritalService.create(data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdateRelatorioDistritalInput(OpenIMISMutation.Input):
    """Input for updating a district bimonthly report"""
    id = graphene.Int(required=True)

    # Estatísticas gerais
    numero_localidades_atendidas = graphene.Int(required=False)
    numero_familias_atendidas = graphene.Int(required=False)
    numero_tecnicos_formadores = graphene.Int(required=False)
    numero_sessoes_conduzidas = graphene.Int(required=False)
    numero_sessoes_esperadas = graphene.Int(required=False)
    numero_familias_presentes = graphene.Int(required=False)
    numero_familias_esperadas = graphene.Int(required=False)
    numero_familias_migraram = graphene.Int(required=False)
    numero_sessoes_perdidas = graphene.Int(required=False)

    # Percentuais calculados
    percentual_sessoes = graphene.Float(required=False)
    percentual_familias = graphene.Float(required=False)
    media_familia_presente = graphene.Float(required=False)
    media_familia_esperada = graphene.Float(required=False)

    # Tabela de dados por técnico
    dados_tecnicos = graphene.JSONString(required=False)

    # Dados de encaminhamentos
    dados_encaminhamentos = graphene.JSONString(required=False)

    # Observações
    observacoes = graphene.String(required=False)


class UpdateRelatorioDistritalMutation(OpenIMISMutation):
    """Update a district bimonthly report"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateRelatorioDistritalMutation"

    class Input(UpdateRelatorioDistritalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            relatorio_id = data.pop('id')
            relatorio = RelatorioDistritalService.update(relatorio_id, data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class DeleteRelatorioDistritalInput(OpenIMISMutation.Input):
    """Input for deleting a district bimonthly report"""
    id = graphene.Int(required=True)


class DeleteRelatorioDistritalMutation(OpenIMISMutation):
    """Delete a district bimonthly report (soft delete)"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteRelatorioDistritalMutation"

    class Input(DeleteRelatorioDistritalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            RelatorioDistritalService.delete(data['id'], user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== ENCAMINHAMENTO MUTATIONS ==========

class CreateEncaminhamentoInput(OpenIMISMutation.Input):
    """Input for creating a referral"""
    sessao_id = graphene.String(required=True)
    familia_id = graphene.String(required=True)
    nome_familia = graphene.String(required=True)
    codigo_encaminhamento = graphene.String(required=True)
    descricao = graphene.String(required=True)
    status = graphene.String(required=False)
    tecnico_responsavel_id = graphene.String(required=False)
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
            # Convert Relay IDs
            data = convert_ids_in_session_data(data)
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
    tecnico_responsavel_id = graphene.String(required=False)
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
            # Convert Relay IDs to database IDs
            converted_data = convert_ids_in_session_data(data)
            encaminhamento = EncaminhamentoService.update(encaminhamento_id, converted_data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== BIMONTHLY MEETING AGENDA MUTATIONS (Ferramenta 6) ==========

class CreateRoteiroReuniaoInput(OpenIMISMutation.Input):
    """Input for creating a bimonthly meeting agenda (Ferramenta 6)"""
    data_reuniao = graphene.Date(required=True)
    horario = graphene.Time(required=True)
    coordenador_nacional_id = graphene.String(required=True)
    participantes = graphene.JSONString(required=False)  # Array de user IDs
    principais_desafios = graphene.String(required=False)
    oportunidades_melhoria = graphene.String(required=False)
    apreciacao_relatorios = graphene.String(required=False)
    plano_acao = graphene.String(required=False)
    proxima_reuniao = graphene.String(required=False)
    data_proxima_reuniao = graphene.Date(required=False)


class CreateRoteiroReuniaoMutation(OpenIMISMutation):
    """Create a new bimonthly meeting agenda"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateRoteiroReuniaoMutation"

    class Input(CreateRoteiroReuniaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Convert Relay IDs
            data = convert_ids_in_session_data(data)
            roteiro = RoteiroReuniaoService.create(data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdateRoteiroReuniaoInput(OpenIMISMutation.Input):
    """Input for updating a bimonthly meeting agenda (Ferramenta 6)"""
    id = graphene.Int(required=True)
    data_reuniao = graphene.Date(required=False)
    horario = graphene.Time(required=False)
    coordenador_nacional_id = graphene.String(required=False)
    participantes = graphene.JSONString(required=False)
    principais_desafios = graphene.String(required=False)
    oportunidades_melhoria = graphene.String(required=False)
    apreciacao_relatorios = graphene.String(required=False)
    plano_acao = graphene.String(required=False)
    proxima_reuniao = graphene.String(required=False)
    data_proxima_reuniao = graphene.Date(required=False)


class UpdateRoteiroReuniaoMutation(OpenIMISMutation):
    """Update a bimonthly meeting agenda"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateRoteiroReuniaoMutation"

    class Input(UpdateRoteiroReuniaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            roteiro_id = data.pop('id')
            # Convert Relay IDs
            data = convert_ids_in_session_data(data)
            roteiro = RoteiroReuniaoService.update(roteiro_id, data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class DeleteRoteiroReuniaoMutation(OpenIMISMutation):
    """Delete a bimonthly meeting agenda"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteRoteiroReuniaoMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.Int(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            RoteiroReuniaoService.delete(data['id'], user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


# ========== SUPERVISION REPORT MUTATIONS (FERRAMENTA 7) ==========

class CreateRelatorioSupervisaoInput(OpenIMISMutation.Input):
    """Input for creating a bimonthly supervision report (Ferramenta 7)"""
    supervisores = graphene.JSONString(required=False)  # Array de user IDs
    numero_sessoes = graphene.Int(required=True)
    numero_tecnicos_formadores = graphene.Int(required=True)
    distrito_id = graphene.String(required=True)
    periodo = graphene.String(required=True)  # Choices: JAN_FEV, MAR_ABR, etc.
    ano = graphene.Int(required=True)
    avaliacoes_tecnicos = graphene.JSONString(required=False)  # Array: [{idDoTecnico, pontosPositivos, pontosAprimorar}]
    sessoes_pep = graphene.JSONString(required=False)  # Array: [{passo, nota}]
    modulos_dificuldade = graphene.JSONString(required=False)  # Array: [{modulo, selected}]
    observacoes = graphene.String(required=False)


class CreateRelatorioSupervisaoMutation(OpenIMISMutation):
    """Create a new bimonthly supervision report"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateRelatorioSupervisaoMutation"

    class Input(CreateRelatorioSupervisaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            from .services import RelatorioSupervisaoService
            # Convert Relay IDs to database IDs
            converted_data = convert_ids_in_session_data(data)
            relatorio = RelatorioSupervisaoService.create(converted_data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class UpdateRelatorioSupervisaoInput(OpenIMISMutation.Input):
    """Input for updating a bimonthly supervision report (Ferramenta 7)"""
    id = graphene.Int(required=True)
    supervisores = graphene.JSONString(required=False)
    numero_sessoes = graphene.Int(required=False)
    numero_tecnicos_formadores = graphene.Int(required=False)
    distrito_id = graphene.String(required=False)
    periodo = graphene.String(required=False)
    ano = graphene.Int(required=False)
    avaliacoes_tecnicos = graphene.JSONString(required=False)
    sessoes_pep = graphene.JSONString(required=False)
    modulos_dificuldade = graphene.JSONString(required=False)
    observacoes = graphene.String(required=False)


class UpdateRelatorioSupervisaoMutation(OpenIMISMutation):
    """Update an existing bimonthly supervision report"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateRelatorioSupervisaoMutation"

    class Input(UpdateRelatorioSupervisaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            from .services import RelatorioSupervisaoService
            # Convert Relay IDs to database IDs
            converted_data = convert_ids_in_session_data(data)
            relatorio = RelatorioSupervisaoService.update(converted_data, user)
            return None
        except Exception as exc:
            return [{
                'message': str(exc),
                'detail': str(exc)
            }]


class DeleteRelatorioSupervisaoInput(OpenIMISMutation.Input):
    """Input for deleting a bimonthly supervision report"""
    id = graphene.Int(required=True)


class DeleteRelatorioSupervisaoMutation(OpenIMISMutation):
    """Delete (soft delete) a bimonthly supervision report"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteRelatorioSupervisaoMutation"

    class Input(DeleteRelatorioSupervisaoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            from .services import RelatorioSupervisaoService
            RelatorioSupervisaoService.delete(data['id'], user)
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
    create_multiple_sessoes_pep = CreateMultipleSessoesPEPMutation.Field()
    update_sessao_pep = UpdateSessaoPEPMutation.Field()
    update_multiple_sessoes_pep = UpdateMultipleSessoesPEPMutation.Field()
    delete_sessao_pep = DeleteSessaoPEPMutation.Field()

    # Session Attendance mutations (Ferramenta 2)
    create_presenca_sessao = CreatePresencaSessaoMutation.Field()
    update_presenca_sessao = UpdatePresencaSessaoMutation.Field()
    delete_presenca_sessao = DeletePresencaSessaoMutation.Field()
    registrar_presencas_batch = RegistrarPresencasBatchMutation.Field()

    # Session Execution mutations (Ferramenta 3)
    create_execucao_sessao = CreateExecucaoSessaoMutation.Field()
    update_execucao_sessao = UpdateExecucaoSessaoMutation.Field()

    # Session Supervision mutations (Ferramenta 4)
    create_supervisao_sessao = CreateSupervisaoSessaoMutation.Field()
    update_supervisao_sessao = UpdateSupervisaoSessaoMutation.Field()

    # District Bimonthly Report mutations (Ferramenta 5)
    create_relatorio_distrital = CreateRelatorioDistritalMutation.Field()
    update_relatorio_distrital = UpdateRelatorioDistritalMutation.Field()
    delete_relatorio_distrital = DeleteRelatorioDistritalMutation.Field()

    # Referral mutations
    create_encaminhamento = CreateEncaminhamentoMutation.Field()
    update_encaminhamento = UpdateEncaminhamentoMutation.Field()

    # Bimonthly Meeting Agenda mutations (Ferramenta 6)
    create_roteiro_reuniao = CreateRoteiroReuniaoMutation.Field()
    update_roteiro_reuniao = UpdateRoteiroReuniaoMutation.Field()
    delete_roteiro_reuniao = DeleteRoteiroReuniaoMutation.Field()

    # Bimonthly Supervision Report mutations (Ferramenta 7)
    create_relatorio_supervisao = CreateRelatorioSupervisaoMutation.Field()
    update_relatorio_supervisao = UpdateRelatorioSupervisaoMutation.Field()
    delete_relatorio_supervisao = DeleteRelatorioSupervisaoMutation.Field()
