from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Iterable, Mapping, Sequence

# Example memory entry stored by ``CpasEnabledAgent``:
# {
#     "id": "<uuid>",
#     "timestamp": "2024-01-01T00:00:00Z",
#     "role": "assistant",
#     "sender": "agent",
#     "recipient": "user",
#     "content": "hello",
#     "metadata": {"confidence": 0.6, "rifg": 0.25, "provenance": ["unit"]}
# }
# Import ConversableAgent from the updated autogen package
from autogen import ConversableAgent
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import StructuredMessage
from autogen_core import CancellationToken, MessageContext, RoutedAgent, message_handler
from autogen_core.memory import MemoryContent, MemoryMimeType

from .models import ChatMessage, CPASMetadata, TBeepMessage
from .protocol import Role, decode, encode


def _bayesian_confidence(prior: float, reliability: float = 0.6) -> float:
    """Return the posterior confidence using a simple Bayesian update."""
    numerator = prior * reliability
    denominator = numerator + (1 - prior) * (1 - reliability)
    return round(numerator / denominator, 3)


def aggregate_bayesian_confidence(scores: Sequence[float]) -> float:
    """Return a cumulative Bayesian confidence across ``scores``."""
    if not scores:
        return 0.5
    posterior = scores[0]
    for score in scores[1:]:
        posterior = _bayesian_confidence(posterior, score)
    return _bayesian_confidence(posterior)


class EchoAgent(RoutedAgent):
    """Minimal agent that echoes user content."""

    def __init__(self) -> None:
        super().__init__("Echo agent")

    @message_handler
    async def handle_message(self, message: ChatMessage, ctx: MessageContext) -> ChatMessage:
        return ChatMessage.simple(Role.ASSISTANT, message.content)


class CpasEnabledAgent(ConversableAgent):
    """Conversable agent that echoes messages with updated CPAS metadata."""

    def __init__(self, name: str = "bot", *args, **kwargs) -> None:
        super().__init__(name, *args, **kwargs)

    def receive(self, message, sender=None, **kwargs):  # type: ignore[override]
        """Validate ``message`` using :func:`decode` before delegating."""
        decode(message)
        return ConversableAgent.receive(self, message, sender=sender, **kwargs)

    def generate_reply(self, messages, sender=None, **kwargs):  # type: ignore[override]
        """Return an echo response with updated confidence and provenance."""
        raw = messages[-1]
        incoming = decode(raw)
        meta = incoming.metadata

        prior_scores: list[float] = []
        memory_attr = getattr(self, "memory", None)
        if memory_attr:
            memories: Iterable[Any] = memory_attr if isinstance(memory_attr, Sequence) else [memory_attr]
            for mem in memories:
                try:
                    result = asyncio.run(mem.query(MemoryContent(content="", mime_type=MemoryMimeType.JSON)))
                except Exception:
                    continue
                for item in result.results:
                    data = item.content
                    if not isinstance(data, Mapping):
                        continue
                    participants = {data.get("sender"), data.get("recipient")}
                    if participants == {self.name, incoming.sender}:
                        m = data.get("metadata", {})
                        if isinstance(m, Mapping) and "confidence" in m:
                            try:
                                prior_scores.append(float(m["confidence"]))
                            except (TypeError, ValueError):
                                pass

        new_confidence = aggregate_bayesian_confidence([meta.confidence, *prior_scores])
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
        if memory_attr:
            entry = MemoryContent(content=reply.to_dict(), mime_type=MemoryMimeType.JSON)
            for mem in memories:
                try:
                    asyncio.run(mem.add(entry))
                except Exception:
                    pass

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
        return Response(
            chat_message=TBeepChatMessage(
                content=decoded.model_dump(mode="python"),
                source=self.name,
            )
        )

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass
