from autogen_cpas.models import ChatMessage
from autogen_cpas.protocol import Role


def test_roundtrip() -> None:
    msg = ChatMessage(role=Role.USER, content="hello")
    data = msg.model_dump()
    assert ChatMessage.model_validate(data) == msg
