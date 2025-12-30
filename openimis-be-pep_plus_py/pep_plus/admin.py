"""
Django Admin configuration for PEP+ module
"""
from django.contrib import admin
from .models import (
    ModuloEducacional,
    GrupoFamiliar,
    SessaoPEP,
    PresencaSessao,
    ExecucaoSessao,
    SupervisaoSessao,
    RelatorioDistritalBimestral,
    EncaminhamentoSessao,
    RoteiroReuniaoBimestral,
    RelatorioSupervisaoBimestral
)


@admin.register(ModuloEducacional)
class ModuloEducacionalAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'ordem', 'ativo', 'validity_from')
    list_filter = ('ativo', 'validity_from')
    search_fields = ('codigo', 'nome')
    ordering = ('ordem', 'codigo')


@admin.register(GrupoFamiliar)
class GrupoFamiliarAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'distrito', 'localidade', 'ativo', 'validity_from')
    list_filter = ('ativo', 'distrito', 'validity_from')
    search_fields = ('codigo', 'nome')
    ordering = ('codigo',)


@admin.register(SessaoPEP)
class SessaoPEPAdmin(admin.ModelAdmin):
    list_display = ('codigo_sessao', 'modulo', 'grupo_familia', 'data_sessao', 'status', 'tem_supervisao')
    list_filter = ('status', 'tem_supervisao', 'distrito', 'data_sessao')
    search_fields = ('codigo_sessao',)
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
    list_display = ('sessao', 'formador', 'data_execucao', 'localidade', 'necessita_encaminhamento')
    list_filter = ('necessita_encaminhamento', 'data_execucao')
    search_fields = ('formador__username',)
    date_hierarchy = 'data_execucao'
    ordering = ('-data_execucao',)


@admin.register(SupervisaoSessao)
class SupervisaoSessaoAdmin(admin.ModelAdmin):
    list_display = ('sessao', 'supervisor', 'formador', 'data_supervisao', 'identificador_grupo')
    list_filter = ('data_supervisao',)
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
    search_fields = ('coordenador_nacional', 'participantes')
    date_hierarchy = 'data_reuniao'
    ordering = ('-data_reuniao',)


@admin.register(RelatorioSupervisaoBimestral)
class RelatorioSupervisaoBimestralAdmin(admin.ModelAdmin):
    list_display = ('distrito', 'periodo', 'ano', 'num_sessoes_supervisionadas', 'num_tecnicos_supervisionados', 'periodo_inicio', 'periodo_fim')
    list_filter = ('periodo', 'ano', 'distrito')
    search_fields = ('nome_supervisores', 'distrito__name')
    ordering = ('-ano', '-periodo')
