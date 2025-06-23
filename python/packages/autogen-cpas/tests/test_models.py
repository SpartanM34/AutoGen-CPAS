import sys
import types

autogen_stub = types.ModuleType("autogen")


class _DummyCA:
    def __init__(self, *args, **kwargs) -> None:
        pass


autogen_stub.ConversableAgent = _DummyCA
autogen_stub.config_list_from_models = lambda models: []
sys.modules.setdefault("autogen", autogen_stub)

from autogen_cpas.models import ChatMessage
from autogen_cpas.protocol import Role


def test_roundtrip() -> None:
    msg = ChatMessage.simple(Role.USER, "ping")
    data = msg.model_dump()
    assert ChatMessage.model_validate(data) == msg
