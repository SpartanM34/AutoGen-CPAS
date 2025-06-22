from __future__ import annotations

"""Utilities for constructing T-BEEP messages."""

from datetime import datetime
from typing import Any, Optional
import uuid

from autogen_cpas.models import CPASMetadata, TBeepMessage
from autogen_cpas.protocol import RIFG, Role


class TBeepMessenger:
    """Helper for creating :class:`TBeepMessage` objects."""

    def __init__(self, instance_name: str, **metadata_defaults: Any) -> None:
        self.instance_name = instance_name
        self.metadata_defaults = {
            "confidence": 0.5,
            "rifg": RIFG.LOW,
            "provenance": [instance_name],
        }
        self.metadata_defaults.update(metadata_defaults)
        self.message_history: list[TBeepMessage] = []

    def create_message(
        self,
        *,
        role: Role,
        recipient: str,
        content: str,
        metadata: Optional[CPASMetadata] = None,
        message_id: Optional[str] = None,
    ) -> TBeepMessage:
        """Return a new :class:`TBeepMessage` with defaults applied."""
        meta = metadata or CPASMetadata(**self.metadata_defaults)
        msg = TBeepMessage(
            id=message_id or str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            role=role,
            sender=self.instance_name,
            recipient=recipient,
            content=content,
            metadata=meta,
        )
        self.message_history.append(msg)
        return msg


__all__ = ["TBeepMessenger", "TBeepMessage"]
