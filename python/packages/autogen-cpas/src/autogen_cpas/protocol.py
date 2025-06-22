from __future__ import annotations

from enum import Enum

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


def encode(message: TBeepMessage) -> dict:
    """Return a dictionary representation of ``message``."""
    return message.to_dict()


def decode(data: dict) -> TBeepMessage:
    """Validate ``data`` and return a :class:`TBeepMessage`."""
    if not isinstance(data, dict):
        raise TypeError("message must be a dictionary")
    return TBeepMessage.from_dict(data)


__all__ = ["Role", "RIFG", "encode", "decode"]
