from enum import Enum


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
