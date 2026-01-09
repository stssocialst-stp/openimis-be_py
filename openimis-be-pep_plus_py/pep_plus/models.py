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

    # Campos obrigatórios - Informações Básicas
    codigo_sessao = models.CharField(db_column='CodigoSessao', max_length=50, unique=True)
    data_planejamento = models.DateField(db_column='DataPlanejamento', help_text='Data do planejamento')
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
    nome_modulo = models.CharField(db_column='NomeModulo', max_length=255, help_text='Nome do módulo educacional')
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
        ('FALT', 'Faltou'),
        ('ENCA', 'Encaminhado'),
    ]

    id = models.AutoField(db_column='PresencaSessaoID', primary_key=True)
    uuid = models.CharField(db_column='PresencaSessaoUUID', max_length=36, default=uuid.uuid4, unique=True)

    sessao = models.ForeignKey(SessaoPEP, db_column='SessaoID', on_delete=models.CASCADE,
                               related_name='presencas')
    # Usando CharField para ID da família para flexibilidade de integração
    familia_id = models.CharField(db_column='FamiliaID', max_length=50)
    nome_familia = models.CharField(db_column='NomeFamilia', max_length=255, null=True, blank=True)
    grupo_id = models.CharField(db_column='GrupoID', max_length=50, null=True, blank=True)

    estado = models.CharField(db_column='Estado', max_length=4, choices=ESTADO_CHOICES, default='PRES')
    codigo_encaminhamento = models.CharField(db_column='CodigoEncaminhamento', max_length=50,
                                            null=True, blank=True,
                                            help_text='Código de encaminhamento quando estado=ENCA')
    nome_instituicao = models.CharField(db_column='NomeInstituicao', max_length=255,
                                       null=True, blank=True,
                                       help_text='Nome da instituição quando estado=ENCA')
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

    NUMERO_CUIDADORES_CHOICES = [
        ('0', '0 cuidadores'),
        ('1-5', '1 a 5 cuidadores'),
        ('6-10', '6 a 10 cuidadores'),
        ('15+', 'Mais de 15 cuidadores'),
    ]

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

    # Detalhes da execução
    numero_cuidadores = models.CharField(
        db_column='NumeroCuidadores',
        max_length=10,
        choices=NUMERO_CUIDADORES_CHOICES,
        default='0',
        help_text='Número de cuidadores presentes'
    )

    # Práticas positivas: [{ descricao: "...", confirmacao: "Sim/Não/N/A" }]
    praticas_positivas = models.JSONField(
        db_column='PraticasPositivas',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ descricao, confirmacao: Sim/Não/N/A }]'
    )
    outras_praticas_positivas = models.TextField(
        db_column='OutrasPraticasPositivas',
        null=True,
        blank=True,
        help_text='Outras práticas positivas observadas'
    )

    # Desafios na transmissão: mesma estrutura das práticas positivas
    desafios_transmissao = models.JSONField(
        db_column='DesafiosTransmissao',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ descricao, confirmacao: Sim/Não/N/A }]'
    )
    outros_desafios = models.TextField(
        db_column='OutrosDesafios',
        null=True,
        blank=True,
        help_text='Outros desafios identificados'
    )

    necessita_encaminhamento = models.BooleanField(
        db_column='NecessitaEncaminhamento',
        default=False,
        help_text='Indica se há necessidade de encaminhamento'
    )

    # Auto-avaliação do formador: [{ descricao: "...", avaliacao: "1/2/3/4/5" }]
    auto_avaliacao_pontos_fortes = models.JSONField(
        db_column='AutoAvaliacaoPontosFortes',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ descricao, avaliacao: 1-5 }]'
    )
    auto_avaliacao_pontos_atencao = models.JSONField(
        db_column='AutoAvaliacaoPontosAtencao',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ descricao, avaliacao: 1-5 }]'
    )
    avaliacao_metodologia = models.JSONField(
        db_column='AvaliacaoMetodologia',
        default=dict,
        blank=True,
        help_text='Avaliação da metodologia utilizada'
    )

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

    NUMERO_PARTICIPANTES_CHOICES = [
        ('0', '0 participantes'),
        ('1-5', '1 a 5 participantes'),
        ('6-10', '6 a 10 participantes'),
        ('15+', 'Mais de 15 participantes'),
    ]

    id = models.AutoField(db_column='SupervisaoSessaoID', primary_key=True)
    uuid = models.CharField(db_column='SupervisaoSessaoUUID', max_length=36, default=uuid.uuid4, unique=True)

    sessao = models.ForeignKey(SessaoPEP, db_column='SessaoID', on_delete=models.CASCADE,
                              related_name='supervisoes')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='SupervisorID',
                                  on_delete=models.PROTECT, related_name='supervisoes_realizadas')
    formador = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='FormadorID',
                                on_delete=models.PROTECT, related_name='supervisoes_recebidas')
    localidade = models.ForeignKey(Location, db_column='LocalidadeID', on_delete=models.PROTECT,
                                   null=True, blank=True, related_name='supervisoes_localidade')
    grupo = models.ForeignKey(GrupoFamiliar, db_column='GrupoID', on_delete=models.PROTECT,
                             null=True, blank=True, related_name='supervisoes_grupo')

    data_supervisao = models.DateField(db_column='DataSupervisao')
    data_modulo_anterior = models.DateField(db_column='DataModuloAnterior', null=True, blank=True)
    identificador_grupo = models.CharField(db_column='IdentificadorGrupo', max_length=50)

    # Número de participantes
    numero_participantes = models.CharField(
        db_column='NumeroParticipantes',
        max_length=10,
        choices=NUMERO_PARTICIPANTES_CHOICES,
        default='0',
        help_text='Número de participantes presentes'
    )

    # Práticas positivas e estratégias: [{ descricao: "...", confirmacao: "Sim/Não/N/A" }]
    praticas_positivas_estrategias = models.JSONField(
        db_column='PraticasPositivasEstrategias',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ descricao, confirmacao: Sim/Não/N/A }]'
    )

    # Desafios na transmissão: [{ descricao: "...", confirmacao: "Sim/Não/N/A" }]
    desafios_transmissao = models.JSONField(
        db_column='DesafiosTransmissao',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ descricao, confirmacao: Sim/Não/N/A }]'
    )

    necessita_encaminhamento = models.BooleanField(
        db_column='NecessitaEncaminhamento',
        default=False,
        help_text='Indica se há necessidade de encaminhamento'
    )

    # Auto-avaliação do formador: [{ descricao: "...", confirmacao: boolean }]
    auto_avaliacao_pontos_fortes = models.JSONField(
        db_column='AutoAvaliacaoPontosFortes',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ descricao, confirmacao: boolean }]'
    )
    auto_avaliacao_pontos_atencao = models.JSONField(
        db_column='AutoAvaliacaoPontosAtencao',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ descricao, confirmacao: boolean }]'
    )

    # Avaliação da execução dos passos da metodologia
    # [{ descricao: "...", confirmacao: "Não fez/Não adequado/Adequado/Excelente/N/A" }]
    avaliacao_execucao_metodologia = models.JSONField(
        db_column='AvaliacaoExecucaoMetodologia',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ descricao, confirmacao: Não fez/Não adequado/Adequado/Excelente/N/A }]'
    )

    # Novos campos de feedback
    metodologia_passos = models.JSONField(
        db_column='MetodologiaPassos',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ descricao, confirmacao: Adequado/N/A/etc }]'
    )
    feedback_pontos_fortes = models.TextField(
        db_column='FeedbackPontosFortes',
        null=True,
        blank=True,
        help_text='Feedback sobre pontos fortes observados'
    )
    feedback_desafios = models.TextField(
        db_column='FeedbackDesafios',
        null=True,
        blank=True,
        help_text='Feedback sobre desafios observados'
    )
    compromisso_formador = models.TextField(
        db_column='CompromissoFormador',
        null=True,
        blank=True,
        help_text='Compromissos assumidos pelo formador'
    )

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
    numero_localidades_atendidas = models.IntegerField(db_column='NumeroLocalidadesAtendidas', default=0,
                                                       help_text='Número de localidades atendidas no período')
    numero_familias_atendidas = models.IntegerField(db_column='NumeroFamiliasAtendidas', default=0,
                                                    help_text='Número total de famílias atendidas')
    numero_tecnicos_formadores = models.IntegerField(db_column='NumeroTecnicosFormadores', default=0,
                                                     help_text='Número de técnicos formadores')
    numero_sessoes_conduzidas = models.IntegerField(db_column='NumeroSessoesConduzidas', default=0,
                                                    help_text='Número de sessões efetivamente conduzidas')
    numero_sessoes_esperadas = models.IntegerField(db_column='NumeroSessoesEsperadas', default=0,
                                                   help_text='Número de sessões esperadas/planejadas')
    numero_familias_presentes = models.IntegerField(db_column='NumeroFamiliasPresentes', default=0,
                                                    help_text='Número total de famílias presentes nas sessões')
    numero_familias_esperadas = models.IntegerField(db_column='NumeroFamiliasEsperadas', default=0,
                                                    help_text='Número total de famílias esperadas nas sessões')
    numero_familias_migraram = models.IntegerField(db_column='NumeroFamiliasMigraram', default=0,
                                                   help_text='Número total de famílias que migraram')
    numero_sessoes_perdidas = models.IntegerField(db_column='NumeroSessoesPerdidas', default=0,
                                                  help_text='Número total de sessões perdidas')

    # Percentuais calculados (opcionais)
    percentual_sessoes = models.DecimalField(db_column='PercentualSessoes', max_digits=5,
                                            decimal_places=2, default=0, blank=True,
                                            help_text='Percentual de sessões realizadas')
    percentual_familias = models.DecimalField(db_column='PercentualFamilias', max_digits=5,
                                             decimal_places=2, default=0, blank=True,
                                             help_text='Percentual de famílias presentes')
    media_familia_presente = models.DecimalField(db_column='MediaFamiliaPresente', max_digits=5,
                                                decimal_places=2, default=0, blank=True,
                                                help_text='Média de famílias presentes por sessão')
    media_familia_esperada = models.DecimalField(db_column='MediaFamiliaEsperada', max_digits=5,
                                                decimal_places=2, default=0, blank=True,
                                                help_text='Média de famílias esperadas por sessão')

    # Dados detalhados por técnico (JSON)
    # Array: [{ tecnicoFormador, sessoesExecutadas, sessoesPerdidas, modulos,
    #          familiasPresentes, familiasMigraram, naoCompareceram2Sessoes, naoCompareceram1Sessao }]
    dados_tecnicos = models.JSONField(
        db_column='DadosTecnicos',
        default=list,
        blank=True,
        help_text='Array de objetos com dados por técnico formador'
    )

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


