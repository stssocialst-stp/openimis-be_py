# Generated migration for seeding test data
# Only runs if FEED_DATA environment variable is set to 'true'

import os
import uuid
from datetime import date, time, timedelta
from django.db import migrations
from django.utils import timezone


def should_run_seed():
    """Check if FEED_DATA environment variable is set to true"""
    feed_data = os.environ.get('FEED_DATA', 'false').lower()
    return feed_data in ('true', '1', 'yes')


def safe_get_model(apps, app_label, model_name, operation_name):
    """Safely get a model, returning None if not available"""
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        print(f"[PEP+ Seed] {app_label}.{model_name} model not available yet, skipping {operation_name}...")
        return None


def seed_test_users(apps, schema_editor):
    """Create test users for PEP+ system"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping user seed - FEED_DATA not set to true")
        return

    try:
        User = apps.get_model('core', 'User')
    except LookupError:
        print("[PEP+ Seed] core.User model not available yet, skipping user seed...")
        return

    # Check if User table exists
    if not schema_editor.connection.introspection.table_names():
        print("[PEP+ Seed] Database tables not created yet, skipping user seed...")
        return

    try:
        # Check if test users already exist
        if User.objects.filter(username__in=['coord_distrital_test', 'coord_nacional_test']).exists():
            print("[PEP+ Seed] Test users already exist, skipping...")
            return
    except Exception as e:
        print(f"[PEP+ Seed] Cannot access User table yet: {e}")
        return

    print("[PEP+ Seed] Creating test users...")

    users_data = [
        {'username': 'coord_distrital_test', 'id': uuid.uuid4()},
        {'username': 'coord_nacional_test', 'id': uuid.uuid4()},
        {'username': 'tecnico_social_test', 'id': uuid.uuid4()},
        {'username': 'tecnico_admin_test', 'id': uuid.uuid4()},
        {'username': 'formador_test', 'id': uuid.uuid4()},
        {'username': 'supervisor_test', 'id': uuid.uuid4()},
    ]

    try:
        for user_data in users_data:
            User.objects.create(
                id=user_data['id'],
                username=user_data['username'],
            )
        print(f"[PEP+ Seed] Created {len(users_data)} test users")
    except Exception as e:
        print(f"[PEP+ Seed] Failed to create users: {e}")


def seed_test_locations(apps, schema_editor):
    """Create test locations (districts and localities)"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping location seed - FEED_DATA not set to true")
        return

    try:
        Location = apps.get_model('location', 'Location')
    except LookupError:
        print("[PEP+ Seed] location.Location model not available yet, skipping location seed...")
        return

    try:
        # Check if test locations already exist
        if Location.objects.filter(code__in=['test_distrito_1', 'test_distrito_2']).exists():
            print("[PEP+ Seed] Test locations already exist, skipping...")
            return
    except Exception as e:
        print(f"[PEP+ Seed] Cannot access Location table yet: {e}")
        return

    print("[PEP+ Seed] Creating test locations...")

    try:
        # Create parent location (country level)
        parent_location = Location.objects.create(
            id=1000000,
            uuid=uuid.uuid4(),
            code='TEST_COUNTRY',
            name='Test Country',
            type='C',
        )

        # Create test districts
        districts = [
            {'code': 'test_distrito_1', 'name': 'Distrito Teste 1'},
            {'code': 'test_distrito_2', 'name': 'Distrito Teste 2'},
        ]

        created_districts = []
        for i, district_data in enumerate(districts, start=1):
            district = Location.objects.create(
                id=1000000 + i,
                uuid=uuid.uuid4(),
                code=district_data['code'],
                name=district_data['name'],
                type='D',
                parent_id=parent_location.id,
            )
            created_districts.append(district)

        # Create test localities (villages)
        localities = [
            {'code': 'test_localidade_1', 'name': 'Localidade Teste 1', 'parent': created_districts[0]},
            {'code': 'test_localidade_2', 'name': 'Localidade Teste 2', 'parent': created_districts[0]},
            {'code': 'test_localidade_3', 'name': 'Localidade Teste 3', 'parent': created_districts[1]},
        ]

        for i, locality_data in enumerate(localities, start=100):
            Location.objects.create(
                id=1000000 + i,
                uuid=uuid.uuid4(),
                code=locality_data['code'],
                name=locality_data['name'],
                type='V',
                parent=locality_data['parent'],
            )

        print(f"[PEP+ Seed] Created {len(districts)} districts and {len(localities)} localities")
    except Exception as e:
        print(f"[PEP+ Seed] Failed to create locations: {e}")


