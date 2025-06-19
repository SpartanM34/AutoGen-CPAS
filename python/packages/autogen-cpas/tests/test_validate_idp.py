import pytest

pytest.importorskip("jsonschema")
import runpy

validate_module = runpy.run_path("python/packages/autogen-cpas/tests/validate_idp.py")
validate_instance = validate_module["validate_instance"]


def test_validate_instance_pass(capsys):
    instance = "agents/json/openai/Clarence-9.json"
    schema = "agents/idp-v1.0-schema.json"
    validate_instance(instance, schema)
    captured = capsys.readouterr().out
    assert "Validation passed" in captured
