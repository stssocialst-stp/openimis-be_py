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
    ModuloEducacional, GrupoFamiliar, SessaoPEP, PresencaSessao,
    ExecucaoSessao, SupervisaoSessao, RelatorioDistritalBimestral,
    EncaminhamentoSessao, RoteiroReuniaoBimestral, RelatorioSupervisaoBimestral
)


class ModuloEducacionalGQLType(DjangoObjectType):
    """GraphQL Type for Educational Module"""

    class Meta:
        model = ModuloEducacional
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "codigo": ["exact", "icontains"],
            "nome": ["exact", "icontains"],
            "ativo": ["exact"],
            "ordem": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


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
    modulo = graphene.Field(ModuloEducacionalGQLType)
    grupo_familia = graphene.Field(GrupoFamiliarGQLType)

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
            "data_sessao": ["exact", "lt", "lte", "gt", "gte"],
            "status": ["exact"],
            "tem_supervisao": ["exact"],
            "dia_semana": ["exact"],
        }
        connection_class = ExtendedConnection


class PresencaSessaoGQLType(DjangoObjectType):
    """GraphQL Type for Session Attendance"""

    sessao = graphene.Field(SessaoPEPGQLType)

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
            "necessita_encaminhamento": ["exact"],
            "data_execucao": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


class SupervisaoSessaoGQLType(DjangoObjectType):
    """GraphQL Type for Session Supervision"""

    sessao = graphene.Field(SessaoPEPGQLType)
    supervisor = graphene.Field(UserGQLType)
    formador = graphene.Field(UserGQLType)

    class Meta:
        model = SupervisaoSessao
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "sessao_id": ["exact"],
            "supervisor_id": ["exact"],
            "formador_id": ["exact"],
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
            "data_encaminhamento": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


class RoteiroReuniaoBimestralGQLType(DjangoObjectType):
    """GraphQL Type for Bimonthly Meeting Agenda"""

    class Meta:
        model = RoteiroReuniaoBimestral
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "coordenador_nacional": ["exact", "icontains"],
            "data_reuniao": ["exact", "lt", "lte", "gt", "gte"],
            "data_proxima_reuniao": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


class RelatorioSupervisaoBimestralGQLType(DjangoObjectType):
    """GraphQL Type for Bimonthly Supervision Report"""

    distrito = graphene.Field(LocationGQLType)
    modulo_maior_dificuldade = graphene.Field(ModuloEducacionalGQLType)

    class Meta:
        model = RelatorioSupervisaoBimestral
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "distrito_id": ["exact"],
            "periodo": ["exact"],
            "ano": ["exact", "lt", "lte", "gt", "gte"],
            "periodo_inicio": ["exact", "lt", "lte", "gt", "gte"],
            "periodo_fim": ["exact", "lt", "lte", "gt", "gte"],
            "nome_supervisores": ["exact", "icontains"],
        }
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    """Root Query for PEP+ module"""

    # Educational Modules
    modulo_educacional = graphene.relay.Node.Field(ModuloEducacionalGQLType)
    modulos_educacionais = OrderedDjangoFilterConnectionField(
        ModuloEducacionalGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # Family Groups
    grupo_familiar = graphene.relay.Node.Field(GrupoFamiliarGQLType)
    grupos_familiares = OrderedDjangoFilterConnectionField(
        GrupoFamiliarGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # PEP Sessions
    sessao_pep = graphene.relay.Node.Field(SessaoPEPGQLType)
    sessoes_pep = OrderedDjangoFilterConnectionField(
        SessaoPEPGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # Session Attendance
    presenca_sessao = graphene.relay.Node.Field(PresencaSessaoGQLType)
    presencas_sessao = OrderedDjangoFilterConnectionField(
        PresencaSessaoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # Session Execution
    execucao_sessao = graphene.relay.Node.Field(ExecucaoSessaoGQLType)
    execucoes_sessao = OrderedDjangoFilterConnectionField(
        ExecucaoSessaoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # Session Supervision
    supervisao_sessao = graphene.relay.Node.Field(SupervisaoSessaoGQLType)
    supervisoes_sessao = OrderedDjangoFilterConnectionField(
        SupervisaoSessaoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # District Reports
    relatorio_distrital = graphene.relay.Node.Field(RelatorioDistritalBimestralGQLType)
    relatorios_distritais = OrderedDjangoFilterConnectionField(
        RelatorioDistritalBimestralGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # Referrals
    encaminhamento_sessao = graphene.relay.Node.Field(EncaminhamentoSessaoGQLType)
    encaminhamentos_sessao = OrderedDjangoFilterConnectionField(
        EncaminhamentoSessaoGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # Bimonthly Meeting Agendas
    roteiro_reuniao_bimestral = graphene.relay.Node.Field(RoteiroReuniaoBimestralGQLType)
    roteiros_reuniao_bimestral = OrderedDjangoFilterConnectionField(
        RoteiroReuniaoBimestralGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    # Bimonthly Supervision Reports
    relatorio_supervisao_bimestral = graphene.relay.Node.Field(RelatorioSupervisaoBimestralGQLType)
    relatorios_supervisao_bimestral = OrderedDjangoFilterConnectionField(
        RelatorioSupervisaoBimestralGQLType,
        orderBy=graphene.List(of_type=graphene.String)
    )

    def resolve_modulos_educacionais(self, info, **kwargs):
        """Resolve educational modules query"""
        return ModuloEducacional.objects.filter(validity_to__isnull=True)

    def resolve_grupos_familiares(self, info, **kwargs):
        """Resolve family groups query"""
        return GrupoFamiliar.objects.filter(validity_to__isnull=True).select_related(
            'distrito', 'localidade'
        )

    def resolve_sessoes_pep(self, info, **kwargs):
        """Resolve PEP sessions query"""
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
        """Resolve session attendance query"""
        return PresencaSessao.objects.filter(validity_to__isnull=True).select_related(
            'sessao',
            'sessao__coordenador_distrital',
            'sessao__tecnico_social',
            'sessao__distrito',
            'sessao__modulo',
            'sessao__grupo_familia'
        )

    def resolve_execucoes_sessao(self, info, **kwargs):
        """Resolve session execution query"""
        return ExecucaoSessao.objects.filter(validity_to__isnull=True).select_related(
            'sessao',
            'formador',
            'supervisor',
            'localidade'
        )

    def resolve_supervisoes_sessao(self, info, **kwargs):
        """Resolve session supervision query"""
        return SupervisaoSessao.objects.filter(validity_to__isnull=True).select_related(
            'sessao',
            'supervisor',
            'formador'
        )

    def resolve_relatorios_distritais(self, info, **kwargs):
        """Resolve district reports query"""
        return RelatorioDistritalBimestral.objects.filter(validity_to__isnull=True)

    def resolve_encaminhamentos_sessao(self, info, **kwargs):
        """Resolve referrals query"""
        return EncaminhamentoSessao.objects.filter(validity_to__isnull=True).select_related(
            'sessao',
            'tecnico_responsavel'
        )

    def resolve_roteiros_reuniao_bimestral(self, info, **kwargs):
        """Resolve bimonthly meeting agendas query"""
        return RoteiroReuniaoBimestral.objects.filter(validity_to__isnull=True)

    def resolve_relatorios_supervisao_bimestral(self, info, **kwargs):
        """Resolve bimonthly supervision reports query"""
        return RelatorioSupervisaoBimestral.objects.filter(validity_to__isnull=True).select_related(
            'distrito', 'modulo_maior_dificuldade'
        )
