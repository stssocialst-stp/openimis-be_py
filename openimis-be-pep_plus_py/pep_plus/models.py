"""
PEP+ Models
Defines all database models for the PEP+ (Programa de Educação Positiva) system
"""
import uuid
from django.db import models
from django.conf import settings
from core import models as core_models
from location.models import Location


# =============================================================================
# TABELAS DE PARAMETRIZAÇÃO (Lookup Tables)
# =============================================================================

class ModuloPEP(core_models.VersionedModel):
    """
    Módulo PEP - Tabela de referência para módulos educacionais do PEP+.
    Substitui o campo texto livre 'nome_modulo' em SessaoPEP.
    """
    id = models.AutoField(db_column='ModuloPEPID', primary_key=True)
    uuid = models.CharField(db_column='ModuloPEPUUID', max_length=36, default=uuid.uuid4, unique=True)

    codigo = models.CharField(db_column='Codigo', max_length=50, unique=True)
    nome = models.CharField(db_column='Nome', max_length=255)
    descricao = models.TextField(db_column='Descricao', null=True, blank=True)
    ordem = models.IntegerField(db_column='Ordem', null=True, blank=True)
    duracao_semanas = models.IntegerField(db_column='DuracaoSemanas', null=True, blank=True)
    ativo = models.BooleanField(db_column='Ativo', default=True)

    class Meta:
        managed = True
        db_table = 'tblModuloPEP'
        ordering = ['ordem', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Escola(core_models.VersionedModel):
    """
    Escola - Tabela de referência de escolas.
    Substitui os campos texto livre 'escola' e 'escola_actual' em ModuloEducacional.
    """
    NIVEL_CHOICES = [
        ('EP1', 'EP1 (Ensino Primário 1)'),
        ('EP2', 'EP2 (Ensino Primário 2)'),
        ('ESG1', 'ESG1 (Ensino Secundário Geral 1)'),
        ('ESG2', 'ESG2 (Ensino Secundário Geral 2)'),
        ('OUTRO', 'Outro'),
    ]

    id = models.AutoField(db_column='EscolaID', primary_key=True)
    uuid = models.CharField(db_column='EscolaUUID', max_length=36, default=uuid.uuid4, unique=True)

    nome = models.CharField(db_column='Nome', max_length=255)
    codigo = models.CharField(db_column='Codigo', max_length=50, null=True, blank=True)
    nivel = models.CharField(db_column='Nivel', max_length=50, choices=NIVEL_CHOICES, null=True, blank=True)
    distrito = models.ForeignKey(
        Location, db_column='DistritoID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='escolas_distrito'
    )
    localidade = models.ForeignKey(
        Location, db_column='LocalidadeID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='escolas_localidade'
    )
    ativo = models.BooleanField(db_column='Ativo', default=True)

    class Meta:
        managed = True
        db_table = 'tblEscola'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Classe(core_models.VersionedModel):
    """
    Classe - Tabela de referência de classes/anos escolares (1ª a 12ª Classe, etc.).
    Substitui os campos com choices 'classe' e 'classe_que_frequenta' em ModuloEducacional.
    Relaciona-se com Disciplina via M2M (ClasseDisciplina).
    """
    NIVEL_CHOICES = [
        ('EP1', 'EP1 (Ensino Primário 1 — 1ª a 4ª Classe)'),
        ('EP2', 'EP2 (Ensino Primário 2 — 5ª e 6ª Classe)'),
        ('ESG1', 'ESG1 (Ensino Secundário Geral 1 — 7ª a 9ª Classe)'),
        ('ESG2', 'ESG2 (Ensino Secundário Geral 2 — 10ª a 12ª Classe)'),
        ('OUTRO', 'Outro'),
    ]

    id = models.AutoField(db_column='ClasseID', primary_key=True)
    uuid = models.CharField(db_column='ClasseUUID', max_length=36, default=uuid.uuid4, unique=True)

    nome = models.CharField(db_column='Nome', max_length=100)
    codigo = models.CharField(db_column='Codigo', max_length=10, unique=True)
    nivel = models.CharField(db_column='Nivel', max_length=50, choices=NIVEL_CHOICES, null=True, blank=True)
    ordem = models.IntegerField(db_column='Ordem', null=True, blank=True)
    ativo = models.BooleanField(db_column='Ativo', default=True)

    class Meta:
        managed = True
        db_table = 'tblClasse'
        ordering = ['ordem', 'codigo']

    def __str__(self):
        return self.nome


class Disciplina(core_models.VersionedModel):
    """
    Disciplina - Tabela de referência de disciplinas escolares.
    Substitui os campos texto livre 'disciplinas_basicas' e 'disciplinas_avancadas' em ModuloEducacional.
    Relaciona-se com Classe via M2M (ClasseDisciplina).
    """
    NIVEL_CHOICES = [
        ('BASICA', 'Básica'),
        ('AVANCADA', 'Avançada'),
    ]

    FAIXA_FALTAS_CHOICES = [
        ('1-3', '1 a 3 faltas'),
        ('4-6', '4 a 6 faltas'),
        ('7-10', '7 a 10 faltas'),
        ('+10', 'Mais de 10 faltas'),
    ]

    id = models.AutoField(db_column='DisciplinaID', primary_key=True)
    uuid = models.CharField(db_column='DisciplinaUUID', max_length=36, default=uuid.uuid4, unique=True)

    nome = models.CharField(db_column='Nome', max_length=255)
    nivel = models.CharField(db_column='Nivel', max_length=20, choices=NIVEL_CHOICES)
    ativo = models.BooleanField(db_column='Ativo', default=True)

    faixa_faltas_aceitaveis = models.CharField(
        db_column='FaixaFaltasAceitaveis', max_length=10,
        choices=FAIXA_FALTAS_CHOICES, null=True, blank=True,
        help_text='Faixa de faltas aceitáveis para esta disciplina (ex: 1-3, 4-6)'
    )
    quantidade_faltas_aceitaveis = models.IntegerField(
        db_column='QuantidadeFaltasAceitaveis', null=True, blank=True,
        help_text='Número máximo absoluto de faltas aceitáveis para esta disciplina'
    )

    class Meta:
        managed = True
        db_table = 'tblDisciplina'
        ordering = ['nivel', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.nivel})"


