from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

# Repository root -> docs/examples/dka_digests
ROOT = Path(__file__).resolve().parents[5]
DEFAULT_DIGEST_DIR = ROOT / "docs" / "examples" / "dka_digests"


def generate_digest(agent: Any) -> Dict[str, Any]:
    """Return a simplified DKA digest derived from ``agent`` state."""
    now = datetime.utcnow().isoformat()
    digest = {
        "digest_version": "1.0",
        "digest_id": f"DKA_{uuid.uuid4()}",
        "creation_timestamp": now,
        "last_modified": now,
        "participating_instances": [
            getattr(agent, "idp_metadata", {}).get("instance_name", "unknown")
        ],
        "core_metaphor": {"primary": "", "stability": "stable", "evolution_triggers": []},
        "confidence_gradient": {"overall": 1.0, "components": {}},
        "assumption_tree": {"root_assumption": "", "dependencies": []},
        "evolution_history": [],
        "contested_zones": [],
        "temporal_metadata": {
            "validity_horizon": {},
            "epistemic_half_life": {},
            "invalidation_triggers": [],
        },
        "inter_dka_linkages": [],
        "rehydration_instructions": {
            "priority_concepts": [],
            "required_context": "",
            "initialization_prompts": [],
        },
        "seed_fingerprint": getattr(agent, "last_fingerprint", None),
    }
    return digest


def store_digest(digest: Dict[str, Any], directory: Path = DEFAULT_DIGEST_DIR) -> Path:
    """Persist ``digest`` as a JSON file in ``directory``."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{digest['digest_id']}.json"
    path.write_text(json.dumps(digest, indent=2))
    return path


def retrieve_digests(
    instance_name: str | None = None, directory: Path = DEFAULT_DIGEST_DIR
) -> List[Dict[str, Any]]:
    """Return digests stored in ``directory`` optionally filtered by instance."""
    if not directory.exists():
        return []
    digests = []
    for file in directory.glob("*.json"):
        try:
            data = json.loads(file.read_text())
        except Exception:
            continue
        if instance_name and instance_name not in data.get("participating_instances", []):
            continue
        digests.append(data)
    return digests


def rehydrate_context(agent: Any, digests: Iterable[Dict[str, Any]]) -> None:
    """Attach ``digests`` to ``agent`` for later use."""
    digests = list(digests)
    if digests:
        agent.rehydrated_digests = digests


__all__ = [
    "generate_digest",
    "store_digest",
    "retrieve_digests",
    "rehydrate_context",
    "DEFAULT_DIGEST_DIR",
]
