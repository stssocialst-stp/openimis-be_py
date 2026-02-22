"""
Django Admin configuration for PEP+ module
"""
from django.contrib import admin
from .models import (
    ModuloPEP,
    Escola,
    Classe,
    ClasseDisciplina,
    Disciplina,
    TipoEncaminhamento,
    Aluno,
    ModuloEducacional,
    ModuloEducacionalDisciplina,
    GrupoFamiliar,
    SessaoPEP,
    PresencaSessao,
    ExecucaoSessao,
    SupervisaoSessao,
    RelatorioDistritalBimestral,
    EncaminhamentoSessao,
    RoteiroReuniaoBimestral,
    RelatorioSupervisaoBimestral,
    CoordenacaoDistrital,
    CoordenacaoDistritalTecnico,
)


# =============================================================================
# TABELAS DE PARAMETRIZAÇÃO
# =============================================================================

@admin.register(ModuloPEP)
class ModuloPEPAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'ordem', 'duracao_semanas', 'ativo', 'validity_from')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'nome')
    ordering = ('ordem', 'codigo')


@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'nivel', 'distrito', 'ativo', 'validity_from')
    list_filter = ('nivel', 'ativo', 'distrito')
    search_fields = ('nome', 'codigo')
    ordering = ('nome',)


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'nivel', 'ordem', 'ativo', 'validity_from')
    list_filter = ('nivel', 'ativo')
    search_fields = ('codigo', 'nome')
    ordering = ('ordem', 'codigo')


@admin.register(ClasseDisciplina)
class ClasseDisciplinaAdmin(admin.ModelAdmin):
    list_display = ('classe', 'disciplina')
    list_filter = ('classe__nivel', 'disciplina__nivel')
    search_fields = ('classe__nome', 'classe__codigo', 'disciplina__nome')
    ordering = ('classe', 'disciplina')


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nivel', 'faixa_faltas_aceitaveis', 'quantidade_faltas_aceitaveis', 'ativo', 'validity_from')
    list_filter = ('nivel', 'ativo', 'faixa_faltas_aceitaveis')
    search_fields = ('nome',)
    ordering = ('nivel', 'nome')


@admin.register(TipoEncaminhamento)
class TipoEncaminhamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'ativo', 'validity_from')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'nome')
    ordering = ('codigo',)


@admin.register(ModuloEducacionalDisciplina)
class ModuloEducacionalDisciplinaAdmin(admin.ModelAdmin):
    list_display = ('modulo', 'disciplina', 'tipo')
    list_filter = ('tipo', 'disciplina__nivel')
    search_fields = ('modulo__nome', 'disciplina__nome')
    ordering = ('modulo', 'tipo', 'disciplina')


@admin.register(ModuloEducacional)
class ModuloEducacionalAdmin(admin.ModelAdmin):
    list_display = ('id_membro_crianca', 'nome', 'nome_encarregado', 'escola_actual', 'classe', 'idade', 'validity_from')
    list_filter = ('sexo', 'classe', 'faixa_de_faltas', 'aproveitamento_primeiro_trimestre', 'validity_from')
    search_fields = ('id_membro_crianca', 'nome', 'nome_encarregado', 'id_da_crianca')
    ordering = ('nome',)


@admin.register(GrupoFamiliar)
class GrupoFamiliarAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'distrito', 'localidade', 'ativo', 'validity_from')
    list_filter = ('ativo', 'distrito', 'validity_from')
    search_fields = ('codigo', 'nome')
    ordering = ('codigo',)


@admin.register(SessaoPEP)
class SessaoPEPAdmin(admin.ModelAdmin):
    list_display = ('codigo_sessao', 'modulo', 'grupo_familia', 'data_planejamento', 'data_sessao', 'status', 'tem_supervisao')
    list_filter = ('status', 'tem_supervisao', 'distrito', 'data_sessao', 'data_planejamento', 'modulo')
    search_fields = ('codigo_sessao', 'modulo__nome', 'modulo__codigo')
    date_hierarchy = 'data_sessao'
    ordering = ('-data_sessao',)


@admin.register(PresencaSessao)
class PresencaSessaoAdmin(admin.ModelAdmin):
    list_display = ('sessao', 'familia_id', 'nome_familia', 'estado', 'grupo_id')
    list_filter = ('estado', 'sessao__data_sessao')
    search_fields = ('familia_id', 'nome_familia', 'codigo_encaminhamento')
    ordering = ('sessao', 'nome_familia')


@admin.register(ExecucaoSessao)
class ExecucaoSessaoAdmin(admin.ModelAdmin):
    list_display = ('sessao', 'formador', 'numero_cuidadores', 'data_execucao', 'localidade', 'necessita_encaminhamento')
    list_filter = ('necessita_encaminhamento', 'numero_cuidadores', 'data_execucao')
    search_fields = ('formador__username', 'sessao__codigo_sessao')
    date_hierarchy = 'data_execucao'
    ordering = ('-data_execucao',)
    readonly_fields = ('data_execucao',)


