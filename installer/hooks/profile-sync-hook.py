#!/usr/bin/env python3
"""PostToolUse hook: remind user to sync GitHub profile after editing goal/contribution files.

Watches for Edit/Write operations targeting personal/goals/, personal/contributions/,
or personal/_index/oss-contributions.md. Prints a one-time reminder per calendar day
(session dedup via marker file mtime, same pattern as knowledge-staleness-hook.py).
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

# Paths to watch (relative to 3B root)
WATCHED_PATTERNS = [
    "personal/goals/",
    "personal/contributions/",
    "personal/_index/oss-contributions.md",
]

THREE_B_ROOT = os.environ.get("FORGE_3B_ROOT")
if not THREE_B_ROOT:
    # No 3B configured — hook is a no-op.
    sys.exit(0)
SESSION_MARKER = os.path.expanduser("~/.claude/.profile-sync-reminded")


def already_reminded_today():
    """Only remind once per calendar day."""
    try:
        if os.path.exists(SESSION_MARKER):
            mtime = date.fromtimestamp(os.path.getmtime(SESSION_MARKER))
            if mtime == date.today():
                return True
    except (OSError, ValueError):
        pass
    return False


def mark_reminded():
    """Record that we reminded today."""
    try:
        Path(SESSION_MARKER).touch()
    except OSError:
        pass


def is_watched_path(file_path):
    """Check if the file path matches any watched pattern."""
    # Resolve symlinks and normalize
    try:
        real_path = os.path.realpath(file_path)
    except (OSError, ValueError):
        real_path = file_path

    # Get path relative to 3B root
    try:
        rel_path = os.path.relpath(real_path, os.path.realpath(THREE_B_ROOT))
    except ValueError:
        return False

    # Check if it starts with any watched pattern
    for pattern in WATCHED_PATTERNS:
        if rel_path.startswith(pattern):
            return True
    return False


try:
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")

    if not file_path:
        sys.exit(0)

    if not is_watched_path(file_path):
        sys.exit(0)

    if already_reminded_today():
        sys.exit(0)

    mark_reminded()
    print(
        "\n[PROFILE-SYNC] Goal/contribution data changed "
        "— run /sync-profile to update GitHub profile.\n"
    )

except Exception:
    pass  # Never fail — hooks must be non-blocking

sys.exit(0)
