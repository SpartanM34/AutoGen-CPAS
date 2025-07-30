# DKA-E Persistence Workflow

Dynamic Knowledge Anchor – Enhanced (DKA-E) extends CPAS with a persistence layer so agents can recover context between sessions.
Digests capturing the epistemic state are stored as JSON files inside `docs/examples/dka_digests/` and rehydrated when new conversations begin.

## Workflow Overview

1. **Digest Creation** – at the end of a session or when a major update occurs, the agent serializes its DKA-E state to a digest file under `docs/examples/dka_digests/`.
2. **Digest Loading** – on startup, agents scan this directory and load relevant digests to restore continuity.
3. **Integrity Checks** – digests include metadata and hashes so tools can verify provenance before applying them.

### Example Usage

```python
from cpas_autogen.dkae_persistence import save_digest, load_digests

# save current state
save_digest(agent_state, Path("docs/examples/dka_digests"))

# later restore
state = load_digests(Path("docs/examples/dka_digests"))
```

## Monitoring Scripts

Several scripts help track quality of the DKA-E library:

```bash
# Establish baseline metrics
python tools/baseline_metrics.py

# Monitor after edits
python tools/monitor_dkae.py
```

Metrics are logged to `docs/examples/`:

- `monitor_baseline.json` holds the first baseline values.
- `monitor_log.json` appends results on each monitor run.
- `drift_tracker_log.json`, `wonder_index_log.json` and `emergence_log.json` contain additional statistics consumed by the dashboard.

## Git Post-Commit Hook

To run monitoring automatically, create `.git/hooks/post-commit` with:

```bash
#!/bin/sh
python tools/monitor_dkae.py
```

Make it executable using `chmod +x .git/hooks/post-commit`. The hook reverts the last commit if `monitor_dkae.py` detects a regression.
