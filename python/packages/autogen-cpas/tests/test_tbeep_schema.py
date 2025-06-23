import importlib.util
import sys
import types
from datetime import datetime
from pathlib import Path

import pytest
from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "python" / "packages" / "autogen-cpas" / "src"))
autogen_stub = types.ModuleType("autogen")


class _DummyCA:
    def __init__(self, *args, **kwargs) -> None:
        pass


autogen_stub.ConversableAgent = _DummyCA
autogen_stub.config_list_from_models = lambda models: []
sys.modules.setdefault("autogen", autogen_stub)

def _load_modules():
    src_dir = ROOT / "python" / "packages" / "autogen-cpas" / "src"
    spec_protocol = importlib.util.spec_from_file_location(
        "autogen_cpas.protocol", src_dir / "autogen_cpas" / "protocol.py"
    )
    protocol = importlib.util.module_from_spec(spec_protocol)
    sys.modules["autogen_cpas.protocol"] = protocol
    spec_protocol.loader.exec_module(protocol)

    spec_models = importlib.util.spec_from_file_location(
        "autogen_cpas.models", src_dir / "autogen_cpas" / "models.py"
    )
    models = importlib.util.module_from_spec(spec_models)
    sys.modules["autogen_cpas.models"] = models
    spec_models.loader.exec_module(models)

    spec_validation = importlib.util.spec_from_file_location(
        "autogen_cpas.validation", src_dir / "autogen_cpas" / "validation.py"
    )
    validation = importlib.util.module_from_spec(spec_validation)
    sys.modules["autogen_cpas.validation"] = validation
    spec_validation.loader.exec_module(validation)

    return models, protocol, validation


models, protocol, validation = _load_modules()
CPASMetadata = models.CPASMetadata
TBeepMessage = models.TBeepMessage
RIFG = protocol.RIFG
Role = protocol.Role
validate_tbeep_message = validation.validate_tbeep_message


def _sample_message() -> TBeepMessage:
    meta = CPASMetadata(confidence=0.5, rifg=RIFG.MEDIUM, provenance=["unit"])
    return TBeepMessage(
        id="1",
        timestamp=datetime(2025, 1, 1, 0, 0, 0),
        role=Role.USER,
        sender="alice",
        recipient="bob",
        content="hello",
        metadata=meta,
    )


def test_message_conforms_to_schema() -> None:
    msg = _sample_message()
    validate_tbeep_message(msg)


def test_invalid_message_raises() -> None:
    invalid = {
        "id": "1",
        "timestamp": "bad",
        "role": "user",
        "sender": "alice",
        "recipient": "bob",
        "content": "hi",
        "metadata": {"confidence": 1.2, "rifg": 0.5, "provenance": []},
    }
    with pytest.raises(ValidationError):
        validate_tbeep_message(invalid)


def test_unexpected_message_field() -> None:
    msg = _sample_message().to_dict()
    msg["extra"] = "oops"
    with pytest.raises(ValidationError):
        validate_tbeep_message(msg)


def test_unexpected_metadata_field() -> None:
    msg = _sample_message().to_dict()
    msg["metadata"]["extra"] = "nope"
    with pytest.raises(ValidationError):
        validate_tbeep_message(msg)


def test_missing_message_field() -> None:
    msg = _sample_message().to_dict()
    msg.pop("sender")
    with pytest.raises(ValidationError):
        validate_tbeep_message(msg)


def test_missing_metadata_field() -> None:
    msg = _sample_message().to_dict()
    msg["metadata"].pop("provenance")
    with pytest.raises(ValidationError):
        validate_tbeep_message(msg)


def test_protocol_decode_value_error() -> None:
    with pytest.raises(ValueError):
        protocol.decode("not a dict")


def test_protocol_decode_type_error() -> None:
    with pytest.raises(TypeError):
        protocol.decode(123)
