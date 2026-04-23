"""Portable defaults for the extracted interview package."""

from __future__ import annotations

import os
from pathlib import Path


def get_default_model() -> str:
    """Return the default model identifier for interview completions."""
    return os.environ.get("INTERVIEW_CODEX_MODEL", "default")


def get_default_state_dir() -> Path:
    """Return the default on-disk location for interview state."""
    override = os.environ.get("INTERVIEW_CODEX_STATE_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".interview-codex" / "data"
