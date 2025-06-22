import pytest
from autogen_core import AgentId, SingleThreadedAgentRuntime

from autogen_cpas.agent import EchoAgent
from autogen_cpas.models import ChatMessage
from autogen_cpas.protocol import Role


@pytest.mark.asyncio
async def test_agent_roundtrip() -> None:
    runtime = SingleThreadedAgentRuntime()
    await EchoAgent.register(runtime, "echo", EchoAgent)
    runtime.start()
    response = await runtime.send_message(
        ChatMessage(role=Role.USER, content="ping"), recipient=AgentId("echo", "default")
    )
    await runtime.stop()
    assert isinstance(response, ChatMessage)
    assert response.role is Role.ASSISTANT
    assert response.content == "ping"
