import logging
import types

import pytest
from agents.python import Lumin

pytest.importorskip("autogen")


class DummyAgent:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.idp_metadata = None
        self.seed_token = None

    def generate_reply(self, *args, **kwargs):
        return "mock"


def test_create_agent_has_seed_token(monkeypatch):
    monkeypatch.setattr(Lumin, "ConversableAgent", DummyAgent)
    Lumin.config_list = [{}]
    monkeypatch.setattr(Lumin, "retrieve_digests", lambda *a, **k: [])
    monkeypatch.setattr(Lumin, "rehydrate_context", lambda *a, **k: None)
    monkeypatch.setattr(Lumin.atexit, "register", lambda f: None)
    monkeypatch.setattr(Lumin, "store_digest", lambda *a, **k: None)
    monkeypatch.setattr(Lumin, "generate_digest", lambda *a, **k: {})
    agent = Lumin.create_agent()
    assert hasattr(agent, "seed_token")
    assert agent.seed_token is not None


def test_send_message_warns_on_continuity_failure(monkeypatch, caplog):
    monkeypatch.setattr(Lumin, "ConversableAgent", DummyAgent)
    Lumin.config_list = [{}]
    monkeypatch.setattr(Lumin, "retrieve_digests", lambda *a, **k: [])
    monkeypatch.setattr(Lumin, "rehydrate_context", lambda *a, **k: None)
    monkeypatch.setattr(Lumin.atexit, "register", lambda f: None)
    monkeypatch.setattr(Lumin, "store_digest", lambda *a, **k: None)
    monkeypatch.setattr(Lumin, "generate_digest", lambda *a, **k: {})
    agent = Lumin.create_agent()
    caplog.set_level(logging.WARNING)
    Lumin.send_message(agent, "hello", thread_token="INVALID")
    assert any("Continuity check failed" in r.getMessage() for r in caplog.records)


def test_send_message_invokes_metric_monitor(monkeypatch):
    monkeypatch.setattr(Lumin, "ConversableAgent", DummyAgent)
    Lumin.config_list = [{}]
    monkeypatch.setattr(Lumin, "retrieve_digests", lambda *a, **k: [])
    monkeypatch.setattr(Lumin, "rehydrate_context", lambda *a, **k: None)
    monkeypatch.setattr(Lumin.atexit, "register", lambda f: None)
    monkeypatch.setattr(Lumin, "store_digest", lambda *a, **k: None)
    monkeypatch.setattr(Lumin, "generate_digest", lambda *a, **k: {})
    agent = Lumin.create_agent()

    monkeypatch.setattr(Lumin, "latest_metrics", lambda: {"interpretive_bandwidth": 1.0})
    called = {}

    def fake_check(a, metrics):
        called["m"] = metrics

    monkeypatch.setattr(Lumin, "periodic_metrics_check", fake_check)
    Lumin.send_message(agent, "hi", thread_token="#COMM_PROTO1")
    assert called.get("m") == {"interpretive_bandwidth": 1.0}