def seed_modulos_educacionais(apps, schema_editor):
    """Create educational modules"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping modulos seed - FEED_DATA not set to true")
        return

    ModuloEducacional = safe_get_model(apps, 'pep_plus', 'ModuloEducacional', 'educational modules seed')
    if not ModuloEducacional:
        return

    try:
        # Check if modules already exist
        if ModuloEducacional.objects.filter(codigo__startswith='TEST_M').exists():
            print("[PEP+ Seed] Test modules already exist, skipping...")
            return
    except Exception as e:
        print(f"[PEP+ Seed] Cannot access ModuloEducacional table yet: {e}")
        return

    print("[PEP+ Seed] Creating educational modules...")

    modulos = [
        {'codigo': 'TEST_M01', 'nome': 'Módulo 1: Eu Como Cuidador', 'ordem': 1, 'duracao_semanas': 4},
        {'codigo': 'TEST_M02', 'nome': 'Módulo 2: Rotinas Diárias', 'ordem': 2, 'duracao_semanas': 4},
        {'codigo': 'TEST_M03', 'nome': 'Módulo 3: Dimensão Afetiva', 'ordem': 3, 'duracao_semanas': 4},
        {'codigo': 'TEST_M04', 'nome': 'Módulo 4: Desenvolvimento Integral', 'ordem': 4, 'duracao_semanas': 4},
        {'codigo': 'TEST_M05', 'nome': 'Módulo 5: Conversar e Aprender', 'ordem': 5, 'duracao_semanas': 4},
    ]

    try:
        for modulo_data in modulos:
            ModuloEducacional.objects.create(
                uuid=uuid.uuid4(),
                codigo=modulo_data['codigo'],
                nome=modulo_data['nome'],
                descricao=f"Descrição do {modulo_data['nome']}",
                ordem=modulo_data['ordem'],
                duracao_semanas=modulo_data['duracao_semanas'],
                ativo=True,
            )
        print(f"[PEP+ Seed] Created {len(modulos)} educational modules")
    except Exception as e:
        print(f"[PEP+ Seed] Failed to create educational modules: {e}")


def seed_grupos_familiares(apps, schema_editor):
    """Create family groups"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping grupos seed - FEED_DATA not set to true")
        return

    GrupoFamiliar = safe_get_model(apps, 'pep_plus', 'GrupoFamiliar', 'family groups seed')
    Location = safe_get_model(apps, 'location', 'Location', 'family groups seed')

    if not GrupoFamiliar or not Location:
        return

    try:
        # Check if groups already exist
        if GrupoFamiliar.objects.filter(codigo__startswith='TEST_GF').exists():
            print("[PEP+ Seed] Test family groups already exist, skipping...")
            return
    except Exception as e:
        print(f"[PEP+ Seed] Cannot access GrupoFamiliar table yet: {e}")
        return

    print("[PEP+ Seed] Creating family groups...")

    try:
        distrito = Location.objects.get(code='test_distrito_1')
        localidade = Location.objects.get(code='test_localidade_1')
    except Exception as e:
        print(f"[PEP+ Seed] Test locations not found, skipping family groups: {e}")
        return

    grupos = [
        {'codigo': 'TEST_GF001', 'nome': 'Grupo Familiar Teste 1', 'numero_familias': 15},
        {'codigo': 'TEST_GF002', 'nome': 'Grupo Familiar Teste 2', 'numero_familias': 12},
        {'codigo': 'TEST_GF003', 'nome': 'Grupo Familiar Teste 3', 'numero_familias': 18},
    ]

    try:
        for grupo_data in grupos:
            GrupoFamiliar.objects.create(
                uuid=uuid.uuid4(),
                codigo=grupo_data['codigo'],
                nome=grupo_data['nome'],
                distrito=distrito,
                localidade=localidade,
                numero_familias=grupo_data['numero_familias'],
                ativo=True,
            )
        print(f"[PEP+ Seed] Created {len(grupos)} family groups")
    except Exception as e:
        print(f"[PEP+ Seed] Failed to create family groups: {e}")


