"""
PEP+ Utility Functions
Helper functions for ID conversion and data processing
"""
import logging
import base64
from graphql_relay import from_global_id

logger = logging.getLogger(__name__)


def decode_id(encoded_id):
    """
    Decode a Relay Global ID or return the ID as-is if already decoded.

    Args:
        encoded_id: Can be either:
            - Relay Global ID (base64 string): "VXNlckdRTFR5cGU6MTIz"
            - Direct ID (int or string): 123 or "123"
            - UUID string: "f63cda3c-5635-4a52-9ee8-1843bccb161e"

    Returns:
        The decoded ID (string or int)

    Examples:
        >>> decode_id("VXNlckdRTFR5cGU6MTIz")  # Base64 "UserGQLType:123"
        '123'
        >>> decode_id(123)
        123
        >>> decode_id("123")
        '123'
    """
    if encoded_id is None:
        return None

    # If already an integer, return as-is
    if isinstance(encoded_id, int):
        return encoded_id

    # If it's a string, try to decode it as relay ID
    if isinstance(encoded_id, str):
        # Check if it looks like a UUID (contains hyphens)
        if '-' in encoded_id:
            return encoded_id

        # Check if it's a plain integer string
        if encoded_id.isdigit():
            return int(encoded_id)

        # Try to decode as Relay Global ID
        try:
            node_type, node_id = from_global_id(encoded_id)
            # Try to convert to int if possible
            try:
                return int(node_id)
            except (ValueError, TypeError):
                # If not numeric, return as string (UUID)
                return node_id
        except Exception:
            # If decoding fails, assume it's already a plain ID
            return encoded_id

    return encoded_id


def resolve_id_field(data, field_name):
    """
    Resolve an ID field from input data, handling Relay IDs.

    Args:
        data: Dictionary containing the field
        field_name: Name of the field to resolve

    Returns:
        The resolved ID or None if field doesn't exist
    """
    if field_name not in data:
        return None

    value = data[field_name]
    return decode_id(value)


def convert_ids_in_session_data(session_data):
    """
    Convert all ID fields in session data from Relay IDs to database IDs.

    Args:
        session_data: Dictionary with session data

    Returns:
        Dictionary with converted IDs
    """
    id_fields = [
        'coordenador_distrital_id',
        'tecnico_social_id',
        'distrito_id',
        'modulo_id',
        'modulo_maior_dificuldade_id',
        'grupo_familia_id',
        'localidade_id',
        'formador_id',
        'supervisor_id',
        'tecnico_responsavel_id',
        'sessao_id'
    ]

    converted = session_data.copy()

    for field in id_fields:
        if field in converted and converted[field] is not None:
            decoded = decode_id(converted[field])

            # If it's a UUID (contains hyphens), convert to numeric ID
            if isinstance(decoded, str) and '-' in decoded:
                decoded = convert_uuid_to_id(field, decoded)

            converted[field] = decoded

    return converted


def convert_uuid_to_id(field_name, uuid_value):
    """
    Convert UUID to numeric ID by looking up the database.

    Args:
        field_name: Name of the field (e.g., 'grupo_familia_id')
        uuid_value: UUID string

    Returns:
        Numeric ID or the UUID if conversion fails
    """
    logger.info(f"[PEP+] convert_uuid_to_id: field={field_name}, uuid={uuid_value}")

    # Import models here to avoid circular imports
    from .models import (
        GrupoFamiliar, ModuloEducacional, SessaoPEP,
        PresencaSessao, ExecucaoSessao, SupervisaoSessao
    )
    from core.models import User
    from location.models import Location

    model_mapping = {
        'grupo_familia_id': (GrupoFamiliar, 'uuid'),
        'modulo_id': (ModuloEducacional, 'uuid'),
        'modulo_maior_dificuldade_id': (ModuloEducacional, 'uuid'),
        'coordenador_distrital_id': (User, 'id'),
        'tecnico_social_id': (User, 'id'),
        'formador_id': (User, 'id'),
        'supervisor_id': (User, 'id'),
        'tecnico_responsavel_id': (User, 'id'),
        'distrito_id': (Location, 'uuid'),
        'localidade_id': (Location, 'uuid'),
        'sessao_id': (SessaoPEP, 'uuid'),
    }

    if field_name not in model_mapping:
        logger.warning(f"[PEP+] Field {field_name} not in mapping, returning UUID as-is")
        return uuid_value

    model_class, uuid_field = model_mapping[field_name]
    logger.info(f"[PEP+] Looking up {model_class.__name__} by {uuid_field}={uuid_value}")

    try:
        # Look up the object by UUID and get its numeric ID
        obj = model_class.objects.get(**{uuid_field: uuid_value})
        logger.info(f"[PEP+] Found object! Converting UUID {uuid_value} to ID {obj.id}")
        return obj.id
    except Exception as e:
        # If lookup fails, return the UUID as-is
        logger.error(f"[PEP+] Failed to convert UUID to ID: {e}")
        return uuid_value
