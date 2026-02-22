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
    ModuloEducacional, ModuloEducacionalDisciplina,
    GrupoFamiliar, SessaoPEP, PresencaSessao,
    ExecucaoSessao, SupervisaoSessao, RelatorioDistritalBimestral,
    EncaminhamentoSessao, RoteiroReuniaoBimestral, RelatorioSupervisaoBimestral
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

class ModuloEducacionalGQLType(DjangoObjectType):
    """GraphQL Type for Assiduidade Escolar (Educational Module)"""

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
            "escola_id": ["exact"],
            "escola_actual_id": ["exact"],
            "escolaridade_actual": ["exact"],
            "id_da_crianca": ["exact", "icontains"],
            "sexo": ["exact"],
            "dados_escolar_correctos": ["exact"],
            "classe_id": ["exact"],
            "idade": ["exact", "lt", "lte", "gt", "gte"],
            "dados_escolares_correctos": ["exact"],
            "classe_que_frequenta_id": ["exact"],
            "aproveitamento_primeiro_trimestre": ["exact"],
            "faixa_de_faltas": ["exact"],
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
            "distrito_id": ["exact"],
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


class RelatorioDistritalBimestralGQLType(DjangoObjectType):
    """GraphQL Type for District Bimonthly Report"""

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


class Query(graphene.ObjectType):
    """Root Query for PEP+ module"""

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

    # ---- Educational Modules ----
    modulo_educacional = graphene.relay.Node.Field(ModuloEducacionalGQLType)
    modulos_educacionais = OrderedDjangoFilterConnectionField(
        ModuloEducacionalGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # ---- Family Groups ----
    grupo_familiar = graphene.relay.Node.Field(GrupoFamiliarGQLType)
    grupos_familiares = OrderedDjangoFilterConnectionField(
        GrupoFamiliarGQLType,
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

    def resolve_modulos_educacionais(self, info, **kwargs):
        return ModuloEducacional.objects.filter(validity_to__isnull=True).select_related(
            'escola', 'escola_actual', 'classe', 'classe_que_frequenta'
        )

    def resolve_grupos_familiares(self, info, **kwargs):
        return GrupoFamiliar.objects.filter(validity_to__isnull=True).select_related(
            'distrito', 'localidade'
        )

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
