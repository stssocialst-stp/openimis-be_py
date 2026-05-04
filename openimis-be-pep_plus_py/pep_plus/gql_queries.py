"""
PEP+ GraphQL Queries
Implements READ operations for all PEP+ entities
"""
import logging
import graphene
from graphene_django import DjangoObjectType
from core.schema import OrderedDjangoFilterConnectionField, UserGQLType
from core import ExtendedConnection
from location.gql_queries import LocationGQLType

logger = logging.getLogger(__name__)
from .models import (
    ModuloPEP, Escola, Classe, ClasseDisciplina, Disciplina, TipoEncaminhamento,
    Aluno, ModuloEducacional, ModuloEducacionalDisciplina,
    GrupoFamiliar, SessaoPEP, PresencaSessao,
    ExecucaoSessao, SupervisaoSessao,
    RelatorioDistritalBimestral, RelatorioDistEncaminhamento,
    EncaminhamentoSessao, RoteiroReuniaoBimestral, RelatorioSupervisaoBimestral,
    CoordenacaoDistrital, CoordenacaoDistritalTecnico
)


# =============================================================================
# GQL TYPES — TABELAS DE PARAMETRIZAÇÃO
# =============================================================================

class ModuloPEPGQLType(DjangoObjectType):
    """GraphQL Type for ModuloPEP (lookup table)"""

    class Meta:
        model = ModuloPEP
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "codigo": ["exact", "icontains"],
            "nome": ["exact", "icontains"],
            "ordem": ["exact", "lt", "lte", "gt", "gte"],
            "ativo": ["exact"],
        }
        connection_class = ExtendedConnection


class EscolaGQLType(DjangoObjectType):
    """GraphQL Type for Escola (lookup table)"""

    distrito = graphene.Field(LocationGQLType)
    localidade = graphene.Field(LocationGQLType)

    class Meta:
        model = Escola
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "nome": ["exact", "icontains"],
            "codigo": ["exact", "icontains"],
            "nivel": ["exact"],
            "distrito_id": ["exact"],
            "localidade_id": ["exact"],
            "ativo": ["exact"],
        }
        connection_class = ExtendedConnection


class ClasseGQLType(DjangoObjectType):
    """GraphQL Type for Classe (lookup table)"""

    class Meta:
        model = Classe
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "codigo": ["exact", "icontains"],
            "nome": ["exact", "icontains"],
            "nivel": ["exact"],
            "ordem": ["exact", "lt", "lte", "gt", "gte"],
            "ativo": ["exact"],
        }
        connection_class = ExtendedConnection


class DisciplinaGQLType(DjangoObjectType):
    """GraphQL Type for Disciplina (lookup table)"""

    class Meta:
        model = Disciplina
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "nome": ["exact", "icontains"],
            "nivel": ["exact"],
            "ativo": ["exact"],
            "faixa_faltas_aceitaveis": ["exact"],
            "quantidade_faltas_aceitaveis": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


class ClasseDisciplinaGQLType(DjangoObjectType):
    """GraphQL Type for the M2M through table ClasseDisciplina"""

    classe = graphene.Field(ClasseGQLType)
    disciplina = graphene.Field(DisciplinaGQLType)

    class Meta:
        model = ClasseDisciplina
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "classe_id": ["exact"],
            "disciplina_id": ["exact"],
        }
        connection_class = ExtendedConnection


class TipoEncaminhamentoGQLType(DjangoObjectType):
    """GraphQL Type for TipoEncaminhamento (lookup table)"""

    class Meta:
        model = TipoEncaminhamento
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "codigo": ["exact", "icontains"],
            "nome": ["exact", "icontains"],
            "ativo": ["exact"],
        }
        connection_class = ExtendedConnection


class ModuloEducacionalDisciplinaGQLType(DjangoObjectType):
    """GraphQL Type for the M2M through table ModuloEducacionalDisciplina"""

    disciplina = graphene.Field(DisciplinaGQLType)

    class Meta:
        model = ModuloEducacionalDisciplina
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "modulo_id": ["exact"],
            "disciplina_id": ["exact"],
            "tipo": ["exact"],
        }
        connection_class = ExtendedConnection


# =============================================================================
# GQL TYPES — MODELOS PRINCIPAIS
# =============================================================================