class RoteiroReuniaoBimestral(core_models.VersionedModel):
    """
    Bimonthly Meeting Agenda - Records bimonthly supervision meetings (Ferramenta 6)
    """
    id = models.AutoField(db_column='RoteiroReuniaoID', primary_key=True)
    uuid = models.CharField(db_column='RoteiroReuniaoUUID', max_length=36, default=uuid.uuid4, unique=True)

    # Informações da reunião
    data_reuniao = models.DateField(db_column='DataReuniao', help_text='Data da reunião')
    horario = models.TimeField(db_column='Horario', help_text='Horário da reunião')

    # Coordenador Nacional
    coordenador_nacional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column='CoordenadorNacionalID',
        on_delete=models.PROTECT,
        related_name='reunioes_coordenadas',
        help_text='Coordenador nacional responsável pela reunião'
    )

    # Participantes (array de user IDs)
    participantes = models.JSONField(
        db_column='Participantes',
        default=list,
        blank=True,
        help_text='Array de IDs dos usuários participantes da reunião'
    )

    # Conteúdos da reunião
    principais_desafios = models.TextField(
        db_column='PrincipaisDesafios',
        null=True,
        blank=True,
        help_text='Principais desafios discutidos na reunião'
    )

    oportunidades_melhoria = models.TextField(
        db_column='OportunidadesMelhoria',
        null=True,
        blank=True,
        help_text='Oportunidades de melhoria identificadas'
    )

    apreciacao_relatorios = models.TextField(
        db_column='ApreciacaoRelatorios',
        null=True,
        blank=True,
        help_text='Apreciação e análise dos relatórios apresentados'
    )

    plano_acao = models.TextField(
        db_column='PlanoAcao',
        null=True,
        blank=True,
        help_text='Plano de ação definido com responsáveis e prazos'
    )

    # Próxima reunião
    proxima_reuniao = models.TextField(
        db_column='ProximaReuniao',
        null=True,
        blank=True,
        help_text='Informações sobre a próxima reunião (data, horário, local)'
    )
    data_proxima_reuniao = models.DateField(
        db_column='DataProximaReuniao',
        null=True,
        blank=True,
        help_text='Data da próxima reunião'
    )

    class Meta:
        managed = True
        db_table = 'tblRoteiroReuniaoBimestral'
        ordering = ['-data_reuniao']

    def __str__(self):
        return f"Reunião {self.data_reuniao} - {self.coordenador_nacional}"


