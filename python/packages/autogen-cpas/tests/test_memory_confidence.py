import asyncio
import sys
import types
from datetime import datetime

import pytest
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType

from autogen_cpas.agent import CpasEnabledAgent
from autogen_cpas.models import CPASMetadata, TBeepMessage
from autogen_cpas.protocol import RIFG, Role, decode, encode

# Stub optional autogen dependency
autogen_stub = types.ModuleType("autogen")
autogen_stub.ConversableAgent = object
autogen_stub.config_list_from_models = lambda models: []
sys.modules.setdefault("autogen", autogen_stub)


def test_generate_reply_aggregates_bayesian_confidence() -> None:
    memory = ListMemory()
    agent = CpasEnabledAgent(name="bot")
    agent.memory = [memory]

    prev_meta1 = CPASMetadata(confidence=0.6, rifg=RIFG.LOW, provenance=["unit"])
    prev_msg1 = TBeepMessage(
        id="p1",
        timestamp=datetime.utcnow(),
        role=Role.ASSISTANT,
        sender="bot",
        recipient="user",
        content="hi",
        metadata=prev_meta1,
    )
    asyncio.run(memory.add(MemoryContent(content=prev_msg1.to_dict(), mime_type=MemoryMimeType.JSON)))

    prev_meta2 = CPASMetadata(confidence=0.7, rifg=RIFG.LOW, provenance=["unit"])
    prev_msg2 = TBeepMessage(
        id="p2",
        timestamp=datetime.utcnow(),
        role=Role.USER,
        sender="user",
        recipient="bot",
        content="yo",
        metadata=prev_meta2,
    )
    asyncio.run(memory.add(MemoryContent(content=prev_msg2.to_dict(), mime_type=MemoryMimeType.JSON)))

    meta = CPASMetadata(confidence=0.5, rifg=RIFG.LOW, provenance=["unit"])
    incoming = TBeepMessage(
        id="n1",
        timestamp=datetime.utcnow(),
        role=Role.USER,
        sender="user",
        recipient="bot",
        content="hello",
        metadata=meta,
    )
    encoded = encode(incoming)
    out = agent.generate_reply([encoded])
    reply = decode(out)

    assert reply.metadata.provenance[-1] == "n1"
    assert reply.metadata.confidence == pytest.approx(0.84)
