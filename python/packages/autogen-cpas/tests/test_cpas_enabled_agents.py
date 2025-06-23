import pytest

pytest.importorskip("autogen")
pytest.importorskip("autogen.core")

from datetime import datetime

from autogen_core import AgentId, SingleThreadedAgentRuntime

from autogen_cpas.agent import CpasEnabledAgent
from autogen_cpas.models import CPASMetadata, TBeepMessage
from autogen_cpas.protocol import RIFG, Role, decode, encode
from pydantic import ValidationError


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
    assert decoded.metadata.provenance == ["unit", "1"]


def test_receive_malformed_message_raises() -> None:
    agent = CpasEnabledAgent(name="a")
    with pytest.raises(ValidationError):
        agent.receive({"bad": "data"})


def test_generate_reply_malformed_message_raises() -> None:
    agent = CpasEnabledAgent(name="a")
    with pytest.raises(ValidationError):
        agent.generate_reply([{"bad": "data"}])


@pytest.mark.asyncio
async def test_provenance_accumulates() -> None:
    runtime = SingleThreadedAgentRuntime()

    sender = CpasEnabledAgent(name="sender")
    receiver = CpasEnabledAgent(name="receiver")

    await sender.register_instance(runtime, AgentId("sender", "default"))
    await receiver.register_instance(runtime, AgentId("receiver", "default"))

    runtime.start()

    meta = CPASMetadata(confidence=0.5, rifg=RIFG.LOW, provenance=["unit"])
    msg = TBeepMessage(
        id="1",
        timestamp=datetime.utcnow(),
        role=Role.USER,
        sender="sender",
        recipient="receiver",
        content="hi",
        metadata=meta,
    )
    encoded = encode(msg)

    r1 = await runtime.send_message(
        encoded,
        recipient=AgentId("receiver", "default"),
        sender=AgentId("sender", "default"),
    )

    r2 = await runtime.send_message(
        r1,
        recipient=AgentId("sender", "default"),
        sender=AgentId("receiver", "default"),
    )

    r3 = await runtime.send_message(
        r2,
        recipient=AgentId("receiver", "default"),
        sender=AgentId("sender", "default"),
    )

    await runtime.stop()

    r1_decoded = decode(r1)
    r2_decoded = decode(r2)
    r3_decoded = decode(r3)
    assert r3_decoded.metadata.provenance == ["unit", "1", r1_decoded.id, r2_decoded.id]
