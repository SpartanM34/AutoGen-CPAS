import sys
import types
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "python" / "packages" / "autogen-cpas" / "src"))

# Provide a minimal stub for the optional 'autogen' dependency
autogen_stub = types.ModuleType("autogen")


class _DummyCA:
    def __init__(self, *args, **kwargs) -> None:
        pass


autogen_stub.ConversableAgent = _DummyCA
autogen_stub.config_list_from_models = lambda models: []
sys.modules.setdefault("autogen", autogen_stub)

from autogen_cpas.models import CPASMetadata, TBeepMessage
from autogen_cpas.protocol import RIFG, Role


def test_unknown_metadata_field_raises() -> None:
    with pytest.raises(ValidationError):
        CPASMetadata(confidence=0.5, rifg=RIFG.LOW, provenance=["unit"], extra=1)


def test_unknown_message_field_raises() -> None:
    meta = CPASMetadata(confidence=0.5, rifg=RIFG.LOW, provenance=["unit"])
    with pytest.raises(ValidationError):
        TBeepMessage(
            id="1",
            timestamp=datetime.utcnow(),
            role=Role.USER,
            sender="alice",
            recipient="bob",
            content="hi",
            metadata=meta,
            extra_field=42,
        )


def test_confidence_out_of_range() -> None:
    with pytest.raises(ValueError):
        CPASMetadata(confidence=1.5, rifg=RIFG.LOW, provenance=["unit"])


def test_notes_omitted_when_none() -> None:
    meta = CPASMetadata(confidence=0.5, rifg=RIFG.MEDIUM, provenance=["unit"])
    dumped = meta.model_dump(exclude_none=True)
    assert "notes" not in dumped


def test_bad_timestamp_string_raises() -> None:
    data = {
        "id": "1",
        "timestamp": "not-a-time",
        "role": "user",
        "sender": "alice",
        "recipient": "bob",
        "content": "hi",
        "metadata": {"confidence": 0.5, "rifg": 0.0, "provenance": ["unit"]},
    }
    with pytest.raises(ValidationError):
        TBeepMessage.from_dict(data)


def test_invalid_role_value_raises() -> None:
    data = {
        "id": "1",
        "timestamp": datetime.utcnow().isoformat(),
        "role": "bot",
        "sender": "alice",
        "recipient": "bob",
        "content": "hi",
        "metadata": {"confidence": 0.5, "rifg": 0.0, "provenance": ["unit"]},
    }
    with pytest.raises(ValidationError):
        TBeepMessage.from_dict(data)
