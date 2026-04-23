#!/usr/bin/env python3
"""PreToolUse hook: deny edits to .me.md files.

Files ending in .me.md are human-authored seed documents that must never be
modified by Claude. This hook enforces the "NEVER edit .me.md files" rule
from global CLAUDE.md with a hard deny instead of relying on advisory text.
"""
import json
import sys

try:
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")

    if file_path and file_path.endswith(".me.md"):
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Blocked: {file_path} is a .me.md file "
                    "(human-authored seed document, read-only)"
                ),
            }
        }
        json.dump(result, sys.stdout)

    sys.exit(0)

except Exception:
    sys.exit(0)  # Never block on errors