class ClasseDisciplina(models.Model):
    """
    Tabela intermediária M2M entre Classe e Disciplina.
    Uma classe pode ter várias disciplinas; uma disciplina pode pertencer a várias classes.
    """
    id = models.AutoField(db_column='ClasseDisciplinaID', primary_key=True)
    classe = models.ForeignKey(
        Classe, db_column='ClasseID', on_delete=models.CASCADE,
        related_name='disciplinas_associadas'
    )
    disciplina = models.ForeignKey(
        Disciplina, db_column='DisciplinaID', on_delete=models.PROTECT,
        related_name='classes_associadas'
    )

    class Meta:
        managed = True
        db_table = 'tblClasseDisciplina'
        unique_together = [['classe', 'disciplina']]

    def __str__(self):
        return f"{self.classe} — {self.disciplina}"


class TipoEncaminhamento(core_models.VersionedModel):
    """
    Tipo de Encaminhamento - Tabela de referência para tipos/instituições de encaminhamento.
    Substitui o campo texto livre 'nome_instituicao' em PresencaSessao.
    Adicionado também em EncaminhamentoSessao.
    """
    id = models.AutoField(db_column='TipoEncaminhamentoID', primary_key=True)
    uuid = models.CharField(db_column='TipoEncaminhamentoUUID', max_length=36, default=uuid.uuid4, unique=True)

    codigo = models.CharField(db_column='Codigo', max_length=50, unique=True)
    nome = models.CharField(db_column='Nome', max_length=255)
    descricao = models.TextField(db_column='Descricao', null=True, blank=True)
    ativo = models.BooleanField(db_column='Ativo', default=True)

    class Meta:
        managed = True
        db_table = 'tblTipoEncaminhamento'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