class AlunoGQLType(DjangoObjectType):
    """
    GraphQL Type para Aluno.
    Perfil centralizado de aluno, ligado ao Individual openIMIS.
    Expõe os dados de localização e escolares de forma estruturada.
    """

    distrito = graphene.Field(LocationGQLType)
    localidade = graphene.Field(LocationGQLType)
    escola = graphene.Field(EscolaGQLType)
    escola_actual = graphene.Field(EscolaGQLType)
    classe = graphene.Field(ClasseGQLType)
    classe_que_frequenta = graphene.Field(ClasseGQLType)

    # Campos do Individual expostos directamente para conveniência
    first_name = graphene.String()
    last_name = graphene.String()
    dob = graphene.String()

    class Meta:
        model = Aluno
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id_membro_crianca": ["exact", "icontains"],
            "id_da_crianca": ["exact", "icontains"],
            "nome_encarregado": ["exact", "icontains"],
            "sexo": ["exact"],
            "distrito_id": ["exact"],
            "localidade_id": ["exact"],
            "escola_id": ["exact"],
            "escola_actual_id": ["exact"],
            "escolaridade_actual": ["exact"],
            "classe_id": ["exact"],
            "classe_que_frequenta_id": ["exact"],
            "dados_escolares_correctos": ["exact"],
            "ativo": ["exact"],
        }
        connection_class = ExtendedConnection

    def resolve_first_name(self, info, **kwargs):
        return self.individual.first_name if self.individual_id else None

    def resolve_last_name(self, info, **kwargs):
        return self.individual.last_name if self.individual_id else None

    def resolve_dob(self, info, **kwargs):
        return str(self.individual.dob) if self.individual_id and self.individual.dob else None


class ModuloEducacionalGQLType(DjangoObjectType):
    """GraphQL Type for Assiduidade Escolar (Educational Module)"""

    aluno = graphene.Field(AlunoGQLType)
    escola = graphene.Field(EscolaGQLType)
    escola_actual = graphene.Field(EscolaGQLType)
    classe = graphene.Field(ClasseGQLType)
    classe_que_frequenta = graphene.Field(ClasseGQLType)
    disciplinas = graphene.List(ModuloEducacionalDisciplinaGQLType)

    class Meta:
        model = ModuloEducacional
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id_membro_crianca": ["exact", "icontains"],
            "nome": ["exact", "icontains"],
            "nome_encarregado": ["exact", "icontains"],
            "id_da_crianca": ["exact", "icontains"],
            # sexo: filtro directo por valor (M / F / I)
            "sexo": ["exact"],
            "escolaridade_actual": ["exact"],
            "dados_escolar_correctos": ["exact"],
            "dados_escolares_correctos": ["exact"],
            "ano_registo": ["exact", "lt", "lte", "gt", "gte"],
            "idade": ["exact", "lt", "lte", "gt", "gte"],
            "aproveitamento_primeiro_trimestre": ["exact"],
            "faixa_de_faltas": ["exact"],
            # FKs para escola, classe, aluno, distrito, localidade são tratadas
            # via parâmetros Relay ID no campo modulos_educacionais (resolver abaixo)
        }
        connection_class = ExtendedConnection

    def resolve_disciplinas(self, info, **kwargs):
        return self.disciplinas_associadas.filter(disciplina__validity_to__isnull=True)


class GrupoFamiliarGQLType(DjangoObjectType):
    """GraphQL Type for Family Group"""

    distrito = graphene.Field(LocationGQLType)
    localidade = graphene.Field(LocationGQLType)

    class Meta:
        model = GrupoFamiliar
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "codigo": ["exact", "icontains"],
            "nome": ["exact", "icontains"],
            "localidade_id": ["exact"],
            "ativo": ["exact"],
        }
        connection_class = ExtendedConnection