def seed_sessoes_pep(apps, schema_editor):
    """Create PEP sessions"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping sessoes seed - FEED_DATA not set to true")
        return

    SessaoPEP = apps.get_model('pep_plus', 'SessaoPEP')
    GrupoFamiliar = apps.get_model('pep_plus', 'GrupoFamiliar')
    Location = apps.get_model('location', 'Location')
    User = apps.get_model('core', 'User')

    # Check if sessions already exist
    if SessaoPEP.objects.filter(codigo_sessao__startswith='TEST_SESS').exists():
        print("[PEP+ Seed] Test sessions already exist, skipping...")
        return

    print("[PEP+ Seed] Creating PEP sessions...")

    grupo = GrupoFamiliar.objects.get(codigo='TEST_GF001')
    distrito = Location.objects.get(code='test_distrito_1')
    coord = User.objects.get(username='coord_distrital_test')
    tecnico = User.objects.get(username='tecnico_social_test')

    today = date.today()

    sessoes = [
        {
            'codigo_sessao': 'TEST_SESS001',
            'nome_modulo': 'Módulo 1: Eu Como Cuidador',
            'data_sessao': today + timedelta(days=7),
            'dia_semana': 'SEG',
            'hora_sessao': time(9, 0),
        },
        {
            'codigo_sessao': 'TEST_SESS002',
            'nome_modulo': 'Módulo 2: Rotinas Diárias',
            'data_sessao': today + timedelta(days=14),
            'dia_semana': 'TER',
            'hora_sessao': time(10, 0),
        },
        {
            'codigo_sessao': 'TEST_SESS003',
            'nome_modulo': 'Módulo 3: Dimensão Afetiva',
            'data_sessao': today + timedelta(days=21),
            'dia_semana': 'QUA',
            'hora_sessao': time(14, 0),
        },
    ]

    for sessao_data in sessoes:
        SessaoPEP.objects.create(
            uuid=uuid.uuid4(),
            codigo_sessao=sessao_data['codigo_sessao'],
            data_planejamento=today,
            coordenador_distrital=coord,
            tecnico_social=tecnico,
            distrito=distrito,
            nome_modulo=sessao_data['nome_modulo'],
            dia_semana=sessao_data['dia_semana'],
            data_sessao=sessao_data['data_sessao'],
            hora_sessao=sessao_data['hora_sessao'],
            zona='Zona Urbana',
            numero_familias=grupo.numero_familias,
            grupo_familia=grupo,
            feedback_documentacao='Sessão planejada adequadamente',
            tem_supervisao=True,
            status='PLAN',
        )

    print(f"[PEP+ Seed] Created {len(sessoes)} PEP sessions")


def seed_execucoes_sessao(apps, schema_editor):
    """Create session executions"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping execucoes seed - FEED_DATA not set to true")
        return

    ExecucaoSessao = apps.get_model('pep_plus', 'ExecucaoSessao')
    SessaoPEP = apps.get_model('pep_plus', 'SessaoPEP')
    User = apps.get_model('core', 'User')
    Location = apps.get_model('location', 'Location')

    # Check if executions already exist
    if ExecucaoSessao.objects.filter(sessao__codigo_sessao__startswith='TEST_SESS').exists():
        print("[PEP+ Seed] Test executions already exist, skipping...")
        return

    print("[PEP+ Seed] Creating session executions...")

    sessao = SessaoPEP.objects.filter(codigo_sessao='TEST_SESS001').first()
    if not sessao:
        print("[PEP+ Seed] No test session found, skipping executions...")
        return

    formador = User.objects.get(username='formador_test')
    supervisor = User.objects.get(username='supervisor_test')
    localidade = Location.objects.get(code='test_localidade_1')

    ExecucaoSessao.objects.create(
        uuid=uuid.uuid4(),
        sessao=sessao,
        formador=formador,
        supervisor=supervisor,
        localidade=localidade,
        numero_cuidadores='6-10',
        praticas_positivas=[
            {'descricao': 'Formador demonstrou paciência', 'confirmacao': 'Sim'},
            {'descricao': 'Uso adequado de materiais', 'confirmacao': 'Sim'},
        ],
        desafios_transmissao=[
            {'descricao': 'Dificuldade com horário', 'confirmacao': 'Não'},
        ],
        necessita_encaminhamento=False,
        auto_avaliacao_pontos_fortes=[
            {'descricao': 'Boa comunicação', 'confirmacao': True},
            {'descricao': 'Domínio do conteúdo', 'confirmacao': True},
        ],
        auto_avaliacao_pontos_atencao=[
            {'descricao': 'Gestão do tempo', 'confirmacao': True},
        ],
        observacoes='Sessão executada com sucesso',
    )

    print("[PEP+ Seed] Created 1 session execution")