class RelatorioSupervisaoBimestral(core_models.VersionedModel):
    """
    Bimonthly Supervision Report - Records supervisor's observations and evaluations (Ferramenta 7)
    """
    id = models.AutoField(db_column='RelatorioSupervisaoID', primary_key=True)
    uuid = models.CharField(db_column='RelatorioSupervisaoUUID', max_length=36, default=uuid.uuid4, unique=True)

    # 1. Identificação
    nome_supervisores = models.TextField(db_column='NomeSupervisores',
                                         help_text='Nome(s) do(s) supervisor(es) responsável(eis) pelo relatório')
    num_sessoes_supervisionadas = models.IntegerField(db_column='NumSessoes', default=0,
                                                       help_text='Quantidade total de sessões acompanhadas no bimestre')
    num_tecnicos_supervisionados = models.IntegerField(db_column='NumTecnicos', default=0,
                                                        help_text='Total de técnicos formadores supervisionados')

    # 2. Marque seu Distrito
    distrito = models.ForeignKey('location.Location', models.DO_NOTHING, db_column='DistritoID',
                                 related_name='relatorios_supervisao')

    # 3. Marque o Período do Relatório
    PERIODO_CHOICES = [
        (1, 'Janeiro e Fevereiro'),
        (2, 'Março e Abril'),
        (3, 'Maio e Junho'),
        (4, 'Julho e Agosto'),
        (5, 'Setembro e Outubro'),
        (6, 'Novembro e Dezembro'),
    ]
    periodo = models.IntegerField(db_column='Periodo', choices=PERIODO_CHOICES)
    ano = models.IntegerField(db_column='Ano')
    periodo_inicio = models.DateField(db_column='PeriodoInicio')
    periodo_fim = models.DateField(db_column='PeriodoFim')

    # 4. Avaliação dos Técnicos Formadores
    # Array de objetos: [{nome_tecnico: str, pontos_positivos: str, pontos_aprimorar: str}, ...]
    avaliacoes_tecnicos = models.JSONField(db_column='AvaliacoesTecnicos', default=list, blank=True,
                                           help_text='Avaliações dos técnicos formadores supervisionados')

    # 5. Sessões do PEP+
    # Objeto com as 10 notas dos passos: {passo_a: float, passo_b: float, ..., passo_j: float}
    notas_sessoes_pep = models.JSONField(db_column='NotasSessoes', default=dict, blank=True,
                                         help_text='Notas dos 10 passos das sessões supervisionadas')

    # 5B. Qual módulo no Bimestre observou maior dificuldade
    modulo_maior_dificuldade = models.ForeignKey(ModuloEducacional, models.DO_NOTHING,
                                                  db_column='ModuloDificuldadeID',
                                                  related_name='relatorios_dificuldade',
                                                  null=True, blank=True,
                                                  help_text='Módulo com menor nota (maior dificuldade)')

    # 6. Observações Adicionais
    observacoes_adicionais = models.TextField(db_column='ObservacoesAdicionais',
                                              null=True, blank=True,
                                              help_text='Observações complementares para discussão')

    class Meta:
        managed = True
        db_table = 'tblRelatorioSupervisaoBimestral'
        ordering = ['-ano', '-periodo']
        unique_together = [['distrito', 'periodo', 'ano']]

    def __str__(self):
        periodo_str = dict(self.PERIODO_CHOICES).get(self.periodo, '')
        return f"Supervisão {self.distrito.name if self.distrito else ''} - {periodo_str}/{self.ano}"
