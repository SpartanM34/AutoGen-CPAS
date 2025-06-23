import json

import pytest
from cpas_autogen import metrics_monitor


def test_load_baseline(tmp_path, monkeypatch):
    data = {"2025": {"x": 1.0}}
    f = tmp_path / "baseline.json"
    f.write_text(json.dumps(data))
    monkeypatch.setattr(metrics_monitor, "BASELINE_FILE", f)
    assert metrics_monitor.load_baseline() == {"x": 1.0}


def test_load_baseline_missing(tmp_path, monkeypatch):
    """load_baseline should return an empty dict when the file is absent."""
    f = tmp_path / "does_not_exist.json"
    monkeypatch.setattr(metrics_monitor, "BASELINE_FILE", f)
    assert metrics_monitor.load_baseline() == {}
    assert metrics_monitor.diff_report({"a": 1.0}) == {"similarity": 0.0}


def test_load_baseline_invalid_json(tmp_path, monkeypatch):
    """load_baseline should handle invalid JSON gracefully."""
    f = tmp_path / "bad.json"
    f.write_text("{invalid json}")
    monkeypatch.setattr(metrics_monitor, "BASELINE_FILE", f)
    assert metrics_monitor.load_baseline() == {}
    assert metrics_monitor.diff_report({"a": 1.0}) == {"similarity": 0.0}


def test_load_baseline_non_dict(tmp_path, monkeypatch):
    """load_baseline should return empty dict for non-dict JSON."""
    f = tmp_path / "list.json"
    f.write_text(json.dumps([1, 2]))
    monkeypatch.setattr(metrics_monitor, "BASELINE_FILE", f)
    assert metrics_monitor.load_baseline() == {}
    assert metrics_monitor.diff_report({"x": 1.0}) == {"similarity": 0.0}


def test_diff_report(monkeypatch):
    monkeypatch.setattr(metrics_monitor, "load_baseline", lambda: {"a": 1.0})
    report = metrics_monitor.diff_report({"a": 1.2})
    assert report["a"]["delta"] == pytest.approx(0.2)
    assert "similarity" in report
