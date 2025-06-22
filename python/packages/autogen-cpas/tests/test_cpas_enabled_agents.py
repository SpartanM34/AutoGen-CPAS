import pytest

pytest.importorskip("autogen")
pytest.importorskip("autogen.core")

from datetime import datetime

from autogen_core import AgentId, SingleThreadedAgentRuntime

from autogen_cpas.agent import CpasEnabledAgent
from autogen_cpas.models import CPASMetadata, TBeepMessage
from autogen_cpas.protocol import RIFG, Role, decode, encode


@pytest.mark.asyncio
async def test_cpas_enabled_agents() -> None:
    runtime = SingleThreadedAgentRuntime()

    sender = CpasEnabledAgent(name="sender")
    receiver = CpasEnabledAgent(name="receiver")

    await sender.register_instance(runtime, AgentId("sender", "default"))
    await receiver.register_instance(runtime, AgentId("receiver", "default"))

    runtime.start()

    meta = CPASMetadata(confidence=0.5, rifg=RIFG.LOW, provenance=["unit"])
    message = TBeepMessage(
        id="1",
        timestamp=datetime.utcnow(),
        role=Role.USER,
        sender="sender",
        recipient="receiver",
        content="hello",
        metadata=meta,
    )
    encoded = encode(message)

    await runtime.send_message(
        encoded,
        recipient=AgentId("receiver", "default"),
        sender=AgentId("sender", "default"),
    )

    last = sender.last_message(receiver)
    assert last is not None
    decoded = decode(last)

    await runtime.stop()

    assert decoded.content == "hello"
    assert decoded.metadata.confidence == pytest.approx(0.6)
    assert decoded.metadata.provenance == ["unit", "receiver"]
