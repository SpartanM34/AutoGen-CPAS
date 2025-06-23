import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "python" / "packages" / "autogen-cpas" / "src"))

# stub autogen module to satisfy optional imports
autogen_stub = types.ModuleType("autogen")


class _DummyCA:
    def __init__(self, *args, **kwargs) -> None:
        pass


autogen_stub.ConversableAgent = _DummyCA
autogen_stub.config_list_from_models = lambda models: []
sys.modules.setdefault("autogen", autogen_stub)

src_dir = ROOT / "python" / "packages" / "autogen-cpas" / "src"

def _load_modules():
    spec_protocol = importlib.util.spec_from_file_location(
        "autogen_cpas.protocol", src_dir / "autogen_cpas" / "protocol.py"
    )
    protocol = importlib.util.module_from_spec(spec_protocol)
    protocol.__package__ = "autogen_cpas"
    sys.modules["autogen_cpas.protocol"] = protocol
    spec_protocol.loader.exec_module(protocol)

    spec_models = importlib.util.spec_from_file_location(
        "autogen_cpas.models", src_dir / "autogen_cpas" / "models.py"
    )
    models = importlib.util.module_from_spec(spec_models)
    models.__package__ = "autogen_cpas"
    sys.modules["autogen_cpas.models"] = models
    spec_models.loader.exec_module(models)

    spec_messenger = importlib.util.spec_from_file_location(
        "tbeep_messenger", src_dir / "T-BEEP" / "tbeep_messenger.py"
    )
    messenger = importlib.util.module_from_spec(spec_messenger)
    spec_messenger.loader.exec_module(messenger)

    return models, protocol, messenger

models, protocol, messenger_mod = _load_modules()

CPASMetadata = models.CPASMetadata
RIFG = protocol.RIFG
Role = protocol.Role
TBeepMessenger = messenger_mod.TBeepMessenger


def test_create_message_defaults_and_overrides() -> None:
    messenger = TBeepMessenger("unit")
    start_len = len(messenger.message_history)

    msg1 = messenger.create_message(role=Role.USER, recipient="bob", content="hi")

    assert msg1.metadata.confidence == 0.5
    assert msg1.metadata.rifg is RIFG.LOW
    assert msg1.metadata.provenance == ["unit"]
    assert msg1.id
    assert len(messenger.message_history) == start_len + 1

    custom = CPASMetadata(confidence=0.9, rifg=RIFG.HIGH, provenance=["x"])
    msg2 = messenger.create_message(
        role=Role.ASSISTANT, recipient="bob", content="hello", metadata=custom
    )

    assert msg2.metadata == custom
    assert msg2.id != msg1.id
    assert len(messenger.message_history) == start_len + 2
