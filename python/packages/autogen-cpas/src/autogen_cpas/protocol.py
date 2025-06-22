from enum import Enum


class Role(str, Enum):
    """Sender role for a chat message."""

    USER = "user"
    ASSISTANT = "assistant"
