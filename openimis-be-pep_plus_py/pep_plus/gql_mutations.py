"""
PEP+ GraphQL Mutations
Implements CREATE, UPDATE, DELETE operations for all PEP+ entities
"""
import logging
import graphene
from core.schema import OpenIMISMutation

logger = logging.getLogger(__name__)
from .models import (
    ModuloPEP, Escola, Classe, Disciplina, TipoEncaminhamento,
    Aluno, ModuloEducacional, GrupoFamiliar, SessaoPEP, PresencaSessao,
    ExecucaoSessao, SupervisaoSessao,
    RelatorioDistritalBimestral, RelatorioDistEncaminhamento,
    EncaminhamentoSessao, RoteiroReuniaoBimestral,
    CoordenacaoDistrital, CoordenacaoDistritalTecnico
)
from .gql_queries import (
    ModuloPEPGQLType, EscolaGQLType, ClasseGQLType, DisciplinaGQLType, TipoEncaminhamentoGQLType,
    AlunoGQLType, ModuloEducacionalGQLType, GrupoFamiliarGQLType, SessaoPEPGQLType,
    PresencaSessaoGQLType, ExecucaoSessaoGQLType, SupervisaoSessaoGQLType,
    RelatorioDistritalBimestralGQLType, RelatorioDistEncaminhamentoGQLType,
    EncaminhamentoSessaoGQLType,
    RoteiroReuniaoBimestralGQLType, CoordenacaoDistritalGQLType
)
from .services import (
    ModuloPEPService, EscolaService, ClasseService, DisciplinaService, TipoEncaminhamentoService,
    AlunoService, ModuloEducacionalService, GrupoFamiliarService, SessaoPEPService,
    PresencaSessaoService, ExecucaoSessaoService, SupervisaoSessaoService,
    RelatorioDistritalService, EncaminhamentoService, RoteiroReuniaoService,
    CoordenacaoDistritalService, RelatorioDistEncaminhamentoService
)
from .utils import convert_ids_in_session_data, decode_id


# =============================================================================
# PARAMETRIZAÇÃO: MODULO PEP MUTATIONS
# =============================================================================

class CreateModuloPEPInput(OpenIMISMutation.Input):
    """Input for creating a ModuloPEP record"""
    codigo = graphene.String(required=True)
    nome = graphene.String(required=True)
    descricao = graphene.String(required=False)
    ordem = graphene.Int(required=False)
    duracao_semanas = graphene.Int(required=False)
    ativo = graphene.Boolean(required=False)