class SessaoPEPGQLType(DjangoObjectType):
    """GraphQL Type for PEP Session"""

    coordenador_distrital = graphene.Field(UserGQLType)
    tecnico_social = graphene.Field(UserGQLType)
    distrito = graphene.Field(LocationGQLType)
    grupo_familia = graphene.Field(GrupoFamiliarGQLType)
    modulo = graphene.Field(ModuloPEPGQLType)

    class Meta:
        model = SessaoPEP
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "codigo_sessao": ["exact", "icontains"],
            "distrito_id": ["exact"],
            "modulo_id": ["exact"],
            "coordenador_distrital_id": ["exact"],
            "tecnico_social_id": ["exact"],
            "grupo_familia_id": ["exact"],
            "data_planejamento": ["exact", "lt", "lte", "gt", "gte"],
            "data_sessao": ["exact", "lt", "lte", "gt", "gte"],
            "status": ["exact"],
            "tem_supervisao": ["exact"],
            "dia_semana": ["exact"],
        }
        connection_class = ExtendedConnection


class PresencaSessaoGQLType(DjangoObjectType):
    """GraphQL Type for Session Attendance"""

    sessao = graphene.Field(SessaoPEPGQLType)
    tipo_encaminhamento = graphene.Field(TipoEncaminhamentoGQLType)

    class Meta:
        model = PresencaSessao
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "sessao_id": ["exact"],
            "familia_id": ["exact", "icontains"],
            "nome_familia": ["exact", "icontains"],
            "grupo_id": ["exact"],
            "estado": ["exact"],
            "codigo_encaminhamento": ["exact", "icontains"],
            "tipo_encaminhamento_id": ["exact"],
        }
        connection_class = ExtendedConnection


class ExecucaoSessaoGQLType(DjangoObjectType):
    """GraphQL Type for Session Execution"""

    sessao = graphene.Field(SessaoPEPGQLType)
    formador = graphene.Field(UserGQLType)
    supervisor = graphene.Field(UserGQLType)
    localidade = graphene.Field(LocationGQLType)

    class Meta:
        model = ExecucaoSessao
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "sessao_id": ["exact"],
            "formador_id": ["exact"],
            "supervisor_id": ["exact"],
            "localidade_id": ["exact"],
            "numero_cuidadores": ["exact"],
            "necessita_encaminhamento": ["exact"],
            "data_execucao": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


class SupervisaoSessaoGQLType(DjangoObjectType):
    """GraphQL Type for Session Supervision"""

    sessao = graphene.Field(SessaoPEPGQLType)
    supervisor = graphene.Field(UserGQLType)
    formador = graphene.Field(UserGQLType)
    localidade = graphene.Field(LocationGQLType)
    grupo = graphene.Field(GrupoFamiliarGQLType)

    class Meta:
        model = SupervisaoSessao
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "sessao_id": ["exact"],
            "supervisor_id": ["exact"],
            "formador_id": ["exact"],
            "localidade_id": ["exact"],
            "grupo_id": ["exact"],
            "numero_participantes": ["exact"],
            "necessita_encaminhamento": ["exact"],
            "data_supervisao": ["exact", "lt", "lte", "gt", "gte"],
            "identificador_grupo": ["exact", "icontains"],
        }
        connection_class = ExtendedConnection


class RelatorioDistEncaminhamentoGQLType(DjangoObjectType):
    """
    GraphQL Type para RelatorioDistEncaminhamento.
    Ligação estruturada entre RelatorioDistritalBimestral e PresencaSessao (estado=ENCA).
    Expõe o código de encaminhamento, família e tipo directamente da presença.
    """

    # Campos da presença expostos directamente para conveniência do frontend
    familia_id = graphene.String()
    nome_familia = graphene.String()
    codigo_encaminhamento = graphene.String()
    tipo_encaminhamento = graphene.Field(TipoEncaminhamentoGQLType)
    sessao_codigo = graphene.String()

    class Meta:
        model = RelatorioDistEncaminhamento
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "relatorio_id": ["exact"],
            "presenca_id": ["exact"],
            "presenca__familia_id": ["exact", "icontains"],
            "presenca__codigo_encaminhamento": ["exact", "icontains"],
        }
        connection_class = ExtendedConnection

    def resolve_familia_id(self, info, **kwargs):
        return self.presenca.familia_id if self.presenca_id else None

    def resolve_nome_familia(self, info, **kwargs):
        return self.presenca.nome_familia if self.presenca_id else None

    def resolve_codigo_encaminhamento(self, info, **kwargs):
        return self.presenca.codigo_encaminhamento if self.presenca_id else None

    def resolve_tipo_encaminhamento(self, info, **kwargs):
        return self.presenca.tipo_encaminhamento if self.presenca_id else None

    def resolve_sessao_codigo(self, info, **kwargs):
        return self.presenca.sessao.codigo_sessao if self.presenca_id else None


