from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import RefResolver, validate, validators

# Directory containing schema files at repository root
_SCHEMAS_DIR = Path(__file__).resolve().parents[5] / "schema"


def load_schema(name: str | Path) -> dict:
    """Load a JSON schema by name or path."""
    path = Path(name)
    if not path.is_absolute():
        path = _SCHEMAS_DIR / path
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_instance(instance: Mapping[str, Any], schema: str | Mapping[str, Any]) -> None:
    """Validate ``instance`` against ``schema``.

    ``schema`` may be a mapping or the file name of a schema located in
    the repository ``schema`` directory.
    """
    if isinstance(schema, (str, Path)):
        schema_path = Path(schema)
        if not schema_path.is_absolute():
            schema_path = _SCHEMAS_DIR / schema_path
        schema = load_schema(schema_path)
        base_uri = f"file://{schema_path.parent.as_posix()}/"
        validator_cls = validators.validator_for(schema)
        validator = validator_cls(schema, resolver=RefResolver(base_uri, schema))
        validator.validate(instance)
    else:
        validate(instance=instance, schema=schema)


def validate_tbeep_message(message: Any) -> None:
    """Validate a T-BEEP message or dictionary representation."""
    if hasattr(message, "model_dump"):
        instance = message.model_dump(mode="json", exclude_none=True)
    elif hasattr(message, "to_dict"):
        instance = message.to_dict()
    else:
        instance = dict(message)
    validate_instance(instance, "tbeep_message.schema.json")
