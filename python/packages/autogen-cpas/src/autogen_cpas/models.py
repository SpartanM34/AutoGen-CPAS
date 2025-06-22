from pydantic import BaseModel

from .protocol import Role


class ChatMessage(BaseModel):
    """Simple chat message used for tests."""

    role: Role
    content: str