class RelatorioDistritalBimestralGQLType(DjangoObjectType):
    """GraphQL Type for District Bimonthly Report"""

    encaminhamentos_estruturados = graphene.List(RelatorioDistEncaminhamentoGQLType)

    class Meta:
        model = RelatorioDistritalBimestral
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "distrito_id": ["exact"],
            "coordenador_distrital_id": ["exact"],
            "periodo": ["exact"],
            "ano": ["exact", "lt", "lte", "gt", "gte"],
            "periodo_inicio": ["exact", "lt", "lte", "gt", "gte"],
            "periodo_fim": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection

    def resolve_encaminhamentos_estruturados(self, info, **kwargs):
        return self.encaminhamentos_estruturados.select_related(
            'presenca', 'presenca__tipo_encaminhamento', 'presenca__sessao'
        )


class EncaminhamentoSessaoGQLType(DjangoObjectType):
    """GraphQL Type for Session Referral"""

    sessao = graphene.Field(SessaoPEPGQLType)
    tecnico_responsavel = graphene.Field(UserGQLType)
    tipo_encaminhamento = graphene.Field(TipoEncaminhamentoGQLType)

    class Meta:
        model = EncaminhamentoSessao
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "sessao_id": ["exact"],
            "familia_id": ["exact", "icontains"],
            "nome_familia": ["exact", "icontains"],
            "codigo_encaminhamento": ["exact", "icontains"],
            "status": ["exact"],
            "tecnico_responsavel_id": ["exact"],
            "tipo_encaminhamento_id": ["exact"],
            "data_encaminhamento": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


class RoteiroReuniaoBimestralGQLType(DjangoObjectType):
    """GraphQL Type for Bimonthly Meeting Agenda"""

    coordenador_nacional = graphene.Field(UserGQLType)

    class Meta:
        model = RoteiroReuniaoBimestral
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "coordenador_nacional": ["exact"],
            "coordenador_nacional__username": ["exact", "icontains"],
            "data_reuniao": ["exact", "lt", "lte", "gt", "gte"],
            "data_proxima_reuniao": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


class RelatorioSupervisaoBimestralGQLType(DjangoObjectType):
    """GraphQL Type for Bimonthly Supervision Report"""

    distrito = graphene.Field(LocationGQLType)

    class Meta:
        model = RelatorioSupervisaoBimestral
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "distrito_id": ["exact"],
            "periodo": ["exact"],
            "ano": ["exact", "lt", "lte", "gt", "gte"],
            "numero_sessoes": ["exact", "lt", "lte", "gt", "gte"],
            "numero_tecnicos_formadores": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


# =============================================================================
# GQL TYPES — COORDENAÇÃO DISTRITAL
# =============================================================================

class CoordenacaoDistritalTecnicoGQLType(DjangoObjectType):
    """GraphQL Type for the M2M through table CoordenacaoDistritalTecnico (técnicos operacionais)"""

    tecnico = graphene.Field(UserGQLType)

    class Meta:
        model = CoordenacaoDistritalTecnico
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "coordenacao_id": ["exact"],
            "tecnico_id": ["exact"],
        }
        connection_class = ExtendedConnection


class CoordenacaoDistritalGQLType(DjangoObjectType):
    """GraphQL Type for CoordenacaoDistrital"""

    distrito = graphene.Field(LocationGQLType)
    coordenador = graphene.Field(UserGQLType)
    tecnico_administrativo = graphene.Field(UserGQLType)
    tecnicos_operacionais = graphene.List(CoordenacaoDistritalTecnicoGQLType)

    class Meta:
        model = CoordenacaoDistrital
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "distrito_id": ["exact"],
            "coordenador_id": ["exact"],
            "tecnico_administrativo_id": ["exact"],
            "ativo": ["exact"],
        }
        connection_class = ExtendedConnection

    def resolve_tecnicos_operacionais(self, info, **kwargs):
        return self.tecnicos_operacionais.all()


