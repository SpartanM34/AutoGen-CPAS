import logging
from datetime import datetime
import json

import pytest
from cpas_autogen import (
    continuity_check,
    should_realign,
    latest_metrics,
    metrics_monitor,
    wrap_with_seed_token,
    generate_fingerprint,
)


def test_continuity_check_success():
    seed = {"alignment_profile": "CPAS-Core v1.1"}
    assert continuity_check(seed, "#COMM_PROTO_X")


def test_continuity_check_failure(caplog):
    seed = {"alignment_profile": "wrong"}
    with caplog.at_level(logging.WARNING):
        assert not continuity_check(seed, "BAD")
        assert any("Seed token alignment" in r.getMessage() for r in caplog.records)


def test_should_realign_false():
    m = {"symbolic_density": 1.0, "interpretive_bandwidth": 1.0, "divergence_score": 1.0}
    assert not should_realign(m)


def test_should_realign_true():
    m = {"symbolic_density": 0.1, "interpretive_bandwidth": 1.0, "divergence_score": 1.0}
    assert should_realign(m)


def test_latest_metrics_missing(monkeypatch, tmp_path):
    f = tmp_path / "missing.json"
    monkeypatch.setattr("cpas_autogen.drift_monitor.DRIFT_LOG", f)
    assert latest_metrics() == {}


def test_latest_metrics_malformed(monkeypatch, tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("oops")
    monkeypatch.setattr("cpas_autogen.drift_monitor.DRIFT_LOG", f)
    assert latest_metrics() == {}


def test_latest_metrics_valid(monkeypatch, tmp_path):
    data = [{"avg_7_day": {"interpretive_bandwidth": 0.9, "symbolic_density": 0.8, "divergence_space": 0.7}}]
    f = tmp_path / "log.json"
    f.write_text(json.dumps(data))
    monkeypatch.setattr("cpas_autogen.drift_monitor.DRIFT_LOG", f)
    assert latest_metrics()["divergence_score"] == 0.7


class DummyAgent:
    def __init__(self):
        self.idp_metadata = {"instance_name": "a"}


def test_periodic_metrics_check(monkeypatch):
    calls = []
    def fake_diff(current):
        calls.append(current)
        return {}
    monkeypatch.setattr(metrics_monitor, "diff_report", fake_diff)
    times = [datetime(2024,1,1,0,0,0), datetime(2024,1,1,0,1,0), datetime(2024,1,1,0,31,0)]
    class FakeDT:
        @classmethod
        def utcnow(cls):
            return times.pop(0)
    monkeypatch.setattr(metrics_monitor, "datetime", FakeDT)
    agent = DummyAgent()
    metrics_monitor.periodic_metrics_check(agent, {"x":1})
    metrics_monitor.periodic_metrics_check(agent, {"x":2})
    metrics_monitor.periodic_metrics_check(agent, {"x":3})
    assert len(calls) == 2


def test_wrap_and_fingerprint():
    seed = {"model": "m", "alignment_profile": "a"}
    wrapped = wrap_with_seed_token("hello", seed)
    assert wrapped.startswith("### Seed Instance")
    fp = generate_fingerprint("hello", seed)
    assert set(["fingerprint", "timestamp", "prompt", "model", "alignment_profile"]) <= fp.keys()
    assert len(fp["fingerprint"]) == 64


from cpas_autogen.instance_diff_engine import similarity_score, compare_seed_tokens


def test_similarity_score_all_match():
    t1 = {"alignment_profile": "a", "model": "m", "hash": "h", "extra": 1}
    t2 = {"alignment_profile": "a", "model": "m", "hash": "h", "extra": 1}
    assert similarity_score(t1, t2) == 1.0


def test_similarity_score_partial_match():
    t1 = {"alignment_profile": "a", "model": "m1", "hash": "h"}
    t2 = {"alignment_profile": "a", "model": "m2", "hash": "h"}
    assert similarity_score(t1, t2) == pytest.approx(2 / 3)


def test_compare_seed_tokens_all_match():
    t1 = {"alignment_profile": "a", "model": "m", "hash": "h"}
    t2 = {"alignment_profile": "a", "model": "m", "hash": "h"}
    report = compare_seed_tokens(t1, t2)
    assert all(report[f]["match"] for f in ["alignment_profile", "model", "hash"])
    assert report["similarity"] == 1.0


def test_compare_seed_tokens_partial_match():
    t1 = {"alignment_profile": "a", "model": "m1", "hash": "h"}
    t2 = {"alignment_profile": "a", "model": "m2", "hash": "h2"}
    report = compare_seed_tokens(t1, t2)
    assert report["alignment_profile"]["match"]
    assert not report["model"]["match"]
    assert not report["hash"]["match"]
    assert report["similarity"] == pytest.approx(1 / 3)


def test_seed_token_no_shared_keys() -> None:
    token1 = {"foo": 1}
    token2 = {"bar": 2}
    assert similarity_score(token1, token2) == 0.0
    report = compare_seed_tokens(token1, token2)
    assert report["similarity"] == 0.0


def test_generate_fingerprint_not_equal() -> None:
    """Fingerprints should differ for different prompts."""
    seed = {"model": "m", "alignment_profile": "a"}
    fp1 = generate_fingerprint("hello", seed)
    fp2 = generate_fingerprint("bye", seed)
    assert fp1["fingerprint"] != fp2["fingerprint"]