class CreateModuloPEPMutation(OpenIMISMutation):
    """Create a new ModuloPEP"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateModuloPEPMutation"

    class Input(CreateModuloPEPInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            modulo = ModuloPEPService.create(data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateModuloPEPInput(OpenIMISMutation.Input):
    """Input for updating a ModuloPEP record"""
    id = graphene.String(required=True)
    codigo = graphene.String(required=False)
    nome = graphene.String(required=False)
    descricao = graphene.String(required=False)
    ordem = graphene.Int(required=False)
    duracao_semanas = graphene.Int(required=False)
    ativo = graphene.Boolean(required=False)


class UpdateModuloPEPMutation(OpenIMISMutation):
    """Update an existing ModuloPEP"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateModuloPEPMutation"

    class Input(UpdateModuloPEPInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            modulo_id = decode_id(data.pop('id'))
            ModuloPEPService.update(modulo_id, data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteModuloPEPMutation(OpenIMISMutation):
    """Delete (soft delete) a ModuloPEP"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteModuloPEPMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            ModuloPEPService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# PARAMETRIZAÇÃO: ESCOLA MUTATIONS
# =============================================================================

class CreateEscolaInput(OpenIMISMutation.Input):
    """Input for creating an Escola record"""
    nome = graphene.String(required=True)
    codigo = graphene.String(required=False)
    nivel = graphene.String(required=False)
    distrito_id = graphene.String(required=False)
    localidade_id = graphene.String(required=False)
    ativo = graphene.Boolean(required=False)


class CreateEscolaMutation(OpenIMISMutation):
    """Create a new Escola"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateEscolaMutation"

    class Input(CreateEscolaInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            converted_data = convert_ids_in_session_data(data)
            EscolaService.create(converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateEscolaInput(OpenIMISMutation.Input):
    """Input for updating an Escola record"""
    id = graphene.String(required=True)
    nome = graphene.String(required=False)
    codigo = graphene.String(required=False)
    nivel = graphene.String(required=False)
    distrito_id = graphene.String(required=False)
    localidade_id = graphene.String(required=False)
    ativo = graphene.Boolean(required=False)


class UpdateEscolaMutation(OpenIMISMutation):
    """Update an existing Escola"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateEscolaMutation"

    class Input(UpdateEscolaInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            escola_id = decode_id(data.pop('id'))
            converted_data = convert_ids_in_session_data(data)
            EscolaService.update(escola_id, converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteEscolaMutation(OpenIMISMutation):
    """Delete (soft delete) an Escola"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteEscolaMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            EscolaService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# PARAMETRIZAÇÃO: CLASSE MUTATIONS
# =============================================================================

class CreateClasseInput(OpenIMISMutation.Input):
    """Input for creating a Classe record"""
    nome = graphene.String(required=True)
    codigo = graphene.String(required=True)
    nivel = graphene.String(required=False)   # EP1, EP2, ESG1, ESG2, OUTRO
    ordem = graphene.Int(required=False)
    ativo = graphene.Boolean(required=False)
    # IDs das disciplinas associadas a esta classe (M2M)
    disciplinas_ids = graphene.List(graphene.String, required=False)


class CreateClasseMutation(OpenIMISMutation):
    """Create a new Classe"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateClasseMutation"

    class Input(CreateClasseInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            converted_data = convert_ids_in_session_data(data)
            ClasseService.create(converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateClasseInput(OpenIMISMutation.Input):
    """Input for updating a Classe record"""
    id = graphene.String(required=True)
    nome = graphene.String(required=False)
    codigo = graphene.String(required=False)
    nivel = graphene.String(required=False)
    ordem = graphene.Int(required=False)
    ativo = graphene.Boolean(required=False)
    disciplinas_ids = graphene.List(graphene.String, required=False)


class UpdateClasseMutation(OpenIMISMutation):
    """Update an existing Classe"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateClasseMutation"

    class Input(UpdateClasseInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            classe_id = decode_id(data.pop('id'))
            converted_data = convert_ids_in_session_data(data)
            ClasseService.update(classe_id, converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteClasseMutation(OpenIMISMutation):
    """Delete (soft delete) a Classe"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteClasseMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            ClasseService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# PARAMETRIZAÇÃO: DISCIPLINA MUTATIONS
# =============================================================================

class CreateDisciplinaInput(OpenIMISMutation.Input):
    """Input for creating a Disciplina record"""
    nome = graphene.String(required=True)
    nivel = graphene.String(required=True)   # BASICA ou AVANCADA
    ativo = graphene.Boolean(required=False)
    faixa_faltas_aceitaveis = graphene.String(required=False)   # 1-3, 4-6, 7-10, +10
    quantidade_faltas_aceitaveis = graphene.Int(required=False)


class CreateDisciplinaMutation(OpenIMISMutation):
    """Create a new Disciplina"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateDisciplinaMutation"

    class Input(CreateDisciplinaInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            DisciplinaService.create(data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateDisciplinaInput(OpenIMISMutation.Input):
    """Input for updating a Disciplina record"""
    id = graphene.String(required=True)
    nome = graphene.String(required=False)
    nivel = graphene.String(required=False)
    ativo = graphene.Boolean(required=False)
    faixa_faltas_aceitaveis = graphene.String(required=False)
    quantidade_faltas_aceitaveis = graphene.Int(required=False)


class UpdateDisciplinaMutation(OpenIMISMutation):
    """Update an existing Disciplina"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateDisciplinaMutation"

    class Input(UpdateDisciplinaInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            disciplina_id = decode_id(data.pop('id'))
            DisciplinaService.update(disciplina_id, data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteDisciplinaMutation(OpenIMISMutation):
    """Delete (soft delete) a Disciplina"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteDisciplinaMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            DisciplinaService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# PARAMETRIZAÇÃO: TIPO ENCAMINHAMENTO MUTATIONS
# =============================================================================

class CreateTipoEncaminhamentoInput(OpenIMISMutation.Input):
    """Input for creating a TipoEncaminhamento record"""
    codigo = graphene.String(required=True)
    nome = graphene.String(required=True)
    descricao = graphene.String(required=False)
    ativo = graphene.Boolean(required=False)


class CreateTipoEncaminhamentoMutation(OpenIMISMutation):
    """Create a new TipoEncaminhamento"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateTipoEncaminhamentoMutation"

    class Input(CreateTipoEncaminhamentoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            TipoEncaminhamentoService.create(data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateTipoEncaminhamentoInput(OpenIMISMutation.Input):
    """Input for updating a TipoEncaminhamento record"""
    id = graphene.String(required=True)
    codigo = graphene.String(required=False)
    nome = graphene.String(required=False)
    descricao = graphene.String(required=False)
    ativo = graphene.Boolean(required=False)


class UpdateTipoEncaminhamentoMutation(OpenIMISMutation):
    """Update an existing TipoEncaminhamento"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateTipoEncaminhamentoMutation"

    class Input(UpdateTipoEncaminhamentoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            tipo_id = decode_id(data.pop('id'))
            TipoEncaminhamentoService.update(tipo_id, data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteTipoEncaminhamentoMutation(OpenIMISMutation):
    """Delete (soft delete) a TipoEncaminhamento"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteTipoEncaminhamentoMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            TipoEncaminhamentoService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# EDUCATIONAL MODULE MUTATIONS
# =============================================================================

class FaixaDeFaltasEnum(graphene.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class CreateModuloEducacionalInput(OpenIMISMutation.Input):
    """Input for creating school attendance record (Assiduidade Escolar)"""
    ano_registo = graphene.Int(required=False, description="Ano lectivo do registo (ex: 2026). Se omitido, usa o ano actual.")

    # Ligação ao perfil centralizado do Aluno (opcional)
    aluno_id = graphene.String(required=False, description="Relay ID do Aluno criado via createAluno")

    # Identificação
    id_membro_crianca = graphene.String(required=False)
    nome = graphene.String(required=True)
    nome_encarregado = graphene.String(required=False)

    # Dados escolares (FKs para tabelas parametrizadas)
    escola_id = graphene.String(required=False)
    escolaridade_actual = graphene.String(required=False)
    data_nascimento = graphene.Date(required=False)
    id_da_crianca = graphene.String(required=False)
    sexo = graphene.String(required=False)  # M, F, I
    dados_escolar_correctos = graphene.Boolean(required=False)
    escola_actual_id = graphene.String(required=False)
    classe_id = graphene.String(required=False)          # FK para Classe (substituiu classe: String)
    idade = graphene.Int(required=False)
    dados_escolares_correctos = graphene.Boolean(required=False)

    # Localização (JSON)
    informacoes_localizacao = graphene.JSONString(required=False)

    # Frequência escolar
    classe_que_frequenta_id = graphene.String(required=False)  # FK para Classe (substituiu classe_que_frequenta: String)
    aproveitamento_primeiro_trimestre = graphene.String(required=False)
    faixa_de_faltas = graphene.Field(FaixaDeFaltasEnum, required=False)

    # Disciplinas (lista de IDs de Disciplina)
    disciplinas_ids = graphene.List(graphene.String, required=False)

    # Observações
    observacoes = graphene.String(required=False)


class CreateModuloEducacionalMutation(OpenIMISMutation):
    """Create a new school attendance record (Assiduidade Escolar)"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateModuloEducacionalMutation"

    class Input(CreateModuloEducacionalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            print(f"[PEP+] CreateModuloEducacional: Iniciando criação para user={user.id if user else 'None'}")
            print(f"[PEP+] CreateModuloEducacional: Dados recebidos: {data}")
            logger.info(f"[PEP+] CreateModuloEducacional: Iniciando criação para user={user.id if user else 'None'}")

            converted_data = convert_ids_in_session_data(data)
            modulo = ModuloEducacionalService.create(converted_data, user)

            print(f"[PEP+] CreateModuloEducacional: SUCESSO - ID={modulo.id}, UUID={modulo.uuid}, nome={modulo.nome}")
            logger.info(f"[PEP+] CreateModuloEducacional: SUCESSO - Registo criado com ID={modulo.id}, UUID={modulo.uuid}")
            return None
        except Exception as exc:
            print(f"[PEP+] CreateModuloEducacional: ERRO - {str(exc)}")
            logger.error(f"[PEP+] CreateModuloEducacional: ERRO - {str(exc)}")
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateModuloEducacionalInput(OpenIMISMutation.Input):
    """Input for updating school attendance record (Assiduidade Escolar)"""
    id = graphene.String(required=True)

    ano_registo = graphene.Int(required=False, description="Ano lectivo do registo (ex: 2026)")

    # Ligação ao perfil centralizado do Aluno (opcional)
    aluno_id = graphene.String(required=False, description="Relay ID do Aluno criado via createAluno")

    # Identificação
    id_membro_crianca = graphene.String(required=False)
    nome = graphene.String(required=False)
    nome_encarregado = graphene.String(required=False)

    # Dados escolares
    escola_id = graphene.String(required=False)
    escolaridade_actual = graphene.String(required=False)
    data_nascimento = graphene.Date(required=False)
    id_da_crianca = graphene.String(required=False)
    sexo = graphene.String(required=False)
    dados_escolar_correctos = graphene.Boolean(required=False)
    escola_actual_id = graphene.String(required=False)
    classe_id = graphene.String(required=False)              # FK para Classe
    idade = graphene.Int(required=False)
    dados_escolares_correctos = graphene.Boolean(required=False)

    # Localização (JSON)
    informacoes_localizacao = graphene.JSONString(required=False)

    # Frequência escolar
    classe_que_frequenta_id = graphene.String(required=False)  # FK para Classe
    aproveitamento_primeiro_trimestre = graphene.String(required=False)
    faixa_de_faltas = graphene.Field(FaixaDeFaltasEnum, required=False)

    # Disciplinas (lista de IDs de Disciplina — substitui tudo)
    disciplinas_ids = graphene.List(graphene.String, required=False)

    # Observações
    observacoes = graphene.String(required=False)


class UpdateModuloEducacionalMutation(OpenIMISMutation):
    """Update a school attendance record (Assiduidade Escolar)"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateModuloEducacionalMutation"

    class Input(UpdateModuloEducacionalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            print(f"[PEP+] UpdateModuloEducacional: Iniciando atualização para user={user.id if user else 'None'}")
            print(f"[PEP+] UpdateModuloEducacional: Dados recebidos: {data}")

            modulo_id = decode_id(data.pop('id'))
            print(f"[PEP+] UpdateModuloEducacional: ID decodificado: {modulo_id}")

            converted_data = convert_ids_in_session_data(data)
            modulo = ModuloEducacionalService.update(modulo_id, converted_data, user)

            print(f"[PEP+] UpdateModuloEducacional: SUCESSO - ID={modulo.id}, nome={modulo.nome}")
            return None
        except Exception as exc:
            print(f"[PEP+] UpdateModuloEducacional: ERRO - {str(exc)}")
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteModuloEducacionalMutation(OpenIMISMutation):
    """Delete a school attendance record (Assiduidade Escolar)"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteModuloEducacionalMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            print(f"[PEP+] DeleteModuloEducacional: Iniciando exclusão para user={user.id if user else 'None'}")
            print(f"[PEP+] DeleteModuloEducacional: ID recebido: {data.get('id')}")

            modulo_id = decode_id(data['id'])
            print(f"[PEP+] DeleteModuloEducacional: ID decodificado: {modulo_id}")

            ModuloEducacionalService.delete(modulo_id, user)

            print(f"[PEP+] DeleteModuloEducacional: SUCESSO - ID={modulo_id}")
            return None
        except Exception as exc:
            print(f"[PEP+] DeleteModuloEducacional: ERRO - {str(exc)}")
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# FAMILY GROUP MUTATIONS
# =============================================================================

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
            converted_data = convert_ids_in_session_data(data)
            GrupoFamiliarService.create(converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateGrupoFamiliarInput(OpenIMISMutation.Input):
    """Input for updating a family group"""
    id = graphene.String(required=True)
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
            grupo_id = decode_id(data.pop('id'))
            converted_data = convert_ids_in_session_data(data)
            GrupoFamiliarService.update(grupo_id, converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteGrupoFamiliarMutation(OpenIMISMutation):
    """Delete a family group"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteGrupoFamiliarMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            GrupoFamiliarService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# PEP SESSION MUTATIONS (Ferramenta 1)
# =============================================================================

class CreateSessaoPEPInput(OpenIMISMutation.Input):
    """Input for creating a PEP session"""
    codigo_sessao = graphene.String(required=True)
    data_planejamento = graphene.Date(required=True)
    coordenador_distrital_id = graphene.String(required=True)
    tecnico_social_id = graphene.String(required=True)
    distrito_id = graphene.String(required=True)
    modulo_id = graphene.String(required=False)     # FK para ModuloPEP (substituiu nome_modulo)
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
            converted_data = convert_ids_in_session_data(data)
            SessaoPEPService.create(converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateSessaoPEPInput(OpenIMISMutation.Input):
    """Input for updating a PEP session"""
    id = graphene.String(required=True)
    data_planejamento = graphene.Date(required=False)
    coordenador_distrital_id = graphene.String(required=False)
    tecnico_social_id = graphene.String(required=False)
    distrito_id = graphene.String(required=False)
    modulo_id = graphene.String(required=False)     # FK para ModuloPEP
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
            sessao_id = decode_id(data.pop('id'))
            converted_data = convert_ids_in_session_data(data)
            SessaoPEPService.update(sessao_id, converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteSessaoPEPMutation(OpenIMISMutation):
    """Delete a PEP session"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteSessaoPEPMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            SessaoPEPService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class SessaoPEPInputType(graphene.InputObjectType):
    """Input type for a single session in bulk creation"""
    codigo_sessao = graphene.String(required=True)
    data_planejamento = graphene.Date(required=True)
    coordenador_distrital_id = graphene.String(required=True)
    tecnico_social_id = graphene.String(required=True)
    distrito_id = graphene.String(required=True)
    modulo_id = graphene.String(required=False)
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
            converted_sessions = [convert_ids_in_session_data(session) for session in sessions_list]
            SessaoPEPService.create_multiple(converted_sessions, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class SessaoPEPUpdateInputType(graphene.InputObjectType):
    """Input type for a single session in bulk update"""
    id = graphene.String(required=True)
    codigo_sessao = graphene.String(required=False)
    data_planejamento = graphene.Date(required=False)
    coordenador_distrital_id = graphene.String(required=False)
    tecnico_social_id = graphene.String(required=False)
    distrito_id = graphene.String(required=False)
    modulo_id = graphene.String(required=False)
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
            converted_sessions = [convert_ids_in_session_data(session) for session in sessions_list]
            SessaoPEPService.update_multiple(converted_sessions, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# SESSION ATTENDANCE MUTATIONS (Ferramenta 2)
# =============================================================================

class CreatePresencaSessaoInput(OpenIMISMutation.Input):
    """Input for creating an attendance record"""
    sessao_id = graphene.String(required=True)
    familia_id = graphene.String(required=True)
    nome_familia = graphene.String(required=False)
    grupo_id = graphene.String(required=False)
    estado = graphene.String(required=False)
    codigo_encaminhamento = graphene.String(required=False)
    tipo_encaminhamento_id = graphene.String(required=False)  # FK para TipoEncaminhamento
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
            converted_data = convert_ids_in_session_data(data)
            PresencaSessaoService.create(converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdatePresencaSessaoInput(OpenIMISMutation.Input):
    """Input for updating an attendance record"""
    id = graphene.String(required=True)
    estado = graphene.String(required=False)
    codigo_encaminhamento = graphene.String(required=False)
    tipo_encaminhamento_id = graphene.String(required=False)
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
            presenca_id = decode_id(data.pop('id'))
            converted_data = convert_ids_in_session_data(data)
            PresencaSessaoService.update(presenca_id, converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeletePresencaSessaoMutation(OpenIMISMutation):
    """Delete an attendance record"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeletePresencaSessaoMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            PresencaSessaoService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# Batch mutation for registering attendance with session details
class PresencaItemInput(graphene.InputObjectType):
    """Input for a single family attendance record"""
    familia_id = graphene.String(required=True)
    estado = graphene.String(required=True)  # PRES, FALT, ENCA
    codigo_encaminhamento = graphene.String(required=False)
    tipo_encaminhamento_id = graphene.String(required=False)


class RegistrarPresencasBatchInput(OpenIMISMutation.Input):
    """Input for batch attendance registration with session details (Ferramenta 2)"""
    # Detalhes da sessão
    sessao_id = graphene.String(required=True)
    data_sessao = graphene.Date(required=True)
    distrito_id = graphene.String(required=True)
    formador_id = graphene.String(required=True)
    localidade_id = graphene.String(required=False)
    modulo_id = graphene.String(required=False)   # FK para ModuloPEP
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
            converted_data = convert_ids_in_session_data(data)
            PresencaSessaoService.registrar_presencas_batch(converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# SESSION EXECUTION MUTATIONS (Ferramenta 3)
# =============================================================================

class CreateExecucaoSessaoInput(OpenIMISMutation.Input):
    """Input for creating a session execution record (Ferramenta 3)"""
    sessao_id = graphene.String(required=True)
    formador_id = graphene.String(required=True)
    supervisor_id = graphene.String(required=False)
    localidade_id = graphene.String(required=False)

    numero_cuidadores = graphene.String(required=False)

    praticas_positivas = graphene.JSONString(required=False)
    outras_praticas_positivas = graphene.String(required=False)

    desafios_transmissao = graphene.JSONString(required=False)
    outros_desafios = graphene.String(required=False)

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
            data = convert_ids_in_session_data(data)
            ExecucaoSessaoService.create(data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateExecucaoSessaoInput(OpenIMISMutation.Input):
    """Input for updating a session execution record"""
    id = graphene.String(required=True)

    numero_cuidadores = graphene.String(required=False)

    praticas_positivas = graphene.JSONString(required=False)
    outras_praticas_positivas = graphene.String(required=False)

    desafios_transmissao = graphene.JSONString(required=False)
    outros_desafios = graphene.String(required=False)

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
            execucao_id = decode_id(data.pop('id'))
            ExecucaoSessaoService.update(execucao_id, data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# SESSION SUPERVISION MUTATIONS (Ferramenta 4)
# =============================================================================

class CreateSupervisaoSessaoInput(OpenIMISMutation.Input):
    """Input for creating a supervision record (Ferramenta 4)"""
    sessao_id = graphene.String(required=True)
    supervisor_id = graphene.String(required=True)
    formador_id = graphene.String(required=True)
    localidade_id = graphene.String(required=False)
    grupo_id = graphene.String(required=False)
    data_supervisao = graphene.Date(required=True)
    data_modulo_anterior = graphene.Date(required=False)
    identificador_grupo = graphene.String(required=True)

    numero_participantes = graphene.String(required=False)

    praticas_positivas_estrategias = graphene.JSONString(required=False)
    desafios_transmissao = graphene.JSONString(required=False)
    necessita_encaminhamento = graphene.Boolean(required=False)

    auto_avaliacao_pontos_fortes = graphene.JSONString(required=False)
    auto_avaliacao_pontos_atencao = graphene.JSONString(required=False)
    avaliacao_execucao_metodologia = graphene.JSONString(required=False)

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
            data = convert_ids_in_session_data(data)
            SupervisaoSessaoService.create(data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateSupervisaoSessaoInput(OpenIMISMutation.Input):
    """Input for updating a supervision record"""
    id = graphene.String(required=True)

    numero_participantes = graphene.String(required=False)

    praticas_positivas_estrategias = graphene.JSONString(required=False)
    desafios_transmissao = graphene.JSONString(required=False)
    necessita_encaminhamento = graphene.Boolean(required=False)

    auto_avaliacao_pontos_fortes = graphene.JSONString(required=False)
    auto_avaliacao_pontos_atencao = graphene.JSONString(required=False)
    avaliacao_execucao_metodologia = graphene.JSONString(required=False)

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
            supervisao_id = decode_id(data.pop('id'))
            SupervisaoSessaoService.update(supervisao_id, data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# RELATORIO DISTRITAL BIMESTRAL MUTATIONS (Ferramenta 5)
# =============================================================================

class CreateRelatorioDistritalInput(OpenIMISMutation.Input):
    """
    Input para criar um Relatório Distrital Bimestral (Ferramenta 5).

    Campos mínimos obrigatórios: distrito_id, periodo, ano.
    Todos os restantes dados (datas do período, coordenador, indicadores estatísticos)
    são calculados automaticamente a partir dos registos existentes (SessaoPEP, PresencaSessao).
    Podem ser sobrescritos passando os valores explicitamente.
    """
    distrito_id = graphene.String(required=True)
    periodo = graphene.String(required=True, description="BIM1 a BIM6")
    ano = graphene.Int(required=True)

    # Opcionais — auto-preenchidos a partir de CoordenacaoDistrital
    coordenador_distrital_id = graphene.String(required=False)
    tecnico_administrativo_id = graphene.String(required=False)

    # Opcionais — auto-calculados a partir dos registos; podem ser corrigidos manualmente
    numero_localidades_atendidas = graphene.Int(required=False)
    numero_familias_atendidas = graphene.Int(required=False)
    numero_tecnicos_formadores = graphene.Int(required=False)
    numero_sessoes_conduzidas = graphene.Int(required=False)
    numero_sessoes_esperadas = graphene.Int(required=False)
    numero_familias_presentes = graphene.Int(required=False)
    numero_familias_esperadas = graphene.Int(required=False)
    numero_familias_migraram = graphene.Int(required=False)
    numero_sessoes_perdidas = graphene.Int(required=False)
    percentual_sessoes = graphene.Float(required=False)
    percentual_familias = graphene.Float(required=False)
    media_familia_presente = graphene.Float(required=False)
    media_familia_esperada = graphene.Float(required=False)

    dados_tecnicos = graphene.JSONString(required=False)
    dados_encaminhamentos = graphene.JSONString(required=False)
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
            data = convert_ids_in_session_data(data)
            RelatorioDistritalService.create(data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateRelatorioDistritalInput(OpenIMISMutation.Input):
    """Input for updating a district bimonthly report"""
    id = graphene.String(required=True)

    numero_localidades_atendidas = graphene.Int(required=False)
    numero_familias_atendidas = graphene.Int(required=False)
    numero_tecnicos_formadores = graphene.Int(required=False)
    numero_sessoes_conduzidas = graphene.Int(required=False)
    numero_sessoes_esperadas = graphene.Int(required=False)
    numero_familias_presentes = graphene.Int(required=False)
    numero_familias_esperadas = graphene.Int(required=False)
    numero_familias_migraram = graphene.Int(required=False)
    numero_sessoes_perdidas = graphene.Int(required=False)

    percentual_sessoes = graphene.Float(required=False)
    percentual_familias = graphene.Float(required=False)
    media_familia_presente = graphene.Float(required=False)
    media_familia_esperada = graphene.Float(required=False)

    dados_tecnicos = graphene.JSONString(required=False)
    dados_encaminhamentos = graphene.JSONString(required=False)

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
            relatorio_id = decode_id(data.pop('id'))
            RelatorioDistritalService.update(relatorio_id, data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteRelatorioDistritalMutation(OpenIMISMutation):
    """Delete a district bimonthly report (soft delete)"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteRelatorioDistritalMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            RelatorioDistritalService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# ENCAMINHAMENTO MUTATIONS
# =============================================================================

class CreateEncaminhamentoInput(OpenIMISMutation.Input):
    """Input for creating a referral"""
    sessao_id = graphene.String(required=True)
    familia_id = graphene.String(required=True)
    nome_familia = graphene.String(required=True)
    codigo_encaminhamento = graphene.String(required=True)
    descricao = graphene.String(required=True)
    tipo_encaminhamento_id = graphene.String(required=False)  # FK para TipoEncaminhamento
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
            data = convert_ids_in_session_data(data)
            EncaminhamentoService.create(data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateEncaminhamentoInput(OpenIMISMutation.Input):
    """Input for updating a referral"""
    id = graphene.String(required=True)
    tipo_encaminhamento_id = graphene.String(required=False)
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
            encaminhamento_id = decode_id(data.pop('id'))
            converted_data = convert_ids_in_session_data(data)
            EncaminhamentoService.update(encaminhamento_id, converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# BIMONTHLY MEETING AGENDA MUTATIONS (Ferramenta 6)
# =============================================================================

class CreateRoteiroReuniaoInput(OpenIMISMutation.Input):
    """Input for creating a bimonthly meeting agenda (Ferramenta 6)"""
    data_reuniao = graphene.Date(required=True)
    horario = graphene.Time(required=True)
    coordenador_nacional_id = graphene.String(required=True)
    participantes = graphene.JSONString(required=False)
    participantes_manuais = graphene.JSONString(required=False)
    resumo_da_agenda = graphene.JSONString(required=False)
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
            data = convert_ids_in_session_data(data)
            RoteiroReuniaoService.create(data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateRoteiroReuniaoInput(OpenIMISMutation.Input):
    """Input for updating a bimonthly meeting agenda (Ferramenta 6)"""
    id = graphene.String(required=True)
    data_reuniao = graphene.Date(required=False)
    horario = graphene.Time(required=False)
    coordenador_nacional_id = graphene.String(required=False)
    participantes = graphene.JSONString(required=False)
    participantes_manuais = graphene.JSONString(required=False)
    resumo_da_agenda = graphene.JSONString(required=False)
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
            roteiro_id = decode_id(data.pop('id'))
            data = convert_ids_in_session_data(data)
            RoteiroReuniaoService.update(roteiro_id, data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteRoteiroReuniaoMutation(OpenIMISMutation):
    """Delete a bimonthly meeting agenda"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteRoteiroReuniaoMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            RoteiroReuniaoService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# SUPERVISION REPORT MUTATIONS (FERRAMENTA 7)
# =============================================================================

class CreateRelatorioSupervisaoInput(OpenIMISMutation.Input):
    """Input for creating a bimonthly supervision report (Ferramenta 7)"""
    supervisores = graphene.JSONString(required=False)
    numero_sessoes = graphene.Int(required=True)
    numero_tecnicos_formadores = graphene.Int(required=True)
    distrito_id = graphene.String(required=True)
    periodo = graphene.String(required=True)
    ano = graphene.Int(required=True)
    avaliacoes_tecnicos = graphene.JSONString(required=False)
    sessoes_pep = graphene.JSONString(required=False)
    modulos_dificuldade = graphene.JSONString(required=False)
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
            converted_data = convert_ids_in_session_data(data)
            RelatorioSupervisaoService.create(converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateRelatorioSupervisaoInput(OpenIMISMutation.Input):
    """Input for updating a bimonthly supervision report (Ferramenta 7)"""
    id = graphene.String(required=True)
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
            converted_data = convert_ids_in_session_data(data)
            RelatorioSupervisaoService.update(converted_data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteRelatorioSupervisaoMutation(OpenIMISMutation):
    """Delete (soft delete) a bimonthly supervision report"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteRelatorioSupervisaoMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            from .services import RelatorioSupervisaoService
            RelatorioSupervisaoService.delete(decode_id(data['id']), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# =============================================================================
# RELATÓRIO DISTRITAL — ENCAMINHAMENTOS ESTRUTURADOS
# =============================================================================

class AddEncaminhamentoRelatorioInput(OpenIMISMutation.Input):
    """
    Adiciona uma PresencaSessao (estado=ENCA) a um RelatorioDistritalBimestral.
    O código de encaminhamento, família e tipo são lidos directamente da presença.
    """
    relatorio_id = graphene.String(required=True, description="Relay ID do RelatorioDistritalBimestral")
    presenca_id = graphene.String(required=True, description="Relay ID da PresencaSessao (deve ter estado=ENCA)")
    observacoes = graphene.String(required=False, description="Notas adicionais para este encaminhamento no relatório")


class AddEncaminhamentoRelatorioMutation(OpenIMISMutation):
    """Adiciona uma presença encaminhada (ENCA) ao relatório distrital"""
    _mutation_module = "pep_plus"
    _mutation_class = "AddEncaminhamentoRelatorioMutation"

    class Input(AddEncaminhamentoRelatorioInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            relatorio_id = decode_id(data.get('relatorio_id'))
            presenca_id = decode_id(data.get('presenca_id'))
            RelatorioDistEncaminhamentoService.add(relatorio_id, presenca_id, data.get('observacoes'), user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class RemoveEncaminhamentoRelatorioInput(OpenIMISMutation.Input):
    """Remove a ligação entre uma PresencaSessao e um RelatorioDistritalBimestral"""
    relatorio_id = graphene.String(required=True)
    presenca_id = graphene.String(required=True)


class RemoveEncaminhamentoRelatorioMutation(OpenIMISMutation):
    """Remove uma presença encaminhada do relatório distrital"""
    _mutation_module = "pep_plus"
    _mutation_class = "RemoveEncaminhamentoRelatorioMutation"

    class Input(RemoveEncaminhamentoRelatorioInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            relatorio_id = decode_id(data.get('relatorio_id'))
            presenca_id = decode_id(data.get('presenca_id'))
            RelatorioDistEncaminhamentoService.remove(relatorio_id, presenca_id, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class SetEncaminhamentosRelatorioInput(OpenIMISMutation.Input):
    """
    Substitui a lista completa de encaminhamentos de um relatório.
    Útil para guardar a selecção de uma só vez a partir do formulário.
    """
    relatorio_id = graphene.String(required=True, description="Relay ID do RelatorioDistritalBimestral")
    presencas_ids = graphene.List(
        graphene.String, required=True,
        description="Lista de Relay IDs de PresencaSessao (estado=ENCA) a associar. "
                    "Remove todos os anteriores e define estes como os novos."
    )


class SetEncaminhamentosRelatorioMutation(OpenIMISMutation):
    """Substitui em bloco todos os encaminhamentos de um relatório distrital"""
    _mutation_module = "pep_plus"
    _mutation_class = "SetEncaminhamentosRelatorioMutation"

    class Input(SetEncaminhamentosRelatorioInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            relatorio_id = decode_id(data.get('relatorio_id'))
            presencas_ids = [decode_id(pid) for pid in (data.get('presencas_ids') or [])]
            RelatorioDistEncaminhamentoService.set_all(relatorio_id, presencas_ids, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# ALUNO MUTATIONS
# =============================================================================

class CreateAlunoInput(OpenIMISMutation.Input):
    """
    Input para criar um Aluno.

    Há duas formas de uso:
    A) Fornecer individual_id → liga a um Individual existente no openIMIS
    B) Fornecer first_name + last_name + dob → o service cria o Individual
       automaticamente e depois cria o Aluno com a referência associada
    """
    # --- Opção A: ligar a Individual existente ---
    individual_id = graphene.String(required=False, description="UUID Relay do Individual openIMIS existente")

    # --- Opção B: dados para criar Individual novo ---
    first_name = graphene.String(required=False, description="Primeiro nome (usado se individual_id não for fornecido)")
    last_name = graphene.String(required=False, description="Apelido (usado se individual_id não for fornecido)")
    dob = graphene.String(required=False, description="Data de nascimento ISO (YYYY-MM-DD)")

    # --- Dados do Aluno (sempre) ---
    id_membro_crianca = graphene.String(required=False)
    id_da_crianca = graphene.String(required=False)
    nome_encarregado = graphene.String(required=False)
    sexo = graphene.String(required=False, description="M / F / I")

    # Localização
    distrito_id = graphene.String(required=False, description="ID Relay do Distrito (Location)")
    localidade_id = graphene.String(required=False, description="ID Relay da Localidade (Location)")
    ponto_referencia = graphene.String(required=False)
    meio_residencia = graphene.String(required=False)

    # Dados escolares
    escola_id = graphene.String(required=False)
    escola_actual_id = graphene.String(required=False)
    escolaridade_actual = graphene.String(required=False)
    classe_id = graphene.String(required=False)
    classe_que_frequenta_id = graphene.String(required=False)
    dados_escolares_correctos = graphene.Boolean(required=False)
    ativo = graphene.Boolean(required=False)


class CreateAlunoMutation(OpenIMISMutation):
    """
    Cria um novo Aluno.
    Se individual_id for fornecido, liga ao Individual existente.
    Caso contrário, cria o Individual automaticamente com first_name/last_name/dob.
    """
    _mutation_module = "pep_plus"
    _mutation_class = "CreateAlunoMutation"

    class Input(CreateAlunoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            AlunoService.create(data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateAlunoInput(OpenIMISMutation.Input):
    """Input para actualizar um Aluno existente"""
    id = graphene.String(required=True)

    id_membro_crianca = graphene.String(required=False)
    id_da_crianca = graphene.String(required=False)
    nome_encarregado = graphene.String(required=False)
    sexo = graphene.String(required=False)
    distrito_id = graphene.String(required=False)
    localidade_id = graphene.String(required=False)
    ponto_referencia = graphene.String(required=False)
    meio_residencia = graphene.String(required=False)
    escola_id = graphene.String(required=False)
    escola_actual_id = graphene.String(required=False)
    escolaridade_actual = graphene.String(required=False)
    classe_id = graphene.String(required=False)
    classe_que_frequenta_id = graphene.String(required=False)
    dados_escolares_correctos = graphene.Boolean(required=False)
    ativo = graphene.Boolean(required=False)


class UpdateAlunoMutation(OpenIMISMutation):
    """Actualiza um Aluno existente"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateAlunoMutation"

    class Input(UpdateAlunoInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            aluno_id = decode_id(data.pop('id'))
            AlunoService.update(aluno_id, data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteAlunoMutation(OpenIMISMutation):
    """Desactiva (soft delete) um Aluno"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteAlunoMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            aluno_id = decode_id(data.get('id'))
            AlunoService.delete(aluno_id, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# =============================================================================
# COORDENAÇÃO DISTRITAL MUTATIONS
# =============================================================================

class CreateCoordenacaoDistritalInput(OpenIMISMutation.Input):
    """Input para criar uma Coordenação Distrital"""
    distrito_id = graphene.String(required=True, description="ID Relay do Distrito (Location)")
    coordenador_id = graphene.String(required=True, description="ID Relay do Coordenador Distrital")
    tecnico_administrativo_id = graphene.String(required=False, description="ID Relay do Técnico Administrativo (1 por distrito)")
    tecnicos_operacionais_ids = graphene.List(graphene.String, required=False, description="Lista de IDs Relay dos Técnicos Operacionais")
    ativo = graphene.Boolean(required=False)
    observacoes = graphene.String(required=False)


class CreateCoordenacaoDistritalMutation(OpenIMISMutation):
    """Cria uma nova Coordenação Distrital"""
    _mutation_module = "pep_plus"
    _mutation_class = "CreateCoordenacaoDistritalMutation"

    class Input(CreateCoordenacaoDistritalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            CoordenacaoDistritalService.create(data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class UpdateCoordenacaoDistritalInput(OpenIMISMutation.Input):
    """Input para actualizar uma Coordenação Distrital"""
    id = graphene.String(required=True, description="ID Relay da CoordenacaoDistrital a actualizar")
    coordenador_id = graphene.String(required=False)
    tecnico_administrativo_id = graphene.String(required=False)
    tecnicos_operacionais_ids = graphene.List(graphene.String, required=False, description="Substitui todos os técnicos operacionais")
    ativo = graphene.Boolean(required=False)
    observacoes = graphene.String(required=False)


class UpdateCoordenacaoDistritalMutation(OpenIMISMutation):
    """Actualiza uma Coordenação Distrital existente"""
    _mutation_module = "pep_plus"
    _mutation_class = "UpdateCoordenacaoDistritalMutation"

    class Input(UpdateCoordenacaoDistritalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            coord_id = decode_id(data.pop('id'))
            CoordenacaoDistritalService.update(coord_id, data, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class DeleteCoordenacaoDistritalMutation(OpenIMISMutation):
    """Desactiva (soft delete) uma Coordenação Distrital"""
    _mutation_module = "pep_plus"
    _mutation_class = "DeleteCoordenacaoDistritalMutation"

    class Input(OpenIMISMutation.Input):
        id = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            coord_id = decode_id(data.get('id'))
            CoordenacaoDistritalService.delete(coord_id, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class AddTecnicoOperacionalInput(OpenIMISMutation.Input):
    """Input para adicionar um técnico operacional a uma Coordenação Distrital"""
    coordenacao_id = graphene.String(required=True, description="ID Relay da CoordenacaoDistrital")
    tecnico_id = graphene.String(required=True, description="ID Relay do utilizador a adicionar como técnico operacional")


class AddTecnicoOperacionalMutation(OpenIMISMutation):
    """Adiciona um técnico operacional a uma Coordenação Distrital"""
    _mutation_module = "pep_plus"
    _mutation_class = "AddTecnicoOperacionalMutation"

    class Input(AddTecnicoOperacionalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            coord_id = decode_id(data.get('coordenacao_id'))
            tecnico_id = decode_id(data.get('tecnico_id'))
            CoordenacaoDistritalService.add_tecnico_operacional(coord_id, tecnico_id, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


class RemoveTecnicoOperacionalInput(OpenIMISMutation.Input):
    """Input para remover um técnico operacional de uma Coordenação Distrital"""
    coordenacao_id = graphene.String(required=True, description="ID Relay da CoordenacaoDistrital")
    tecnico_id = graphene.String(required=True, description="ID Relay do utilizador a remover")


class RemoveTecnicoOperacionalMutation(OpenIMISMutation):
    """Remove um técnico operacional de uma Coordenação Distrital"""
    _mutation_module = "pep_plus"
    _mutation_class = "RemoveTecnicoOperacionalMutation"

    class Input(RemoveTecnicoOperacionalInput):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            coord_id = decode_id(data.get('coordenacao_id'))
            tecnico_id = decode_id(data.get('tecnico_id'))
            CoordenacaoDistritalService.remove_tecnico_operacional(coord_id, tecnico_id, user)
            return None
        except Exception as exc:
            return [{'message': str(exc), 'detail': str(exc)}]


# ROOT MUTATION
# =============================================================================

class Mutation(graphene.ObjectType):
    """Root Mutation for PEP+ module"""

    # ---- Parametrização: ModuloPEP ----
    create_modulo_pep = CreateModuloPEPMutation.Field()
    update_modulo_pep = UpdateModuloPEPMutation.Field()
    delete_modulo_pep = DeleteModuloPEPMutation.Field()

    # ---- Parametrização: Escola ----
    create_escola = CreateEscolaMutation.Field()
    update_escola = UpdateEscolaMutation.Field()
    delete_escola = DeleteEscolaMutation.Field()

    # ---- Parametrização: Classe ----
    create_classe = CreateClasseMutation.Field()
    update_classe = UpdateClasseMutation.Field()
    delete_classe = DeleteClasseMutation.Field()

    # ---- Parametrização: Disciplina ----
    create_disciplina = CreateDisciplinaMutation.Field()
    update_disciplina = UpdateDisciplinaMutation.Field()
    delete_disciplina = DeleteDisciplinaMutation.Field()

    # ---- Parametrização: TipoEncaminhamento ----
    create_tipo_encaminhamento = CreateTipoEncaminhamentoMutation.Field()
    update_tipo_encaminhamento = UpdateTipoEncaminhamentoMutation.Field()
    delete_tipo_encaminhamento = DeleteTipoEncaminhamentoMutation.Field()

    # ---- Aluno (Registar Indivíduo/Aluno) ----
    create_aluno = CreateAlunoMutation.Field()
    update_aluno = UpdateAlunoMutation.Field()
    delete_aluno = DeleteAlunoMutation.Field()

    # ---- Educational Module mutations ----
    create_modulo_educacional = CreateModuloEducacionalMutation.Field()
    update_modulo_educacional = UpdateModuloEducacionalMutation.Field()
    delete_modulo_educacional = DeleteModuloEducacionalMutation.Field()

    # ---- Family Group mutations ----
    create_grupo_familiar = CreateGrupoFamiliarMutation.Field()
    update_grupo_familiar = UpdateGrupoFamiliarMutation.Field()
    delete_grupo_familiar = DeleteGrupoFamiliarMutation.Field()

    # ---- PEP Session mutations (Ferramenta 1) ----
    create_sessao_pep = CreateSessaoPEPMutation.Field()
    create_multiple_sessoes_pep = CreateMultipleSessoesPEPMutation.Field()
    update_sessao_pep = UpdateSessaoPEPMutation.Field()
    update_multiple_sessoes_pep = UpdateMultipleSessoesPEPMutation.Field()
    delete_sessao_pep = DeleteSessaoPEPMutation.Field()

    # ---- Session Attendance mutations (Ferramenta 2) ----
    create_presenca_sessao = CreatePresencaSessaoMutation.Field()
    update_presenca_sessao = UpdatePresencaSessaoMutation.Field()
    delete_presenca_sessao = DeletePresencaSessaoMutation.Field()
    registrar_presencas_batch = RegistrarPresencasBatchMutation.Field()

    # ---- Session Execution mutations (Ferramenta 3) ----
    create_execucao_sessao = CreateExecucaoSessaoMutation.Field()
    update_execucao_sessao = UpdateExecucaoSessaoMutation.Field()

    # ---- Session Supervision mutations (Ferramenta 4) ----
    create_supervisao_sessao = CreateSupervisaoSessaoMutation.Field()
    update_supervisao_sessao = UpdateSupervisaoSessaoMutation.Field()

    # ---- District Bimonthly Report mutations (Ferramenta 5) ----
    create_relatorio_distrital = CreateRelatorioDistritalMutation.Field()
    update_relatorio_distrital = UpdateRelatorioDistritalMutation.Field()
    delete_relatorio_distrital = DeleteRelatorioDistritalMutation.Field()

    # ---- Encaminhamentos estruturados do relatório distrital ----
    add_encaminhamento_relatorio = AddEncaminhamentoRelatorioMutation.Field()
    remove_encaminhamento_relatorio = RemoveEncaminhamentoRelatorioMutation.Field()
    set_encaminhamentos_relatorio = SetEncaminhamentosRelatorioMutation.Field()

    # ---- Referral mutations ----
    create_encaminhamento = CreateEncaminhamentoMutation.Field()
    update_encaminhamento = UpdateEncaminhamentoMutation.Field()

    # ---- Bimonthly Meeting Agenda mutations (Ferramenta 6) ----
    create_roteiro_reuniao = CreateRoteiroReuniaoMutation.Field()
    update_roteiro_reuniao = UpdateRoteiroReuniaoMutation.Field()
    delete_roteiro_reuniao = DeleteRoteiroReuniaoMutation.Field()

    # ---- Bimonthly Supervision Report mutations (Ferramenta 7) ----
    create_relatorio_supervisao = CreateRelatorioSupervisaoMutation.Field()
    update_relatorio_supervisao = UpdateRelatorioSupervisaoMutation.Field()
    delete_relatorio_supervisao = DeleteRelatorioSupervisaoMutation.Field()

    # ---- Coordenação Distrital ----
    create_coordenacao_distrital = CreateCoordenacaoDistritalMutation.Field()
    update_coordenacao_distrital = UpdateCoordenacaoDistritalMutation.Field()
    delete_coordenacao_distrital = DeleteCoordenacaoDistritalMutation.Field()
    add_tecnico_operacional = AddTecnicoOperacionalMutation.Field()
    remove_tecnico_operacional = RemoveTecnicoOperacionalMutation.Field()