class PreviewRelatorioDistritalType(graphene.ObjectType):
    """
    Pré-visualização dos dados calculados automaticamente para um Relatório Distrital.

    Use a query previewRelatorioDistrital(distritoId, periodo, ano) para obter este objecto
    e pré-preencher o formulário antes de criar o relatório com createRelatorioDistrital.
    """
    distrito_id = graphene.Int()
    periodo = graphene.String()
    ano = graphene.Int()
    periodo_inicio = graphene.Date()
    periodo_fim = graphene.Date()

    # Coordenação (auto-preenchida a partir de CoordenacaoDistrital)
    coordenador_distrital_id = graphene.Int()
    coordenador_distrital_nome = graphene.String()
    tecnico_administrativo_id = graphene.Int()
    tecnico_administrativo_nome = graphene.String()

    # Indicadores calculados a partir dos registos existentes
    numero_sessoes_conduzidas = graphene.Int()
    numero_sessoes_esperadas = graphene.Int()
    numero_sessoes_perdidas = graphene.Int()
    numero_localidades_atendidas = graphene.Int()
    numero_tecnicos_formadores = graphene.Int()
    numero_familias_presentes = graphene.Int()
    numero_familias_esperadas = graphene.Int()
    numero_familias_migraram = graphene.Int()
    numero_familias_atendidas = graphene.Int()
    percentual_sessoes = graphene.Float()
    percentual_familias = graphene.Float()
    media_familia_presente = graphene.Float()
    media_familia_esperada = graphene.Float()


# =============================================================================
# GQL TYPES — ROLES / PERMISSIONS (global scope)
# =============================================================================

class PermissaoGQLType(graphene.ObjectType):
    """A single permission entry discovered from any installed module."""
    right_id = graphene.Int()
    nome = graphene.String()
    modulo = graphene.String()


class RoleSimpleGQLType(graphene.ObjectType):
    """Minimal role representation (id + name)."""
    id = graphene.ID()
    nome = graphene.String()


class RoleRightSimpleGQLType(graphene.ObjectType):
    """Minimal RoleRight representation."""
    id = graphene.ID()
    right_id = graphene.Int()


