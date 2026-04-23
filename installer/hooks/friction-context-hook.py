#!/usr/bin/env python3
"""UserPromptSubmit hook: loads active friction patterns as session context.

Runs once per day (timestamp marker pattern from knowledge-staleness-hook.py).
Reads friction-log.json and surfaces patterns with count >= 2 that are still
accumulating, so Claude is aware of known pitfalls before hitting them again.

Design principles:
  - Same once-per-day pattern as knowledge-staleness-hook.py
  - Regex-based frontmatter parsing (no PyYAML dependency)
  - Fail-open: any exception → sys.exit(0)
  - Zero output if no relevant patterns (no context overhead)
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

# Configuration
FRICTION_LOG_PATH = os.path.expanduser("~/.claude/friction-log.json")
SESSION_MARKER = os.path.expanduser("~/.claude/.friction-context-ts")
MAX_ALERTS = 5
MIN_COUNT = 2  # Minimum occurrences to surface


def already_checked_today():
    """Only run once per session day."""
    try:
        if os.path.exists(SESSION_MARKER):
            mtime = date.fromtimestamp(os.path.getmtime(SESSION_MARKER))
            if mtime == date.today():
                return True
    except (OSError, ValueError):
        pass
    return False


def mark_checked():
    """Record that we ran today."""
    try:
        Path(SESSION_MARKER).touch()
    except OSError:
        pass


def load_friction_patterns():
    """Load friction patterns from the log file."""
    try:
        if not os.path.exists(FRICTION_LOG_PATH):
            return {}
        with open(FRICTION_LOG_PATH, "r") as f:
            data = json.load(f)
        # friction-log.json has patterns as top-level keys (or nested)
        # Handle both flat and nested structures
        if "patterns" in data:
            return data["patterns"]
        # Try treating top-level keys as patterns (skip metadata keys)
        patterns = {}
        skip_keys = {"archive_file", "observations", "metadata", "version"}
        for key, value in data.items():
            if key not in skip_keys and isinstance(value, dict):
                patterns[key] = value
        return patterns
    except (json.JSONDecodeError, OSError):
        return {}


def find_active_patterns(patterns):
    """Find patterns that are accumulating with count >= MIN_COUNT."""
    active = []
    for label, pattern in patterns.items():
        status = pattern.get("status", "")
        count = pattern.get("count", 0)

        if status == "accumulating" and count >= MIN_COUNT:
            active.append({
                "label": label,
                "count": count,
                "last_seen": pattern.get("last_seen", "unknown"),
                "target": pattern.get("target", {}).get("path", ""),
                "severity": _infer_severity(pattern),
            })

    # Sort by count (most frequent first)
    active.sort(key=lambda x: x["count"], reverse=True)
    return active[:MAX_ALERTS]


def _infer_severity(pattern):
    """Infer severity from observations or pattern metadata."""
    # Check if any observation has blocker/critical severity
    observations = pattern.get("observations", [])
    if isinstance(observations, list):
        for obs_id in observations:
            if isinstance(obs_id, dict):
                sev = obs_id.get("severity", "")
                if sev in ("blocker", "critical"):
                    return sev
    # Fall back to pattern-level severity if present
    return pattern.get("severity", "friction")


try:
    # Read hook input (UserPromptSubmit provides user prompt)
    data = json.load(sys.stdin)

    # Only check once per day
    if already_checked_today():
        sys.exit(0)

    patterns = load_friction_patterns()
    mark_checked()

    active = find_active_patterns(patterns)

    if active:
        print(f"\n[FRICTION-ALERT] {len(active)} known friction pattern(s) "
              "active — avoid repeating these mistakes:")
        for p in active:
            severity_tag = f" [{p['severity'].upper()}]" if p["severity"] in (
                "blocker", "critical") else ""
            target = f" → {p['target']}" if p["target"] else ""
            print(f"  - {p['label']} ({p['count']}x, last: "
                  f"{p['last_seen']}){severity_tag}{target}")
        print("  Check friction-log.json for details on each pattern.\n")

except Exception:
    pass  # Never fail — hooks must be non-blocking
