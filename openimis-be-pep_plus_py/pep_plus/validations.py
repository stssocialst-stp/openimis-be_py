"""
PEP+ Validations
Business rules validation based on PEP+ documentation (Ferramenta 1-7)
"""


def validate_sessao_planeamento(data):
    """
    Validates session planning data (Ferramenta 1)

    Business Rules from document:
    - Código de sessão é obrigatório
    - Selecione pelo menos um coordenador distrital
    - Data é obrigatória
    - Selecione pelo menos um técnico social
    - Distrito é obrigatório
    - Nome do módulo é obrigatório
    - Selecione pelo menos um mês do módulo anterior
    - Sessão 1: Dia da semana é obrigatório
    - Sessão 1: Data é obrigatória
    - Sessão 1: Zona é obrigatória
    - Sessão 1: Número de famílias deve ser maior que 0
    - Sessão 1: Grupo de família é obrigatório
    - Sessão 1: Hora da sessão é obrigatória
    - Sessão 1: Feedback e documentação é obrigatório
    """
    errors = []

    # Código de sessão obrigatório
    if not data.get('codigo_sessao'):
        errors.append({
            'field': 'codigo_sessao',
            'message': 'Código de sessão é obrigatório'
        })

    # Coordenador distrital obrigatório
    if not data.get('coordenador_distrital_id'):
        errors.append({
            'field': 'coordenador_distrital_id',
            'message': 'Selecione pelo menos um coordenador distrital'
        })

    # Data obrigatória
    if not data.get('data_sessao'):
        errors.append({
            'field': 'data_sessao',
            'message': 'Data é obrigatória'
        })

    # Técnico social obrigatório
    if not data.get('tecnico_social_id'):
        errors.append({
            'field': 'tecnico_social_id',
            'message': 'Selecione pelo menos um técnico social'
        })

    # Distrito obrigatório
    if not data.get('distrito_id'):
        errors.append({
            'field': 'distrito_id',
            'message': 'Distrito é obrigatório'
        })

    # Módulo obrigatório
    if not data.get('modulo_id'):
        errors.append({
            'field': 'modulo_id',
            'message': 'Nome do módulo é obrigatório'
        })

    # Dia da semana obrigatório
    if not data.get('dia_semana'):
        errors.append({
            'field': 'dia_semana',
            'message': 'Dia da semana é obrigatório'
        })

    # Zona obrigatória
    if not data.get('zona'):
        errors.append({
            'field': 'zona',
            'message': 'Zona é obrigatória'
        })

    # Número de famílias deve ser maior que 0
    numero_familias = data.get('numero_familias', 0)
    if not numero_familias or numero_familias <= 0:
        errors.append({
            'field': 'numero_familias',
            'message': 'Número de famílias deve ser maior que 0'
        })

    # Grupo de família obrigatório
    if not data.get('grupo_familia_id'):
        errors.append({
            'field': 'grupo_familia_id',
            'message': 'Grupo de família é obrigatório'
        })

    # Hora da sessão obrigatória
    if not data.get('hora_sessao'):
        errors.append({
            'field': 'hora_sessao',
            'message': 'Hora da sessão é obrigatória'
        })

    # Feedback e documentação obrigatório
    if not data.get('feedback_documentacao'):
        errors.append({
            'field': 'feedback_documentacao',
            'message': 'Feedback e documentação é obrigatório'
        })

    return errors


def validate_presenca_sessao(data):
    """
    Validates attendance registration data (Ferramenta 2)
    """
    errors = []

    # Sessão obrigatória
    if not data.get('sessao_id'):
        errors.append({
            'field': 'sessao_id',
            'message': 'Sessão é obrigatória'
        })

    # ID da família obrigatório
    if not data.get('familia_id'):
        errors.append({
            'field': 'familia_id',
            'message': 'ID da família é obrigatório'
        })

    # Nome da família obrigatório
    if not data.get('nome_familia'):
        errors.append({
            'field': 'nome_familia',
            'message': 'Nome da família é obrigatório'
        })

    # Estado obrigatório
    if not data.get('estado'):
        errors.append({
            'field': 'estado',
            'message': 'Estado é obrigatório'
        })

    # Validar estado válido
    estados_validos = ['PRES', 'AUSE', 'JUST']
    if data.get('estado') and data.get('estado') not in estados_validos:
        errors.append({
            'field': 'estado',
            'message': f'Estado deve ser um de: {", ".join(estados_validos)}'
        })

    return errors


def validate_execucao_sessao(data):
    """
    Validates session execution data (Ferramenta 3)
    """
    errors = []

    # Sessão obrigatória
    if not data.get('sessao_id'):
        errors.append({
            'field': 'sessao_id',
            'message': 'Sessão é obrigatória'
        })

    # Formador obrigatório
    if not data.get('formador_id'):
        errors.append({
            'field': 'formador_id',
            'message': 'Formador é obrigatório'
        })

    # Número de participantes que praticaram compromissos
    if data.get('numero_participantes_compromissos') is None:
        errors.append({
            'field': 'numero_participantes_compromissos',
            'message': 'Número de participantes que praticaram compromissos é obrigatório'
        })

    return errors


