from datetime import datetime

import pytest

from autogen_cpas.models import CPASMetadata, TBeepMessage
from autogen_cpas.protocol import RIFG, Role


def test_metadata_precision():
    CPASMetadata(confidence=0.5, rifg=RIFG.MEDIUM, provenance=["test"])
    with pytest.raises(ValueError):
        CPASMetadata(confidence=0.1234, rifg=RIFG.MEDIUM, provenance=["test"])


def test_message_roundtrip():
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
