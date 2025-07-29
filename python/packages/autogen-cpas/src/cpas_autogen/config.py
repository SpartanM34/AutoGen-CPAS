from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "docs" / "examples"
BASELINE_FILE = EXAMPLES_DIR / "baseline_metrics.json"
DRIFT_LOG = EXAMPLES_DIR / "drift_tracker_log.json"
MONITOR_BASELINE = EXAMPLES_DIR / "monitor_baseline.json"
MONITOR_LOG = EXAMPLES_DIR / "monitor_log.json"
EMERGENCE_LOG = EXAMPLES_DIR / "emergence_log.json"
WONDER_INDEX_LOG = EXAMPLES_DIR / "wonder_index_log.json"
__all__ = [
    "REPO_ROOT",
    "EXAMPLES_DIR",
    "BASELINE_FILE",
    "DRIFT_LOG",
    "MONITOR_BASELINE",
    "MONITOR_LOG",
    "EMERGENCE_LOG",
    "WONDER_INDEX_LOG",
]
