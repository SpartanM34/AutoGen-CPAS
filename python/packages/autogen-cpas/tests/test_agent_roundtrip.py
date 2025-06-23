import sys
import types
import pytest
from autogen_core import AgentId, SingleThreadedAgentRuntime

autogen_stub = types.ModuleType("autogen")
autogen_stub.ConversableAgent = object
autogen_stub.config_list_from_models = lambda models: []
sys.modules.setdefault("autogen", autogen_stub)

from autogen_cpas.agent import EchoAgent, _bayesian_confidence
from autogen_cpas.models import ChatMessage
from autogen_cpas.protocol import Role


@pytest.mark.asyncio
async def test_agent_roundtrip() -> None:
    runtime = SingleThreadedAgentRuntime()
    await EchoAgent.register(runtime, "echo", EchoAgent)
    runtime.start()
    response = await runtime.send_message(
        ChatMessage.simple(Role.USER, "ping"), recipient=AgentId("echo", "default")
    )
    await runtime.stop()
    assert isinstance(response, ChatMessage)
    assert response.role is Role.ASSISTANT
    assert response.content == "ping"


@pytest.mark.asyncio
async def test_send_to_unknown_agent_raises() -> None:
    runtime = SingleThreadedAgentRuntime()
    await EchoAgent.register(runtime, "echo", EchoAgent)
    runtime.start()
    with pytest.raises(Exception, match="Recipient not found"):
        await runtime.send_message(
            ChatMessage.simple(Role.USER, "ping"),
            recipient=AgentId("missing", "default"),
        )
    await runtime.stop()


def test_bayesian_confidence_bounds() -> None:
    """_bayesian_confidence should return values within [0,1] at the extremes."""
    assert 0.0 <= _bayesian_confidence(0.0) <= 1.0
    assert 0.0 <= _bayesian_confidence(1.0) <= 1.0
