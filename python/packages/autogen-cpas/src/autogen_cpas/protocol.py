from __future__ import annotations

import json
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:  # pragma: no cover - used for type hints only
    from .models import TBeepMessage


class Role(str, Enum):
    """Sender role for a chat message."""

    USER = "user"
    ASSISTANT = "assistant"
    AGENT = "agent"
    SYSTEM = "system"


class RIFG(float, Enum):
    """Reflective Inference Fidelity Grade."""

    VERY_LOW = 0.0
    LOW = 0.25
    MEDIUM = 0.5
    HIGH = 0.75
    VERY_HIGH = 1.0


def encode(message: "TBeepMessage") -> Mapping[str, Any]:
    """Return a JSON-compatible mapping representation of ``message``.

    Datetime values are converted to ISO 8601 strings and fields with ``None``
    values are omitted to comply with the JSON schema.
    """

    return message.model_dump(mode="json", exclude_none=True)


def decode(data: Mapping[str, Any] | str) -> "TBeepMessage":
    """Validate ``data`` and return a :class:`TBeepMessage`.

    ``data`` may be a mapping or a JSON string produced by :func:`encode`.
    """

    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError("message must be valid JSON") from exc
    if not isinstance(data, Mapping):
        raise TypeError("message must be a mapping or JSON string")
    from .models import TBeepMessage
    return TBeepMessage.from_dict(dict(data))


__all__ = ["Role", "RIFG", "encode", "decode"]
