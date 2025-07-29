import json
import types
import ast
import importlib.machinery
from pathlib import Path

import pandas as pd
import pytest

from cpas_autogen.dka_persistence import generate_digest, store_digest

_BASE = Path(__file__).resolve().parents[1]
_tools = _BASE / "tools"

# Provide stubs for heavy dependencies required during import
import sys
sys.modules.setdefault("spacy", types.SimpleNamespace(load=lambda *a, **k: None))
sys.modules.setdefault(
    "sentence_transformers",
    types.SimpleNamespace(
        SentenceTransformer=lambda *a, **k: None,
        util=types.SimpleNamespace(cos_sim=lambda *a, **k: type("obj", (), {"item": lambda: 0})()),
    ),
)
sys.modules.setdefault(
    "sklearn.cluster",
    types.SimpleNamespace(AgglomerativeClustering=lambda *a, **k: None),
)
sys.modules.setdefault(
    "sklearn",
    types.SimpleNamespace(cluster=sys.modules["sklearn.cluster"]),
)

monitor_dkae = importlib.machinery.SourceFileLoader(
    "monitor_dkae", str(_tools / "monitor_dkae.py")
).load_module()
metrics_drift_tracker = importlib.machinery.SourceFileLoader(
    "metrics_drift_tracker", str(_tools / "metrics_drift_tracker.py")
).load_module()


class DummyAgent:
    def __init__(self):
        self.idp_metadata = {"instance_name": "tester"}
        self.last_fingerprint = "abc123"


def test_generate_and_store_digest(tmp_path):
    agent = DummyAgent()
    digest = generate_digest(agent)
    assert digest["participating_instances"] == ["tester"]
    assert digest["seed_fingerprint"] == "abc123"
    path = store_digest(digest, directory=tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["digest_id"] == digest["digest_id"]


def test_monitor_log_results(tmp_path, monkeypatch):
    log_file = tmp_path / "log.json"
    monkeypatch.setattr(monitor_dkae, "LOG_FILE", log_file)
    metrics1 = {"a": 1}
    metrics2 = {"a": 2}
    monitor_dkae.log_results(metrics1)
    assert json.loads(log_file.read_text())[0]["a"] == 1
    monitor_dkae.log_results(metrics2)
    data = json.loads(log_file.read_text())
    assert len(data) == 2
    assert data[1]["a"] == 2


def test_drift_tracker_save_results(tmp_path):
    log = tmp_path / "drift.json"
    r1 = [{"timestamp": "2024-01-01T00:00:00", "flexibility_pulse": 1}]
    metrics_drift_tracker.save_results(r1, log)
    assert json.loads(log.read_text())[0]["flexibility_pulse"] == 1
    r2 = r1 + [{"timestamp": "2024-01-02T00:00:00", "flexibility_pulse": 2}]
    metrics_drift_tracker.save_results(r2, log)
    data = json.loads(log.read_text())
    assert len(data) == 2
    assert data[1]["flexibility_pulse"] == 2


def load_suggest_realign():
    path = Path(__file__).resolve().parents[1] / "ui" / "dashboard.py"
    src = path.read_text()
    tree = ast.parse(src)
    func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "suggest_realign")
    module = ast.Module(body=[func], type_ignores=[])
    code = compile(ast.fix_missing_locations(module), str(path), "exec")
    env = {"pd": pd}
    exec(code, env)
    return env["suggest_realign"]


def test_dashboard_suggest_realign(monkeypatch):
    func = load_suggest_realign()
    calls = []
    stub = types.SimpleNamespace(
        warning=lambda msg: calls.append(("warn", msg)),
        success=lambda msg: calls.append(("success", msg)),
    )
    df = pd.DataFrame([
        {"symbolic_density": 0.1, "interpretive_bandwidth": 0.1, "divergence_score": 0.1}
    ])
    monkeypatch.setitem(func.__globals__, "st", stub)
    monkeypatch.setitem(func.__globals__, "should_realign", lambda m: True)
    func(df)
    assert calls and calls[0][0] == "warn"

    calls.clear()
    monkeypatch.setitem(func.__globals__, "should_realign", lambda m: False)
    func(df)
    assert calls and calls[0][0] == "success"
