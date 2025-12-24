"""
PEP+ Models
Defines all database models for the PEP+ (Programa de Educação Positiva) system
"""
import uuid
from django.db import models
from django.conf import settings
from core import models as core_models
from location.models import Location


class ModuloEducacional(core_models.VersionedModel):
    """
    Educational Module - Represents a PEP+ educational module
    """
    id = models.AutoField(db_column='ModuloEducacionalID', primary_key=True)
    uuid = models.CharField(db_column='ModuloEducacionalUUID', max_length=36, default=uuid.uuid4, unique=True)

    codigo = models.CharField(db_column='Codigo', max_length=50, unique=True)
    nome = models.CharField(db_column='Nome', max_length=255)
    descricao = models.TextField(db_column='Descricao', null=True, blank=True)
    ordem = models.IntegerField(db_column='Ordem', default=0)
    duracao_semanas = models.IntegerField(db_column='DuracaoSemanas', default=1)
    ativo = models.BooleanField(db_column='Ativo', default=True)

    class Meta:
        managed = True
        db_table = 'tblModuloEducacional'

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class GrupoFamiliar(core_models.VersionedModel):
    """
    Family Group - Represents a group of families attending sessions together
    """
    id = models.AutoField(db_column='GrupoFamiliarID', primary_key=True)
    uuid = models.CharField(db_column='GrupoFamiliarUUID', max_length=36, default=uuid.uuid4, unique=True)

    codigo = models.CharField(db_column='Codigo', max_length=50, unique=True)
    nome = models.CharField(db_column='Nome', max_length=255)
    distrito = models.ForeignKey(Location, db_column='DistritoID', on_delete=models.PROTECT,
                                 related_name='grupos_familiares')
    localidade = models.ForeignKey(Location, db_column='LocalidadeID', on_delete=models.PROTECT,
                                    related_name='grupos_familiares_localidade', null=True, blank=True)
    numero_familias = models.IntegerField(db_column='NumeroFamilias', default=0)
    ativo = models.BooleanField(db_column='Ativo', default=True)

    class Meta:
        managed = True
        db_table = 'tblGrupoFamiliar'

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class SessaoPEP(core_models.VersionedModel):
    """
    PEP Session - Planning of educational sessions (Ferramenta 1)
    """
    DIAS_SEMANA = [
        ('SEG', 'Segunda-feira'),
        ('TER', 'Terça-feira'),
        ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'),
        ('SEX', 'Sexta-feira'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    ]

    id = models.AutoField(db_column='SessaoPEPID', primary_key=True)
    uuid = models.CharField(db_column='SessaoPEPUUID', max_length=36, default=uuid.uuid4, unique=True)

    # Campos obrigatórios
    codigo_sessao = models.CharField(db_column='CodigoSessao', max_length=50, unique=True)
    coordenador_distrital = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column='CoordenadorDistritalID',
        on_delete=models.PROTECT,
        related_name='sessoes_coordenadas'
    )
    tecnico_social = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column='TecnicoSocialID',
        on_delete=models.PROTECT,
        related_name='sessoes_tecnico'
    )
    distrito = models.ForeignKey(Location, db_column='DistritoID', on_delete=models.PROTECT)
    modulo = models.ForeignKey(ModuloEducacional, db_column='ModuloID', on_delete=models.PROTECT)
    mes_modulo_anterior = models.CharField(db_column='MesModuloAnterior', max_length=50, null=True, blank=True)

    # Detalhes da sessão
    dia_semana = models.CharField(db_column='DiaSemana', max_length=3, choices=DIAS_SEMANA)
    data_sessao = models.DateField(db_column='DataSessao')
    hora_sessao = models.TimeField(db_column='HoraSessao')
    zona = models.CharField(db_column='Zona', max_length=255)
    numero_familias = models.IntegerField(db_column='NumeroFamilias')
    grupo_familia = models.ForeignKey(GrupoFamiliar, db_column='GrupoFamiliaID', on_delete=models.PROTECT)

    # Campos opcionais
    tempo_deslocamento = models.IntegerField(db_column='TempoDeslocamento', null=True, blank=True,
                                            help_text='Tempo em minutos')
    feedback_documentacao = models.TextField(db_column='FeedbackDocumentacao')
    tem_supervisao = models.BooleanField(db_column='TemSupervisao', default=False)
    observacoes = models.TextField(db_column='Observacoes', null=True, blank=True)

    # Status
    STATUS_CHOICES = [
        ('PLAN', 'Planeada'),
        ('EXEC', 'Executada'),
        ('CANC', 'Cancelada'),
    ]
    status = models.CharField(db_column='Status', max_length=4, choices=STATUS_CHOICES, default='PLAN')

    class Meta:
        managed = True
        db_table = 'tblSessaoPEP'
        ordering = ['-data_sessao', '-hora_sessao']

    def __str__(self):
        return f"{self.codigo_sessao} - {self.data_sessao}"


