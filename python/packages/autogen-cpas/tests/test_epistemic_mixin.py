import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "python" / "packages" / "autogen-cpas" / "src"))

from cpas_autogen.mixins import EpistemicAgentMixin


class StubConversableAgent:
    """Minimal stub mimicking autogen.ConversableAgent."""

    def __init__(self):
        self.generate_reply_calls = []

    def generate_reply(self, messages, *args, **kwargs):
        self.generate_reply_calls.append((messages, args, kwargs))
        return "ok"


class DummyAgent(EpistemicAgentMixin, StubConversableAgent):
    pass


def test_conversable_setup_requires_metadata():
    agent = DummyAgent()
    with pytest.raises(AttributeError):
        agent.conversable_setup()


def test_get_epistemic_fingerprint_stable():
    meta = {
        "id": "1",
        "model": "gpt",
        "timestamp": "2025",
        "alignment_profile": "CPAS-Core v1.1",
    }
    agent1 = DummyAgent()
    agent1.idp_metadata = meta
    agent1.conversable_setup()
    fp1 = agent1.get_epistemic_fingerprint()
    fp2 = agent1.get_epistemic_fingerprint()

    agent2 = DummyAgent()
    agent2.idp_metadata = meta
    agent2.conversable_setup()
    fp3 = agent2.get_epistemic_fingerprint()

    assert fp1 == fp2 == fp3


def test_generate_reply_updates_fingerprint_and_wraps(monkeypatch):
    meta = {
        "id": "1",
        "model": "gpt",
        "timestamp": "2025",
        "alignment_profile": "CPAS-Core v1.1",
    }
    agent = DummyAgent()
    agent.idp_metadata = meta
    agent.conversable_setup()
    original_seed = agent.seed_token

    monkeypatch.setattr(
        "cpas_autogen.mixins.wrap_with_seed_token", lambda p, s: f"WRAP:{p}"
    )
    monkeypatch.setattr(
        "cpas_autogen.mixins.generate_fingerprint",
        lambda p, s: {"fingerprint": f"HASH:{p}"},
    )
    monkeypatch.setattr(
        "cpas_autogen.mixins.continuity_check", lambda s, t: True
    )
    monkeypatch.setattr(
        "cpas_autogen.mixins.latest_metrics", lambda: {}
    )
    monkeypatch.setattr(
        "cpas_autogen.mixins.periodic_metrics_check", lambda a, m: None
    )
    monkeypatch.setattr(
        "cpas_autogen.mixins.should_realign", lambda m: False
    )

    msgs = [{"role": "user", "content": "hi"}]
    result = agent.generate_reply(msgs, thread_token="#COMM_PROTO")
    assert result == "ok"
    assert msgs[-1]["content"] == "WRAP:hi"
    assert agent.last_fingerprint == {"fingerprint": "HASH:WRAP:hi"}
    assert agent.seed_token is original_seed


def test_generate_reply_triggers_realign(monkeypatch):
    meta = {
        "id": "1",
        "model": "gpt",
        "timestamp": "2025",
        "alignment_profile": "CPAS-Core v1.1",
    }
    agent = DummyAgent()
    agent.idp_metadata = meta
    agent.conversable_setup()

    monkeypatch.setattr(
        "cpas_autogen.mixins.wrap_with_seed_token", lambda p, s: p
    )
    monkeypatch.setattr(
        "cpas_autogen.mixins.generate_fingerprint",
        lambda p, s: {"fingerprint": p},
    )
    monkeypatch.setattr(
        "cpas_autogen.mixins.continuity_check", lambda s, t: True
    )
    monkeypatch.setattr(
        "cpas_autogen.mixins.latest_metrics", lambda: {"x": 1}
    )
    monkeypatch.setattr(
        "cpas_autogen.mixins.periodic_metrics_check", lambda a, m: None
    )
    monkeypatch.setattr(
        "cpas_autogen.mixins.should_realign", lambda m: True
    )

    old_seed = agent.seed_token
    msgs = [{"role": "user", "content": "hi"}]
    agent.generate_reply(msgs, thread_token="#COMM_PROTO")
    assert agent.seed_token is not old_seed