def seed_supervisoes_sessao(apps, schema_editor):
    """Create session supervisions"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping supervisoes seed - FEED_DATA not set to true")
        return

    SupervisaoSessao = apps.get_model('pep_plus', 'SupervisaoSessao')
    SessaoPEP = apps.get_model('pep_plus', 'SessaoPEP')
    GrupoFamiliar = apps.get_model('pep_plus', 'GrupoFamiliar')
    User = apps.get_model('core', 'User')
    Location = apps.get_model('location', 'Location')

    # Check if supervisions already exist
    if SupervisaoSessao.objects.filter(sessao__codigo_sessao__startswith='TEST_SESS').exists():
        print("[PEP+ Seed] Test supervisions already exist, skipping...")
        return

    print("[PEP+ Seed] Creating session supervisions...")

    sessao = SessaoPEP.objects.filter(codigo_sessao='TEST_SESS001').first()
    if not sessao:
        print("[PEP+ Seed] No test session found, skipping supervisions...")
        return

    supervisor = User.objects.get(username='supervisor_test')
    formador = User.objects.get(username='formador_test')
    localidade = Location.objects.get(code='test_localidade_1')
    grupo = GrupoFamiliar.objects.get(codigo='TEST_GF001')

    SupervisaoSessao.objects.create(
        uuid=uuid.uuid4(),
        sessao=sessao,
        supervisor=supervisor,
        formador=formador,
        localidade=localidade,
        grupo=grupo,
        data_supervisao=date.today(),
        identificador_grupo='TEST_GF001',
        numero_participantes='6-10',
        praticas_positivas_estrategias=[
            {'descricao': 'Formador engajou participantes', 'confirmacao': 'Sim'},
        ],
        desafios_transmissao=[
            {'descricao': 'Espaço inadequado', 'confirmacao': 'Não'},
        ],
        necessita_encaminhamento=False,
        auto_avaliacao_pontos_fortes=[
            {'descricao': 'Boa metodologia', 'confirmacao': True},
        ],
        auto_avaliacao_pontos_atencao=[
            {'descricao': 'Melhorar material visual', 'confirmacao': True},
        ],
        avaliacao_execucao_metodologia=[
            {'descricao': 'Acolhida', 'confirmacao': 'Excelente'},
            {'descricao': 'Discussão', 'confirmacao': 'Adequado'},
        ],
        feedback_pontos_fortes='Formador demonstrou domínio do conteúdo',
        feedback_desafios='Necessita melhorar gestão do tempo',
        compromisso_formador='Preparar melhor o material visual',
        observacoes='Supervisão realizada conforme planejado',
    )

    print("[PEP+ Seed] Created 1 session supervision")


def seed_relatorios_distritais(apps, schema_editor):
    """Create district bimonthly reports"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping relatorios distritais seed - FEED_DATA not set to true")
        return

    RelatorioDistritalBimestral = apps.get_model('pep_plus', 'RelatorioDistritalBimestral')
    Location = apps.get_model('location', 'Location')
    User = apps.get_model('core', 'User')

    # Check if reports already exist
    if RelatorioDistritalBimestral.objects.filter(distrito__code__startswith='test_distrito').exists():
        print("[PEP+ Seed] Test district reports already exist, skipping...")
        return

    print("[PEP+ Seed] Creating district reports...")

    distrito = Location.objects.get(code='test_distrito_1')
    coord = User.objects.get(username='coord_distrital_test')
    tecnico_admin = User.objects.get(username='tecnico_admin_test')

    RelatorioDistritalBimestral.objects.create(
        uuid=uuid.uuid4(),
        distrito=distrito,
        coordenador_distrital=coord,
        tecnico_administrativo=tecnico_admin,
        periodo='BIM1',
        ano=date.today().year,
        periodo_inicio=date(date.today().year, 1, 1),
        periodo_fim=date(date.today().year, 2, 28),
        numero_localidades_atendidas=3,
        numero_familias_atendidas=45,
        numero_tecnicos_formadores=5,
        numero_sessoes_conduzidas=12,
        numero_sessoes_esperadas=15,
        numero_familias_presentes=40,
        numero_familias_esperadas=45,
        numero_familias_migraram=2,
        numero_sessoes_perdidas=3,
        percentual_sessoes=80.0,
        percentual_familias=88.9,
        media_familia_presente=3.33,
        media_familia_esperada=3.75,
        dados_tecnicos=[
            {
                'tecnicoFormador': 'Formador Teste 1',
                'sessoesExecutadas': 8,
                'sessoesPerdidas': 2,
                'modulos': 'M1, M2',
                'familiasPresentes': 25,
                'familiasMigraram': 1,
                'naoCompareceram2Sessoes': 3,
                'naoCompareceram1Sessao': 5,
            }
        ],
        dados_encaminhamentos=[
            {'tipo': 'Saúde', 'quantidade': 3},
            {'tipo': 'Educação', 'quantidade': 2},
        ],
        observacoes='Relatório do primeiro bimestre com bons resultados',
    )

    print("[PEP+ Seed] Created 1 district report")


