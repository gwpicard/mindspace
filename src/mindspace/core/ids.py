"""ULID generation for capture IDs."""

from ulid import ULID


def generate_id() -> str:
    """Generate a new ULID as a string."""
    return str(ULID())
