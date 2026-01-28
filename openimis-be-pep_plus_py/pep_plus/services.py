"""
PEP+ Services
Business logic for CRUD operations
"""
import json
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from core.services import BaseService
from .models import (
    ModuloEducacional, GrupoFamiliar, SessaoPEP, PresencaSessao,
    ExecucaoSessao, SupervisaoSessao, RelatorioDistritalBimestral,
    EncaminhamentoSessao, RoteiroReuniaoBimestral
)
from .validations import (
    validate_sessao_planeamento, validate_presenca_sessao,
    validate_execucao_sessao, validate_supervisao_sessao,
    validate_relatorio_distrital, validate_encaminhamento,
    validate_modulo_educacional, validate_grupo_familiar
)


def parse_json_field(value, default=None):
    """
    Parse JSON field that might come as string or already parsed object.

    Args:
        value: The value to parse (string, list, dict, or None)
        default: Default value if parsing fails or value is None

    Returns:
        Parsed value or default
    """
    if value is None:
        return default if default is not None else []

    # If already parsed (list or dict), return as is
    if isinstance(value, (list, dict)):
        return value

    # If string, try to parse JSON
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            # If parse fails, return default
            return default if default is not None else []

    # Unknown type, return default
    return default if default is not None else []


class ModuloEducacionalService(BaseService):
    """Service for School Attendance (Assiduidade Escolar) operations"""

    OBJECT_TYPE = ModuloEducacional

    @classmethod
    def create(cls, data, user):
        """Create a new school attendance record"""
        # Validate
        errors = validate_modulo_educacional(data)
        if errors:
            raise ValidationError(errors)

        # Check permissions
        if not user.has_perms(['pep_plus.add_moduloeducacional']):
            raise PermissionDenied("User does not have permission to create school attendance records")

        with transaction.atomic():
            modulo = ModuloEducacional.objects.create(
                # Identificação
                id_membro_crianca=data.get('id_membro_crianca'),
                nome=data['nome'],
                nome_encarregado=data.get('nome_encarregado'),

                # Dados escolares
                escola=data.get('escola'),
                escolaridade_actual=data.get('escolaridade_actual'),
                data_nascimento=data.get('data_nascimento'),
                id_da_crianca=data.get('id_da_crianca'),
                sexo=data.get('sexo'),
                dados_escolar_correctos=data.get('dados_escolar_correctos'),
                escola_actual=data.get('escola_actual'),
                classe=data.get('classe'),
                idade=data.get('idade'),
                dados_escolares_correctos=data.get('dados_escolares_correctos'),

                # Localização
                informacoes_localizacao=parse_json_field(data.get('informacoes_localizacao'), {}),

                # Frequência escolar
                classe_que_frequenta=data.get('classe_que_frequenta'),
                aproveitamento_primeiro_trimestre=data.get('aproveitamento_primeiro_trimestre'),
                faixa_de_faltas=data.get('faixa_de_faltas'),

                # Disciplinas
                disciplinas_basicas=data.get('disciplinas_basicas'),
                disciplinas_avancadas=data.get('disciplinas_avancadas'),

                # Observações
                observacoes=data.get('observacoes')
            )
            modulo.audit_user_id = user.id_for_audit
            modulo.save()
            return modulo

    @classmethod
    def update(cls, modulo_id, data, user):
        """Update a school attendance record"""
        try:
            modulo = ModuloEducacional.objects.get(id=modulo_id, validity_to__isnull=True)
        except ModuloEducacional.DoesNotExist:
            raise ValidationError([{'message': 'School attendance record not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_moduloeducacional']):
            raise PermissionDenied("User does not have permission to update school attendance records")

        # Validate
        errors = validate_modulo_educacional(data)
        if errors:
            raise ValidationError(errors)

        with transaction.atomic():
            # Identificação
            if 'id_membro_crianca' in data:
                modulo.id_membro_crianca = data['id_membro_crianca']
            if 'nome' in data:
                modulo.nome = data['nome']
            if 'nome_encarregado' in data:
                modulo.nome_encarregado = data['nome_encarregado']

            # Dados escolares
            if 'escola' in data:
                modulo.escola = data['escola']
            if 'escolaridade_actual' in data:
                modulo.escolaridade_actual = data['escolaridade_actual']
            if 'data_nascimento' in data:
                modulo.data_nascimento = data['data_nascimento']
            if 'id_da_crianca' in data:
                modulo.id_da_crianca = data['id_da_crianca']
            if 'sexo' in data:
                modulo.sexo = data['sexo']
            if 'dados_escolar_correctos' in data:
                modulo.dados_escolar_correctos = data['dados_escolar_correctos']
            if 'escola_actual' in data:
                modulo.escola_actual = data['escola_actual']
            if 'classe' in data:
                modulo.classe = data['classe']
            if 'idade' in data:
                modulo.idade = data['idade']
            if 'dados_escolares_correctos' in data:
                modulo.dados_escolares_correctos = data['dados_escolares_correctos']

            # Localização
            if 'informacoes_localizacao' in data:
                modulo.informacoes_localizacao = parse_json_field(data['informacoes_localizacao'], modulo.informacoes_localizacao)

            # Frequência escolar
            if 'classe_que_frequenta' in data:
                modulo.classe_que_frequenta = data['classe_que_frequenta']
            if 'aproveitamento_primeiro_trimestre' in data:
                modulo.aproveitamento_primeiro_trimestre = data['aproveitamento_primeiro_trimestre']
            if 'faixa_de_faltas' in data:
                modulo.faixa_de_faltas = data['faixa_de_faltas']

            # Disciplinas
            if 'disciplinas_basicas' in data:
                modulo.disciplinas_basicas = data['disciplinas_basicas']
            if 'disciplinas_avancadas' in data:
                modulo.disciplinas_avancadas = data['disciplinas_avancadas']

            # Observações
            if 'observacoes' in data:
                modulo.observacoes = data['observacoes']

            modulo.audit_user_id = user.id_for_audit
            modulo.save()
            return modulo

    @classmethod
    def delete(cls, modulo_id, user):
        """Soft delete a school attendance record"""
        try:
            modulo = ModuloEducacional.objects.get(id=modulo_id, validity_to__isnull=True)
        except ModuloEducacional.DoesNotExist:
            raise ValidationError([{'message': 'School attendance record not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.delete_moduloeducacional']):
            raise PermissionDenied("User does not have permission to delete school attendance records")

        with transaction.atomic():
            modulo.delete_history(user=user)
            return modulo


class GrupoFamiliarService(BaseService):
    """Service for Family Group operations"""

    OBJECT_TYPE = GrupoFamiliar

    @classmethod
    def create(cls, data, user):
        """Create a new family group"""
        # Validate
        errors = validate_grupo_familiar(data)
        if errors:
            raise ValidationError(errors)

        # Check permissions
        if not user.has_perms(['pep_plus.add_grupofamiliar']):
            raise PermissionDenied("User does not have permission to create family groups")

        with transaction.atomic():
            grupo = GrupoFamiliar.objects.create(
                codigo=data['codigo'],
                nome=data['nome'],
                distrito_id=data['distrito_id'],
                localidade_id=data.get('localidade_id'),
                numero_familias=data.get('numero_familias', 0),
                ativo=data.get('ativo', True)
            )
            grupo.audit_user_id = user.id_for_audit
            grupo.save()
            return grupo

    @classmethod
    def update(cls, grupo_id, data, user):
        """Update a family group"""
        try:
            grupo = GrupoFamiliar.objects.get(id=grupo_id, validity_to__isnull=True)
        except GrupoFamiliar.DoesNotExist:
            raise ValidationError([{'message': 'Family group not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_grupofamiliar']):
            raise PermissionDenied("User does not have permission to update family groups")

        with transaction.atomic():
            grupo.nome = data.get('nome', grupo.nome)
            grupo.distrito_id = data.get('distrito_id', grupo.distrito_id)
            grupo.localidade_id = data.get('localidade_id', grupo.localidade_id)
            grupo.numero_familias = data.get('numero_familias', grupo.numero_familias)
            grupo.ativo = data.get('ativo', grupo.ativo)
            grupo.audit_user_id = user.id_for_audit
            grupo.save()
            return grupo

    @classmethod
    def delete(cls, grupo_id, user):
        """Soft delete a family group"""
        try:
            grupo = GrupoFamiliar.objects.get(id=grupo_id, validity_to__isnull=True)
        except GrupoFamiliar.DoesNotExist:
            raise ValidationError([{'message': 'Family group not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.delete_grupofamiliar']):
            raise PermissionDenied("User does not have permission to delete family groups")

        with transaction.atomic():
            grupo.delete_history(user=user)
            return grupo


class SessaoPEPService(BaseService):
    """Service for PEP Session operations (Ferramenta 1)"""

    OBJECT_TYPE = SessaoPEP

    @classmethod
    def create(cls, data, user):
        """Create a new PEP session"""
        # Validate
        errors = validate_sessao_planeamento(data)
        if errors:
            raise ValidationError(errors)

        # Check permissions
        if not user.has_perms(['pep_plus.add_sessaopep']):
            raise PermissionDenied("User does not have permission to create PEP sessions")

        with transaction.atomic():
            sessao = SessaoPEP.objects.create(
                codigo_sessao=data['codigo_sessao'],
                data_planejamento=data['data_planejamento'],
                coordenador_distrital_id=data['coordenador_distrital_id'],
                tecnico_social_id=data['tecnico_social_id'],
                distrito_id=data['distrito_id'],
                nome_modulo=data['nome_modulo'],
                mes_modulo_anterior=data.get('mes_modulo_anterior'),
                dia_semana=data['dia_semana'],
                data_sessao=data['data_sessao'],
                hora_sessao=data['hora_sessao'],
                zona=data['zona'],
                numero_familias=data['numero_familias'],
                grupo_familia_id=data['grupo_familia_id'],
                tempo_deslocamento=data.get('tempo_deslocamento'),
                feedback_documentacao=data['feedback_documentacao'],
                tem_supervisao=data.get('tem_supervisao', False),
                observacoes=data.get('observacoes'),
                status=data.get('status', 'PLAN')
            )
            sessao.audit_user_id = user.id_for_audit
            sessao.save()
            return sessao

    @classmethod
    def update(cls, sessao_id, data, user):
        """Update a PEP session"""
        try:
            sessao = SessaoPEP.objects.get(id=sessao_id, validity_to__isnull=True)
        except SessaoPEP.DoesNotExist:
            raise ValidationError([{'message': 'PEP session not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_sessaopep']):
            raise PermissionDenied("User does not have permission to update PEP sessions")

        # Validate
        errors = validate_sessao_planeamento(data)
        if errors:
            raise ValidationError(errors)

        with transaction.atomic():
            sessao.data_planejamento = data.get('data_planejamento', sessao.data_planejamento)
            sessao.coordenador_distrital_id = data.get('coordenador_distrital_id', sessao.coordenador_distrital_id)
            sessao.tecnico_social_id = data.get('tecnico_social_id', sessao.tecnico_social_id)
            sessao.distrito_id = data.get('distrito_id', sessao.distrito_id)
            sessao.nome_modulo = data.get('nome_modulo', sessao.nome_modulo)
            sessao.mes_modulo_anterior = data.get('mes_modulo_anterior', sessao.mes_modulo_anterior)
            sessao.dia_semana = data.get('dia_semana', sessao.dia_semana)
            sessao.data_sessao = data.get('data_sessao', sessao.data_sessao)
            sessao.hora_sessao = data.get('hora_sessao', sessao.hora_sessao)
            sessao.zona = data.get('zona', sessao.zona)
            sessao.numero_familias = data.get('numero_familias', sessao.numero_familias)
            sessao.grupo_familia_id = data.get('grupo_familia_id', sessao.grupo_familia_id)
            sessao.tempo_deslocamento = data.get('tempo_deslocamento', sessao.tempo_deslocamento)
            sessao.feedback_documentacao = data.get('feedback_documentacao', sessao.feedback_documentacao)
            sessao.tem_supervisao = data.get('tem_supervisao', sessao.tem_supervisao)
            sessao.observacoes = data.get('observacoes', sessao.observacoes)
            sessao.status = data.get('status', sessao.status)
            sessao.audit_user_id = user.id_for_audit
            sessao.save()
            return sessao

    @classmethod
    def delete(cls, sessao_id, user):
        """Soft delete a PEP session"""
        try:
            sessao = SessaoPEP.objects.get(id=sessao_id, validity_to__isnull=True)
        except SessaoPEP.DoesNotExist:
            raise ValidationError([{'message': 'PEP session not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.delete_sessaopep']):
            raise PermissionDenied("User does not have permission to delete PEP sessions")

        with transaction.atomic():
            sessao.delete_history(user=user)
            return sessao

    @classmethod
    def create_multiple(cls, sessions_list, user):
        """Create multiple PEP sessions at once"""
        # Check permissions
        if not user.has_perms(['pep_plus.add_sessaopep']):
            raise PermissionDenied("User does not have permission to create PEP sessions")

        with transaction.atomic():
            sessoes = []
            for session_data in sessions_list:
                # Validate each session
                errors = validate_sessao_planeamento(session_data)
                if errors:
                    raise ValidationError(errors)

                sessao = SessaoPEP.objects.create(
                    codigo_sessao=session_data['codigo_sessao'],
                    data_planejamento=session_data['data_planejamento'],
                    coordenador_distrital_id=session_data['coordenador_distrital_id'],
                    tecnico_social_id=session_data['tecnico_social_id'],
                    distrito_id=session_data['distrito_id'],
                    nome_modulo=session_data['nome_modulo'],
                    mes_modulo_anterior=session_data.get('mes_modulo_anterior'),
                    dia_semana=session_data['dia_semana'],
                    data_sessao=session_data['data_sessao'],
                    hora_sessao=session_data['hora_sessao'],
                    zona=session_data['zona'],
                    numero_familias=session_data['numero_familias'],
                    grupo_familia_id=session_data['grupo_familia_id'],
                    tempo_deslocamento=session_data.get('tempo_deslocamento'),
                    feedback_documentacao=session_data['feedback_documentacao'],
                    tem_supervisao=session_data.get('tem_supervisao', False),
                    observacoes=session_data.get('observacoes'),
                    status=session_data.get('status', 'PLAN')
                )
                sessao.audit_user_id = user.id_for_audit
                sessao.save()
                sessoes.append(sessao)

            return sessoes

    @classmethod
    def update_multiple(cls, sessions_list, user):
        """Update multiple PEP sessions at once"""
        # Check permissions
        if not user.has_perms(['pep_plus.change_sessaopep']):
            raise PermissionDenied("User does not have permission to update PEP sessions")

        with transaction.atomic():
            sessoes = []
            for session_data in sessions_list:
                sessao_id = session_data.pop('id')

                try:
                    sessao = SessaoPEP.objects.get(id=sessao_id, validity_to__isnull=True)
                except SessaoPEP.DoesNotExist:
                    raise ValidationError([{'message': f'Session with id {sessao_id} not found'}])

                # Update only provided fields
                if 'codigo_sessao' in session_data:
                    sessao.codigo_sessao = session_data['codigo_sessao']
                if 'data_planejamento' in session_data:
                    sessao.data_planejamento = session_data['data_planejamento']
                if 'coordenador_distrital_id' in session_data:
                    sessao.coordenador_distrital_id = session_data['coordenador_distrital_id']
                if 'tecnico_social_id' in session_data:
                    sessao.tecnico_social_id = session_data['tecnico_social_id']
                if 'distrito_id' in session_data:
                    sessao.distrito_id = session_data['distrito_id']
                if 'nome_modulo' in session_data:
                    sessao.nome_modulo = session_data['nome_modulo']
                if 'mes_modulo_anterior' in session_data:
                    sessao.mes_modulo_anterior = session_data['mes_modulo_anterior']
                if 'dia_semana' in session_data:
                    sessao.dia_semana = session_data['dia_semana']
                if 'data_sessao' in session_data:
                    sessao.data_sessao = session_data['data_sessao']
                if 'hora_sessao' in session_data:
                    sessao.hora_sessao = session_data['hora_sessao']
                if 'zona' in session_data:
                    sessao.zona = session_data['zona']
                if 'numero_familias' in session_data:
                    sessao.numero_familias = session_data['numero_familias']
                if 'grupo_familia_id' in session_data:
                    sessao.grupo_familia_id = session_data['grupo_familia_id']
                if 'tempo_deslocamento' in session_data:
                    sessao.tempo_deslocamento = session_data['tempo_deslocamento']
                if 'feedback_documentacao' in session_data:
                    sessao.feedback_documentacao = session_data['feedback_documentacao']
                if 'tem_supervisao' in session_data:
                    sessao.tem_supervisao = session_data['tem_supervisao']
                if 'observacoes' in session_data:
                    sessao.observacoes = session_data['observacoes']
                if 'status' in session_data:
                    sessao.status = session_data['status']

                sessao.audit_user_id = user.id_for_audit
                sessao.save()
                sessoes.append(sessao)

            return sessoes


class PresencaSessaoService(BaseService):
    """Service for Session Attendance operations (Ferramenta 2)"""

    OBJECT_TYPE = PresencaSessao

    @classmethod
    def create(cls, data, user):
        """Create a new attendance record"""
        # Validate
        errors = validate_presenca_sessao(data)
        if errors:
            raise ValidationError(errors)

        # Check permissions
        if not user.has_perms(['pep_plus.add_presencasessao']):
            raise PermissionDenied("User does not have permission to create attendance records")

        with transaction.atomic():
            presenca = PresencaSessao.objects.create(
                sessao_id=data['sessao_id'],
                familia_id=data['familia_id'],
                nome_familia=data.get('nome_familia'),
                grupo_id=data.get('grupo_id'),
                estado=data.get('estado', 'PRES'),
                codigo_encaminhamento=data.get('codigo_encaminhamento'),
                nome_instituicao=data.get('nome_instituicao'),
                observacoes=data.get('observacoes')
            )
            presenca.audit_user_id = user.id_for_audit
            presenca.save()
            return presenca

    @classmethod
    def update(cls, presenca_id, data, user):
        """Update an attendance record"""
        try:
            presenca = PresencaSessao.objects.get(id=presenca_id, validity_to__isnull=True)
        except PresencaSessao.DoesNotExist:
            raise ValidationError([{'message': 'Attendance record not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_presencasessao']):
            raise PermissionDenied("User does not have permission to update attendance records")

        with transaction.atomic():
            presenca.estado = data.get('estado', presenca.estado)
            presenca.codigo_encaminhamento = data.get('codigo_encaminhamento', presenca.codigo_encaminhamento)
            presenca.nome_instituicao = data.get('nome_instituicao', presenca.nome_instituicao)
            presenca.observacoes = data.get('observacoes', presenca.observacoes)
            presenca.audit_user_id = user.id_for_audit
            presenca.save()
            return presenca

    @classmethod
    def delete(cls, presenca_id, user):
        """Soft delete an attendance record"""
        try:
            presenca = PresencaSessao.objects.get(id=presenca_id, validity_to__isnull=True)
        except PresencaSessao.DoesNotExist:
            raise ValidationError([{'message': 'Attendance record not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.delete_presencasessao']):
            raise PermissionDenied("User does not have permission to delete attendance records")

        with transaction.atomic():
            presenca.delete_history(user=user)
            return presenca

    @classmethod
    def register_multiple_attendances(cls, sessao_id, familias_list, user):
        """Register multiple family attendances at once"""
        # Check permissions
        if not user.has_perms(['pep_plus.add_presencasessao']):
            raise PermissionDenied("User does not have permission to create attendance records")

        with transaction.atomic():
            presencas = []
            for familia_data in familias_list:
                data = {
                    'sessao_id': sessao_id,
                    **familia_data
                }
                errors = validate_presenca_sessao(data)
                if errors:
                    raise ValidationError(errors)

                presenca = PresencaSessao.objects.create(
                    sessao_id=sessao_id,
                    familia_id=familia_data['familia_id'],
                    nome_familia=familia_data.get('nome_familia'),
                    grupo_id=familia_data.get('grupo_id'),
                    estado=familia_data.get('estado', 'PRES'),
                    codigo_encaminhamento=familia_data.get('codigo_encaminhamento'),
                    nome_instituicao=familia_data.get('nome_instituicao'),
                    observacoes=familia_data.get('observacoes')
                )
                presenca.audit_user_id = user.id_for_audit
                presenca.save()
                presencas.append(presenca)

            return presencas

    @classmethod
    def registrar_presencas_batch(cls, data, user):
        """Batch register attendance with session execution details (Ferramenta 2)"""
        from .models import SessaoPEP, ExecucaoSessao

        # Check permissions
        if not user.has_perms(['pep_plus.add_presencasessao']):
            raise PermissionDenied("User does not have permission to create attendance records")

        # Validate session exists
        try:
            sessao = SessaoPEP.objects.get(id=data['sessao_id'], validity_to__isnull=True)
        except SessaoPEP.DoesNotExist:
            raise ValidationError([{'message': 'Session not found'}])

        # Validate session details match
        if sessao.distrito_id != data['distrito_id']:
            raise ValidationError([{'message': 'District ID does not match session district'}])
        if sessao.grupo_familia_id != data['grupo_familia_id']:
            raise ValidationError([{'message': 'Family group ID does not match session family group'}])

        with transaction.atomic():
            # Update SessaoPEP with actual execution data
            sessao.data_sessao = data['data_sessao']
            sessao.nome_modulo = data['nome_modulo']
            if 'mes_modulo_anterior' in data:
                sessao.mes_modulo_anterior = data['mes_modulo_anterior']
            sessao.audit_user_id = user.id_for_audit
            sessao.save()

            # Create or update ExecucaoSessao with session details
            execucao, created = ExecucaoSessao.objects.update_or_create(
                sessao=sessao,
                defaults={
                    'formador_id': data['formador_id'],
                    'localidade_id': data.get('localidade_id'),
                    'data_execucao': data['data_sessao']
                }
            )
            if created:
                execucao.audit_user_id = user.id_for_audit
                execucao.save()

            # Register all family attendances
            presencas = []
            for presenca_item in data['presencas']:
                # Delete existing attendance for this family if exists
                PresencaSessao.objects.filter(
                    sessao=sessao,
                    familia_id=presenca_item['familia_id'],
                    validity_to__isnull=True
                ).delete()

                # Create new attendance
                presenca = PresencaSessao.objects.create(
                    sessao=sessao,
                    familia_id=presenca_item['familia_id'],
                    nome_familia=presenca_item.get('nome_familia'),
                    grupo_id=sessao.grupo_familia_id,  # Get from session
                    estado=presenca_item['estado'],
                    codigo_encaminhamento=presenca_item.get('codigo_encaminhamento'),
                    nome_instituicao=presenca_item.get('nome_instituicao'),
                    observacoes=presenca_item.get('observacoes')
                )
                presenca.audit_user_id = user.id_for_audit
                presenca.save()
                presencas.append(presenca)

            return {
                'execucao': execucao,
                'presencas': presencas
            }


class ExecucaoSessaoService(BaseService):
    """Service for Session Execution operations (Ferramenta 3)"""

    OBJECT_TYPE = ExecucaoSessao

    @classmethod
    def create(cls, data, user):
        """Create a new session execution record"""
        # Validate
        errors = validate_execucao_sessao(data)
        if errors:
            raise ValidationError(errors)

        # Check permissions
        if not user.has_perms(['pep_plus.add_execucaosessao']):
            raise PermissionDenied("User does not have permission to create execution records")

        # Check if session already has an execution record (OneToOne constraint)
        sessao_id = data['sessao_id']
        existing_execucao = ExecucaoSessao.objects.filter(
            sessao_id=sessao_id,
            validity_to__isnull=True
        ).first()

        if existing_execucao:
            raise ValidationError(
                f'Esta sessão já possui uma execução registrada (ID: {existing_execucao.id}). '
                f'Cada sessão pode ter apenas uma execução. '
                f'Use a operação de atualização para modificar a execução existente.'
            )

        with transaction.atomic():
            execucao = ExecucaoSessao.objects.create(
                sessao_id=data['sessao_id'],
                formador_id=data['formador_id'],
                supervisor_id=data.get('supervisor_id'),
                localidade_id=data.get('localidade_id'),
                numero_cuidadores=data.get('numero_cuidadores', '0'),
                praticas_positivas=parse_json_field(data.get('praticas_positivas'), []),
                outras_praticas_positivas=data.get('outras_praticas_positivas'),
                desafios_transmissao=parse_json_field(data.get('desafios_transmissao'), []),
                outros_desafios=data.get('outros_desafios'),
                necessita_encaminhamento=data.get('necessita_encaminhamento', False),
                auto_avaliacao_pontos_fortes=parse_json_field(data.get('auto_avaliacao_pontos_fortes'), []),
                auto_avaliacao_pontos_atencao=parse_json_field(data.get('auto_avaliacao_pontos_atencao'), []),
                avaliacao_metodologia=parse_json_field(data.get('avaliacao_metodologia'), {}),
                observacoes=data.get('observacoes')
            )
            execucao.audit_user_id = user.id_for_audit
            execucao.save()

            # Update session status
            sessao = execucao.sessao
            sessao.status = 'EXEC'
            sessao.save()

            return execucao

    @classmethod
    def update(cls, execucao_id, data, user):
        """Update a session execution record"""
        try:
            execucao = ExecucaoSessao.objects.get(id=execucao_id, validity_to__isnull=True)
        except ExecucaoSessao.DoesNotExist:
            raise ValidationError([{'message': 'Execution record not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_execucaosessao']):
            raise PermissionDenied("User does not have permission to update execution records")

        with transaction.atomic():
            execucao.numero_cuidadores = data.get('numero_cuidadores', execucao.numero_cuidadores)
            if 'praticas_positivas' in data:
                execucao.praticas_positivas = parse_json_field(data['praticas_positivas'], execucao.praticas_positivas)
            execucao.outras_praticas_positivas = data.get('outras_praticas_positivas',
                                                          execucao.outras_praticas_positivas)
            if 'desafios_transmissao' in data:
                execucao.desafios_transmissao = parse_json_field(data['desafios_transmissao'], execucao.desafios_transmissao)
            execucao.outros_desafios = data.get('outros_desafios', execucao.outros_desafios)
            execucao.necessita_encaminhamento = data.get('necessita_encaminhamento',
                                                         execucao.necessita_encaminhamento)
            if 'auto_avaliacao_pontos_fortes' in data:
                execucao.auto_avaliacao_pontos_fortes = parse_json_field(data['auto_avaliacao_pontos_fortes'],
                                                                         execucao.auto_avaliacao_pontos_fortes)
            if 'auto_avaliacao_pontos_atencao' in data:
                execucao.auto_avaliacao_pontos_atencao = parse_json_field(data['auto_avaliacao_pontos_atencao'],
                                                                          execucao.auto_avaliacao_pontos_atencao)
            if 'avaliacao_metodologia' in data:
                execucao.avaliacao_metodologia = parse_json_field(data['avaliacao_metodologia'], execucao.avaliacao_metodologia)
            execucao.observacoes = data.get('observacoes', execucao.observacoes)
            execucao.audit_user_id = user.id_for_audit
            execucao.save()
            return execucao


class SupervisaoSessaoService(BaseService):
    """Service for Session Supervision operations (Ferramenta 4)"""

    OBJECT_TYPE = SupervisaoSessao

    @classmethod
    def create(cls, data, user):
        """Create a new supervision record"""
        # Validate
        errors = validate_supervisao_sessao(data)
        if errors:
            raise ValidationError(errors)

        # Check permissions
        if not user.has_perms(['pep_plus.add_supervisaosessao']):
            raise PermissionDenied("User does not have permission to create supervision records")

        with transaction.atomic():
            supervisao = SupervisaoSessao.objects.create(
                sessao_id=data['sessao_id'],
                supervisor_id=data['supervisor_id'],
                formador_id=data['formador_id'],
                localidade_id=data.get('localidade_id'),
                grupo_id=data.get('grupo_id'),
                data_supervisao=data['data_supervisao'],
                data_modulo_anterior=data.get('data_modulo_anterior'),
                identificador_grupo=data['identificador_grupo'],
                numero_participantes=data.get('numero_participantes', '0'),
                praticas_positivas_estrategias=parse_json_field(data.get('praticas_positivas_estrategias'), []),
                desafios_transmissao=parse_json_field(data.get('desafios_transmissao'), []),
                necessita_encaminhamento=data.get('necessita_encaminhamento', False),
                auto_avaliacao_pontos_fortes=parse_json_field(data.get('auto_avaliacao_pontos_fortes'), []),
                auto_avaliacao_pontos_atencao=parse_json_field(data.get('auto_avaliacao_pontos_atencao'), []),
                avaliacao_execucao_metodologia=parse_json_field(data.get('avaliacao_execucao_metodologia'), []),
                metodologia_passos=parse_json_field(data.get('metodologia_passos'), []),
                feedback_pontos_fortes=data.get('feedback_pontos_fortes'),
                feedback_desafios=data.get('feedback_desafios'),
                compromisso_formador=data.get('compromisso_formador'),
                observacoes=data.get('observacoes')
            )
            supervisao.audit_user_id = user.id_for_audit
            supervisao.save()
            return supervisao

    @classmethod
    def update(cls, supervisao_id, data, user):
        """Update a supervision record"""
        try:
            supervisao = SupervisaoSessao.objects.get(id=supervisao_id, validity_to__isnull=True)
        except SupervisaoSessao.DoesNotExist:
            raise ValidationError([{'message': 'Supervision record not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_supervisaosessao']):
            raise PermissionDenied("User does not have permission to update supervision records")

        with transaction.atomic():
            supervisao.numero_participantes = data.get('numero_participantes', supervisao.numero_participantes)
            if 'praticas_positivas_estrategias' in data:
                supervisao.praticas_positivas_estrategias = parse_json_field(data['praticas_positivas_estrategias'],
                                                                             supervisao.praticas_positivas_estrategias)
            if 'desafios_transmissao' in data:
                supervisao.desafios_transmissao = parse_json_field(data['desafios_transmissao'], supervisao.desafios_transmissao)
            supervisao.necessita_encaminhamento = data.get('necessita_encaminhamento',
                                                           supervisao.necessita_encaminhamento)
            if 'auto_avaliacao_pontos_fortes' in data:
                supervisao.auto_avaliacao_pontos_fortes = parse_json_field(data['auto_avaliacao_pontos_fortes'],
                                                                           supervisao.auto_avaliacao_pontos_fortes)
            if 'auto_avaliacao_pontos_atencao' in data:
                supervisao.auto_avaliacao_pontos_atencao = parse_json_field(data['auto_avaliacao_pontos_atencao'],
                                                                            supervisao.auto_avaliacao_pontos_atencao)
            if 'avaliacao_execucao_metodologia' in data:
                supervisao.avaliacao_execucao_metodologia = parse_json_field(data['avaliacao_execucao_metodologia'],
                                                                              supervisao.avaliacao_execucao_metodologia)
            if 'metodologia_passos' in data:
                supervisao.metodologia_passos = parse_json_field(data['metodologia_passos'], supervisao.metodologia_passos)
            supervisao.feedback_pontos_fortes = data.get('feedback_pontos_fortes', supervisao.feedback_pontos_fortes)
            supervisao.feedback_desafios = data.get('feedback_desafios', supervisao.feedback_desafios)
            supervisao.compromisso_formador = data.get('compromisso_formador', supervisao.compromisso_formador)
            supervisao.observacoes = data.get('observacoes', supervisao.observacoes)
            supervisao.audit_user_id = user.id_for_audit
            supervisao.save()
            return supervisao


class RelatorioDistritalService(BaseService):
    """Service for District Bimonthly Report operations (Ferramenta 5)"""

    OBJECT_TYPE = RelatorioDistritalBimestral

    @classmethod
    def generate(cls, distrito_id, periodo, ano, user):
        """Generate a new bimonthly report"""
        # Implementation for automatic report generation
        # This would aggregate data from sessions, attendance, etc.
        pass

    @classmethod
    def create(cls, data, user):
        """Create a new district report"""
        # Validate
        errors = validate_relatorio_distrital(data)
        if errors:
            raise ValidationError(errors)

        # Check permissions
        if not user.has_perms(['pep_plus.add_relat oriodistritalbimestral']):
            raise PermissionDenied("User does not have permission to create district reports")

        with transaction.atomic():
            relatorio = RelatorioDistritalBimestral.objects.create(
                distrito_id=data['distrito_id'],
                coordenador_distrital_id=data['coordenador_distrital_id'],
                tecnico_administrativo_id=data.get('tecnico_administrativo_id'),
                periodo=data['periodo'],
                ano=data['ano'],
                periodo_inicio=data['periodo_inicio'],
                periodo_fim=data['periodo_fim'],
                numero_localidades_atendidas=data.get('numero_localidades_atendidas', 0),
                numero_familias_atendidas=data.get('numero_familias_atendidas', 0),
                numero_tecnicos_formadores=data.get('numero_tecnicos_formadores', 0),
                numero_sessoes_conduzidas=data.get('numero_sessoes_conduzidas', 0),
                numero_sessoes_esperadas=data.get('numero_sessoes_esperadas', 0),
                numero_familias_presentes=data.get('numero_familias_presentes', 0),
                numero_familias_esperadas=data.get('numero_familias_esperadas', 0),
                percentual_sessoes=data.get('percentual_sessoes', 0),
                percentual_familias=data.get('percentual_familias', 0),
                numero_familias_migraram=data.get('numero_familias_migraram', 0),
                numero_sessoes_perdidas=data.get('numero_sessoes_perdidas', 0),
                media_familia_presente=data.get('media_familia_presente', 0),
                media_familia_esperada=data.get('media_familia_esperada', 0),
                dados_tecnicos=data.get('dados_tecnicos', []),
                dados_encaminhamentos=data.get('dados_encaminhamentos', []),
                observacoes=data.get('observacoes')
            )
            relatorio.audit_user_id = user.id_for_audit
            relatorio.save()
            return relatorio

    @classmethod
    def update(cls, relatorio_id, data, user):
        """Update a district report"""
        try:
            relatorio = RelatorioDistritalBimestral.objects.get(id=relatorio_id, validity_to__isnull=True)
        except RelatorioDistritalBimestral.DoesNotExist:
            raise ValidationError([{'message': 'District report not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_relatoriodistritalbimestral']):
            raise PermissionDenied("User does not have permission to update district reports")

        with transaction.atomic():
            # Update statistics
            if 'numero_localidades_atendidas' in data:
                relatorio.numero_localidades_atendidas = data['numero_localidades_atendidas']
            if 'numero_familias_atendidas' in data:
                relatorio.numero_familias_atendidas = data['numero_familias_atendidas']
            if 'numero_tecnicos_formadores' in data:
                relatorio.numero_tecnicos_formadores = data['numero_tecnicos_formadores']
            if 'numero_sessoes_conduzidas' in data:
                relatorio.numero_sessoes_conduzidas = data['numero_sessoes_conduzidas']
            if 'numero_sessoes_esperadas' in data:
                relatorio.numero_sessoes_esperadas = data['numero_sessoes_esperadas']
            if 'numero_familias_presentes' in data:
                relatorio.numero_familias_presentes = data['numero_familias_presentes']
            if 'numero_familias_esperadas' in data:
                relatorio.numero_familias_esperadas = data['numero_familias_esperadas']
            if 'numero_familias_migraram' in data:
                relatorio.numero_familias_migraram = data['numero_familias_migraram']
            if 'numero_sessoes_perdidas' in data:
                relatorio.numero_sessoes_perdidas = data['numero_sessoes_perdidas']

            # Update calculated percentages
            if 'percentual_sessoes' in data:
                relatorio.percentual_sessoes = data['percentual_sessoes']
            if 'percentual_familias' in data:
                relatorio.percentual_familias = data['percentual_familias']
            if 'media_familia_presente' in data:
                relatorio.media_familia_presente = data['media_familia_presente']
            if 'media_familia_esperada' in data:
                relatorio.media_familia_esperada = data['media_familia_esperada']

            # Update detailed data
            if 'dados_tecnicos' in data:
                relatorio.dados_tecnicos = data['dados_tecnicos']
            if 'dados_encaminhamentos' in data:
                relatorio.dados_encaminhamentos = data['dados_encaminhamentos']
            if 'observacoes' in data:
                relatorio.observacoes = data['observacoes']

            relatorio.audit_user_id = user.id_for_audit
            relatorio.save()
            return relatorio

    @classmethod
    def delete(cls, relatorio_id, user):
        """Delete (soft delete) a district report"""
        try:
            relatorio = RelatorioDistritalBimestral.objects.get(id=relatorio_id, validity_to__isnull=True)
        except RelatorioDistritalBimestral.DoesNotExist:
            raise ValidationError([{'message': 'District report not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.delete_relatoriodistritalbimestral']):
            raise PermissionDenied("User does not have permission to delete district reports")

        with transaction.atomic():
            relatorio.delete_history()
            return relatorio


class EncaminhamentoService(BaseService):
    """Service for Referral operations"""

    OBJECT_TYPE = EncaminhamentoSessao

    @classmethod
    def create(cls, data, user):
        """Create a new referral"""
        # Validate
        errors = validate_encaminhamento(data)
        if errors:
            raise ValidationError(errors)

        # Check permissions
        if not user.has_perms(['pep_plus.add_encaminhamentosessao']):
            raise PermissionDenied("User does not have permission to create referrals")

        with transaction.atomic():
            encaminhamento = EncaminhamentoSessao.objects.create(
                sessao_id=data['sessao_id'],
                familia_id=data['familia_id'],
                nome_familia=data['nome_familia'],
                codigo_encaminhamento=data['codigo_encaminhamento'],
                descricao=data['descricao'],
                status=data.get('status', 'PEND'),
                tecnico_responsavel_id=data.get('tecnico_responsavel_id'),
                observacoes=data.get('observacoes')
            )
            encaminhamento.audit_user_id = user.id_for_audit
            encaminhamento.save()
            return encaminhamento

    @classmethod
    def update(cls, encaminhamento_id, data, user):
        """Update a referral"""
        try:
            encaminhamento = EncaminhamentoSessao.objects.get(id=encaminhamento_id, validity_to__isnull=True)
        except EncaminhamentoSessao.DoesNotExist:
            raise ValidationError([{'message': 'Referral not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_encaminhamentosessao']):
            raise PermissionDenied("User does not have permission to update referrals")

        with transaction.atomic():
            encaminhamento.status = data.get('status', encaminhamento.status)
            encaminhamento.tecnico_responsavel_id = data.get('tecnico_responsavel_id',
                                                             encaminhamento.tecnico_responsavel_id)
            encaminhamento.observacoes = data.get('observacoes', encaminhamento.observacoes)
            if data.get('status') == 'CONC' and not encaminhamento.data_conclusao:
                from django.utils import timezone
                encaminhamento.data_conclusao = timezone.now().date()
            encaminhamento.audit_user_id = user.id_for_audit
            encaminhamento.save()
            return encaminhamento


class RoteiroReuniaoService(BaseService):
    """Service for Bimonthly Meeting Agenda operations (Ferramenta 6)"""

    @classmethod
    def create(cls, data, user):
        """Create a new bimonthly meeting agenda"""
        # Check permissions
        if not user.has_perms(['pep_plus.add_roteioreuniaobimestral']):
            raise PermissionDenied("User does not have permission to create bimonthly meeting agendas")

        with transaction.atomic():
            roteiro = RoteiroReuniaoBimestral.objects.create(
                data_reuniao=data['data_reuniao'],
                horario=data['horario'],
                coordenador_nacional_id=data['coordenador_nacional_id'],
                participantes=parse_json_field(data.get('participantes'), []),
                resumo_da_agenda=parse_json_field(data.get('resumo_da_agenda'), []),
                principais_desafios=data.get('principais_desafios'),
                oportunidades_melhoria=data.get('oportunidades_melhoria'),
                apreciacao_relatorios=data.get('apreciacao_relatorios'),
                plano_acao=data.get('plano_acao'),
                proxima_reuniao=data.get('proxima_reuniao'),
                data_proxima_reuniao=data.get('data_proxima_reuniao')
            )
            roteiro.audit_user_id = user.id_for_audit
            roteiro.save()
            return roteiro

    @classmethod
    def update(cls, roteiro_id, data, user):
        """Update a bimonthly meeting agenda"""
        try:
            roteiro = RoteiroReuniaoBimestral.objects.get(id=roteiro_id, validity_to__isnull=True)
        except RoteiroReuniaoBimestral.DoesNotExist:
            raise ValidationError([{'message': 'Bimonthly meeting agenda not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_roteioreuniaobimestral']):
            raise PermissionDenied("User does not have permission to update bimonthly meeting agendas")

        with transaction.atomic():
            # Update fields if provided
            if 'data_reuniao' in data:
                roteiro.data_reuniao = data['data_reuniao']
            if 'horario' in data:
                roteiro.horario = data['horario']
            if 'coordenador_nacional_id' in data:
                roteiro.coordenador_nacional_id = data['coordenador_nacional_id']
            if 'participantes' in data:
                roteiro.participantes = parse_json_field(data['participantes'], roteiro.participantes)
            if 'resumo_da_agenda' in data:
                roteiro.resumo_da_agenda = parse_json_field(data['resumo_da_agenda'], roteiro.resumo_da_agenda)
            if 'principais_desafios' in data:
                roteiro.principais_desafios = data['principais_desafios']
            if 'oportunidades_melhoria' in data:
                roteiro.oportunidades_melhoria = data['oportunidades_melhoria']
            if 'apreciacao_relatorios' in data:
                roteiro.apreciacao_relatorios = data['apreciacao_relatorios']
            if 'plano_acao' in data:
                roteiro.plano_acao = data['plano_acao']
            if 'proxima_reuniao' in data:
                roteiro.proxima_reuniao = data['proxima_reuniao']
            if 'data_proxima_reuniao' in data:
                roteiro.data_proxima_reuniao = data['data_proxima_reuniao']

            roteiro.audit_user_id = user.id_for_audit
            roteiro.save()
            return roteiro

    @classmethod
    def delete(cls, roteiro_id, user):
        """Soft delete a bimonthly meeting agenda"""
        try:
            roteiro = RoteiroReuniaoBimestral.objects.get(id=roteiro_id, validity_to__isnull=True)
        except RoteiroReuniaoBimestral.DoesNotExist:
            raise ValidationError([{'message': 'Bimonthly meeting agenda not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.delete_roteioreuniaobimestral']):
            raise PermissionDenied("User does not have permission to delete bimonthly meeting agendas")

        with transaction.atomic():
            from django.utils import timezone
            roteiro.validity_to = timezone.now()
            roteiro.audit_user_id = user.id_for_audit
            roteiro.save()
            return roteiro


class RelatorioSupervisaoService(BaseService):
    """Service for Bimonthly Supervision Report operations (Ferramenta 7)"""

    @classmethod
    def create(cls, data, user):
        """Create a new bimonthly supervision report (Ferramenta 7)"""
        from .models import RelatorioSupervisaoBimestral

        # Check permissions
        if not user.has_perms(['pep_plus.add_relatoriosupervisaobimestral']):
            raise PermissionDenied("User does not have permission to create bimonthly supervision reports")

        with transaction.atomic():
            relatorio = RelatorioSupervisaoBimestral.objects.create(
                supervisores=parse_json_field(data.get('supervisores'), []),
                numero_sessoes=data['numero_sessoes'],
                numero_tecnicos_formadores=data['numero_tecnicos_formadores'],
                distrito_id=data['distrito_id'],
                periodo=data['periodo'],
                ano=data['ano'],
                avaliacoes_tecnicos=parse_json_field(data.get('avaliacoes_tecnicos'), []),
                sessoes_pep=parse_json_field(data.get('sessoes_pep'), []),
                modulos_dificuldade=parse_json_field(data.get('modulos_dificuldade'), []),
                observacoes=data.get('observacoes')
            )
            relatorio.audit_user_id = user.id_for_audit
            relatorio.save()
            return relatorio

    @classmethod
    def update(cls, data, user):
        """Update an existing bimonthly supervision report (Ferramenta 7)"""
        from .models import RelatorioSupervisaoBimestral

        try:
            relatorio = RelatorioSupervisaoBimestral.objects.get(id=data['id'], validity_to__isnull=True)
        except RelatorioSupervisaoBimestral.DoesNotExist:
            raise ValidationError([{'message': 'Bimonthly supervision report not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_relatoriosupervisaobimestral']):
            raise PermissionDenied("User does not have permission to update bimonthly supervision reports")

        with transaction.atomic():
            # Update fields if provided
            if 'supervisores' in data:
                relatorio.supervisores = parse_json_field(data['supervisores'], relatorio.supervisores)
            if 'numero_sessoes' in data:
                relatorio.numero_sessoes = data['numero_sessoes']
            if 'numero_tecnicos_formadores' in data:
                relatorio.numero_tecnicos_formadores = data['numero_tecnicos_formadores']
            if 'distrito_id' in data:
                relatorio.distrito_id = data['distrito_id']
            if 'periodo' in data:
                relatorio.periodo = data['periodo']
            if 'ano' in data:
                relatorio.ano = data['ano']
            if 'avaliacoes_tecnicos' in data:
                relatorio.avaliacoes_tecnicos = parse_json_field(data['avaliacoes_tecnicos'], relatorio.avaliacoes_tecnicos)
            if 'sessoes_pep' in data:
                relatorio.sessoes_pep = parse_json_field(data['sessoes_pep'], relatorio.sessoes_pep)
            if 'modulos_dificuldade' in data:
                relatorio.modulos_dificuldade = parse_json_field(data['modulos_dificuldade'], relatorio.modulos_dificuldade)
            if 'observacoes' in data:
                relatorio.observacoes = data['observacoes']

            relatorio.audit_user_id = user.id_for_audit
            relatorio.save()
            return relatorio

    @classmethod
    def delete(cls, relatorio_id, user):
        """Soft delete a bimonthly supervision report"""
        from .models import RelatorioSupervisaoBimestral

        try:
            relatorio = RelatorioSupervisaoBimestral.objects.get(id=relatorio_id, validity_to__isnull=True)
        except RelatorioSupervisaoBimestral.DoesNotExist:
            raise ValidationError([{'message': 'Bimonthly supervision report not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.delete_relatoriosupervisaobimestral']):
            raise PermissionDenied("User does not have permission to delete bimonthly supervision reports")

        with transaction.atomic():
            from django.utils import timezone
            relatorio.validity_to = timezone.now()
            relatorio.audit_user_id = user.id_for_audit
            relatorio.save()
            return relatorio
