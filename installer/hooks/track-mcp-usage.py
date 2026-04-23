#!/usr/bin/env python3
"""Track MCP server usage from PostToolUse events matching ^mcp__.

Fires on every MCP tool invocation. Classifies each server as:
- plugin:           server declared in an installed plugin's .mcp.json
- project:          server declared in a project-level .mcp.json (fallback)
- anthropic-hosted: server name starts with claude_ai_ (Gmail, Sentry, etc.)

Dual .mcp.json schema handling:
- Wrapped:   {"mcpServers": {"server": {...}}}   (sentry)
- Unwrapped: {"server": {...}}                    (context7, playwright, github, chrome-devtools-mcp)

Output: $CLAUDE_TRACKER_OUTPUT_DIR/mcp-usage.json
        (falls back to $CLAUDE_CONFIG_DIR/mcp-usage.json)

Env vars:
- CLAUDE_TRACKER_DRY_RUN=1 → compute delta, print to stderr, skip write
- CLAUDE_TRACKER_OUTPUT_DIR=<dir> → override output dir
"""
import json
import os
import subprocess
import sys
import tempfile
from datetime import date

CONFIG_DIR = os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude"))
OUTPUT_DIR = os.environ.get("CLAUDE_TRACKER_OUTPUT_DIR", CONFIG_DIR)
USAGE_FILE = os.path.join(OUTPUT_DIR, "mcp-usage.json")
DRY_RUN = os.environ.get("CLAUDE_TRACKER_DRY_RUN") == "1"

MAX_DATES = 30
MAX_TOOLS = 50


def detect_project():
    """Detect current project from git repo name or cwd basename."""
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


def load_plugin_servers():
    """Return {server_name: plugin_name_with_registry} for plugin-owned MCP servers.

    Reads ~/.claude/plugins/installed_plugins.json, then for each plugin tries
    to open {installPath}/.mcp.json. Handles BOTH schemas:
    - Wrapped:   {"mcpServers": {"server": {...}}}   (sentry)
    - Unwrapped: {"server": {...}}                    (context7, playwright, github, chrome-devtools-mcp)

    Each plugin file is wrapped in its own try/except — a single malformed
    .mcp.json must not poison the whole scan.

    Stores dual keys so the `plugin_{plugin}_{server}` tool-name variant
    resolves without post-hoc parsing:
        "sentry"                          -> sentry@claude-plugins-official
        "plugin_sentry_sentry"            -> sentry@claude-plugins-official
    """
    result = {}
    try:
        installed_path = os.path.join(CONFIG_DIR, "plugins", "installed_plugins.json")
        with open(installed_path) as f:
            installed = json.load(f)
    except Exception:
        return result

    for plugin_name, installs in installed.get("plugins", {}).items():
        if not isinstance(installs, list) or not installs:
            continue
        install_path = installs[0].get("installPath", "")
        if not install_path:
            continue
        mcp_path = os.path.join(install_path, ".mcp.json")
        if not os.path.isfile(mcp_path):
            continue
        try:
            with open(mcp_path) as f:
                mcp_data = json.load(f)
        except Exception:
            continue

        if not isinstance(mcp_data, dict):
            continue

        # Dual schema: prefer explicit mcpServers wrapper, else treat root
        # as a server map (filter to dict-valued keys only).
        if isinstance(mcp_data.get("mcpServers"), dict):
            server_map = mcp_data["mcpServers"]
        else:
            server_map = {k: v for k, v in mcp_data.items() if isinstance(v, dict)}

        if not server_map:
            continue

        plugin_slug = plugin_name.split("@", 1)[0]
        for server_name in server_map.keys():
            result[server_name] = plugin_name
            result[f"plugin_{plugin_slug}_{server_name}"] = plugin_name

    return result


def classify(server_part, plugin_servers):
    """Classify an MCP server_part into (scope, owning_plugin).

    server_part is the text between `mcp__` and the first subsequent `__`.
    """
    if server_part.startswith("claude_ai_"):
        return ("anthropic-hosted", None)
    if server_part in plugin_servers:
        return ("plugin", plugin_servers[server_part])
    return ("project", None)


def parse_tool(tool):
    """Return (server_part, full_tool_name) or (None, None) if not an MCP tool.

    Splits on the FIRST `__` after the `mcp__` prefix. Everything left of
    that split is the server_part; everything right is the sub-tool name
    (not separately used, but kept for future extension).
    """
    if not tool.startswith("mcp__"):
        return (None, None)
    rest = tool[len("mcp__"):]
    if "__" not in rest:
        # Degenerate case: `mcp__server` with no sub-tool. Treat whole
        # remainder as the server_part.
        return (rest, tool)
    server_part, _ = rest.split("__", 1)
    return (server_part, tool)


def atomic_write(path, data):
    """Write JSON atomically via mkstemp + os.replace."""
    dir_ = os.path.dirname(path) or "."
    os.makedirs(dir_, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dir_, prefix=".mcp-usage-", suffix=".tmp")
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


def main():
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    server_part, full_tool_name = parse_tool(tool)
    if not server_part:
        sys.exit(0)

    plugin_servers = load_plugin_servers()
    scope, owning_plugin = classify(server_part, plugin_servers)

    today = date.today().isoformat()
    project = detect_project()

    if DRY_RUN:
        sys.stderr.write(
            f"[mcp-tracker dry-run] server={server_part} scope={scope} "
            f"owning={owning_plugin or 'none'} tool={full_tool_name} "
            f"project={project}\n"
        )
        sys.exit(0)

    try:
        with open(USAGE_FILE) as f:
            usage = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        usage = {}

    if server_part not in usage:
        usage[server_part] = {
            "scope": scope,
            "owning_plugin": owning_plugin,
            "count": 0,
            "first_used": today,
            "last_used": today,
            "by_project": {},
            "by_date": {},
            "by_tool": {},
        }

    entry = usage[server_part]

    # Ensure all fields exist (in case an older entry is missing something).
    for field in ("by_project", "by_date", "by_tool"):
        if field not in entry:
            entry[field] = {}
    entry.setdefault("count", 0)
    entry.setdefault("first_used", today)

    # Overwrite scope + ownership on every hit so ownership transitions
    # (e.g., project → plugin) are captured. first_used is preserved.
    entry["scope"] = scope
    entry["owning_plugin"] = owning_plugin

    entry["count"] += 1
    entry["last_used"] = today
    entry["by_project"][project] = entry["by_project"].get(project, 0) + 1
    entry["by_date"][today] = entry["by_date"].get(today, 0) + 1
    entry["by_tool"][full_tool_name] = entry["by_tool"].get(full_tool_name, 0) + 1

    # Trim by_date to the 30 most recent (lexical sort works for ISO dates).
    dates = sorted(entry["by_date"].keys())
    if len(dates) > MAX_DATES:
        for old_date in dates[:-MAX_DATES]:
            del entry["by_date"][old_date]

    # Trim by_tool to the top 50 by count (bias toward active tools).
    if len(entry["by_tool"]) > MAX_TOOLS:
        sorted_tools = sorted(entry["by_tool"].items(), key=lambda x: x[1])
        entry["by_tool"] = dict(sorted_tools[-MAX_TOOLS:])

    atomic_write(USAGE_FILE, usage)


try:
    main()
except Exception:
    pass  # Never fail — hooks must be non-blocking