def seed_roteiros_reuniao(apps, schema_editor):
    """Create bimonthly meeting agendas"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping roteiros seed - FEED_DATA not set to true")
        return

    RoteiroReuniaoBimestral = apps.get_model('pep_plus', 'RoteiroReuniaoBimestral')
    User = apps.get_model('core', 'User')

    # Check if agendas already exist
    if RoteiroReuniaoBimestral.objects.filter(coordenador_nacional__username='coord_nacional_test').exists():
        print("[PEP+ Seed] Test meeting agendas already exist, skipping...")
        return

    print("[PEP+ Seed] Creating meeting agendas...")

    coord_nacional = User.objects.get(username='coord_nacional_test')
    coord_distrital = User.objects.get(username='coord_distrital_test')

    RoteiroReuniaoBimestral.objects.create(
        uuid=uuid.uuid4(),
        data_reuniao=date.today(),
        horario=time(14, 0),
        coordenador_nacional=coord_nacional,
        participantes=[str(coord_distrital.id)],
        resumo_da_agenda=[
            {
                'aberturaEBoasVindas': True,
                'relatoDesafiosSolucoes': True,
                'compartilhamentoOportunidades': True,
                'apreciacaoRelatorios': True,
                'definicaoAcoesEncaminhamentos': True,
                'encerramentoProximaReuniao': True,
            }
        ],
        principais_desafios='Dificuldades com transporte e atrasos nas sessões',
        oportunidades_melhoria='Melhorar comunicação entre coordenadores e formadores',
        apreciacao_relatorios='Relatórios distritais apresentados com boa qualidade',
        plano_acao='Implementar sistema de lembretes para sessões',
        proxima_reuniao='Próxima reunião marcada para daqui a dois meses',
        data_proxima_reuniao=date.today() + timedelta(days=60),
    )

    print("[PEP+ Seed] Created 1 meeting agenda")


def seed_relatorios_supervisao(apps, schema_editor):
    """Create bimonthly supervision reports"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping relatorios supervisao seed - FEED_DATA not set to true")
        return

    RelatorioSupervisaoBimestral = apps.get_model('pep_plus', 'RelatorioSupervisaoBimestral')
    Location = apps.get_model('location', 'Location')
    User = apps.get_model('core', 'User')

    # Check if reports already exist
    if RelatorioSupervisaoBimestral.objects.filter(distrito__code__startswith='test_distrito').exists():
        print("[PEP+ Seed] Test supervision reports already exist, skipping...")
        return

    print("[PEP+ Seed] Creating supervision reports...")

    distrito = Location.objects.get(code='test_distrito_1')
    supervisor = User.objects.get(username='supervisor_test')
    formador = User.objects.get(username='formador_test')

    RelatorioSupervisaoBimestral.objects.create(
        uuid=uuid.uuid4(),
        supervisores=[str(supervisor.id)],
        numero_sessoes=5,
        numero_tecnicos_formadores=3,
        distrito=distrito,
        periodo='JAN_FEV',
        ano=date.today().year,
        avaliacoes_tecnicos=[
            {
                'idDoTecnico': str(formador.id),
                'pontosPositivos': 'Excelente domínio do conteúdo e boa relação com participantes',
                'pontosAprimorar': 'Melhorar gestão do tempo durante as sessões',
            }
        ],
        sessoes_pep=[
            {'passo': 'a. Acolhida e apresentação dos cuidadores', 'nota': 9},
            {'passo': 'b. Acolheu a presença dos cuidadores', 'nota': 10},
            {'passo': 'c. Reviu os compromissos do mês passado', 'nota': 8},
            {'passo': 'd. Fez a discussão com a imagem preparada no guia', 'nota': 7},
            {'passo': 'e. Compartilhou as mensagens chave', 'nota': 9},
            {'passo': 'f. Facilitou a prática de acordo com o guia', 'nota': 8},
            {'passo': 'g. Fez a reflexão de acordo com o guia', 'nota': 9},
            {'passo': 'h. Pediu os compromissos aos cuidadores', 'nota': 10},
            {'passo': 'i. Informou sobre a próxima sessão', 'nota': 10},
        ],
        modulos_dificuldade=[
            {
                'modulo': 'modulo1',
                'description': 'Módulo 1: Eu Como Cuidador',
                'confirmacao': True,
            },
            {
                'modulo': 'modulo3',
                'description': 'Módulo 3: Dimensão Afetiva',
                'confirmacao': True,
            },
        ],
        observacoes='Supervisão bimestral realizada com sucesso. Formadores demonstram boa capacidade.',
    )

    print("[PEP+ Seed] Created 1 supervision report")


