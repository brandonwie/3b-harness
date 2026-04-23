#!/usr/bin/env python3
"""Track skill invocation counts for Claude Code.

Enhanced in v1.5 to include project context and session date,
enabling routing table refinement based on actual usage patterns.
"""
import json
import os
import subprocess
import sys
from datetime import date

config_dir = os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude"))
USAGE_FILE = os.path.join(config_dir, "skill-usage.json")


def detect_project():
    """Detect current project from git repo name or cwd."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return os.path.basename(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return os.path.basename(os.getcwd())


try:
    data = json.load(sys.stdin)
    skill = data.get("tool_input", {}).get("skill", "")
    if not skill:
        sys.exit(0)

    try:
        with open(USAGE_FILE) as f:
            usage = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        usage = {}

    today = date.today().isoformat()
    project = detect_project()

    if skill not in usage:
        usage[skill] = {
            "count": 0,
            "first_used": today,
            "last_used": today,
            "by_project": {},
            "by_date": {},
            "by_source": {},
        }

    # Ensure fields exist for entries created before v1.5/v2
    for field in ("by_project", "by_date", "by_source"):
        if field not in usage[skill]:
            usage[skill][field] = {}

    usage[skill]["count"] += 1
    usage[skill]["last_used"] = today

    # Track by project
    usage[skill]["by_project"][project] = usage[skill]["by_project"].get(project, 0) + 1

    # Track by date (keep last 30 dates to avoid unbounded growth)
    usage[skill]["by_date"][today] = usage[skill]["by_date"].get(today, 0) + 1
    dates = sorted(usage[skill]["by_date"].keys())
    if len(dates) > 30:
        for old_date in dates[:-30]:
            del usage[skill]["by_date"][old_date]

    # Track by source (programmatic Skill tool call)
    usage[skill]["by_source"]["tool"] = usage[skill]["by_source"].get("tool", 0) + 1

    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f, indent=2, sort_keys=True)
except Exception:
    pass  # Never fail - hooks must be non-blocking
