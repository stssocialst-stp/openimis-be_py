"""
PEP+ Services
Business logic for CRUD operations
"""
import json
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from core.services import BaseService
from .models import (
    ModuloPEP, Escola, Classe, ClasseDisciplina, Disciplina, TipoEncaminhamento,
    Aluno, ModuloEducacional, ModuloEducacionalDisciplina,
    GrupoFamiliar, SessaoPEP, PresencaSessao,
    ExecucaoSessao, SupervisaoSessao,
    RelatorioDistritalBimestral, RelatorioDistEncaminhamento,
    EncaminhamentoSessao, RoteiroReuniaoBimestral,
    CoordenacaoDistrital, CoordenacaoDistritalTecnico
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
    """
    if value is None:
        return default if default is not None else []
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return default if default is not None else []
    return default if default is not None else []


# =============================================================================
# SERVIÇOS DE PARAMETRIZAÇÃO
# =============================================================================

class ModuloPEPService(BaseService):
    """Service for ModuloPEP lookup table operations"""

    OBJECT_TYPE = ModuloPEP

    @classmethod
    def create(cls, data, user):
        if not user.has_perms(['pep_plus.add_modulopep']):
            raise PermissionDenied("User does not have permission to create ModuloPEP records")

        with transaction.atomic():
            modulo = ModuloPEP.objects.create(
                codigo=data['codigo'],
                nome=data['nome'],
                descricao=data.get('descricao'),
                ordem=data.get('ordem'),
                duracao_semanas=data.get('duracao_semanas'),
                ativo=data.get('ativo', True),
            )
            modulo.audit_user_id = user.id_for_audit
            modulo.save()
            return modulo

    @classmethod
    def update(cls, modulo_id, data, user):
        try:
            modulo = ModuloPEP.objects.get(id=modulo_id, validity_to__isnull=True)
        except ModuloPEP.DoesNotExist:
            raise ValidationError([{'message': 'ModuloPEP not found'}])

        if not user.has_perms(['pep_plus.change_modulopep']):
            raise PermissionDenied("User does not have permission to update ModuloPEP records")

        with transaction.atomic():
            if 'codigo' in data:
                modulo.codigo = data['codigo']
            if 'nome' in data:
                modulo.nome = data['nome']
            if 'descricao' in data:
                modulo.descricao = data['descricao']
            if 'ordem' in data:
                modulo.ordem = data['ordem']
            if 'duracao_semanas' in data:
                modulo.duracao_semanas = data['duracao_semanas']
            if 'ativo' in data:
                modulo.ativo = data['ativo']
            modulo.audit_user_id = user.id_for_audit
            modulo.save()
            return modulo

    @classmethod
    def delete(cls, modulo_id, user):
        try:
            modulo = ModuloPEP.objects.get(id=modulo_id, validity_to__isnull=True)
        except ModuloPEP.DoesNotExist:
            raise ValidationError([{'message': 'ModuloPEP not found'}])

        if not user.has_perms(['pep_plus.delete_modulopep']):
            raise PermissionDenied("User does not have permission to delete ModuloPEP records")

        with transaction.atomic():
            modulo.delete_history(user=user)
            return modulo


class EscolaService(BaseService):
    """Service for Escola lookup table operations"""

    OBJECT_TYPE = Escola

    @classmethod
    def create(cls, data, user):
        if not user.has_perms(['pep_plus.add_escola']):
            raise PermissionDenied("User does not have permission to create Escola records")

        with transaction.atomic():
            escola = Escola.objects.create(
                nome=data['nome'],
                codigo=data.get('codigo'),
                nivel=data.get('nivel'),
                distrito_id=data.get('distrito_id'),
                localidade_id=data.get('localidade_id'),
                ativo=data.get('ativo', True),
            )
            escola.audit_user_id = user.id_for_audit
            escola.save()
            return escola

    @classmethod
    def update(cls, escola_id, data, user):
        try:
            escola = Escola.objects.get(id=escola_id, validity_to__isnull=True)
        except Escola.DoesNotExist:
            raise ValidationError([{'message': 'Escola not found'}])

        if not user.has_perms(['pep_plus.change_escola']):
            raise PermissionDenied("User does not have permission to update Escola records")

        with transaction.atomic():
            if 'nome' in data:
                escola.nome = data['nome']
            if 'codigo' in data:
                escola.codigo = data['codigo']
            if 'nivel' in data:
                escola.nivel = data['nivel']
            if 'distrito_id' in data:
                escola.distrito_id = data['distrito_id']
            if 'localidade_id' in data:
                escola.localidade_id = data['localidade_id']
            if 'ativo' in data:
                escola.ativo = data['ativo']
            escola.audit_user_id = user.id_for_audit
            escola.save()
            return escola

    @classmethod
    def delete(cls, escola_id, user):
        try:
            escola = Escola.objects.get(id=escola_id, validity_to__isnull=True)
        except Escola.DoesNotExist:
            raise ValidationError([{'message': 'Escola not found'}])

        if not user.has_perms(['pep_plus.delete_escola']):
            raise PermissionDenied("User does not have permission to delete Escola records")

        with transaction.atomic():
            escola.delete_history(user=user)
            return escola


class ClasseService(BaseService):
    """Service for Classe lookup table operations"""

    OBJECT_TYPE = Classe

    @classmethod
    def _sync_disciplinas(cls, classe, disciplinas_ids):
        """Sync M2M disciplinas for a Classe record."""
        if disciplinas_ids is None:
            return
        ClasseDisciplina.objects.filter(classe=classe).delete()
        for raw_id in disciplinas_ids:
            try:
                from .utils import decode_id
                disc_id = decode_id(raw_id)
            except Exception:
                disc_id = raw_id
            try:
                disciplina = Disciplina.objects.get(id=disc_id, validity_to__isnull=True)
                ClasseDisciplina.objects.create(classe=classe, disciplina=disciplina)
            except Disciplina.DoesNotExist:
                raise ValidationError([{'message': f'Disciplina with id {disc_id} not found'}])

    @classmethod
    def create(cls, data, user):
        if not user.has_perms(['pep_plus.add_classe']):
            raise PermissionDenied("User does not have permission to create Classe records")

        disciplinas_ids = data.pop('disciplinas_ids', None)

        with transaction.atomic():
            classe = Classe.objects.create(
                nome=data['nome'],
                codigo=data['codigo'],
                nivel=data.get('nivel'),
                ordem=data.get('ordem'),
                ativo=data.get('ativo', True),
            )
            classe.audit_user_id = user.id_for_audit
            classe.save()
            cls._sync_disciplinas(classe, disciplinas_ids)
            return classe

    @classmethod
    def update(cls, classe_id, data, user):
        try:
            classe = Classe.objects.get(id=classe_id, validity_to__isnull=True)
        except Classe.DoesNotExist:
            raise ValidationError([{'message': 'Classe not found'}])

        if not user.has_perms(['pep_plus.change_classe']):
            raise PermissionDenied("User does not have permission to update Classe records")

        disciplinas_ids = data.pop('disciplinas_ids', None)

        with transaction.atomic():
            if 'nome' in data:
                classe.nome = data['nome']
            if 'codigo' in data:
                classe.codigo = data['codigo']
            if 'nivel' in data:
                classe.nivel = data['nivel']
            if 'ordem' in data:
                classe.ordem = data['ordem']
            if 'ativo' in data:
                classe.ativo = data['ativo']
            classe.audit_user_id = user.id_for_audit
            classe.save()
            cls._sync_disciplinas(classe, disciplinas_ids)
            return classe

    @classmethod
    def delete(cls, classe_id, user):
        try:
            classe = Classe.objects.get(id=classe_id, validity_to__isnull=True)
        except Classe.DoesNotExist:
            raise ValidationError([{'message': 'Classe not found'}])

        if not user.has_perms(['pep_plus.delete_classe']):
            raise PermissionDenied("User does not have permission to delete Classe records")

        with transaction.atomic():
            classe.delete_history(user=user)
            return classe


class DisciplinaService(BaseService):
    """Service for Disciplina lookup table operations"""

    OBJECT_TYPE = Disciplina

    @classmethod
    def create(cls, data, user):
        if not user.has_perms(['pep_plus.add_disciplina']):
            raise PermissionDenied("User does not have permission to create Disciplina records")

        with transaction.atomic():
            disciplina = Disciplina.objects.create(
                nome=data['nome'],
                nivel=data['nivel'],
                ativo=data.get('ativo', True),
                faixa_faltas_aceitaveis=data.get('faixa_faltas_aceitaveis'),
                quantidade_faltas_aceitaveis=data.get('quantidade_faltas_aceitaveis'),
            )
            disciplina.audit_user_id = user.id_for_audit
            disciplina.save()
            return disciplina

    @classmethod
    def update(cls, disciplina_id, data, user):
        try:
            disciplina = Disciplina.objects.get(id=disciplina_id, validity_to__isnull=True)
        except Disciplina.DoesNotExist:
            raise ValidationError([{'message': 'Disciplina not found'}])

        if not user.has_perms(['pep_plus.change_disciplina']):
            raise PermissionDenied("User does not have permission to update Disciplina records")

        with transaction.atomic():
            if 'nome' in data:
                disciplina.nome = data['nome']
            if 'nivel' in data:
                disciplina.nivel = data['nivel']
            if 'ativo' in data:
                disciplina.ativo = data['ativo']
            if 'faixa_faltas_aceitaveis' in data:
                disciplina.faixa_faltas_aceitaveis = data['faixa_faltas_aceitaveis']
            if 'quantidade_faltas_aceitaveis' in data:
                disciplina.quantidade_faltas_aceitaveis = data['quantidade_faltas_aceitaveis']
            disciplina.audit_user_id = user.id_for_audit
            disciplina.save()
            return disciplina

    @classmethod
    def delete(cls, disciplina_id, user):
        try:
            disciplina = Disciplina.objects.get(id=disciplina_id, validity_to__isnull=True)
        except Disciplina.DoesNotExist:
            raise ValidationError([{'message': 'Disciplina not found'}])

        if not user.has_perms(['pep_plus.delete_disciplina']):
            raise PermissionDenied("User does not have permission to delete Disciplina records")

        with transaction.atomic():
            disciplina.delete_history(user=user)
            return disciplina


class TipoEncaminhamentoService(BaseService):
    """Service for TipoEncaminhamento lookup table operations"""

    OBJECT_TYPE = TipoEncaminhamento

    @classmethod
    def create(cls, data, user):
        if not user.has_perms(['pep_plus.add_tipoencaminhamento']):
            raise PermissionDenied("User does not have permission to create TipoEncaminhamento records")

        with transaction.atomic():
            tipo = TipoEncaminhamento.objects.create(
                codigo=data['codigo'],
                nome=data['nome'],
                descricao=data.get('descricao'),
                ativo=data.get('ativo', True),
            )
            tipo.audit_user_id = user.id_for_audit
            tipo.save()
            return tipo

    @classmethod
    def update(cls, tipo_id, data, user):
        try:
            tipo = TipoEncaminhamento.objects.get(id=tipo_id, validity_to__isnull=True)
        except TipoEncaminhamento.DoesNotExist:
            raise ValidationError([{'message': 'TipoEncaminhamento not found'}])

        if not user.has_perms(['pep_plus.change_tipoencaminhamento']):
            raise PermissionDenied("User does not have permission to update TipoEncaminhamento records")

        with transaction.atomic():
            if 'codigo' in data:
                tipo.codigo = data['codigo']
            if 'nome' in data:
                tipo.nome = data['nome']
            if 'descricao' in data:
                tipo.descricao = data['descricao']
            if 'ativo' in data:
                tipo.ativo = data['ativo']
            tipo.audit_user_id = user.id_for_audit
            tipo.save()
            return tipo

    @classmethod
    def delete(cls, tipo_id, user):
        try:
            tipo = TipoEncaminhamento.objects.get(id=tipo_id, validity_to__isnull=True)
        except TipoEncaminhamento.DoesNotExist:
            raise ValidationError([{'message': 'TipoEncaminhamento not found'}])

        if not user.has_perms(['pep_plus.delete_tipoencaminhamento']):
            raise PermissionDenied("User does not have permission to delete TipoEncaminhamento records")

        with transaction.atomic():
            tipo.delete_history(user=user)
            return tipo


# =============================================================================
# SERVIÇOS PRINCIPAIS
# =============================================================================

class ModuloEducacionalService(BaseService):
    """Service for School Attendance (Assiduidade Escolar) operations"""

    OBJECT_TYPE = ModuloEducacional

    @classmethod
    def _sync_disciplinas(cls, modulo, disciplinas_ids):
        """Sync the M2M disciplinas for a ModuloEducacional record."""
        if disciplinas_ids is None:
            return
        # Remove existing associations
        ModuloEducacionalDisciplina.objects.filter(modulo=modulo).delete()
        # Create new ones
        for raw_id in disciplinas_ids:
            # IDs can come as Relay global IDs or plain integers
            try:
                from .utils import decode_id
                disc_id = decode_id(raw_id)
            except Exception:
                disc_id = raw_id
            try:
                disciplina = Disciplina.objects.get(id=disc_id, validity_to__isnull=True)
                ModuloEducacionalDisciplina.objects.create(
                    modulo=modulo,
                    disciplina=disciplina,
                    tipo=disciplina.nivel,
                )
            except Disciplina.DoesNotExist:
                raise ValidationError([{'message': f'Disciplina with id {disc_id} not found'}])

    @classmethod
    def create(cls, data, user):
        """Create a new school attendance record"""
        errors = validate_modulo_educacional(data)
        if errors:
            raise ValidationError(errors)

        if not user.has_perms(['pep_plus.add_moduloeducacional']):
            raise PermissionDenied("User does not have permission to create school attendance records")

        disciplinas_ids = data.pop('disciplinas_ids', None)

        with transaction.atomic():
            modulo = ModuloEducacional.objects.create(
                id_membro_crianca=data.get('id_membro_crianca'),
                nome=data['nome'],
                nome_encarregado=data.get('nome_encarregado'),
                escola_id=data.get('escola_id'),
                escolaridade_actual=data.get('escolaridade_actual'),
                data_nascimento=data.get('data_nascimento'),
                id_da_crianca=data.get('id_da_crianca'),
                sexo=data.get('sexo'),
                dados_escolar_correctos=data.get('dados_escolar_correctos'),
                escola_actual_id=data.get('escola_actual_id'),
                classe_id=data.get('classe_id'),
                idade=data.get('idade'),
                dados_escolares_correctos=data.get('dados_escolares_correctos'),
                informacoes_localizacao=parse_json_field(data.get('informacoes_localizacao'), {}),
                classe_que_frequenta_id=data.get('classe_que_frequenta_id'),
                aproveitamento_primeiro_trimestre=data.get('aproveitamento_primeiro_trimestre'),
                faixa_de_faltas=data.get('faixa_de_faltas'),
                observacoes=data.get('observacoes')
            )
            modulo.audit_user_id = user.id_for_audit
            modulo.save()
            cls._sync_disciplinas(modulo, disciplinas_ids)
            return modulo

    @classmethod
    def update(cls, modulo_id, data, user):
        """Update a school attendance record"""
        try:
            modulo = ModuloEducacional.objects.get(id=modulo_id, validity_to__isnull=True)
        except ModuloEducacional.DoesNotExist:
            raise ValidationError([{'message': 'School attendance record not found'}])

        if not user.has_perms(['pep_plus.change_moduloeducacional']):
            raise PermissionDenied("User does not have permission to update school attendance records")

        errors = validate_modulo_educacional(data)
        if errors:
            raise ValidationError(errors)

        disciplinas_ids = data.pop('disciplinas_ids', None)

        with transaction.atomic():
            if 'id_membro_crianca' in data:
                modulo.id_membro_crianca = data['id_membro_crianca']
            if 'nome' in data:
                modulo.nome = data['nome']
            if 'nome_encarregado' in data:
                modulo.nome_encarregado = data['nome_encarregado']
            if 'escola_id' in data:
                modulo.escola_id = data['escola_id']
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
            if 'escola_actual_id' in data:
                modulo.escola_actual_id = data['escola_actual_id']
            if 'classe_id' in data:
                modulo.classe_id = data['classe_id']
            if 'idade' in data:
                modulo.idade = data['idade']
            if 'dados_escolares_correctos' in data:
                modulo.dados_escolares_correctos = data['dados_escolares_correctos']
            if 'informacoes_localizacao' in data:
                modulo.informacoes_localizacao = parse_json_field(data['informacoes_localizacao'], modulo.informacoes_localizacao)
            if 'classe_que_frequenta_id' in data:
                modulo.classe_que_frequenta_id = data['classe_que_frequenta_id']
            if 'aproveitamento_primeiro_trimestre' in data:
                modulo.aproveitamento_primeiro_trimestre = data['aproveitamento_primeiro_trimestre']
            if 'faixa_de_faltas' in data:
                modulo.faixa_de_faltas = data['faixa_de_faltas']
            if 'observacoes' in data:
                modulo.observacoes = data['observacoes']

            modulo.audit_user_id = user.id_for_audit
            modulo.save()
            cls._sync_disciplinas(modulo, disciplinas_ids)
            return modulo

    @classmethod
    def delete(cls, modulo_id, user):
        """Soft delete a school attendance record"""
        try:
            modulo = ModuloEducacional.objects.get(id=modulo_id, validity_to__isnull=True)
        except ModuloEducacional.DoesNotExist:
            raise ValidationError([{'message': 'School attendance record not found'}])

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
        errors = validate_grupo_familiar(data)
        if errors:
            raise ValidationError(errors)

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
        try:
            grupo = GrupoFamiliar.objects.get(id=grupo_id, validity_to__isnull=True)
        except GrupoFamiliar.DoesNotExist:
            raise ValidationError([{'message': 'Family group not found'}])

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
        try:
            grupo = GrupoFamiliar.objects.get(id=grupo_id, validity_to__isnull=True)
        except GrupoFamiliar.DoesNotExist:
            raise ValidationError([{'message': 'Family group not found'}])

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
        errors = validate_sessao_planeamento(data)
        if errors:
            raise ValidationError(errors)

        if not user.has_perms(['pep_plus.add_sessaopep']):
            raise PermissionDenied("User does not have permission to create PEP sessions")

        with transaction.atomic():
            sessao = SessaoPEP.objects.create(
                codigo_sessao=data['codigo_sessao'],
                data_planejamento=data['data_planejamento'],
                coordenador_distrital_id=data['coordenador_distrital_id'],
                tecnico_social_id=data['tecnico_social_id'],
                distrito_id=data['distrito_id'],
                modulo_id=data.get('modulo_id'),
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
        try:
            sessao = SessaoPEP.objects.get(id=sessao_id, validity_to__isnull=True)
        except SessaoPEP.DoesNotExist:
            raise ValidationError([{'message': 'PEP session not found'}])

        if not user.has_perms(['pep_plus.change_sessaopep']):
            raise PermissionDenied("User does not have permission to update PEP sessions")

        errors = validate_sessao_planeamento(data)
        if errors:
            raise ValidationError(errors)

        with transaction.atomic():
            sessao.data_planejamento = data.get('data_planejamento', sessao.data_planejamento)
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
        try:
            sessao = SessaoPEP.objects.get(id=sessao_id, validity_to__isnull=True)
        except SessaoPEP.DoesNotExist:
            raise ValidationError([{'message': 'PEP session not found'}])

        if not user.has_perms(['pep_plus.delete_sessaopep']):
            raise PermissionDenied("User does not have permission to delete PEP sessions")

        with transaction.atomic():
            sessao.delete_history(user=user)
            return sessao

    @classmethod
    def create_multiple(cls, sessions_list, user):
        if not user.has_perms(['pep_plus.add_sessaopep']):
            raise PermissionDenied("User does not have permission to create PEP sessions")

        with transaction.atomic():
            sessoes = []
            for session_data in sessions_list:
                errors = validate_sessao_planeamento(session_data)
                if errors:
                    raise ValidationError(errors)

                sessao = SessaoPEP.objects.create(
                    codigo_sessao=session_data['codigo_sessao'],
                    data_planejamento=session_data['data_planejamento'],
                    coordenador_distrital_id=session_data['coordenador_distrital_id'],
                    tecnico_social_id=session_data['tecnico_social_id'],
                    distrito_id=session_data['distrito_id'],
                    modulo_id=session_data.get('modulo_id'),
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
                if 'modulo_id' in session_data:
                    sessao.modulo_id = session_data['modulo_id']
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
        errors = validate_presenca_sessao(data)
        if errors:
            raise ValidationError(errors)

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
                tipo_encaminhamento_id=data.get('tipo_encaminhamento_id'),
                observacoes=data.get('observacoes')
            )
            presenca.audit_user_id = user.id_for_audit
            presenca.save()
            return presenca

    @classmethod
    def update(cls, presenca_id, data, user):
        try:
            presenca = PresencaSessao.objects.get(id=presenca_id, validity_to__isnull=True)
        except PresencaSessao.DoesNotExist:
            raise ValidationError([{'message': 'Attendance record not found'}])

        if not user.has_perms(['pep_plus.change_presencasessao']):
            raise PermissionDenied("User does not have permission to update attendance records")

        with transaction.atomic():
            presenca.estado = data.get('estado', presenca.estado)
            presenca.codigo_encaminhamento = data.get('codigo_encaminhamento', presenca.codigo_encaminhamento)
            presenca.tipo_encaminhamento_id = data.get('tipo_encaminhamento_id', presenca.tipo_encaminhamento_id)
            presenca.observacoes = data.get('observacoes', presenca.observacoes)
            presenca.audit_user_id = user.id_for_audit
            presenca.save()
            return presenca

    @classmethod
    def delete(cls, presenca_id, user):
        try:
            presenca = PresencaSessao.objects.get(id=presenca_id, validity_to__isnull=True)
        except PresencaSessao.DoesNotExist:
            raise ValidationError([{'message': 'Attendance record not found'}])

        if not user.has_perms(['pep_plus.delete_presencasessao']):
            raise PermissionDenied("User does not have permission to delete attendance records")

        with transaction.atomic():
            presenca.delete_history(user=user)
            return presenca

    @classmethod
    def register_multiple_attendances(cls, sessao_id, familias_list, user):
        if not user.has_perms(['pep_plus.add_presencasessao']):
            raise PermissionDenied("User does not have permission to create attendance records")

        with transaction.atomic():
            presencas = []
            for familia_data in familias_list:
                data = {'sessao_id': sessao_id, **familia_data}
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
                    tipo_encaminhamento_id=familia_data.get('tipo_encaminhamento_id'),
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

        if not user.has_perms(['pep_plus.add_presencasessao']):
            raise PermissionDenied("User does not have permission to create attendance records")

        try:
            sessao = SessaoPEP.objects.get(id=data['sessao_id'], validity_to__isnull=True)
        except SessaoPEP.DoesNotExist:
            raise ValidationError([{'message': 'Session not found'}])

        if sessao.distrito_id != data['distrito_id']:
            raise ValidationError([{'message': 'District ID does not match session district'}])
        if sessao.grupo_familia_id != data['grupo_familia_id']:
            raise ValidationError([{'message': 'Family group ID does not match session family group'}])

        with transaction.atomic():
            # Update SessaoPEP with actual execution data
            sessao.data_sessao = data['data_sessao']
            if 'modulo_id' in data and data['modulo_id']:
                sessao.modulo_id = data['modulo_id']
            if 'mes_modulo_anterior' in data:
                sessao.mes_modulo_anterior = data['mes_modulo_anterior']
            sessao.audit_user_id = user.id_for_audit
            sessao.save()

            # Create or update ExecucaoSessao
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
                PresencaSessao.objects.filter(
                    sessao=sessao,
                    familia_id=presenca_item['familia_id'],
                    validity_to__isnull=True
                ).delete()

                presenca = PresencaSessao.objects.create(
                    sessao=sessao,
                    familia_id=presenca_item['familia_id'],
                    nome_familia=presenca_item.get('nome_familia'),
                    grupo_id=sessao.grupo_familia_id,
                    estado=presenca_item['estado'],
                    codigo_encaminhamento=presenca_item.get('codigo_encaminhamento'),
                    tipo_encaminhamento_id=presenca_item.get('tipo_encaminhamento_id'),
                    observacoes=presenca_item.get('observacoes')
                )
                presenca.audit_user_id = user.id_for_audit
                presenca.save()
                presencas.append(presenca)

            return {'execucao': execucao, 'presencas': presencas}


class ExecucaoSessaoService(BaseService):
    """Service for Session Execution operations (Ferramenta 3)"""

    OBJECT_TYPE = ExecucaoSessao

    @classmethod
    def create(cls, data, user):
        errors = validate_execucao_sessao(data)
        if errors:
            raise ValidationError(errors)

        if not user.has_perms(['pep_plus.add_execucaosessao']):
            raise PermissionDenied("User does not have permission to create execution records")

        sessao_id = data['sessao_id']
        existing_execucao = ExecucaoSessao.objects.filter(
            sessao_id=sessao_id,
            validity_to__isnull=True
        ).first()

        if existing_execucao:
            raise ValidationError(
                f'Esta sessão já possui uma execução registrada (ID: {existing_execucao.id}). '
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

            sessao = execucao.sessao
            sessao.status = 'EXEC'
            sessao.save()

            return execucao

    @classmethod
    def update(cls, execucao_id, data, user):
        try:
            execucao = ExecucaoSessao.objects.get(id=execucao_id, validity_to__isnull=True)
        except ExecucaoSessao.DoesNotExist:
            raise ValidationError([{'message': 'Execution record not found'}])

        if not user.has_perms(['pep_plus.change_execucaosessao']):
            raise PermissionDenied("User does not have permission to update execution records")

        with transaction.atomic():
            execucao.numero_cuidadores = data.get('numero_cuidadores', execucao.numero_cuidadores)
            if 'praticas_positivas' in data:
                execucao.praticas_positivas = parse_json_field(data['praticas_positivas'], execucao.praticas_positivas)
            execucao.outras_praticas_positivas = data.get('outras_praticas_positivas', execucao.outras_praticas_positivas)
            if 'desafios_transmissao' in data:
                execucao.desafios_transmissao = parse_json_field(data['desafios_transmissao'], execucao.desafios_transmissao)
            execucao.outros_desafios = data.get('outros_desafios', execucao.outros_desafios)
            execucao.necessita_encaminhamento = data.get('necessita_encaminhamento', execucao.necessita_encaminhamento)
            if 'auto_avaliacao_pontos_fortes' in data:
                execucao.auto_avaliacao_pontos_fortes = parse_json_field(data['auto_avaliacao_pontos_fortes'], execucao.auto_avaliacao_pontos_fortes)
            if 'auto_avaliacao_pontos_atencao' in data:
                execucao.auto_avaliacao_pontos_atencao = parse_json_field(data['auto_avaliacao_pontos_atencao'], execucao.auto_avaliacao_pontos_atencao)
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
        errors = validate_supervisao_sessao(data)
        if errors:
            raise ValidationError(errors)

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
        try:
            supervisao = SupervisaoSessao.objects.get(id=supervisao_id, validity_to__isnull=True)
        except SupervisaoSessao.DoesNotExist:
            raise ValidationError([{'message': 'Supervision record not found'}])

        if not user.has_perms(['pep_plus.change_supervisaosessao']):
            raise PermissionDenied("User does not have permission to update supervision records")

        with transaction.atomic():
            supervisao.numero_participantes = data.get('numero_participantes', supervisao.numero_participantes)
            if 'praticas_positivas_estrategias' in data:
                supervisao.praticas_positivas_estrategias = parse_json_field(data['praticas_positivas_estrategias'], supervisao.praticas_positivas_estrategias)
            if 'desafios_transmissao' in data:
                supervisao.desafios_transmissao = parse_json_field(data['desafios_transmissao'], supervisao.desafios_transmissao)
            supervisao.necessita_encaminhamento = data.get('necessita_encaminhamento', supervisao.necessita_encaminhamento)
            if 'auto_avaliacao_pontos_fortes' in data:
                supervisao.auto_avaliacao_pontos_fortes = parse_json_field(data['auto_avaliacao_pontos_fortes'], supervisao.auto_avaliacao_pontos_fortes)
            if 'auto_avaliacao_pontos_atencao' in data:
                supervisao.auto_avaliacao_pontos_atencao = parse_json_field(data['auto_avaliacao_pontos_atencao'], supervisao.auto_avaliacao_pontos_atencao)
            if 'avaliacao_execucao_metodologia' in data:
                supervisao.avaliacao_execucao_metodologia = parse_json_field(data['avaliacao_execucao_metodologia'], supervisao.avaliacao_execucao_metodologia)
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

    # Mapeamento de período → meses do ano
    PERIODO_MESES = {
        'BIM1': (1, 2),    # Jan-Fev
        'BIM2': (3, 4),    # Mar-Abr
        'BIM3': (5, 6),    # Mai-Jun
        'BIM4': (7, 8),    # Jul-Ago
        'BIM5': (9, 10),   # Set-Out
        'BIM6': (11, 12),  # Nov-Dez
    }

    @staticmethod
    def _get_periodo_datas(periodo, ano):
        """Devolve (periodo_inicio, periodo_fim) como date a partir de periodo (BIM1-6) e ano."""
        import calendar
        from datetime import date
        meses = RelatorioDistritalService.PERIODO_MESES.get(periodo)
        if not meses:
            raise ValidationError([{'message': f"Período '{periodo}' inválido. Use BIM1 a BIM6."}])
        mes_inicio, mes_fim = meses
        inicio = date(ano, mes_inicio, 1)
        fim = date(ano, mes_fim, calendar.monthrange(ano, mes_fim)[1])
        return inicio, fim

    @classmethod
    def _get_coordenacao_do_distrito(cls, distrito_id):
        """Devolve a CoordenacaoDistrital activa do distrito, ou None se não existir."""
        from .models import CoordenacaoDistrital
        return CoordenacaoDistrital.objects.filter(
            distrito_id=distrito_id,
            ativo=True,
            validity_to__isnull=True,
        ).select_related('coordenador', 'tecnico_administrativo').first()

    @classmethod
    def _calcular_estatisticas(cls, distrito_id, periodo_inicio, periodo_fim):
        """
        Calcula automaticamente todos os indicadores do relatório a partir dos
        registos de SessaoPEP, PresencaSessao e ExecucaoSessao existentes.
        """
        # Sessões do distrito no período
        sessoes_qs = SessaoPEP.objects.filter(
            validity_to__isnull=True,
            distrito_id=distrito_id,
            data_sessao__gte=periodo_inicio,
            data_sessao__lte=periodo_fim,
        )
        sessoes_executadas = sessoes_qs.filter(status='EXEC')

        numero_sessoes_conduzidas = sessoes_executadas.count()
        numero_sessoes_esperadas = sessoes_qs.filter(status__in=['PLAN', 'EXEC']).count()
        numero_sessoes_perdidas = sessoes_qs.filter(status='CANC').count()

        # Localidades distintas das sessões executadas (via ExecucaoSessao.localidade)
        numero_localidades_atendidas = ExecucaoSessao.objects.filter(
            validity_to__isnull=True,
            sessao__in=sessoes_executadas,
            localidade__isnull=False,
        ).values('localidade_id').distinct().count()

        # Técnicos formadores distintos nas sessões executadas
        numero_tecnicos_formadores = ExecucaoSessao.objects.filter(
            validity_to__isnull=True,
            sessao__in=sessoes_executadas,
        ).values('formador_id').distinct().count()

        # Presenças nas sessões do período
        presencas_qs = PresencaSessao.objects.filter(
            validity_to__isnull=True,
            sessao__in=sessoes_qs,
        )
        numero_familias_presentes = presencas_qs.filter(estado='PRES').count()
        numero_familias_esperadas = presencas_qs.count()
        numero_familias_migraram = presencas_qs.filter(estado='MIGR').count()
        numero_familias_atendidas = (
            presencas_qs.filter(estado='PRES').values('familia_id').distinct().count()
        )

        # Percentuais e médias
        percentual_sessoes = round(
            numero_sessoes_conduzidas / numero_sessoes_esperadas * 100, 2
        ) if numero_sessoes_esperadas > 0 else 0

        percentual_familias = round(
            numero_familias_presentes / numero_familias_esperadas * 100, 2
        ) if numero_familias_esperadas > 0 else 0

        media_familia_presente = round(
            numero_familias_presentes / numero_sessoes_conduzidas, 2
        ) if numero_sessoes_conduzidas > 0 else 0

        media_familia_esperada = round(
            numero_familias_esperadas / numero_sessoes_esperadas, 2
        ) if numero_sessoes_esperadas > 0 else 0

        return {
            'numero_sessoes_conduzidas': numero_sessoes_conduzidas,
            'numero_sessoes_esperadas': numero_sessoes_esperadas,
            'numero_sessoes_perdidas': numero_sessoes_perdidas,
            'numero_localidades_atendidas': numero_localidades_atendidas,
            'numero_tecnicos_formadores': numero_tecnicos_formadores,
            'numero_familias_presentes': numero_familias_presentes,
            'numero_familias_esperadas': numero_familias_esperadas,
            'numero_familias_migraram': numero_familias_migraram,
            'numero_familias_atendidas': numero_familias_atendidas,
            'percentual_sessoes': percentual_sessoes,
            'percentual_familias': percentual_familias,
            'media_familia_presente': media_familia_presente,
            'media_familia_esperada': media_familia_esperada,
        }

    @classmethod
    def generate(cls, distrito_id, periodo, ano, user):
        """
        Gera o preview do relatório calculando todos os dados automaticamente.
        Retorna um dict com todos os campos pré-preenchidos (sem guardar na BD).
        """
        periodo_inicio, periodo_fim = cls._get_periodo_datas(periodo, ano)
        coordenacao = cls._get_coordenacao_do_distrito(distrito_id)
        stats = cls._calcular_estatisticas(distrito_id, periodo_inicio, periodo_fim)

        return {
            'distrito_id': distrito_id,
            'periodo': periodo,
            'ano': ano,
            'periodo_inicio': periodo_inicio,
            'periodo_fim': periodo_fim,
            'coordenador_distrital_id': coordenacao.coordenador_id if coordenacao else None,
            'coordenador_distrital_nome': (
                f"{coordenacao.coordenador.first_name} {coordenacao.coordenador.last_name}".strip()
                if coordenacao else None
            ),
            'tecnico_administrativo_id': (
                coordenacao.tecnico_administrativo_id if coordenacao else None
            ),
            **stats,
        }

    @classmethod
    def create(cls, data, user):
        errors = validate_relatorio_distrital(data)
        if errors:
            raise ValidationError(errors)

        if not user.has_perms(['pep_plus.add_relatoriodistritalbimestral']):
            raise PermissionDenied("User does not have permission to create district reports")

        # Calcular tudo automaticamente; os valores passados explicitamente têm precedência
        generated = cls.generate(data['distrito_id'], data['periodo'], data['ano'], user)

        coordenador_id = data.get('coordenador_distrital_id') or generated.get('coordenador_distrital_id')
        if not coordenador_id:
            raise ValidationError([{
                'message': (
                    'Não foi encontrada uma Coordenação Distrital activa para este distrito. '
                    'Configure a Coordenação Distrital antes de criar o relatório.'
                )
            }])

        with transaction.atomic():
            relatorio = RelatorioDistritalBimestral.objects.create(
                distrito_id=data['distrito_id'],
                coordenador_distrital_id=coordenador_id,
                tecnico_administrativo_id=(
                    data.get('tecnico_administrativo_id') or generated.get('tecnico_administrativo_id')
                ),
                periodo=data['periodo'],
                ano=data['ano'],
                periodo_inicio=generated['periodo_inicio'],
                periodo_fim=generated['periodo_fim'],
                numero_localidades_atendidas=data.get(
                    'numero_localidades_atendidas', generated['numero_localidades_atendidas']),
                numero_familias_atendidas=data.get(
                    'numero_familias_atendidas', generated['numero_familias_atendidas']),
                numero_tecnicos_formadores=data.get(
                    'numero_tecnicos_formadores', generated['numero_tecnicos_formadores']),
                numero_sessoes_conduzidas=data.get(
                    'numero_sessoes_conduzidas', generated['numero_sessoes_conduzidas']),
                numero_sessoes_esperadas=data.get(
                    'numero_sessoes_esperadas', generated['numero_sessoes_esperadas']),
                numero_familias_presentes=data.get(
                    'numero_familias_presentes', generated['numero_familias_presentes']),
                numero_familias_esperadas=data.get(
                    'numero_familias_esperadas', generated['numero_familias_esperadas']),
                percentual_sessoes=data.get(
                    'percentual_sessoes', generated['percentual_sessoes']),
                percentual_familias=data.get(
                    'percentual_familias', generated['percentual_familias']),
                numero_familias_migraram=data.get(
                    'numero_familias_migraram', generated['numero_familias_migraram']),
                numero_sessoes_perdidas=data.get(
                    'numero_sessoes_perdidas', generated['numero_sessoes_perdidas']),
                media_familia_presente=data.get(
                    'media_familia_presente', generated['media_familia_presente']),
                media_familia_esperada=data.get(
                    'media_familia_esperada', generated['media_familia_esperada']),
                dados_tecnicos=data.get('dados_tecnicos', []),
                dados_encaminhamentos=data.get('dados_encaminhamentos', []),
                observacoes=data.get('observacoes'),
            )
            relatorio.audit_user_id = user.id_for_audit
            relatorio.save()
            return relatorio

    @classmethod
    def update(cls, relatorio_id, data, user):
        try:
            relatorio = RelatorioDistritalBimestral.objects.get(id=relatorio_id, validity_to__isnull=True)
        except RelatorioDistritalBimestral.DoesNotExist:
            raise ValidationError([{'message': 'District report not found'}])

        if not user.has_perms(['pep_plus.change_relatoriodistritalbimestral']):
            raise PermissionDenied("User does not have permission to update district reports")

        with transaction.atomic():
            for field in [
                'numero_localidades_atendidas', 'numero_familias_atendidas',
                'numero_tecnicos_formadores', 'numero_sessoes_conduzidas',
                'numero_sessoes_esperadas', 'numero_familias_presentes',
                'numero_familias_esperadas', 'numero_familias_migraram',
                'numero_sessoes_perdidas', 'percentual_sessoes', 'percentual_familias',
                'media_familia_presente', 'media_familia_esperada',
                'dados_tecnicos', 'dados_encaminhamentos', 'observacoes',
            ]:
                if field in data:
                    setattr(relatorio, field, data[field])
            relatorio.audit_user_id = user.id_for_audit
            relatorio.save()
            return relatorio

    @classmethod
    def delete(cls, relatorio_id, user):
        try:
            relatorio = RelatorioDistritalBimestral.objects.get(id=relatorio_id, validity_to__isnull=True)
        except RelatorioDistritalBimestral.DoesNotExist:
            raise ValidationError([{'message': 'District report not found'}])

        if not user.has_perms(['pep_plus.delete_relatoriodistritalbimestral']):
            raise PermissionDenied("User does not have permission to delete district reports")

        with transaction.atomic():
            relatorio.delete_history()
            return relatorio


class RelatorioDistEncaminhamentoService:
    """
    Service para gestão dos encaminhamentos estruturados do RelatorioDistritalBimestral.

    Garante que apenas PresencaSessao com estado='ENCA' são associadas.
    Expõe add/remove individual e set_all (substituição em bloco).
    """

    @classmethod
    def _get_relatorio(cls, relatorio_id):
        try:
            return RelatorioDistritalBimestral.objects.get(
                id=relatorio_id, validity_to__isnull=True
            )
        except RelatorioDistritalBimestral.DoesNotExist:
            raise ValidationError([{'message': 'Relatório Distrital não encontrado'}])

    @classmethod
    def _get_presenca_enca(cls, presenca_id):
        try:
            presenca = PresencaSessao.objects.select_related('sessao').get(
                id=presenca_id, validity_to__isnull=True
            )
        except PresencaSessao.DoesNotExist:
            raise ValidationError([{'message': f'Registo de presença não encontrado (id={presenca_id})'}])

        if presenca.estado != 'ENCA':
            raise ValidationError([{
                'message': (
                    f"A presença da família '{presenca.nome_familia}' "
                    f"(código: {presenca.codigo_encaminhamento or '—'}) "
                    f"tem estado '{presenca.estado}', mas apenas presenças com "
                    f"estado 'ENCA' (encaminhadas) podem ser associadas ao relatório."
                )
            }])
        return presenca

    @classmethod
    def add(cls, relatorio_id, presenca_id, observacoes, user):
        """Adiciona uma PresencaSessao (ENCA) ao relatório."""
        relatorio = cls._get_relatorio(relatorio_id)
        presenca = cls._get_presenca_enca(presenca_id)

        if RelatorioDistEncaminhamento.objects.filter(
            relatorio=relatorio, presenca=presenca
        ).exists():
            raise ValidationError([{
                'message': f"A família '{presenca.nome_familia}' já está associada a este relatório."
            }])

        RelatorioDistEncaminhamento.objects.create(
            relatorio=relatorio,
            presenca=presenca,
            observacoes=observacoes,
        )

    @classmethod
    def remove(cls, relatorio_id, presenca_id, user):
        """Remove a ligação entre uma presença e o relatório."""
        deleted, _ = RelatorioDistEncaminhamento.objects.filter(
            relatorio_id=relatorio_id, presenca_id=presenca_id
        ).delete()
        if not deleted:
            raise ValidationError([{
                'message': 'Encaminhamento não encontrado neste relatório.'
            }])

    @classmethod
    def set_all(cls, relatorio_id, presenca_ids, user):
        """
        Substitui em bloco todos os encaminhamentos do relatório.
        Valida que cada presença tem estado=ENCA antes de guardar.
        """
        relatorio = cls._get_relatorio(relatorio_id)

        # Validar todas as presenças antes de qualquer escrita
        presencas = []
        for pid in presenca_ids:
            presencas.append(cls._get_presenca_enca(pid))

        with transaction.atomic():
            # Remove todos os actuais
            RelatorioDistEncaminhamento.objects.filter(relatorio=relatorio).delete()
            # Cria os novos
            RelatorioDistEncaminhamento.objects.bulk_create([
                RelatorioDistEncaminhamento(relatorio=relatorio, presenca=p)
                for p in presencas
            ])


class EncaminhamentoService(BaseService):
    """Service for Referral operations"""

    OBJECT_TYPE = EncaminhamentoSessao

    @classmethod
    def create(cls, data, user):
        errors = validate_encaminhamento(data)
        if errors:
            raise ValidationError(errors)

        if not user.has_perms(['pep_plus.add_encaminhamentosessao']):
            raise PermissionDenied("User does not have permission to create referrals")

        with transaction.atomic():
            encaminhamento = EncaminhamentoSessao.objects.create(
                sessao_id=data['sessao_id'],
                familia_id=data['familia_id'],
                nome_familia=data['nome_familia'],
                codigo_encaminhamento=data['codigo_encaminhamento'],
                descricao=data['descricao'],
                tipo_encaminhamento_id=data.get('tipo_encaminhamento_id'),
                status=data.get('status', 'PEND'),
                tecnico_responsavel_id=data.get('tecnico_responsavel_id'),
                observacoes=data.get('observacoes')
            )
            encaminhamento.audit_user_id = user.id_for_audit
            encaminhamento.save()
            return encaminhamento

    @classmethod
    def update(cls, encaminhamento_id, data, user):
        try:
            encaminhamento = EncaminhamentoSessao.objects.get(id=encaminhamento_id, validity_to__isnull=True)
        except EncaminhamentoSessao.DoesNotExist:
            raise ValidationError([{'message': 'Referral not found'}])

        if not user.has_perms(['pep_plus.change_encaminhamentosessao']):
            raise PermissionDenied("User does not have permission to update referrals")

        with transaction.atomic():
            encaminhamento.status = data.get('status', encaminhamento.status)
            encaminhamento.tipo_encaminhamento_id = data.get('tipo_encaminhamento_id', encaminhamento.tipo_encaminhamento_id)
            encaminhamento.tecnico_responsavel_id = data.get('tecnico_responsavel_id', encaminhamento.tecnico_responsavel_id)
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
        try:
            roteiro = RoteiroReuniaoBimestral.objects.get(id=roteiro_id, validity_to__isnull=True)
        except RoteiroReuniaoBimestral.DoesNotExist:
            raise ValidationError([{'message': 'Bimonthly meeting agenda not found'}])

        if not user.has_perms(['pep_plus.change_roteioreuniaobimestral']):
            raise PermissionDenied("User does not have permission to update bimonthly meeting agendas")

        with transaction.atomic():
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
        try:
            roteiro = RoteiroReuniaoBimestral.objects.get(id=roteiro_id, validity_to__isnull=True)
        except RoteiroReuniaoBimestral.DoesNotExist:
            raise ValidationError([{'message': 'Bimonthly meeting agenda not found'}])

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
        from .models import RelatorioSupervisaoBimestral

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
        from .models import RelatorioSupervisaoBimestral

        try:
            relatorio = RelatorioSupervisaoBimestral.objects.get(id=data['id'], validity_to__isnull=True)
        except RelatorioSupervisaoBimestral.DoesNotExist:
            raise ValidationError([{'message': 'Bimonthly supervision report not found'}])

        if not user.has_perms(['pep_plus.change_relatoriosupervisaobimestral']):
            raise PermissionDenied("User does not have permission to update bimonthly supervision reports")

        with transaction.atomic():
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
        from .models import RelatorioSupervisaoBimestral

        try:
            relatorio = RelatorioSupervisaoBimestral.objects.get(id=relatorio_id, validity_to__isnull=True)
        except RelatorioSupervisaoBimestral.DoesNotExist:
            raise ValidationError([{'message': 'Bimonthly supervision report not found'}])

        if not user.has_perms(['pep_plus.delete_relatoriosupervisaobimestral']):
            raise PermissionDenied("User does not have permission to delete bimonthly supervision reports")

        with transaction.atomic():
            from django.utils import timezone
            relatorio.validity_to = timezone.now()
            relatorio.audit_user_id = user.id_for_audit
            relatorio.save()
            return relatorio


# =============================================================================
# ALUNO SERVICE
# =============================================================================

class AlunoService:
    """
    Service para Aluno.

    Lógica de criação automática de Individual:
    - Se individual_id fornecido → usa o Individual existente
    - Se first_name + last_name + dob fornecidos → cria Individual primeiro,
      depois cria o Aluno com a referência associada
    - Apenas 1 Aluno activo por Individual (validity_to IS NULL)
    """

    @staticmethod
    def _decode_fk(relay_id):
        from .utils import decode_id
        return decode_id(relay_id) if relay_id else None

    @classmethod
    def _get_or_create_individual(cls, data, user):
        """
        Retorna um Individual existente (por individual_id) ou cria um novo.
        Lança ValidationError se não for possível identificar/criar o Individual.
        """
        from individual.models import Individual

        individual_id = data.pop('individual_id', None)

        if individual_id:
            # Relay ID → UUID (Individual usa UUID como PK)
            from .utils import decode_id
            individual_uuid = decode_id(individual_id)
            try:
                return Individual.objects.get(id=individual_uuid)
            except Individual.DoesNotExist:
                raise ValidationError([{'message': f'Individual não encontrado: {individual_uuid}'}])

        # Criar novo Individual com os dados pessoais fornecidos
        first_name = data.pop('first_name', '').strip()
        last_name = data.pop('last_name', '').strip()
        dob = data.pop('dob', None)

        if not first_name or not last_name or not dob:
            raise ValidationError([{
                'message': 'Para criar um novo Individual, são obrigatórios: '
                           'first_name, last_name e dob (ou individual_id para ligar a existente)'
            }])

        # Usar IndividualService do openIMIS para criar o Individual
        try:
            from individual.services import IndividualService as IndService
            ind_service = IndService(user)
            individual_data = {
                'first_name': first_name,
                'last_name': last_name,
                'dob': dob,
            }
            individual = ind_service.create(individual_data)
            # IndividualService.create retorna a instância do modelo
            if not isinstance(individual, Individual):
                # Algumas versões do BaseService retornam dict com chave 'data'
                if isinstance(individual, dict) and 'data' in individual:
                    individual = individual['data']
                else:
                    raise ValidationError([{'message': 'Falha ao criar Individual'}])
            return individual
        except (ImportError, Exception) as exc:
            # Fallback: criar directamente (para compatibilidade)
            if 'IndividualService' in str(exc) or 'import' in str(exc).lower():
                individual = Individual(
                    first_name=first_name,
                    last_name=last_name,
                    dob=dob,
                )
                individual.save(user=user)
                return individual
            raise

    @classmethod
    def create(cls, data, user):
        # Remover campos de dados pessoais antes de processar (vão para Individual)
        individual = cls._get_or_create_individual(data, user)

        # Verificar se já existe um Aluno activo para este Individual
        if Aluno.objects.filter(individual=individual, validity_to__isnull=True).exists():
            raise ValidationError([{
                'message': f'Já existe um Aluno activo para este indivíduo. '
                           f'Use updateAluno para actualizar.'
            }])

        with transaction.atomic():
            aluno = Aluno(
                individual=individual,
                id_membro_crianca=data.get('id_membro_crianca'),
                id_da_crianca=data.get('id_da_crianca'),
                nome_encarregado=data.get('nome_encarregado'),
                sexo=data.get('sexo'),
                distrito_id=cls._decode_fk(data.get('distrito_id')),
                localidade_id=cls._decode_fk(data.get('localidade_id')),
                ponto_referencia=data.get('ponto_referencia'),
                meio_residencia=data.get('meio_residencia'),
                escola_id=cls._decode_fk(data.get('escola_id')),
                escola_actual_id=cls._decode_fk(data.get('escola_actual_id')),
                escolaridade_actual=data.get('escolaridade_actual'),
                classe_id=cls._decode_fk(data.get('classe_id')),
                classe_que_frequenta_id=cls._decode_fk(data.get('classe_que_frequenta_id')),
                dados_escolares_correctos=data.get('dados_escolares_correctos'),
                ativo=data.get('ativo', True),
                audit_user_id=user.id_for_audit,
            )
            aluno.save()
            return aluno

    @classmethod
    def update(cls, aluno_id, data, user):
        try:
            aluno = Aluno.objects.get(id=aluno_id, validity_to__isnull=True)
        except Aluno.DoesNotExist:
            raise ValidationError([{'message': 'Aluno não encontrado'}])

        with transaction.atomic():
            simple_fields = [
                'id_membro_crianca', 'id_da_crianca', 'nome_encarregado',
                'sexo', 'ponto_referencia', 'meio_residencia',
                'escolaridade_actual', 'dados_escolares_correctos', 'ativo',
            ]
            for field in simple_fields:
                if field in data:
                    setattr(aluno, field, data[field])

            fk_fields = [
                ('distrito_id', 'distrito_id'),
                ('localidade_id', 'localidade_id'),
                ('escola_id', 'escola_id'),
                ('escola_actual_id', 'escola_actual_id'),
                ('classe_id', 'classe_id'),
                ('classe_que_frequenta_id', 'classe_que_frequenta_id'),
            ]
            for input_key, model_attr in fk_fields:
                if input_key in data:
                    setattr(aluno, model_attr, cls._decode_fk(data[input_key]))

            aluno.audit_user_id = user.id_for_audit
            aluno.save()
            return aluno

    @classmethod
    def delete(cls, aluno_id, user):
        try:
            aluno = Aluno.objects.get(id=aluno_id, validity_to__isnull=True)
        except Aluno.DoesNotExist:
            raise ValidationError([{'message': 'Aluno não encontrado'}])

        with transaction.atomic():
            from django.utils import timezone
            aluno.validity_to = timezone.now()
            aluno.ativo = False
            aluno.audit_user_id = user.id_for_audit
            aluno.save()
            return aluno


# =============================================================================
# COORDENAÇÃO DISTRITAL SERVICE
# =============================================================================

class CoordenacaoDistritalService:
    """
    Service para CoordenacaoDistrital.

    Regras de negócio:
    - Um distrito só pode ter 1 CoordenacaoDistrital activa (validity_to IS NULL + ativo=True)
    - 1 coordenador por distrito (FK)
    - 1 técnico administrativo por distrito (FK, opcional)
    - N técnicos operacionais (M2M via CoordenacaoDistritalTecnico)
    - tecnicos_operacionais_ids em create/update substitui a lista completa
    """

    @staticmethod
    def _decode_pk(relay_id):
        """Decode Relay global ID para PK inteiro."""
        from .utils import decode_id
        return decode_id(relay_id) if relay_id else None

    @classmethod
    def _resolve_tecnico_ids(cls, ids_list):
        """Converte lista de Relay IDs para PKs de utilizadores."""
        from django.conf import settings
        from django.apps import apps
        User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
        pks = [cls._decode_pk(rid) for rid in (ids_list or []) if rid]
        return list(User.objects.filter(pk__in=pks))

    @classmethod
    def create(cls, data, user):
        from django.utils import timezone
        from location.models import Location
        from django.conf import settings
        from django.apps import apps

        User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))

        distrito_id = cls._decode_pk(data.get('distrito_id'))
        coordenador_id = cls._decode_pk(data.get('coordenador_id'))
        tecnico_admin_id = cls._decode_pk(data.get('tecnico_administrativo_id'))
        tecnicos_ids = data.get('tecnicos_operacionais_ids', [])

        if not distrito_id:
            raise ValidationError([{'message': 'distrito_id é obrigatório'}])
        if not coordenador_id:
            raise ValidationError([{'message': 'coordenador_id é obrigatório'}])

        # Verificar que não existe já uma coordenação activa para este distrito
        if CoordenacaoDistrital.objects.filter(
            distrito_id=distrito_id, ativo=True, validity_to__isnull=True
        ).exists():
            raise ValidationError([{
                'message': 'Já existe uma Coordenação Distrital activa para este distrito. '
                           'Desactive a existente antes de criar uma nova.'
            }])

        with transaction.atomic():
            coord = CoordenacaoDistrital(
                distrito_id=distrito_id,
                coordenador_id=coordenador_id,
                tecnico_administrativo_id=tecnico_admin_id,
                ativo=data.get('ativo', True),
                observacoes=data.get('observacoes'),
                audit_user_id=user.id_for_audit,
            )
            coord.save()

            # Técnicos operacionais
            for tecnico in cls._resolve_tecnico_ids(tecnicos_ids):
                CoordenacaoDistritalTecnico.objects.create(
                    coordenacao=coord,
                    tecnico=tecnico,
                )

            return coord

    @classmethod
    def update(cls, coord_id, data, user):
        try:
            coord = CoordenacaoDistrital.objects.get(id=coord_id, validity_to__isnull=True)
        except CoordenacaoDistrital.DoesNotExist:
            raise ValidationError([{'message': 'Coordenação Distrital não encontrada'}])

        with transaction.atomic():
            if 'coordenador_id' in data and data['coordenador_id']:
                coord.coordenador_id = cls._decode_pk(data['coordenador_id'])
            if 'tecnico_administrativo_id' in data:
                coord.tecnico_administrativo_id = cls._decode_pk(data['tecnico_administrativo_id'])
            if 'ativo' in data:
                coord.ativo = data['ativo']
            if 'observacoes' in data:
                coord.observacoes = data['observacoes']

            # Se foram fornecidos tecnicos_operacionais_ids, substitui lista completa
            if 'tecnicos_operacionais_ids' in data:
                coord.tecnicos_operacionais.all().delete()
                for tecnico in cls._resolve_tecnico_ids(data['tecnicos_operacionais_ids']):
                    CoordenacaoDistritalTecnico.objects.create(
                        coordenacao=coord,
                        tecnico=tecnico,
                    )

            coord.audit_user_id = user.id_for_audit
            coord.save()
            return coord

    @classmethod
    def delete(cls, coord_id, user):
        try:
            coord = CoordenacaoDistrital.objects.get(id=coord_id, validity_to__isnull=True)
        except CoordenacaoDistrital.DoesNotExist:
            raise ValidationError([{'message': 'Coordenação Distrital não encontrada'}])

        with transaction.atomic():
            from django.utils import timezone
            coord.validity_to = timezone.now()
            coord.ativo = False
            coord.audit_user_id = user.id_for_audit
            coord.save()
            return coord

    @classmethod
    def add_tecnico_operacional(cls, coord_id, tecnico_id, user):
        """Adiciona um único técnico operacional à coordenação."""
        try:
            coord = CoordenacaoDistrital.objects.get(id=coord_id, validity_to__isnull=True)
        except CoordenacaoDistrital.DoesNotExist:
            raise ValidationError([{'message': 'Coordenação Distrital não encontrada'}])

        if CoordenacaoDistritalTecnico.objects.filter(coordenacao=coord, tecnico_id=tecnico_id).exists():
            raise ValidationError([{'message': 'Este técnico já está associado a esta coordenação'}])

        CoordenacaoDistritalTecnico.objects.create(coordenacao=coord, tecnico_id=tecnico_id)

    @classmethod
    def remove_tecnico_operacional(cls, coord_id, tecnico_id, user):
        """Remove um único técnico operacional da coordenação."""
        deleted, _ = CoordenacaoDistritalTecnico.objects.filter(
            coordenacao_id=coord_id, tecnico_id=tecnico_id
        ).delete()
        if not deleted:
            raise ValidationError([{'message': 'Técnico não encontrado nesta coordenação'}])
