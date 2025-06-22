from __future__ import annotations

import uuid
from datetime import datetime

from autogen.core import ConversableAgent
from autogen_core import MessageContext, RoutedAgent, message_handler

from .models import ChatMessage, CPASMetadata, TBeepMessage
from .protocol import Role, decode, encode


class EchoAgent(RoutedAgent):
    """Minimal agent that echoes user content."""

    def __init__(self) -> None:
        super().__init__("Echo agent")

    @message_handler
    async def handle_message(self, message: ChatMessage, ctx: MessageContext) -> ChatMessage:
        return ChatMessage(role=Role.ASSISTANT, content=message.content)


class CpasEnabledAgent(ConversableAgent):
    """Conversable agent that echoes messages with updated CPAS metadata."""

    def receive(self, message, sender=None, **kwargs):  # type: ignore[override]
        """Validate ``message`` using :func:`decode` before delegating."""
        decode(message)
        return super().receive(message, sender=sender, **kwargs)

    def generate_reply(self, messages, sender=None, **kwargs):  # type: ignore[override]
        """Return an echo response with incremented confidence and provenance."""
        raw = messages[-1]
        incoming = decode(raw)
        meta = incoming.metadata
        new_meta = CPASMetadata(
            confidence=min(meta.confidence + 0.1, 1.0),
            rifg=meta.rifg,
            provenance=[*meta.provenance, self.name],
            notes=meta.notes,
        )
        reply = TBeepMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            role=Role.ASSISTANT,
            sender=self.name,
            recipient=incoming.sender,
            content=incoming.content,
            metadata=new_meta,
        )
        return encode(reply)
