#!/usr/bin/env python3
"""Track plugin usage from Skill, Task, and slash command invocations.

Companion to track-skill-usage.py/track-skill-slash.py. Mirrors their pattern
but credits the PLUGIN (colon-namespace prefix) rather than the individual
skill/command. Only namespaced resources are counted — bare names are
user-authored and ignored. Also ignored: slash commands whose prefix is a
user-authored subdirectory (e.g., /foo:bar when ~/.claude/commands/foo/ exists).

Hook registration (in settings.json):
- PostToolUse ^Skill$ -> `track-plugin-usage.py skill`
- PostToolUse ^Task$  -> `track-plugin-usage.py agent`
- UserPromptSubmit    -> `track-plugin-usage.py slash`

Output: $CLAUDE_TRACKER_OUTPUT_DIR/plugin-usage.json
        (falls back to $CLAUDE_CONFIG_DIR/plugin-usage.json)

Env vars:
- CLAUDE_TRACKER_DRY_RUN=1      -> compute delta, print to stderr, skip write
- CLAUDE_TRACKER_OUTPUT_DIR=<d> -> override output dir

Silent failure: the entire main flow is wrapped in try/except so a tracker
error can never block a Claude Code tool call. Exit code is always 0.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date

CONFIG_DIR = os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude"))
OUTPUT_DIR = os.environ.get("CLAUDE_TRACKER_OUTPUT_DIR", CONFIG_DIR)
USAGE_FILE = os.path.join(OUTPUT_DIR, "plugin-usage.json")
DRY_RUN = os.environ.get("CLAUDE_TRACKER_DRY_RUN") == "1"

SLASH_RE = re.compile(r"^/([a-zA-Z0-9_-]+(?::[a-zA-Z0-9_-]+)*)")

# Directories under CLAUDE_CONFIG_DIR where a top-level folder name claims a
# namespace for user-authored content. If any of these exist for a given
# prefix, we do NOT credit a plugin.
USER_NAMESPACE_PARENTS = ("commands", "skills", "agents")


def detect_project():
    """Detect current project from git repo name or cwd basename."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return os.path.basename(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return os.path.basename(os.getcwd())


def is_user_authored_prefix(prefix):
    """Return True if `prefix` is a user-authored subdirectory under any of
    commands/, skills/, or agents/ in CLAUDE_CONFIG_DIR. Such prefixes must
    not be credited as plugins — they collide with the colon-notation used
    by track-skill-slash.py for nested user content."""
    for parent in USER_NAMESPACE_PARENTS:
        candidate = os.path.join(CONFIG_DIR, parent, prefix)
        if os.path.isdir(candidate):
            return True
    return False


def extract_plugin(mode, data):
    """Return the plugin prefix to credit, or None if this event should be
    ignored. `mode` is one of 'skill', 'agent', 'slash'."""
    if mode == "skill":
        name = data.get("tool_input", {}).get("skill", "") or ""
        if ":" not in name:
            return None
        return name.split(":", 1)[0]

    if mode == "agent":
        name = data.get("tool_input", {}).get("subagent_type", "") or ""
        if ":" not in name:
            return None
        return name.split(":", 1)[0]

    if mode == "slash":
        prompt = (data.get("prompt", "") or "").strip()
        match = SLASH_RE.match(prompt)
        if not match:
            return None
        full_name = match.group(1)
        if ":" not in full_name:
            return None
        prefix = full_name.split(":", 1)[0]
        if is_user_authored_prefix(prefix):
            return None
        return prefix

    return None


def atomic_write(path, data):
    """Write JSON atomically: write to a tempfile in the same directory,
    then os.replace() onto the target. Guarantees readers never see a
    half-written file."""
    dir_ = os.path.dirname(path) or "."
    os.makedirs(dir_, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dir_, prefix=".usage-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


def load_usage():
    try:
        with open(USAGE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def update_entry(usage, plugin, source, project, today):
    """Apply the +1 delta for this invocation to the usage dict."""
    if plugin not in usage:
        usage[plugin] = {
            "count": 0,
            "first_used": today,
            "last_used": today,
            "by_project": {},
            "by_date": {},
            "by_source": {},
        }

    entry = usage[plugin]

    # Backfill missing fields for forward-compatibility.
    for field in ("by_project", "by_date", "by_source"):
        if field not in entry:
            entry[field] = {}
    if "first_used" not in entry:
        entry["first_used"] = today

    entry["count"] = entry.get("count", 0) + 1
    entry["last_used"] = today
    entry["by_project"][project] = entry["by_project"].get(project, 0) + 1
    entry["by_date"][today] = entry["by_date"].get(today, 0) + 1

    # Prune by_date to the most recent 30 entries (lexical = chronological
    # for YYYY-MM-DD).
    dates = sorted(entry["by_date"].keys())
    if len(dates) > 30:
        for old in dates[:-30]:
            del entry["by_date"][old]

    entry["by_source"][source] = entry["by_source"].get(source, 0) + 1


def main():
    if len(sys.argv) < 2:
        sys.exit(0)
    mode = sys.argv[1]
    if mode not in ("skill", "agent", "slash"):
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    plugin = extract_plugin(mode, data)
    if not plugin:
        sys.exit(0)

    project = detect_project()
    today = date.today().isoformat()

    if DRY_RUN:
        sys.stderr.write(
            f"[plugin-tracker dry-run] plugin={plugin} source={mode} "
            f"project={project}\n"
        )
        sys.exit(0)

    usage = load_usage()
    update_entry(usage, plugin, mode, project, today)
    atomic_write(USAGE_FILE, usage)


try:
    main()
except Exception:
    pass  # Never fail - hooks must be non-blocking
sys.exit(0)