class Query(graphene.ObjectType):
    """Root Query for PEP+ module"""

    # ---- Gestão de roles/permissões (âmbito global) ----
    permissoes_disponiveis = graphene.List(
        PermissaoGQLType,
        modulo=graphene.String(description="Filtrar por nome do módulo (ex: 'pep_plus')"),
        description="Lista todas as permissões declaradas nos módulos instalados.",
    )
    permissoes_do_role = graphene.List(
        RoleRightSimpleGQLType,
        role_id=graphene.ID(required=True),
        description="Lista os right IDs activos atribuídos a um role.",
    )
    roles_do_utilizador = graphene.List(
        RoleSimpleGQLType,
        user_id=graphene.ID(required=True, description="PK do InteractiveUser"),
        description="Lista os roles activos de um utilizador.",
    )

    # ---- Parametrização: ModuloPEP ----
    modulo_pep = graphene.relay.Node.Field(ModuloPEPGQLType)
    modulos_pep = OrderedDjangoFilterConnectionField(
        ModuloPEPGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Parametrização: Escola ----
    escola = graphene.relay.Node.Field(EscolaGQLType)
    escolas = OrderedDjangoFilterConnectionField(
        EscolaGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Parametrização: Classe ----
    classe_parametro = graphene.relay.Node.Field(ClasseGQLType)
    classes = OrderedDjangoFilterConnectionField(
        ClasseGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Parametrização: Disciplina ----
    disciplina = graphene.relay.Node.Field(DisciplinaGQLType)
    disciplinas = OrderedDjangoFilterConnectionField(
        DisciplinaGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Parametrização: TipoEncaminhamento ----
    tipo_encaminhamento = graphene.relay.Node.Field(TipoEncaminhamentoGQLType)
    tipos_encaminhamento = OrderedDjangoFilterConnectionField(
        TipoEncaminhamentoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Alunos ----
    aluno = graphene.relay.Node.Field(AlunoGQLType)
    alunos = OrderedDjangoFilterConnectionField(
        AlunoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Educational Modules ----
    modulo_educacional = graphene.relay.Node.Field(ModuloEducacionalGQLType)
    modulos_educacionais = OrderedDjangoFilterConnectionField(
        ModuloEducacionalGQLType,
        # Filtros FK com Relay ID (tratados no resolver)
        aluno_id=graphene.String(description="Relay ID do Aluno"),
        escola_id=graphene.String(description="Relay ID da Escola (escola principal)"),
        escola_actual_id=graphene.String(description="Relay ID da Escola actual"),
        classe_id=graphene.String(description="Relay ID da Classe"),
        classe_que_frequenta_id=graphene.String(description="Relay ID da Classe que frequenta"),
        distrito_id=graphene.String(description="Relay ID do Distrito (via Aluno)"),
        localidade_id=graphene.String(description="Relay ID da Localidade (via Aluno)"),
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Family Groups ----
    grupo_familiar = graphene.relay.Node.Field(GrupoFamiliarGQLType)
    grupos_familiares = OrderedDjangoFilterConnectionField(
        GrupoFamiliarGQLType,
        distrito_id=graphene.String(description="Relay ID do distrito — filtra apenas os grupos desse distrito"),
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- PEP Sessions ----
    sessao_pep = graphene.relay.Node.Field(SessaoPEPGQLType)
    sessoes_pep = OrderedDjangoFilterConnectionField(
        SessaoPEPGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Session Attendance ----
    presenca_sessao = graphene.relay.Node.Field(PresencaSessaoGQLType)
    presencas_sessao = OrderedDjangoFilterConnectionField(
        PresencaSessaoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Session Execution ----
    execucao_sessao = graphene.relay.Node.Field(ExecucaoSessaoGQLType)
    execucoes_sessao = OrderedDjangoFilterConnectionField(
        ExecucaoSessaoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Session Supervision ----
    supervisao_sessao = graphene.relay.Node.Field(SupervisaoSessaoGQLType)
    supervisoes_sessao = OrderedDjangoFilterConnectionField(
        SupervisaoSessaoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- District Reports ----
    relatorio_distrital = graphene.relay.Node.Field(RelatorioDistritalBimestralGQLType)
    relatorios_distritais = OrderedDjangoFilterConnectionField(
        RelatorioDistritalBimestralGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Preview: calcular dados do relatório sem guardar ----
    preview_relatorio_distrital = graphene.Field(
        PreviewRelatorioDistritalType,
        distrito_id=graphene.String(required=True, description="Relay ID do Distrito"),
        periodo=graphene.String(required=True, description="BIM1 a BIM6"),
        ano=graphene.Int(required=True, description="Ano do relatório (ex: 2026)"),
        description=(
            "Calcula automaticamente todos os indicadores do relatório a partir dos registos "
            "existentes (SessaoPEP, PresencaSessao, ExecucaoSessao, CoordenacaoDistrital). "
            "Use para pré-preencher o formulário antes de criar o relatório."
        ),
    )

    # ---- Encaminhamentos estruturados de relatório ----
    relatorio_dist_encaminhamento = graphene.relay.Node.Field(RelatorioDistEncaminhamentoGQLType)
    relatorio_dist_encaminhamentos = OrderedDjangoFilterConnectionField(
        RelatorioDistEncaminhamentoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Query auxiliar: presenças ENCA disponíveis para incluir no relatório ----
    presencas_encaminhadas_disponiveis = OrderedDjangoFilterConnectionField(
        PresencaSessaoGQLType,
        distrito_id=graphene.String(required=True, description="Relay ID do Distrito"),
        periodo_inicio=graphene.String(required=True, description="Data início ISO (YYYY-MM-DD)"),
        periodo_fim=graphene.String(required=True, description="Data fim ISO (YYYY-MM-DD)"),
        orderBy=graphene.List(of_type=graphene.String),
        description="Retorna PresencaSessao com estado=ENCA do distrito no período. "
                    "Usar para popular o selector de encaminhamentos ao criar/editar um relatório."
    )

    # ---- Referrals ----
    encaminhamento_sessao = graphene.relay.Node.Field(EncaminhamentoSessaoGQLType)
    encaminhamentos_sessao = OrderedDjangoFilterConnectionField(
        EncaminhamentoSessaoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Bimonthly Meeting Agendas ----
    roteiro_reuniao_bimestral = graphene.relay.Node.Field(RoteiroReuniaoBimestralGQLType)
    roteiros_reuniao_bimestral = OrderedDjangoFilterConnectionField(
        RoteiroReuniaoBimestralGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Bimonthly Supervision Reports ----
    relatorio_supervisao_bimestral = graphene.relay.Node.Field(RelatorioSupervisaoBimestralGQLType)
    relatorios_supervisao_bimestral = OrderedDjangoFilterConnectionField(
        RelatorioSupervisaoBimestralGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Coordenação Distrital ----
    coordenacao_distrital = graphene.relay.Node.Field(CoordenacaoDistritalGQLType)
    coordenacoes_distritais = OrderedDjangoFilterConnectionField(
        CoordenacaoDistritalGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # =========================================================================
    # Resolvers
    # =========================================================================

    def resolve_modulos_pep(self, info, **kwargs):
        return ModuloPEP.objects.filter(validity_to__isnull=True)

    def resolve_escolas(self, info, **kwargs):
        return Escola.objects.filter(validity_to__isnull=True).select_related('distrito', 'localidade')

    def resolve_classes(self, info, **kwargs):
        return Classe.objects.filter(validity_to__isnull=True)

    def resolve_disciplinas(self, info, **kwargs):
        return Disciplina.objects.filter(validity_to__isnull=True)

    def resolve_tipos_encaminhamento(self, info, **kwargs):
        return TipoEncaminhamento.objects.filter(validity_to__isnull=True)

    def resolve_alunos(self, info, **kwargs):
        return Aluno.objects.filter(validity_to__isnull=True).select_related(
            'individual',
            'distrito', 'localidade',
            'escola', 'escola_actual',
            'classe', 'classe_que_frequenta',
        )

    def resolve_modulos_educacionais(self, info,
                                      aluno_id=None,
                                      escola_id=None,
                                      escola_actual_id=None,
                                      classe_id=None,
                                      classe_que_frequenta_id=None,
                                      distrito_id=None,
                                      localidade_id=None,
                                      **kwargs):
        from .utils import decode_id
        qs = ModuloEducacional.objects.filter(validity_to__isnull=True).select_related(
            'aluno', 'aluno__individual',
            'escola', 'escola_actual',
            'classe', 'classe_que_frequenta',
        )
        if aluno_id:
            qs = qs.filter(aluno_id=decode_id(aluno_id))
        if escola_id:
            qs = qs.filter(escola_id=decode_id(escola_id))
        if escola_actual_id:
            qs = qs.filter(escola_actual_id=decode_id(escola_actual_id))
        if classe_id:
            qs = qs.filter(classe_id=decode_id(classe_id))
        if classe_que_frequenta_id:
            qs = qs.filter(classe_que_frequenta_id=decode_id(classe_que_frequenta_id))
        if distrito_id:
            qs = qs.filter(aluno__distrito_id=decode_id(distrito_id))
        if localidade_id:
            qs = qs.filter(aluno__localidade_id=decode_id(localidade_id))
        return qs

    def resolve_grupos_familiares(self, info, distrito_id=None, **kwargs):
        from .utils import decode_id
        qs = GrupoFamiliar.objects.filter(validity_to__isnull=True).select_related(
            'distrito', 'localidade'
        )
        if distrito_id:
            qs = qs.filter(distrito_id=decode_id(distrito_id))
        return qs

    def resolve_sessoes_pep(self, info, **kwargs):
        queryset = SessaoPEP.objects.filter(validity_to__isnull=True).select_related(
            'coordenador_distrital',
            'tecnico_social',
            'distrito',
            'modulo',
            'grupo_familia',
            'grupo_familia__distrito',
            'grupo_familia__localidade'
        )
        total = queryset.count()
        logger.info(f"[PEP+] resolve_sessoes_pep: Found {total} sessions with validity_to IS NULL")
        all_sessions = SessaoPEP.objects.all().count()
        logger.info(f"[PEP+] Total sessions in DB (all): {all_sessions}")
        return queryset

    def resolve_presencas_sessao(self, info, **kwargs):
        return PresencaSessao.objects.filter(validity_to__isnull=True).select_related(
            'sessao',
            'sessao__coordenador_distrital',
            'sessao__tecnico_social',
            'sessao__distrito',
            'sessao__grupo_familia',
            'tipo_encaminhamento'
        )

    def resolve_execucoes_sessao(self, info, **kwargs):
        return ExecucaoSessao.objects.filter(validity_to__isnull=True).select_related(
            'sessao',
            'formador',
            'supervisor',
            'localidade'
        )

    def resolve_supervisoes_sessao(self, info, **kwargs):
        return SupervisaoSessao.objects.filter(validity_to__isnull=True).select_related(
            'sessao',
            'supervisor',
            'formador',
            'localidade',
            'grupo'
        )

    def resolve_relatorios_distritais(self, info, **kwargs):
        return RelatorioDistritalBimestral.objects.filter(validity_to__isnull=True)

    def resolve_preview_relatorio_distrital(self, info, distrito_id, periodo, ano, **kwargs):
        from .utils import decode_id
        from .services import RelatorioDistritalService

        class _Preview:
            def __init__(self, data):
                for k, v in data.items():
                    setattr(self, k, v)

        raw_distrito_id = decode_id(distrito_id)
        data = RelatorioDistritalService.generate(raw_distrito_id, periodo, ano, info.context.user)
        return _Preview(data)

    def resolve_relatorio_dist_encaminhamentos(self, info, **kwargs):
        return RelatorioDistEncaminhamento.objects.select_related(
            'relatorio', 'presenca', 'presenca__tipo_encaminhamento', 'presenca__sessao'
        )

    def resolve_presencas_encaminhadas_disponiveis(self, info, distrito_id=None,
                                                    periodo_inicio=None, periodo_fim=None, **kwargs):
        from .utils import decode_id
        from django.db.models import Q
        import datetime

        qs = PresencaSessao.objects.filter(
            validity_to__isnull=True,
            estado='ENCA',
        ).select_related('sessao', 'tipo_encaminhamento')

        if distrito_id:
            qs = qs.filter(sessao__distrito_id=decode_id(distrito_id))
        if periodo_inicio:
            qs = qs.filter(sessao__data_sessao__gte=periodo_inicio)
        if periodo_fim:
            qs = qs.filter(sessao__data_sessao__lte=periodo_fim)

        return qs

    def resolve_encaminhamentos_sessao(self, info, **kwargs):
        return EncaminhamentoSessao.objects.filter(validity_to__isnull=True).select_related(
            'sessao',
            'tecnico_responsavel',
            'tipo_encaminhamento'
        )

    def resolve_roteiros_reuniao_bimestral(self, info, **kwargs):
        return RoteiroReuniaoBimestral.objects.filter(validity_to__isnull=True).select_related(
            'coordenador_nacional'
        )

    def resolve_relatorios_supervisao_bimestral(self, info, **kwargs):
        return RelatorioSupervisaoBimestral.objects.filter(validity_to__isnull=True).select_related(
            'distrito'
        )

    def resolve_coordenacoes_distritais(self, info, **kwargs):
        return CoordenacaoDistrital.objects.filter(validity_to__isnull=True).select_related(
            'distrito', 'coordenador', 'tecnico_administrativo'
        ).prefetch_related('tecnicos_operacionais__tecnico')

    # ---- Roles / Permissions ----

    def resolve_permissoes_disponiveis(self, info, modulo=None, **kwargs):
        from .services import RolePermissaoService
        entries = RolePermissaoService.listar_permissoes_disponiveis(modulo=modulo)
        return [PermissaoGQLType(**e) for e in entries]

    def resolve_permissoes_do_role(self, info, role_id, **kwargs):
        from .services import RolePermissaoService
        user = info.context.user
        rows = RolePermissaoService.listar_permissoes_do_role(int(role_id), user)
        return [RoleRightSimpleGQLType(id=rr.pk, right_id=rr.right_id) for rr in rows]

    def resolve_roles_do_utilizador(self, info, user_id, **kwargs):
        from .services import RolePermissaoService
        user = info.context.user
        rows = RolePermissaoService.listar_roles_do_utilizador(int(user_id), user)
        return [RoleSimpleGQLType(id=ur.role_id, nome=ur.role.name) for ur in rows]
