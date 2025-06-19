import sys
from pathlib import Path
import types

# Ensure repository root is on sys.path so 'agents' package can be imported
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "python" / "packages" / "autogen-cpas" / "src"))

# Provide a minimal stub for the optional 'autogen' dependency
autogen_stub = types.ModuleType("autogen")
autogen_stub.ConversableAgent = object
autogen_stub.config_list_from_models = lambda models: []
sys.modules.setdefault("autogen", autogen_stub)

from agents import Telos

class StubAgent:
    def __init__(self, name=None, system_message=None, llm_config=None, description=None):
        self.name = name
        self.system_message = system_message
        self.llm_config = llm_config
        self.description = description
        self.idp_metadata = None
        self.seed_token = None
        self.last_fingerprint = None
        self.generate_reply_inputs = []

    def generate_reply(self, messages, sender=None, **kwargs):
        self.generate_reply_inputs.append((messages, sender, kwargs))
        return {"role": "assistant", "content": "ok"}

def test_create_agent(monkeypatch):
    monkeypatch.setattr(Telos, "ConversableAgent", StubAgent)
    monkeypatch.setattr(Telos, "config_list_from_models", lambda models: ["cfg"])
    monkeypatch.setattr(Telos, "config_list", ["cfg"])
    agent = Telos.create_agent()
    assert isinstance(agent, StubAgent)
    assert agent.idp_metadata["instance_name"] == "Telos"
    assert agent.seed_token is not None
    assert agent.llm_config == {"config_list": ["cfg"]}

def test_send_message(monkeypatch):
    agent = StubAgent()
    agent.idp_metadata = {"instance_name": "Telos"}
    agent.seed_token = Telos.SeedToken.generate({"alignment_profile": "CPAS-Core v1.1"})
    monkeypatch.setattr(Telos, "continuity_check", lambda s, t: True)
    monkeypatch.setattr(Telos, "latest_metrics", lambda: {})
    monkeypatch.setattr(Telos, "periodic_metrics_check", lambda a, m: None)
    monkeypatch.setattr(Telos, "should_realign", lambda m: False)
    result = Telos.send_message(agent, "hi", "#COMM_PROTO_X")
    assert result["role"] == "assistant"
    assert agent.last_fingerprint is not None
    assert agent.generate_reply_inputs[0][0][0]["content"].startswith("### Seed Instance")
