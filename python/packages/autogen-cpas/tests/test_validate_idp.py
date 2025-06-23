import json
import logging
import runpy
from importlib.resources import files

import pytest

pytest.importorskip("jsonschema")

validate_path = files("autogen_cpas.tests").joinpath("validate_idp.py")
validate_module = runpy.run_path(str(validate_path))
validate_instance = validate_module["validate_instance"]


def test_validate_instance_pass(caplog):
    instance = "agents/json/openai/Clarence-9.json"
    schema = "agents/idp-v1.0-schema.json"
    with caplog.at_level(logging.INFO):
        validate_instance(instance, schema)
    assert "Validation passed" in caplog.text


def test_validate_instance_missing_field(tmp_path, caplog):
    schema = "agents/idp-v1.0-schema.json"
    data = json.load(open("agents/json/openai/Clarence-9.json"))
    data.pop("instance_name", None)
    instance_file = tmp_path / "invalid.json"
    with instance_file.open("w") as f:
        json.dump(data, f)
    with caplog.at_level(logging.ERROR):
        validate_instance(str(instance_file), schema)
    assert "Validation failed" in caplog.text


def test_validate_instance_invalid_enum(tmp_path, caplog):
    schema = "agents/idp-v1.0-schema.json"
    data = json.load(open("agents/json/openai/Clarence-9.json"))
    data["reasoning_transparency_level"] = "extreme"
    instance_file = tmp_path / "invalid_enum.json"
    with instance_file.open("w") as f:
        json.dump(data, f)
    with caplog.at_level(logging.ERROR):
        validate_instance(str(instance_file), schema)
    assert "Validation failed" in caplog.text


def test_validate_instance_additional_property(tmp_path, caplog):
    """Validation fails when instance has an unexpected property."""
    schema = "agents/idp-v1.0-schema.json"
    data = json.load(open("agents/json/openai/Clarence-9.json"))
    data["bogus_key"] = "bogus"
    instance_file = tmp_path / "extra_prop.json"
    with instance_file.open("w") as f:
        json.dump(data, f)
    with caplog.at_level(logging.ERROR):
        validate_instance(str(instance_file), schema)
    assert "Validation failed" in caplog.text