def reverse_seed(apps, schema_editor):
    """Reverse operation - delete all test data"""
    if not should_run_seed():
        print("[PEP+ Seed] Skipping reverse - FEED_DATA not set to true")
        return

    print("[PEP+ Seed] Removing test data...")

    # Remove in reverse order of dependencies
    RelatorioSupervisaoBimestral = apps.get_model('pep_plus', 'RelatorioSupervisaoBimestral')
    RoteiroReuniaoBimestral = apps.get_model('pep_plus', 'RoteiroReuniaoBimestral')
    RelatorioDistritalBimestral = apps.get_model('pep_plus', 'RelatorioDistritalBimestral')
    SupervisaoSessao = apps.get_model('pep_plus', 'SupervisaoSessao')
    ExecucaoSessao = apps.get_model('pep_plus', 'ExecucaoSessao')
    SessaoPEP = apps.get_model('pep_plus', 'SessaoPEP')
    GrupoFamiliar = apps.get_model('pep_plus', 'GrupoFamiliar')
    ModuloEducacional = apps.get_model('pep_plus', 'ModuloEducacional')
    Location = apps.get_model('location', 'Location')
    User = apps.get_model('core', 'User')

    RelatorioSupervisaoBimestral.objects.filter(distrito__code__startswith='test_distrito').delete()
    RoteiroReuniaoBimestral.objects.filter(coordenador_nacional__username='coord_nacional_test').delete()
    RelatorioDistritalBimestral.objects.filter(distrito__code__startswith='test_distrito').delete()
    SupervisaoSessao.objects.filter(sessao__codigo_sessao__startswith='TEST_SESS').delete()
    ExecucaoSessao.objects.filter(sessao__codigo_sessao__startswith='TEST_SESS').delete()
    SessaoPEP.objects.filter(codigo_sessao__startswith='TEST_SESS').delete()
    GrupoFamiliar.objects.filter(codigo__startswith='TEST_GF').delete()
    ModuloEducacional.objects.filter(codigo__startswith='TEST_M').delete()
    Location.objects.filter(code__startswith='test_').delete()
    Location.objects.filter(code='TEST_COUNTRY').delete()
    User.objects.filter(username__endswith='_test').delete()

    print("[PEP+ Seed] Test data removed")


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0012_add_resumo_da_agenda_field'),
        ('core', '__latest__'),
        ('location', '__latest__'),
    ]

    operations = [
        migrations.RunPython(seed_test_users, reverse_seed),
        migrations.RunPython(seed_test_locations, migrations.RunPython.noop),
        migrations.RunPython(seed_modulos_educacionais, migrations.RunPython.noop),
        migrations.RunPython(seed_grupos_familiares, migrations.RunPython.noop),
        migrations.RunPython(seed_sessoes_pep, migrations.RunPython.noop),
        migrations.RunPython(seed_execucoes_sessao, migrations.RunPython.noop),
        migrations.RunPython(seed_supervisoes_sessao, migrations.RunPython.noop),
        migrations.RunPython(seed_relatorios_distritais, migrations.RunPython.noop),
        migrations.RunPython(seed_roteiros_reuniao, migrations.RunPython.noop),
        migrations.RunPython(seed_relatorios_supervisao, migrations.RunPython.noop),
    ]
