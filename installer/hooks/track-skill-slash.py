#!/usr/bin/env python3
"""Track skill invocations from user-typed /slash-commands.

Companion to track-skill-usage.py (PostToolUse). Together they provide
complete coverage:
- This hook: catches /slash-command invocations (CLI pre-expands SKILL.md,
  bypasses the Skill tool entirely)
- track-skill-usage.py: catches programmatic Skill tool calls from Claude

Both write to the same skill-usage.json with a `by_source` field to
distinguish invocation paths.
"""
import json
import os
import re
import subprocess
import sys
from datetime import date

config_dir = os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude"))
USAGE_FILE = os.path.join(config_dir, "skill-usage.json")
SKILLS_DIR = os.path.join(config_dir, "skills")
COMMANDS_DIR = os.path.join(config_dir, "commands")


def get_known_names():
    """Scan skills and commands directories for valid invocation names."""
    names = set()
    # Skills: each subdirectory containing SKILL.md
    if os.path.isdir(SKILLS_DIR):
        for entry in os.listdir(SKILLS_DIR):
            if os.path.isfile(os.path.join(SKILLS_DIR, entry, "SKILL.md")):
                names.add(entry)
    # Commands: .md files (subdir commands use colon notation)
    if os.path.isdir(COMMANDS_DIR):
        for root, _dirs, files in os.walk(COMMANDS_DIR):
            for f in files:
                if f.endswith(".md"):
                    rel = os.path.relpath(os.path.join(root, f), COMMANDS_DIR)
                    name = rel[:-3].replace(os.sep, ":")
                    names.add(name)
    return names


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
    prompt = data.get("prompt", "").strip()

    # Match /skill-name or /skill-name:subcommand at start of message
    match = re.match(r"^/([a-zA-Z0-9_-]+(?::[a-zA-Z0-9_-]+)*)", prompt)
    if not match:
        sys.exit(0)

    full_name = match.group(1)
    base_name = full_name.split(":")[0]
    known = get_known_names()

    # Only track if the base skill/command exists locally
    if base_name not in known:
        sys.exit(0)

    # Load existing usage data
    try:
        with open(USAGE_FILE) as f:
            usage = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        usage = {}

    today = date.today().isoformat()
    project = detect_project()

    if full_name not in usage:
        usage[full_name] = {
            "count": 0,
            "first_used": today,
            "last_used": today,
            "by_project": {},
            "by_date": {},
            "by_source": {},
        }

    entry = usage[full_name]

    # Ensure fields exist for older entries
    for field in ("by_project", "by_date", "by_source"):
        if field not in entry:
            entry[field] = {}

    entry["count"] += 1
    entry["last_used"] = today

    # Track by project
    entry["by_project"][project] = entry["by_project"].get(project, 0) + 1

    # Track by date (keep last 30)
    entry["by_date"][today] = entry["by_date"].get(today, 0) + 1
    dates = sorted(entry["by_date"].keys())
    if len(dates) > 30:
        for old_date in dates[:-30]:
            del entry["by_date"][old_date]

    # Track by source
    entry["by_source"]["slash"] = entry["by_source"].get("slash", 0) + 1

    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f, indent=2, sort_keys=True)
except Exception:
    pass  # Never fail - hooks must be non-blocking
