"""
PEP+ Services
Business logic for CRUD operations
"""
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from core.services import BaseService
from .models import (
    ModuloEducacional, GrupoFamiliar, SessaoPEP, PresencaSessao,
    ExecucaoSessao, SupervisaoSessao, RelatorioDistritalBimestral,
    EncaminhamentoSessao
)
from .validations import (
    validate_sessao_planeamento, validate_presenca_sessao,
    validate_execucao_sessao, validate_supervisao_sessao,
    validate_relatorio_distrital, validate_encaminhamento,
    validate_modulo_educacional, validate_grupo_familiar
)


class ModuloEducacionalService(BaseService):
    """Service for Educational Module operations"""

    OBJECT_TYPE = ModuloEducacional

    @classmethod
    def create(cls, data, user):
        """Create a new educational module"""
        # Validate
        errors = validate_modulo_educacional(data)
        if errors:
            raise ValidationError(errors)

        # Check permissions
        if not user.has_perms(['pep_plus.add_moduloeducacional']):
            raise PermissionDenied("User does not have permission to create educational modules")

        with transaction.atomic():
            modulo = ModuloEducacional.objects.create(
                codigo=data['codigo'],
                nome=data['nome'],
                descricao=data.get('descricao'),
                ordem=data.get('ordem', 0),
                duracao_semanas=data.get('duracao_semanas', 1),
                ativo=data.get('ativo', True),
                audit_user_id=user.id_for_audit
            )
            return modulo

    @classmethod
    def update(cls, modulo_id, data, user):
        """Update an educational module"""
        try:
            modulo = ModuloEducacional.objects.get(id=modulo_id, validity_to__isnull=True)
        except ModuloEducacional.DoesNotExist:
            raise ValidationError([{'message': 'Educational module not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.change_moduloeducacional']):
            raise PermissionDenied("User does not have permission to update educational modules")

        # Validate
        errors = validate_modulo_educacional(data)
        if errors:
            raise ValidationError(errors)

        with transaction.atomic():
            modulo.nome = data.get('nome', modulo.nome)
            modulo.descricao = data.get('descricao', modulo.descricao)
            modulo.ordem = data.get('ordem', modulo.ordem)
            modulo.duracao_semanas = data.get('duracao_semanas', modulo.duracao_semanas)
            modulo.ativo = data.get('ativo', modulo.ativo)
            modulo.audit_user_id = user.id_for_audit
            modulo.save()
            return modulo

    @classmethod
    def delete(cls, modulo_id, user):
        """Soft delete an educational module"""
        try:
            modulo = ModuloEducacional.objects.get(id=modulo_id, validity_to__isnull=True)
        except ModuloEducacional.DoesNotExist:
            raise ValidationError([{'message': 'Educational module not found'}])

        # Check permissions
        if not user.has_perms(['pep_plus.delete_moduloeducacional']):
            raise PermissionDenied("User does not have permission to delete educational modules")

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
                ativo=data.get('ativo', True),
                audit_user_id=user.id_for_audit
            )
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
                coordenador_distrital_id=data['coordenador_distrital_id'],
                tecnico_social_id=data['tecnico_social_id'],
                distrito_id=data['distrito_id'],
                modulo_id=data['modulo_id'],
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
                status=data.get('status', 'PLAN'),
                audit_user_id=user.id_for_audit
            )
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
            sessao.coordenador_distrital_id = data.get('coordenador_distrital_id', sessao.coordenador_distrital_id)
            sessao.tecnico_social_id = data.get('tecnico_social_id', sessao.tecnico_social_id)
            sessao.distrito_id = data.get('distrito_id', sessao.distrito_id)
            sessao.modulo_id = data.get('modulo_id', sessao.modulo_id)
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
                nome_familia=data['nome_familia'],
                grupo_id=data.get('grupo_id'),
                estado=data.get('estado', 'PRES'),
                codigo_encaminhamento=data.get('codigo_encaminhamento'),
                observacoes=data.get('observacoes'),
                audit_user_id=user.id_for_audit
            )
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
                    nome_familia=familia_data['nome_familia'],
                    grupo_id=familia_data.get('grupo_id'),
                    estado=familia_data.get('estado', 'PRES'),
                    codigo_encaminhamento=familia_data.get('codigo_encaminhamento'),
                    observacoes=familia_data.get('observacoes'),
                    audit_user_id=user.id_for_audit
                )
                presencas.append(presenca)

            return presencas


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

        with transaction.atomic():
            execucao = ExecucaoSessao.objects.create(
                sessao_id=data['sessao_id'],
                formador_id=data['formador_id'],
                supervisor_id=data.get('supervisor_id'),
                localidade_id=data.get('localidade_id'),
                numero_participantes_compromissos=data.get('numero_participantes_compromissos', 0),
                praticas_positivas=data.get('praticas_positivas', []),
                desafios_transmissao=data.get('desafios_transmissao', []),
                necessita_encaminhamento=data.get('necessita_encaminhamento', False),
                auto_avaliacao_pontos_fortes=data.get('auto_avaliacao_pontos_fortes', []),
                auto_avaliacao_pontos_atencao=data.get('auto_avaliacao_pontos_atencao', []),
                avaliacao_metodologia=data.get('avaliacao_metodologia', {}),
                observacoes=data.get('observacoes'),
                audit_user_id=user.id_for_audit
            )

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
            execucao.numero_participantes_compromissos = data.get('numero_participantes_compromissos',
                                                                   execucao.numero_participantes_compromissos)
            execucao.praticas_positivas = data.get('praticas_positivas', execucao.praticas_positivas)
            execucao.desafios_transmissao = data.get('desafios_transmissao', execucao.desafios_transmissao)
            execucao.necessita_encaminhamento = data.get('necessita_encaminhamento',
                                                         execucao.necessita_encaminhamento)
            execucao.auto_avaliacao_pontos_fortes = data.get('auto_avaliacao_pontos_fortes',
                                                            execucao.auto_avaliacao_pontos_fortes)
            execucao.auto_avaliacao_pontos_atencao = data.get('auto_avaliacao_pontos_atencao',
                                                             execucao.auto_avaliacao_pontos_atencao)
            execucao.avaliacao_metodologia = data.get('avaliacao_metodologia', execucao.avaliacao_metodologia)
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
                data_supervisao=data['data_supervisao'],
                data_modulo_anterior=data.get('data_modulo_anterior'),
                identificador_grupo=data['identificador_grupo'],
                perguntas_avaliacao=data.get('perguntas_avaliacao', {}),
                pontos_positivos=data.get('pontos_positivos'),
                pontos_melhorar=data.get('pontos_melhorar'),
                observacoes=data.get('observacoes'),
                audit_user_id=user.id_for_audit
            )
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
            supervisao.perguntas_avaliacao = data.get('perguntas_avaliacao', supervisao.perguntas_avaliacao)
            supervisao.pontos_positivos = data.get('pontos_positivos', supervisao.pontos_positivos)
            supervisao.pontos_melhorar = data.get('pontos_melhorar', supervisao.pontos_melhorar)
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
                observacoes=data.get('observacoes'),
                audit_user_id=user.id_for_audit
            )
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
                observacoes=data.get('observacoes'),
                audit_user_id=user.id_for_audit
            )
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
