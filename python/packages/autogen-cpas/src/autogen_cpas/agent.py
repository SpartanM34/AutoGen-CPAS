from __future__ import annotations

import uuid
from datetime import datetime

import asyncio
import logging
from typing import Any, Mapping, Sequence

from autogen import ConversableAgent
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import StructuredMessage
from autogen_core import CancellationToken, MessageContext, RoutedAgent, message_handler

from .models import ChatMessage, CPASMetadata, TBeepMessage
from .protocol import Role, decode, encode


def _bayesian_confidence(prior: float, reliability: float = 0.6) -> float:
    """Return the posterior confidence using a simple Bayesian update."""
    numerator = prior * reliability
    denominator = numerator + (1 - prior) * (1 - reliability)
    return round(numerator / denominator, 3)


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
        """Return an echo response with updated confidence and provenance."""
        raw = messages[-1]
        incoming = decode(raw)
        meta = incoming.metadata
        new_confidence = _bayesian_confidence(meta.confidence)
        new_meta = CPASMetadata(
            confidence=new_confidence,
            rifg=meta.rifg,
            provenance=[*meta.provenance, incoming.id],
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


TBeepChatMessage = StructuredMessage[TBeepMessage]


class AsyncCpasAgent(BaseChatAgent):
    """Asynchronous wrapper around :class:`CpasEnabledAgent`."""

    def __init__(self, inner: CpasEnabledAgent) -> None:
        super().__init__(inner.name, description=f"{inner.name} async wrapper")
        self._inner = inner
        logging.info("Wrapping %s with AsyncCpasAgent", inner.name)

    @property
    def produced_message_types(self) -> Sequence[type[TBeepChatMessage]]:
        return (TBeepChatMessage,)

    async def a_receive(self, message: Mapping[str, Any], sender: str | None = None) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._inner.receive, message, sender)

    async def a_generate_reply(
        self, messages: Sequence[Mapping[str, Any]], sender: str | None = None
    ) -> Mapping[str, Any]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._inner.generate_reply, list(messages), sender)

    async def on_messages(
        self, messages: Sequence[TBeepChatMessage], cancellation_token: CancellationToken
    ) -> Response:
        encoded_messages = []
        for msg in messages:
            encoded = encode(msg.content)
            await self.a_receive(encoded, sender=msg.source)
            encoded_messages.append(encoded)
        reply = await self.a_generate_reply(encoded_messages, sender=messages[-1].source)
        decoded = decode(reply)
        return Response(chat_message=TBeepChatMessage(content=decoded, source=self.name))

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass
