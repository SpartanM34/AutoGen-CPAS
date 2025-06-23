from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from .protocol import RIFG, Role


class ChatMessage(BaseModel):
    """Simple chat message used for tests."""

    role: Role
    content: str


class CPASMetadata(BaseModel):
    """Metadata embedded in T-BEEP messages."""

    confidence: float
    rifg: RIFG
    provenance: List[str]
    notes: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("confidence")
    @classmethod
    def _check_precision(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if round(v, 3) != v:
            raise ValueError("confidence must have at most 3 decimal places")
        return v


class TBeepMessage(BaseModel):
    """Structured T-BEEP message with CPAS metadata."""

    id: str
    timestamp: datetime
    role: Role
    sender: str
    recipient: str
    content: str
    metadata: CPASMetadata

    model_config = ConfigDict(extra="forbid")

    def to_dict(self) -> dict:
        """Return the serializable representation."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "TBeepMessage":
        """Create a :class:`TBeepMessage` from a dictionary."""
        return cls.model_validate(data)
