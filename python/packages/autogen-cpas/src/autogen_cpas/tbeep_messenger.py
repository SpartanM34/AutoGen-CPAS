"""Wrapper for T-Beep messenger utilities."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_pkg_path = Path(__file__).resolve().parent.parent / "T-BEEP" / "tbeep_messenger.py"
_spec = spec_from_file_location("tbeep_messenger", _pkg_path)
_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)  # type: ignore

TBeepMessenger = _module.TBeepMessenger
TBeepMessage = _module.TBeepMessage

__all__ = ["TBeepMessenger", "TBeepMessage"]