@admin.register(SupervisaoSessao)
class SupervisaoSessaoAdmin(admin.ModelAdmin):
    list_display = ('sessao', 'supervisor', 'formador', 'localidade', 'numero_participantes', 'necessita_encaminhamento', 'data_supervisao')
    list_filter = ('necessita_encaminhamento', 'numero_participantes', 'data_supervisao')
    search_fields = ('supervisor__username', 'formador__username', 'identificador_grupo')
    date_hierarchy = 'data_supervisao'
    ordering = ('-data_supervisao',)


@admin.register(RelatorioDistritalBimestral)
class RelatorioDistritalBimestralAdmin(admin.ModelAdmin):
    list_display = ('distrito', 'periodo', 'ano', 'coordenador_distrital', 'periodo_inicio', 'periodo_fim')
    list_filter = ('periodo', 'ano', 'distrito')
    search_fields = ('distrito__code', 'coordenador_distrital__username')
    ordering = ('-ano', '-periodo')


@admin.register(EncaminhamentoSessao)
class EncaminhamentoSessaoAdmin(admin.ModelAdmin):
    list_display = ('sessao', 'familia_id', 'nome_familia', 'codigo_encaminhamento', 'status', 'data_encaminhamento')
    list_filter = ('status', 'data_encaminhamento')
    search_fields = ('familia_id', 'nome_familia', 'codigo_encaminhamento')
    date_hierarchy = 'data_encaminhamento'
    ordering = ('-data_encaminhamento',)


@admin.register(RoteiroReuniaoBimestral)
class RoteiroReuniaoBimestralAdmin(admin.ModelAdmin):
    list_display = ('data_reuniao', 'coordenador_nacional', 'horario', 'data_proxima_reuniao')
    list_filter = ('data_reuniao', 'coordenador_nacional')
    search_fields = ('coordenador_nacional__username', 'principais_desafios', 'oportunidades_melhoria')
    date_hierarchy = 'data_reuniao'
    ordering = ('-data_reuniao',)


@admin.register(RelatorioSupervisaoBimestral)
class RelatorioSupervisaoBimestralAdmin(admin.ModelAdmin):
    list_display = ('distrito', 'periodo', 'ano', 'numero_sessoes', 'numero_tecnicos_formadores')
    list_filter = ('periodo', 'ano', 'distrito')
    search_fields = ('distrito__name', 'observacoes')
    ordering = ('-ano', '-periodo')


# =============================================================================
# ALUNO
# =============================================================================

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = (
        'individual_nome', 'sexo', 'escola', 'classe',
        'escolaridade_actual', 'distrito', 'ativo',
    )
    list_filter = ('sexo', 'escolaridade_actual', 'ativo', 'escola', 'classe', 'distrito')
    search_fields = (
        'individual__first_name', 'individual__last_name',
        'id_membro_crianca', 'id_da_crianca', 'nome_encarregado',
    )
    ordering = ('individual__first_name', 'individual__last_name')
    raw_id_fields = ('individual', 'escola', 'escola_actual', 'classe', 'classe_que_frequenta')

    def individual_nome(self, obj):
        return f"{obj.individual.first_name} {obj.individual.last_name}" if obj.individual_id else '—'
    individual_nome.short_description = 'Nome'


# =============================================================================
# COORDENAÇÃO DISTRITAL
# =============================================================================

class CoordenacaoDistritalTecnicoInline(admin.TabularInline):
    """Inline dos técnicos operacionais dentro de CoordenacaoDistrital"""
    model = CoordenacaoDistritalTecnico
    extra = 1
    fields = ('tecnico',)
    autocomplete_fields = []
    verbose_name = 'Técnico Operacional'
    verbose_name_plural = 'Técnicos Operacionais'


@admin.register(CoordenacaoDistrital)
class CoordenacaoDistritalAdmin(admin.ModelAdmin):
    list_display = (
        'distrito', 'coordenador', 'tecnico_administrativo',
        'num_tecnicos_operacionais', 'ativo',
    )
    list_filter = ('ativo', 'distrito')
    search_fields = (
        'distrito__name', 'coordenador__username',
        'tecnico_administrativo__username',
    )
    ordering = ('distrito',)
    inlines = [CoordenacaoDistritalTecnicoInline]
    raw_id_fields = ('coordenador', 'tecnico_administrativo')

    def num_tecnicos_operacionais(self, obj):
        return obj.tecnicos_operacionais.count()
    num_tecnicos_operacionais.short_description = 'Nº Técnicos Operacionais'