class PresencaSessao(core_models.VersionedModel):
    """
    Session Attendance - Registration of family attendance (Ferramenta 2)
    """
    ESTADO_CHOICES = [
        ('PRES', 'Presente'),
        ('AUSE', 'Ausente'),
        ('JUST', 'Justificado'),
    ]

    id = models.AutoField(db_column='PresencaSessaoID', primary_key=True)
    uuid = models.CharField(db_column='PresencaSessaoUUID', max_length=36, default=uuid.uuid4, unique=True)

    sessao = models.ForeignKey(SessaoPEP, db_column='SessaoID', on_delete=models.CASCADE,
                               related_name='presencas')
    # Usando CharField para ID da família para flexibilidade de integração
    familia_id = models.CharField(db_column='FamiliaID', max_length=50)
    nome_familia = models.CharField(db_column='NomeFamilia', max_length=255)
    grupo_id = models.CharField(db_column='GrupoID', max_length=50, null=True, blank=True)

    estado = models.CharField(db_column='Estado', max_length=4, choices=ESTADO_CHOICES, default='PRES')
    codigo_encaminhamento = models.CharField(db_column='CodigoEncaminhamento', max_length=50,
                                            null=True, blank=True)
    observacoes = models.TextField(db_column='Observacoes', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'tblPresencaSessao'
        unique_together = [['sessao', 'familia_id']]

    def __str__(self):
        return f"{self.nome_familia} - {self.sessao.codigo_sessao}"


class ExecucaoSessao(core_models.VersionedModel):
    """
    Session Execution - Tracks session implementation (Ferramenta 3)
    """
    id = models.AutoField(db_column='ExecucaoSessaoID', primary_key=True)
    uuid = models.CharField(db_column='ExecucaoSessaoUUID', max_length=36, default=uuid.uuid4, unique=True)

    sessao = models.OneToOneField(SessaoPEP, db_column='SessaoID', on_delete=models.CASCADE,
                                  related_name='execucao')
    formador = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='FormadorID',
                                on_delete=models.PROTECT, related_name='sessoes_formadas')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='SupervisorID',
                                  on_delete=models.PROTECT, related_name='sessoes_supervisionadas',
                                  null=True, blank=True)
    localidade = models.ForeignKey(Location, db_column='LocalidadeID', on_delete=models.PROTECT,
                                   null=True, blank=True)

    # Avaliação da execução
    numero_participantes_compromissos = models.IntegerField(db_column='NumeroParticipantesCompromissos',
                                                            default=0)
    praticas_positivas = models.JSONField(db_column='PraticasPositivas', default=list, blank=True)
    desafios_transmissao = models.JSONField(db_column='DesafiosTransmissao', default=list, blank=True)
    necessita_encaminhamento = models.BooleanField(db_column='NecessitaEncaminhamento', default=False)

    # Auto-avaliação do formador
    auto_avaliacao_pontos_fortes = models.JSONField(db_column='AutoAvaliacaoPontosFortes',
                                                    default=list, blank=True)
    auto_avaliacao_pontos_atencao = models.JSONField(db_column='AutoAvaliacaoPontosAtencao',
                                                     default=list, blank=True)
    avaliacao_metodologia = models.JSONField(db_column='AvaliacaoMetodologia', default=dict, blank=True)

    observacoes = models.TextField(db_column='Observacoes', null=True, blank=True)
    data_execucao = models.DateTimeField(db_column='DataExecucao', auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'tblExecucaoSessao'

    def __str__(self):
        return f"Execução - {self.sessao.codigo_sessao}"


class SupervisaoSessao(core_models.VersionedModel):
    """
    Session Supervision - Supervision of session execution (Ferramenta 4)
    """
    id = models.AutoField(db_column='SupervisaoSessaoID', primary_key=True)
    uuid = models.CharField(db_column='SupervisaoSessaoUUID', max_length=36, default=uuid.uuid4, unique=True)

    sessao = models.ForeignKey(SessaoPEP, db_column='SessaoID', on_delete=models.CASCADE,
                              related_name='supervisoes')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='SupervisorID',
                                  on_delete=models.PROTECT, related_name='supervisoes_realizadas')
    formador = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='FormadorID',
                                on_delete=models.PROTECT, related_name='supervisoes_recebidas')

    data_supervisao = models.DateField(db_column='DataSupervisao')
    data_modulo_anterior = models.DateField(db_column='DataModuloAnterior', null=True, blank=True)
    identificador_grupo = models.CharField(db_column='IdentificadorGrupo', max_length=50)

    # Avaliação da supervisão (perguntas Sim/Não armazenadas como JSON)
    perguntas_avaliacao = models.JSONField(db_column='PerguntasAvaliacao', default=dict)
    pontos_positivos = models.TextField(db_column='PontosPositivos', null=True, blank=True)
    pontos_melhorar = models.TextField(db_column='PontosMelhorar', null=True, blank=True)
    observacoes = models.TextField(db_column='Observacoes', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'tblSupervisaoSessao'
        ordering = ['-data_supervisao']

    def __str__(self):
        return f"Supervisão - {self.sessao.codigo_sessao} - {self.data_supervisao}"


class RelatorioDistritalBimestral(core_models.VersionedModel):
    """
    District Bimonthly Report - Consolidates bimonthly data (Ferramenta 5)
    """
    PERIODO_CHOICES = [
        ('BIM1', '1º Bimestre (Jan-Fev)'),
        ('BIM2', '2º Bimestre (Mar-Abr)'),
        ('BIM3', '3º Bimestre (Mai-Jun)'),
        ('BIM4', '4º Bimestre (Jul-Ago)'),
        ('BIM5', '5º Bimestre (Set-Out)'),
        ('BIM6', '6º Bimestre (Nov-Dez)'),
    ]

    id = models.AutoField(db_column='RelatorioDistritalID', primary_key=True)
    uuid = models.CharField(db_column='RelatorioDistritalUUID', max_length=36, default=uuid.uuid4, unique=True)

    distrito = models.ForeignKey(Location, db_column='DistritoID', on_delete=models.PROTECT)
    coordenador_distrital = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='CoordenadorID',
                                             on_delete=models.PROTECT, related_name='relatorios_coordenados')
    tecnico_administrativo = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='TecnicoAdminID',
                                              on_delete=models.PROTECT, related_name='relatorios_admin',
                                              null=True, blank=True)

    periodo = models.CharField(db_column='Periodo', max_length=4, choices=PERIODO_CHOICES)
    ano = models.IntegerField(db_column='Ano')
    periodo_inicio = models.DateField(db_column='PeriodoInicio')
    periodo_fim = models.DateField(db_column='PeriodoFim')

    # Estatísticas gerais
    numero_localidades_atendidas = models.IntegerField(db_column='NumeroLocalidadesAtendidas', default=0)
    numero_familias_atendidas = models.IntegerField(db_column='NumeroFamiliasAtendidas', default=0)
    numero_tecnicos_formadores = models.IntegerField(db_column='NumeroTecnicosFormadores', default=0)
    numero_sessoes_conduzidas = models.IntegerField(db_column='NumeroSessoesConduzidas', default=0)
    numero_sessoes_esperadas = models.IntegerField(db_column='NumeroSessoesEsperadas', default=0)
    numero_familias_presentes = models.IntegerField(db_column='NumeroFamiliasPresentes', default=0)
    numero_familias_esperadas = models.IntegerField(db_column='NumeroFamiliasEsperadas', default=0)

    # Percentuais calculados
    percentual_sessoes = models.DecimalField(db_column='PercentualSessoes', max_digits=5,
                                            decimal_places=2, default=0)
    percentual_familias = models.DecimalField(db_column='PercentualFamilias', max_digits=5,
                                             decimal_places=2, default=0)

    # Estatísticas adicionais
    numero_familias_migraram = models.IntegerField(db_column='NumeroFamiliasMigraram', default=0)
    numero_sessoes_perdidas = models.IntegerField(db_column='NumeroSessoesPerdidas', default=0)
    media_familia_presente = models.DecimalField(db_column='MediaFamiliaPresente', max_digits=5,
                                                decimal_places=2, default=0)
    media_familia_esperada = models.DecimalField(db_column='MediaFamiliaEsperada', max_digits=5,
                                                decimal_places=2, default=0)

    # Dados detalhados por técnico (JSON)
    dados_tecnicos = models.JSONField(db_column='DadosTecnicos', default=list, blank=True)

    # Dados de encaminhamentos
    dados_encaminhamentos = models.JSONField(db_column='DadosEncaminhamentos', default=list, blank=True)

    observacoes = models.TextField(db_column='Observacoes', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'tblRelatorioDistritalBimestral'
        unique_together = [['distrito', 'periodo', 'ano']]
        ordering = ['-ano', '-periodo']

    def __str__(self):
        return f"Relatório {self.distrito} - {self.periodo}/{self.ano}"


class EncaminhamentoSessao(core_models.VersionedModel):
    """
    Session Referral - Tracks referrals made during sessions
    """
    id = models.AutoField(db_column='EncaminhamentoID', primary_key=True)
    uuid = models.CharField(db_column='EncaminhamentoUUID', max_length=36, default=uuid.uuid4, unique=True)

    sessao = models.ForeignKey(SessaoPEP, db_column='SessaoID', on_delete=models.CASCADE,
                              related_name='encaminhamentos')
    familia_id = models.CharField(db_column='FamiliaID', max_length=50)
    nome_familia = models.CharField(db_column='NomeFamilia', max_length=255)

    codigo_encaminhamento = models.CharField(db_column='CodigoEncaminhamento', max_length=50)
    descricao = models.TextField(db_column='Descricao')

    STATUS_CHOICES = [
        ('PEND', 'Pendente'),
        ('PROC', 'Em Processo'),
        ('CONC', 'Concluído'),
        ('CANC', 'Cancelado'),
    ]
    status = models.CharField(db_column='Status', max_length=4, choices=STATUS_CHOICES, default='PEND')

    tecnico_responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='TecnicoResponsavelID',
                                           on_delete=models.PROTECT, related_name='encaminhamentos_responsavel',
                                           null=True, blank=True)
    data_encaminhamento = models.DateField(db_column='DataEncaminhamento', auto_now_add=True)
    data_conclusao = models.DateField(db_column='DataConclusao', null=True, blank=True)

    observacoes = models.TextField(db_column='Observacoes', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'tblEncaminhamentoSessao'
        ordering = ['-data_encaminhamento']

    def __str__(self):
        return f"{self.codigo_encaminhamento} - {self.nome_familia}"
