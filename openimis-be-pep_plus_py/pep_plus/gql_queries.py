"""
PEP+ GraphQL Queries
Implements READ operations for all PEP+ entities
"""
import graphene
from graphene_django import DjangoObjectType
from core.schema import OrderedDjangoFilterConnectionField
from core import ExtendedConnection
from .models import (
    ModuloEducacional, GrupoFamiliar, SessaoPEP, PresencaSessao,
    ExecucaoSessao, SupervisaoSessao, RelatorioDistritalBimestral,
    EncaminhamentoSessao
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

    def resolve_modulos_educacionais(self, info, **kwargs):
        """Resolve educational modules query"""
        return ModuloEducacional.objects.filter(validity_to__isnull=True)

    def resolve_grupos_familiares(self, info, **kwargs):
        """Resolve family groups query"""
        return GrupoFamiliar.objects.filter(validity_to__isnull=True)

    def resolve_sessoes_pep(self, info, **kwargs):
        """Resolve PEP sessions query"""
        return SessaoPEP.objects.filter(validity_to__isnull=True)

    def resolve_presencas_sessao(self, info, **kwargs):
        """Resolve session attendance query"""
        return PresencaSessao.objects.filter(validity_to__isnull=True)

    def resolve_execucoes_sessao(self, info, **kwargs):
        """Resolve session execution query"""
        return ExecucaoSessao.objects.filter(validity_to__isnull=True)

    def resolve_supervisoes_sessao(self, info, **kwargs):
        """Resolve session supervision query"""
        return SupervisaoSessao.objects.filter(validity_to__isnull=True)

    def resolve_relatorios_distritais(self, info, **kwargs):
        """Resolve district reports query"""
        return RelatorioDistritalBimestral.objects.filter(validity_to__isnull=True)

    def resolve_encaminhamentos_sessao(self, info, **kwargs):
        """Resolve referrals query"""
        return EncaminhamentoSessao.objects.filter(validity_to__isnull=True)
