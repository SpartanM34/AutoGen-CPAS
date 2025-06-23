import sys
import types
from datetime import datetime

import pytest

autogen_stub = types.ModuleType("autogen")
class _DummyCA:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def receive(self, *args, **kwargs):
        pass

    def generate_reply(self, *args, **kwargs):
        return {}

autogen_stub.ConversableAgent = _DummyCA
autogen_stub.config_list_from_models = lambda models: []
sys.modules.setdefault("autogen", autogen_stub)

from autogen_core import CancellationToken
from autogen_agentchat.messages import StructuredMessage

from autogen_cpas.agent import CpasEnabledAgent, AsyncCpasAgent
from autogen_cpas.models import CPASMetadata, TBeepMessage
from autogen_cpas.protocol import RIFG, Role


@pytest.mark.asyncio
async def test_async_cpas_agent_roundtrip() -> None:
    sync_agent = CpasEnabledAgent()
    sync_agent.name = "sync"
    async_agent = AsyncCpasAgent(sync_agent)

    msg = TBeepMessage(
        id="1",
        timestamp=datetime.utcnow(),
        role=Role.USER,
        sender="user",
        recipient="sync",
        content="hello",
        metadata=CPASMetadata(confidence=0.5, rifg=RIFG.LOW, provenance=["unit"]),
    )
    wrapped = StructuredMessage[TBeepMessage](content=msg, source="user")

    response = await async_agent.on_messages([wrapped], CancellationToken())
    out = response.chat_message.content

    assert out.content == "hello"
    assert out.recipient == "user"
    assert out.metadata.confidence == pytest.approx(0.6)
    assert out.metadata.provenance == ["unit", "1"]

