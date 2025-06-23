import json
import logging
import runpy
from pathlib import Path

import pytest

pytest.importorskip("jsonschema")

# Paths to schema and instance files used for validation tests
DATA_ROOT = Path(__file__).parents[3]  # repo root
SCHEMA_FILE = DATA_ROOT / "agents/idp-v1.0-schema.json"
INSTANCE_FILE = DATA_ROOT / "agents/json/openai/Clarence-9.json"

# Skip tests if IDP schema is not present in repo
pytest.skip(
    "IDP files not present", allow_module_level=True
) if not SCHEMA_FILE.exists() else None

validate_path = Path(__file__).with_name("validate_idp.py")
validate_module = runpy.run_path(str(validate_path))
validate_instance = validate_module["validate_instance"]


def test_validate_instance_pass(caplog):
    instance = str(INSTANCE_FILE)
    schema = str(SCHEMA_FILE)
    with caplog.at_level(logging.INFO):
        validate_instance(instance, schema)
    assert "Validation passed" in caplog.text


def test_validate_instance_missing_field(tmp_path, caplog):
    schema = str(SCHEMA_FILE)
    data = json.load(open(INSTANCE_FILE))
    data.pop("instance_name", None)
    instance_file = tmp_path / "invalid.json"
    with instance_file.open("w") as f:
        json.dump(data, f)
    with caplog.at_level(logging.ERROR):
        validate_instance(str(instance_file), schema)
    assert "Validation failed" in caplog.text


def test_validate_instance_invalid_enum(tmp_path, caplog):
    schema = str(SCHEMA_FILE)
    data = json.load(open(INSTANCE_FILE))
    data["reasoning_transparency_level"] = "extreme"
    instance_file = tmp_path / "invalid_enum.json"
    with instance_file.open("w") as f:
        json.dump(data, f)
    with caplog.at_level(logging.ERROR):
        validate_instance(str(instance_file), schema)
    assert "Validation failed" in caplog.text


def test_validate_instance_additional_property(tmp_path, caplog):
    """Validation fails when instance has an unexpected property."""
    schema = str(SCHEMA_FILE)
    data = json.load(open(INSTANCE_FILE))
    data["bogus_key"] = "bogus"
    instance_file = tmp_path / "extra_prop.json"
    with instance_file.open("w") as f:
        json.dump(data, f)
    with caplog.at_level(logging.ERROR):
        validate_instance(str(instance_file), schema)
    assert "Validation failed" in caplog.text
