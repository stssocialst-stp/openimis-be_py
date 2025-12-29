"""
PEP+ Utility Functions
Helper functions for ID conversion and data processing
"""
import base64
from graphql_relay import from_global_id


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
        'grupo_familia_id',
        'localidade_id',
        'formador_id',
        'supervisor_id',
        'tecnico_responsavel_id'
    ]

    converted = session_data.copy()

    for field in id_fields:
        if field in converted and converted[field] is not None:
            converted[field] = decode_id(converted[field])

    return converted