def validate_supervisao_sessao(data):
    """
    Validates session supervision data (Ferramenta 4)
    """
    errors = []

    # Sessão obrigatória
    if not data.get('sessao_id'):
        errors.append({
            'field': 'sessao_id',
            'message': 'Sessão é obrigatória'
        })

    # Supervisor obrigatório
    if not data.get('supervisor_id'):
        errors.append({
            'field': 'supervisor_id',
            'message': 'Supervisor é obrigatório'
        })

    # Formador obrigatório
    if not data.get('formador_id'):
        errors.append({
            'field': 'formador_id',
            'message': 'Formador é obrigatório'
        })

    # Data de supervisão obrigatória
    if not data.get('data_supervisao'):
        errors.append({
            'field': 'data_supervisao',
            'message': 'Data de supervisão é obrigatória'
        })

    # Identificador do grupo obrigatório
    if not data.get('identificador_grupo'):
        errors.append({
            'field': 'identificador_grupo',
            'message': 'Identificador do grupo é obrigatório'
        })

    return errors


def validate_relatorio_distrital(data):
    """
    Validates district bimonthly report data (Ferramenta 5)
    """
    errors = []

    # Distrito obrigatório
    if not data.get('distrito_id'):
        errors.append({
            'field': 'distrito_id',
            'message': 'Distrito é obrigatório'
        })

    # Coordenador distrital obrigatório
    if not data.get('coordenador_distrital_id'):
        errors.append({
            'field': 'coordenador_distrital_id',
            'message': 'Coordenador distrital é obrigatório'
        })

    # Período obrigatório
    if not data.get('periodo'):
        errors.append({
            'field': 'periodo',
            'message': 'Período é obrigatório'
        })

    # Ano obrigatório
    if not data.get('ano'):
        errors.append({
            'field': 'ano',
            'message': 'Ano é obrigatório'
        })

    # Período início obrigatório
    if not data.get('periodo_inicio'):
        errors.append({
            'field': 'periodo_inicio',
            'message': 'Período início é obrigatório'
        })

    # Período fim obrigatório
    if not data.get('periodo_fim'):
        errors.append({
            'field': 'periodo_fim',
            'message': 'Período fim é obrigatório'
        })

    # Validar que período fim é depois de período início
    if data.get('periodo_inicio') and data.get('periodo_fim'):
        if data['periodo_fim'] < data['periodo_inicio']:
            errors.append({
                'field': 'periodo_fim',
                'message': 'Período fim deve ser posterior ao período início'
            })

    return errors


def validate_encaminhamento(data):
    """
    Validates referral data
    """
    errors = []

    # Sessão obrigatória
    if not data.get('sessao_id'):
        errors.append({
            'field': 'sessao_id',
            'message': 'Sessão é obrigatória'
        })

    # ID da família obrigatório
    if not data.get('familia_id'):
        errors.append({
            'field': 'familia_id',
            'message': 'ID da família é obrigatório'
        })

    # Nome da família obrigatório
    if not data.get('nome_familia'):
        errors.append({
            'field': 'nome_familia',
            'message': 'Nome da família é obrigatório'
        })

    # Código de encaminhamento obrigatório
    if not data.get('codigo_encaminhamento'):
        errors.append({
            'field': 'codigo_encaminhamento',
            'message': 'Código de encaminhamento é obrigatório'
        })

    # Descrição obrigatória
    if not data.get('descricao'):
        errors.append({
            'field': 'descricao',
            'message': 'Descrição é obrigatória'
        })

    return errors


def validate_modulo_educacional(data):
    """
    Validates educational module data
    """
    errors = []

    # Código obrigatório
    if not data.get('codigo'):
        errors.append({
            'field': 'codigo',
            'message': 'Código é obrigatório'
        })

    # Nome obrigatório
    if not data.get('nome'):
        errors.append({
            'field': 'nome',
            'message': 'Nome é obrigatório'
        })

    return errors


def validate_grupo_familiar(data):
    """
    Validates family group data
    """
    errors = []

    # Código obrigatório
    if not data.get('codigo'):
        errors.append({
            'field': 'codigo',
            'message': 'Código é obrigatório'
        })

    # Nome obrigatório
    if not data.get('nome'):
        errors.append({
            'field': 'nome',
            'message': 'Nome é obrigatório'
        })

    # Distrito obrigatório
    if not data.get('distrito_id'):
        errors.append({
            'field': 'distrito_id',
            'message': 'Distrito é obrigatório'
        })

    return errors