# =============================================================================
# MODELOS PRINCIPAIS
# =============================================================================

class ModuloEducacional(core_models.VersionedModel):
    """
    Módulo Educacional - Registo de Assiduidade Escolar de Crianças
    """
    # Choices para campos de parametrização simples
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('I', 'Indeterminado'),
    ]

    ESCOLARIDADE_CHOICES = [
        ('EP1', 'EP1'),
        ('EP2', 'EP2'),
        ('ESG1', 'ESG1'),
        ('ESG2', 'ESG2'),
        ('ENSINO_SUPERIOR', 'Ensino Superior'),
        ('OUTRO', 'Outro'),
    ]

    id = models.AutoField(db_column='ModuloEducacionalID', primary_key=True)
    uuid = models.CharField(db_column='ModuloEducacionalUUID', max_length=36, default=uuid.uuid4, unique=True)

    ano_registo = models.IntegerField(
        db_column='AnoRegisto', null=True, blank=True,
        help_text='Ano lectivo do registo (ex: 2026)'
    )

    # Identificação do membro/criança
    id_membro_crianca = models.CharField(db_column='IdMembroCrianca', max_length=100, null=True, blank=True)
    nome = models.CharField(db_column='Nome', max_length=255)
    nome_encarregado = models.CharField(db_column='NomeEncarregado', max_length=255, null=True, blank=True)

    # Dados escolares — escola e escola_actual agora são FK para Escola
    escola = models.ForeignKey(
        Escola, db_column='EscolaID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='modulos_escola'
    )
    escolaridade_actual = models.CharField(
        db_column='EscolaridadeActual', max_length=100,
        choices=ESCOLARIDADE_CHOICES, null=True, blank=True
    )
    data_nascimento = models.DateField(db_column='DataNascimento', null=True, blank=True)
    id_da_crianca = models.CharField(db_column='IdDaCrianca', max_length=100, null=True, blank=True)
    sexo = models.CharField(
        db_column='Sexo', max_length=20,
        choices=SEXO_CHOICES, null=True, blank=True
    )
    dados_escolar_correctos = models.BooleanField(db_column='DadosEscolarCorrectos', null=True, blank=True)
    escola_actual = models.ForeignKey(
        Escola, db_column='EscolaActualID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='modulos_escola_actual'
    )
    # classe e classe_que_frequenta agora são FK para tabela Classe
    classe = models.ForeignKey(
        Classe, db_column='ClasseID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='modulos_classe'
    )
    idade = models.IntegerField(db_column='Idade', null=True, blank=True)
    dados_escolares_correctos = models.BooleanField(db_column='DadosEscolaresCorrectos', null=True, blank=True)

    # Informações de localização (JSON)
    informacoes_localizacao = models.JSONField(
        db_column='InformacoesLocalizacao',
        default=dict,
        blank=True,
        help_text='Objeto: { nomeDaRegiao, distritoId, Localidade, nomeEscola, pontoReferencia, meioResidencia }'
    )

    # Dados de frequência escolar
    classe_que_frequenta = models.ForeignKey(
        Classe, db_column='ClasseQueFrequentaID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='modulos_classe_que_frequenta'
    )

    APROVEITAMENTO_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('+10', '+10'),
    ]
    aproveitamento_primeiro_trimestre = models.CharField(
        db_column='AproveitamentoPrimeiroTrimestre',
        max_length=10,
        choices=APROVEITAMENTO_CHOICES,
        null=True,
        blank=True
    )

    FAIXA_FALTAS_CHOICES = [
        ('low', 'Pouca falta'),
        ('medium', 'Falta moderada'),
        ('high', 'Muita falta'),
    ]
    faixa_de_faltas = models.CharField(
        db_column='FaixaDeFaltas',
        max_length=10,
        choices=FAIXA_FALTAS_CHOICES,
        null=True,
        blank=True
    )

    # Ligação ao perfil centralizado do Aluno (opcional para backward compat)
    aluno = models.ForeignKey(
        'Aluno',
        db_column='AlunoID',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='assiduidades',
        help_text='Perfil centralizado do aluno (criado em Registar Indivíduo)'
    )

    # Observações
    observacoes = models.TextField(db_column='Observacoes', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'tblModuloEducacional'

    def __str__(self):
        return f"{self.id_membro_crianca or self.id} - {self.nome}"


class ModuloEducacionalDisciplina(models.Model):
    """
    Tabela intermediária M2M entre ModuloEducacional e Disciplina.
    Substitui os campos texto livre 'disciplinas_basicas' e 'disciplinas_avancadas'.
    """
    TIPO_CHOICES = [
        ('BASICA', 'Básica'),
        ('AVANCADA', 'Avançada'),
    ]

    id = models.AutoField(db_column='ModuloEducacionalDisciplinaID', primary_key=True)
    modulo = models.ForeignKey(
        ModuloEducacional, db_column='ModuloEducacionalID',
        on_delete=models.CASCADE, related_name='disciplinas_associadas'
    )
    disciplina = models.ForeignKey(
        Disciplina, db_column='DisciplinaID',
        on_delete=models.PROTECT, related_name='modulos_associados'
    )
    tipo = models.CharField(db_column='Tipo', max_length=20, choices=TIPO_CHOICES)

    class Meta:
        managed = True
        db_table = 'tblModuloEducacionalDisciplina'
        unique_together = [['modulo', 'disciplina']]

    def __str__(self):
        return f"{self.modulo} - {self.disciplina} ({self.tipo})"


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

    # modulo substitui nome_modulo (texto livre) por FK para tabela ModuloPEP
    modulo = models.ForeignKey(
        ModuloPEP, db_column='ModuloID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='sessoes'
    )
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
        ('MIGR', 'Migrou'),
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

    # tipo_encaminhamento substitui nome_instituicao (texto livre) por FK para TipoEncaminhamento
    tipo_encaminhamento = models.ForeignKey(
        TipoEncaminhamento, db_column='TipoEncaminhamentoID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='presencas'
    )
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
    numero_localidades_atendidas = models.IntegerField(db_column='NumeroLocalidadesAtendidas', default=0)
    numero_familias_atendidas = models.IntegerField(db_column='NumeroFamiliasAtendidas', default=0)
    numero_tecnicos_formadores = models.IntegerField(db_column='NumeroTecnicosFormadores', default=0)
    numero_sessoes_conduzidas = models.IntegerField(db_column='NumeroSessoesConduzidas', default=0)
    numero_sessoes_esperadas = models.IntegerField(db_column='NumeroSessoesEsperadas', default=0)
    numero_familias_presentes = models.IntegerField(db_column='NumeroFamiliasPresentes', default=0)
    numero_familias_esperadas = models.IntegerField(db_column='NumeroFamiliasEsperadas', default=0)
    numero_familias_migraram = models.IntegerField(db_column='NumeroFamiliasMigraram', default=0)
    numero_sessoes_perdidas = models.IntegerField(db_column='NumeroSessoesPerdidas', default=0)

    # Percentuais calculados (opcionais)
    percentual_sessoes = models.DecimalField(db_column='PercentualSessoes', max_digits=5,
                                            decimal_places=2, default=0, blank=True)
    percentual_familias = models.DecimalField(db_column='PercentualFamilias', max_digits=5,
                                             decimal_places=2, default=0, blank=True)
    media_familia_presente = models.DecimalField(db_column='MediaFamiliaPresente', max_digits=5,
                                                decimal_places=2, default=0, blank=True)
    media_familia_esperada = models.DecimalField(db_column='MediaFamiliaEsperada', max_digits=5,
                                                decimal_places=2, default=0, blank=True)

    dados_tecnicos = models.JSONField(db_column='DadosTecnicos', default=list, blank=True)
    dados_encaminhamentos = models.JSONField(db_column='DadosEncaminhamentos', default=list, blank=True)
    observacoes = models.TextField(db_column='Observacoes', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'tblRelatorioDistritalBimestral'
        unique_together = [['distrito', 'periodo', 'ano']]
        ordering = ['-ano', '-periodo']

    def __str__(self):
        return f"Relatório {self.distrito} - {self.periodo}/{self.ano}"


class RelatorioDistEncaminhamento(models.Model):
    """
    Ligação estruturada entre RelatorioDistritalBimestral e PresencaSessao encaminhadas.

    Substitui o uso do campo JSON livre 'dados_encaminhamentos' para os códigos
    de encaminhamento de famílias. Cada registo liga um relatório a uma presença
    concreta (estado='ENCA'), preservando o código e o tipo de encaminhamento.

    Regra: apenas PresencaSessao com estado='ENCA' podem ser associadas.
    O campo dados_encaminhamentos (JSON) permanece disponível para notas livres.
    """
    id = models.AutoField(db_column='RelatorioDistEncaminhamentoID', primary_key=True)

    relatorio = models.ForeignKey(
        RelatorioDistritalBimestral,
        db_column='RelatorioDistritalID',
        on_delete=models.CASCADE,
        related_name='encaminhamentos_estruturados',
        help_text='Relatório Distrital Bimestral ao qual este encaminhamento pertence'
    )
    presenca = models.ForeignKey(
        'PresencaSessao',
        db_column='PresencaSessaoID',
        on_delete=models.PROTECT,
        related_name='relatorios_distritais',
        help_text='Registo de presença encaminhada (estado obrigatoriamente ENCA)'
    )
    observacoes = models.TextField(
        db_column='Observacoes', null=True, blank=True,
        help_text='Notas adicionais sobre este encaminhamento no contexto do relatório'
    )

    class Meta:
        managed = True
        db_table = 'tblRelatorioDistEncaminhamento'
        unique_together = [['relatorio', 'presenca']]

    def __str__(self):
        return (
            f"{self.relatorio} → {self.presenca.nome_familia} "
            f"({self.presenca.codigo_encaminhamento})"
        )


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

    # tipo_encaminhamento — novo campo FK para TipoEncaminhamento
    tipo_encaminhamento = models.ForeignKey(
        TipoEncaminhamento, db_column='TipoEncaminhamentoID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='encaminhamentos'
    )

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

    # Participantes manuais (nomes inseridos manualmente, não constam na lista)
    participantes_manuais = models.JSONField(
        db_column='ParticipantesManuais',
        default=list,
        blank=True,
        help_text='Array de nomes de participantes inseridos manualmente'
    )

    # Resumo da Agenda (checklist de tópicos abordados)
    resumo_da_agenda = models.JSONField(
        db_column='ResumoDaAgenda',
        default=list,
        blank=True,
        help_text='Array de objetos: [{ aberturaEBoasVindas, relatoDesafiosSolucoes, compartilhamentoOportunidades, apreciacaoRelatorios, definicaoAcoesEncaminhamentos, encerramentoProximaReuniao }]'
    )

    # Conteúdos da reunião
    principais_desafios = models.TextField(db_column='PrincipaisDesafios', null=True, blank=True)
    oportunidades_melhoria = models.TextField(db_column='OportunidadesMelhoria', null=True, blank=True)
    apreciacao_relatorios = models.TextField(db_column='ApreciacaoRelatorios', null=True, blank=True)
    plano_acao = models.TextField(db_column='PlanoAcao', null=True, blank=True)

    # Próxima reunião
    proxima_reuniao = models.TextField(db_column='ProximaReuniao', null=True, blank=True)
    data_proxima_reuniao = models.DateField(db_column='DataProximaReuniao', null=True, blank=True)

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
    supervisores = models.JSONField(db_column='Supervisores', default=list, blank=True)
    numero_sessoes = models.IntegerField(db_column='NumeroSessoes', default=0)
    numero_tecnicos_formadores = models.IntegerField(db_column='NumeroTecnicosFormadores', default=0)

    # 2. Marque seu Distrito
    distrito = models.ForeignKey(
        'location.Location',
        on_delete=models.PROTECT,
        db_column='DistritoID',
        related_name='relatorios_supervisao',
        help_text='Distrito do relatório'
    )

    # 3. Marque o Período do Relatório
    PERIODO_CHOICES = [
        ('JAN_FEV', 'Janeiro e Fevereiro'),
        ('MAR_ABR', 'Março e Abril'),
        ('MAI_JUN', 'Maio e Junho'),
        ('JUL_AGO', 'Julho e Agosto'),
        ('SET_OUT', 'Setembro e Outubro'),
        ('NOV_DEZ', 'Novembro e Dezembro'),
    ]
    periodo = models.CharField(db_column='Periodo', max_length=10, choices=PERIODO_CHOICES)
    ano = models.IntegerField(db_column='Ano', help_text='Ano do relatório')

    # 4. Avaliação dos Técnicos Formadores
    avaliacoes_tecnicos = models.JSONField(db_column='AvaliacoesTecnicos', default=list, blank=True)

    # 5. Sessões do PEP+
    sessoes_pep = models.JSONField(db_column='SessoesPep', default=list, blank=True)

    # 6. Módulos com maior dificuldade
    modulos_dificuldade = models.JSONField(db_column='ModulosDificuldade', default=list, blank=True)

    # 7. Observações
    observacoes = models.TextField(db_column='Observacoes', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'tblRelatorioSupervisaoBimestral'
        ordering = ['-ano', '-periodo']
        unique_together = [['distrito', 'periodo', 'ano']]

    def __str__(self):
        periodo_str = dict(self.PERIODO_CHOICES).get(self.periodo, '')
        return f"Supervisão {self.distrito.name if self.distrito else ''} - {periodo_str}/{self.ano}"


# =============================================================================
# ALUNO
# =============================================================================

class Aluno(core_models.VersionedModel):
    """
    Aluno — Perfil centralizado de aluno/criança no PEP+.

    Todo aluno é um indivíduo (FK → individual.Individual), mas nem todo
    indivíduo é um aluno. A relação é 1-para-1 activa: apenas 1 registo
    Aluno activo por Individual (validity_to IS NULL), permitindo histórico.

    Criação automática: se o Individual não existir, o service cria-o primeiro
    e depois cria o Aluno com a referência associada.

    Campos de localização usam FKs (Distrito / Localidade) em vez do JSON livre
    que existe em ModuloEducacional, tornando os dados estruturados e filtráveis.
    """

    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('I', 'Indeterminado'),
    ]

    ESCOLARIDADE_CHOICES = [
        ('EP1', 'EP1'),
        ('EP2', 'EP2'),
        ('ESG1', 'ESG1'),
        ('ESG2', 'ESG2'),
        ('ENSINO_SUPERIOR', 'Ensino Superior'),
        ('OUTRO', 'Outro'),
    ]

    id = models.AutoField(db_column='AlunoID', primary_key=True)
    uuid = models.CharField(
        db_column='AlunoUUID', max_length=36,
        default=uuid.uuid4, unique=True
    )

    # Ligação ao Individual openIMIS (o Individual é o "pai" do Aluno)
    individual = models.ForeignKey(
        'individual.Individual',
        db_column='IndividualUUID',
        on_delete=models.PROTECT,
        related_name='alunos',
        help_text='Indivíduo openIMIS ao qual este aluno pertence'
    )

    # Identificadores de integração (opcionais, usados para cruzamento de dados)
    id_membro_crianca = models.CharField(
        db_column='IdMembroCrianca', max_length=100, null=True, blank=True
    )
    id_da_crianca = models.CharField(
        db_column='IdDaCrianca', max_length=100, null=True, blank=True
    )
    nome_encarregado = models.CharField(
        db_column='NomeEncarregado', max_length=255, null=True, blank=True
    )

    # Sexo (não existe no Individual, fica no Aluno)
    sexo = models.CharField(
        db_column='Sexo', max_length=20,
        choices=SEXO_CHOICES, null=True, blank=True
    )

    # Localização (FKs estruturadas em vez de JSON livre)
    distrito = models.ForeignKey(
        Location, db_column='DistritoID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='alunos_distrito'
    )
    localidade = models.ForeignKey(
        Location, db_column='LocalidadeID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='alunos_localidade'
    )
    ponto_referencia = models.TextField(
        db_column='PontoReferencia', null=True, blank=True
    )
    meio_residencia = models.CharField(
        db_column='MeioResidencia', max_length=100, null=True, blank=True
    )

    # Dados escolares
    escola = models.ForeignKey(
        Escola, db_column='EscolaID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='alunos_escola'
    )
    escola_actual = models.ForeignKey(
        Escola, db_column='EscolaActualID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='alunos_escola_actual'
    )
    escolaridade_actual = models.CharField(
        db_column='EscolaridadeActual', max_length=100,
        choices=ESCOLARIDADE_CHOICES, null=True, blank=True
    )
    classe = models.ForeignKey(
        Classe, db_column='ClasseID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='alunos_classe'
    )
    classe_que_frequenta = models.ForeignKey(
        Classe, db_column='ClasseQueFrequentaID', on_delete=models.PROTECT,
        null=True, blank=True, related_name='alunos_classe_frequenta'
    )
    dados_escolares_correctos = models.BooleanField(
        db_column='DadosEscolaresCorrectos', null=True, blank=True
    )

    ativo = models.BooleanField(db_column='Ativo', default=True)

    class Meta:
        managed = True
        db_table = 'tblAluno'
        ordering = ['individual__first_name', 'individual__last_name']

    def __str__(self):
        return f"Aluno: {self.individual}"


# =============================================================================
# COORDENAÇÃO DISTRITAL
# =============================================================================

class CoordenacaoDistrital(core_models.VersionedModel):
    """
    Coordenação Distrital — Parametrização dos responsáveis de cada distrito.

    Regras:
    - 1 coordenador por distrito (FK)
    - 1 técnico administrativo por distrito (FK, opcional)
    - N técnicos operacionais por distrito (M2M via CoordenacaoDistritalTecnico)
    - Apenas 1 registo activo por distrito em simultâneo (validado no service)
    """
    id = models.AutoField(db_column='CoordenacaoDistritalID', primary_key=True)
    uuid = models.CharField(
        db_column='CoordenacaoDistritalUUID', max_length=36,
        default=uuid.uuid4, unique=True
    )

    distrito = models.ForeignKey(
        Location,
        db_column='DistritoID',
        on_delete=models.PROTECT,
        related_name='coordenacoes_distritais',
        help_text='Distrito ao qual esta coordenação pertence'
    )
    coordenador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column='CoordenadorID',
        on_delete=models.PROTECT,
        related_name='coordenacoes_como_coordenador',
        help_text='Coordenador distrital (1 por distrito)'
    )
    tecnico_administrativo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column='TecnicoAdministrativoID',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='coordenacoes_como_tecnico_admin',
        help_text='Técnico administrativo (máx. 1 por distrito)'
    )
    ativo = models.BooleanField(db_column='Ativo', default=True)
    observacoes = models.TextField(db_column='Observacoes', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'tblCoordenacaoDistrital'
        ordering = ['distrito']

    def __str__(self):
        return f"Coordenação {self.distrito} — {self.coordenador}"


class CoordenacaoDistritalTecnico(models.Model):
    """
    Tabela intermediária — Técnicos Operacionais de uma Coordenação Distrital.
    Um distrito pode ter vários técnicos operacionais.
    """
    id = models.AutoField(db_column='CoordenacaoDistritalTecnicoID', primary_key=True)

    coordenacao = models.ForeignKey(
        CoordenacaoDistrital,
        db_column='CoordenacaoDistritalID',
        on_delete=models.CASCADE,
        related_name='tecnicos_operacionais'
    )
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column='TecnicoID',
        on_delete=models.PROTECT,
        related_name='coordenacoes_como_tecnico_operacional'
    )

    class Meta:
        managed = True
        db_table = 'tblCoordenacaoDistritalTecnico'
        unique_together = [['coordenacao', 'tecnico']]

    def __str__(self):
        return f"{self.coordenacao} — Técnico: {self.tecnico}"
