import importlib.util
import sys
import types
from datetime import datetime
import pytest


def _load_modules():
    dummy = types.ModuleType("autogen_cpas.models")
    dummy.TBeepMessage = type("TBeepMessage", (), {})
    sys.modules["autogen_cpas.models"] = dummy

    spec_protocol = importlib.util.spec_from_file_location(
        "autogen_cpas.protocol",
        "python/packages/autogen-cpas/src/autogen_cpas/protocol.py",
    )
    protocol = importlib.util.module_from_spec(spec_protocol)
    protocol.__package__ = "autogen_cpas"
    sys.modules["autogen_cpas.protocol"] = protocol
    spec_protocol.loader.exec_module(protocol)

    spec_models = importlib.util.spec_from_file_location(
        "autogen_cpas.models",
        "python/packages/autogen-cpas/src/autogen_cpas/models.py",
    )
    models = importlib.util.module_from_spec(spec_models)
    models.__package__ = "autogen_cpas"
    sys.modules["autogen_cpas.models"] = models
    spec_models.loader.exec_module(models)

    return models, protocol


models, protocol = _load_modules()
CPASMetadata = models.CPASMetadata
TBeepMessage = models.TBeepMessage
RIFG = protocol.RIFG
Role = protocol.Role


def test_metadata_roundtrip():
    meta = CPASMetadata(confidence=0.6, rifg=RIFG.MEDIUM, provenance=["unit"], notes="n")
    dumped = meta.model_dump()
    assert CPASMetadata.model_validate(dumped) == meta


def test_metadata_invalid_range():
    with pytest.raises(ValueError):
        CPASMetadata(confidence=1.1, rifg=RIFG.LOW, provenance=["x"])
    with pytest.raises(ValueError):
        CPASMetadata(confidence=-0.1, rifg=RIFG.LOW, provenance=["x"])


def test_metadata_invalid_rifg():
    with pytest.raises(ValueError):
        CPASMetadata(confidence=0.5, rifg=99, provenance=["x"])


def test_message_roundtrip_again():
    meta = CPASMetadata(confidence=0.9, rifg=RIFG.HIGH, provenance=["unit"])
    msg = TBeepMessage(
        id="1",
        timestamp=datetime(2025, 1, 1, 0, 0, 0),
        role=Role.USER,
        sender="alice",
        recipient="bob",
        content="hello",
        metadata=meta,
    )
    data = msg.to_dict()
    assert TBeepMessage.from_dict(data) == msg
