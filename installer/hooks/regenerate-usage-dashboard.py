#!/usr/bin/env python3
"""Regenerate plugin/MCP/skill usage dashboard from tracker JSONs.

Reads:
- ~/.claude/plugin-usage.json (track-plugin-usage.py output)
- ~/.claude/mcp-usage.json (track-mcp-usage.py output)
- ~/.claude/skill-usage.json (track-skill-usage.py + track-skill-slash.py output)
- ~/.claude/settings.json (enabledPlugins inventory source)
- ~/.claude/plugins/installed_plugins.json (plugin metadata + install paths)
- ~/dev/personal/3b/.claude/project-claude/*.mcp.json (project MCP servers)
- ~/dev/personal/3b/.claude/global-claude-setup/skills/ (global skills inventory)
- ~/dev/personal/3b/projects/3b/reference/plugin-mcp-skill-install-log.md
  (install dates for verdict computation)

Writes:
- ~/dev/personal/3b/projects/3b/reference/plugin-mcp-skill-usage.md
  (full-file overwrite, atomic)

Design notes:
- LEFT-JOIN inventory against tracker so zero-usage items surface (the goal)
- days_tracked = today - max(install_date, EARLIEST_CLEAN_DATE)
- Verdict precedence: ACTIVE > INFREQUENT > NEW > STALE > UNUSED >
  LIKELY-UNUSED > UNKNOWN. Demonstrable use trumps maturity gates — data wins
  over chronology. STALE above UNUSED so was-used-now-dormant deserves more
  reflection than never-used.
- Graceful degradation: missing input file = "No data yet" section, no crash
- Atomic write: tempfile + os.replace (mirrors track-*.py pattern)

Invocation modes:
- python3 regenerate-usage-dashboard.py        write dashboard, summary to stderr
- python3 ... --dry-run                        render to stdout, no write
- python3 ... --check-stale                    exit 1 if dashboard >7d old
"""
import argparse
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude")))
THREE_B_PATH = Path(os.path.expanduser("~/dev/personal/3b"))

PLUGIN_USAGE = CONFIG_DIR / "plugin-usage.json"
MCP_USAGE = CONFIG_DIR / "mcp-usage.json"
SKILL_USAGE = CONFIG_DIR / "skill-usage.json"
INSTALLED_PLUGINS = CONFIG_DIR / "plugins" / "installed_plugins.json"
SETTINGS = CONFIG_DIR / "settings.json"

PROJECT_CLAUDE_DIR = THREE_B_PATH / ".claude" / "project-claude"
GLOBAL_SKILLS_DIR = THREE_B_PATH / ".claude" / "skills"

DASHBOARD_PATH = THREE_B_PATH / "projects" / "3b" / "reference" / "plugin-mcp-skill-usage.md"
INSTALL_LOG_PATH = THREE_B_PATH / "projects" / "3b" / "reference" / "plugin-mcp-skill-install-log.md"

EARLIEST_CLEAN_DATE = date(2026, 4, 9)
TARGET_REMOVAL_DAYS = 30
LIKELY_UNUSED_DAYS = 14

ANTHROPIC_HOSTED = (
    "claude_ai_Gmail",
    "claude_ai_Google_Calendar",
    "claude_ai_Google_Drive",
    "claude_ai_Notion",
    "claude_ai_Sentry",
    "claude_ai_Slack",
)

LSP_SUFFIX = "-lsp"


def atomic_write_text(path: Path, content: str) -> None:
    """Write text atomically via mkstemp + os.replace.

    Pattern adapted from track-plugin-usage.py:103-120.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".dashboard-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


def load_json_or_empty(path: Path) -> dict:
    """Return parsed JSON or {} on missing/malformed. Logs warning to stderr."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        sys.stderr.write(f"[dashboard] missing: {path} (rendering empty section)\n")
        return {}
    except json.JSONDecodeError as e:
        sys.stderr.write(f"[dashboard] malformed JSON {path}: {e}\n")
        return {}


def load_enabled_plugins() -> list[str]:
    settings = load_json_or_empty(SETTINGS)
    enabled = settings.get("enabledPlugins", {})
    return [name for name, on in enabled.items() if on]


def load_plugin_metadata() -> dict:
    """Return {plugin_name: {installPath, ...}} for all installed plugins."""
    installed = load_json_or_empty(INSTALLED_PLUGINS)
    out = {}
    for plugin_name, installs in installed.get("plugins", {}).items():
        if isinstance(installs, list) and installs:
            out[plugin_name] = installs[0]
    return out


def load_plugin_servers() -> dict:
    """Return {server_name: plugin_name} for plugin-owned MCP servers.

    Adapted from track-mcp-usage.py:50-109. Returns only the bare server-name
    side of the dual-key map (the dashboard doesn't need plugin_X_Y aliases).
    """
    out = {}
    metadata = load_plugin_metadata()
    for plugin_name, info in metadata.items():
        install_path = info.get("installPath", "")
        if not install_path:
            continue
        mcp_path = Path(install_path) / ".mcp.json"
        if not mcp_path.is_file():
            continue
        try:
            with open(mcp_path) as f:
                mcp_data = json.load(f)
        except Exception:
            continue
        if not isinstance(mcp_data, dict):
            continue
        if isinstance(mcp_data.get("mcpServers"), dict):
            server_map = mcp_data["mcpServers"]
        else:
            server_map = {k: v for k, v in mcp_data.items() if isinstance(v, dict)}
        for server_name in server_map.keys():
            out[server_name] = plugin_name
    return out


def load_project_mcp_servers() -> list[tuple[str, str]]:
    """Return [(server_name, project_config_filename)] for project-level MCP."""
    out = []
    if not PROJECT_CLAUDE_DIR.is_dir():
        return out
    for mcp_file in sorted(PROJECT_CLAUDE_DIR.glob("*.mcp.json")):
        try:
            with open(mcp_file) as f:
                data = json.load(f)
        except Exception:
            continue
        servers = data.get("mcpServers", data) if isinstance(data, dict) else {}
        if not isinstance(servers, dict):
            continue
        for server_name in servers.keys():
            out.append((server_name, mcp_file.stem))
    return out


def load_global_skills() -> list[str]:
    """Return list of global skill directory names (those with SKILL.md)."""
    if not GLOBAL_SKILLS_DIR.is_dir():
        return []
    return sorted(
        d.name for d in GLOBAL_SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file()
    )


def load_plugin_skills(plugin_metadata: dict) -> list[str]:
    """Return list of {plugin}:{skill} for skills contributed by enabled plugins."""
    out = []
    for plugin_name, info in plugin_metadata.items():
        install_path = info.get("installPath", "")
        if not install_path:
            continue
        skills_dir = Path(install_path) / "skills"
        if not skills_dir.is_dir():
            continue
        plugin_slug = plugin_name.split("@", 1)[0]
        for skill_dir in sorted(skills_dir.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file():
                out.append(f"{plugin_slug}:{skill_dir.name}")
    return out


def parse_install_log() -> dict:
    """Parse install-log markdown table, return {(category, name): install_date}.

    Reads only the latest INSTALL or ENABLE row per (category, name) — REMOVE
    and DISABLE rows shift the verdict elsewhere. Returns empty dict if log
    missing.
    """
    install_dates = {}
    if not INSTALL_LOG_PATH.is_file():
        sys.stderr.write(f"[dashboard] missing install-log: {INSTALL_LOG_PATH}\n")
        return install_dates
    row_re = re.compile(
        r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*([^|]+?)\s*\|"
    )
    rows = []
    with open(INSTALL_LOG_PATH) as f:
        for line in f:
            m = row_re.match(line)
            if m:
                rows.append((m.group(1), m.group(2).upper(), m.group(3).lower(), m.group(4).strip()))
    rows.sort(key=lambda r: r[0])
    for log_date, action, category, name in rows:
        key = (category, name)
        if action in ("INSTALL", "ENABLE"):
            try:
                install_dates[key] = datetime.strptime(log_date, "%Y-%m-%d").date()
            except ValueError:
                continue
        elif action in ("REMOVE", "DISABLE"):
            install_dates.pop(key, None)
    return install_dates


def window_count(by_date: dict, today: date, days: int) -> int:
    cutoff = today - timedelta(days=days)
    total = 0
    for date_str, count in by_date.items():
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d > cutoff:
            total += count
    return total


def compute_trend(by_date: dict, today: date) -> str:
    last_7d = window_count(by_date, today, 7)
    prev_7d = window_count(by_date, today - timedelta(days=7), 7)
    if last_7d == 0 and prev_7d == 0:
        return "·"
    if prev_7d == 0:
        return "↑"
    ratio = last_7d / prev_7d
    if ratio >= 1.5:
        return "↑"
    if ratio <= 0.5:
        return "↓"
    return "→"


def compute_verdict(days_tracked: int | None, count_7d: int, count_14d: int,
                    count_30d: int, has_historic: bool) -> str:
    if days_tracked is None:
        return "UNKNOWN"
    # Demonstrable recent use trumps maturity gates — data wins over chronology
    if count_7d >= 3:
        return "ACTIVE"
    if count_30d >= 1:
        return "INFREQUENT"
    # Zero recent use — apply maturity gates
    if days_tracked < LIKELY_UNUSED_DAYS:
        return "NEW"  # too young to declare unused
    if has_historic and count_30d == 0:
        return "STALE"  # was used (pre-window), now dormant
    if days_tracked >= TARGET_REMOVAL_DAYS and count_30d == 0:
        return "UNUSED"  # never really used, removal candidate
    if count_14d == 0:
        return "LIKELY-UNUSED"  # 14d threshold, awaiting 30d
    return "UNKNOWN"


def build_row(name: str, scope: str, tracker_entry: dict | None,
              install_date: date | None, today: date) -> dict:
    by_date = (tracker_entry or {}).get("by_date", {})
    count_7d = window_count(by_date, today, 7)
    count_14d = window_count(by_date, today, 14)
    count_30d = window_count(by_date, today, 30)
    total = (tracker_entry or {}).get("count", 0)
    first_used = (tracker_entry or {}).get("first_used")
    last_used = (tracker_entry or {}).get("last_used")
    trend = compute_trend(by_date, today) if by_date else "·"

    # has_historic: any usage observed before the 30-day window
    has_historic = False
    if first_used:
        try:
            fu = datetime.strptime(first_used, "%Y-%m-%d").date()
            if fu < today - timedelta(days=30):
                has_historic = True
        except ValueError:
            pass

    if install_date is not None:
        effective_start = max(install_date, EARLIEST_CLEAN_DATE)
        days_tracked = (today - effective_start).days
        days_installed = (today - install_date).days
    else:
        days_tracked = None
        days_installed = None

    verdict = compute_verdict(days_tracked, count_7d, count_14d, count_30d, has_historic)

    return {
        "name": name,
        "scope": scope,
        "first_used": first_used or "—",
        "last_used": last_used or "—",
        "trend": trend,
        "count_7d": count_7d,
        "count_30d": count_30d,
        "total": total,
        "days_installed": days_installed if days_installed is not None else "?",
        "verdict": verdict,
    }


def render_table(rows: list[dict]) -> str:
    if not rows:
        return "_(no items)_\n"
    header = "| Name | Scope | First Used | Last Used | Trend | 7d | 30d | Total | Days Installed | Verdict |\n"
    sep = "|------|-------|------------|-----------|:-----:|---:|----:|------:|---------------:|---------|\n"
    body = ""
    for r in rows:
        body += (
            f"| `{r['name']}` | {r['scope']} | {r['first_used']} | {r['last_used']} | "
            f"{r['trend']} | {r['count_7d']} | {r['count_30d']} | {r['total']} | "
            f"{r['days_installed']} | **{r['verdict']}** |\n"
        )
    return header + sep + body


def render_dashboard(today: date) -> str:
    enabled_plugins = load_enabled_plugins()
    plugin_metadata = load_plugin_metadata()
    plugin_servers = load_plugin_servers()
    project_servers = load_project_mcp_servers()
    global_skills = load_global_skills()
    plugin_skills = load_plugin_skills(plugin_metadata)

    plugin_usage = load_json_or_empty(PLUGIN_USAGE)
    mcp_usage = load_json_or_empty(MCP_USAGE)
    skill_usage = load_json_or_empty(SKILL_USAGE)
    install_dates = parse_install_log()

    days_tracked_global = (today - EARLIEST_CLEAN_DATE).days
    is_mature = days_tracked_global >= TARGET_REMOVAL_DAYS
    next_mature_date = EARLIEST_CLEAN_DATE + timedelta(days=TARGET_REMOVAL_DAYS)

    # Build plugin rows (split LSP from non-LSP)
    plugin_rows = []
    lsp_rows = []
    for plugin in sorted(enabled_plugins):
        slug = plugin.split("@", 1)[0]
        row = build_row(
            plugin, "plugin",
            plugin_usage.get(slug),
            install_dates.get(("plugin", plugin)),
            today,
        )
        if slug.endswith(LSP_SUFFIX):
            lsp_rows.append(row)
        else:
            plugin_rows.append(row)

    # MCP rows
    anthropic_rows = []
    for server in ANTHROPIC_HOSTED:
        anthropic_rows.append(build_row(
            server, "anthropic-hosted",
            mcp_usage.get(server),
            install_dates.get(("mcp", server)),
            today,
        ))
    plugin_mcp_rows = []
    for server, owning_plugin in sorted(plugin_servers.items()):
        plugin_mcp_rows.append(build_row(
            f"{server} ← {owning_plugin.split('@',1)[0]}", "plugin-mcp",
            mcp_usage.get(server),
            install_dates.get(("mcp", server)),
            today,
        ))
    project_mcp_rows = []
    for server, project_file in project_servers:
        project_mcp_rows.append(build_row(
            f"{server} ({project_file})", "project-mcp",
            mcp_usage.get(server),
            install_dates.get(("mcp", server)),
            today,
        ))

    # Skill rows
    global_skill_rows = []
    for skill in global_skills:
        global_skill_rows.append(build_row(
            skill, "global",
            skill_usage.get(skill),
            install_dates.get(("skill", skill)),
            today,
        ))
    plugin_skill_rows = []
    for skill in plugin_skills:
        plugin_skill_rows.append(build_row(
            skill, "plugin-skill",
            skill_usage.get(skill),
            install_dates.get(("skill", skill)),
            today,
        ))

    # "Recommended for Removal" pulls UNUSED + STALE from all categories
    all_rows = (
        plugin_rows + lsp_rows
        + anthropic_rows + plugin_mcp_rows + project_mcp_rows
        + global_skill_rows + plugin_skill_rows
    )
    removal_candidates = [r for r in all_rows if r["verdict"] in ("STALE", "UNUSED")]

    # Render
    lines = []
    lines.append("---")
    lines.append("tags: [3b, reference, usage, auto-generated]")
    lines.append(f"created: 2026-04-15")
    lines.append(f"updated: {today.isoformat()}")
    lines.append("status: in-progress")
    lines.append("auto_generated: true")
    lines.append(f"data_window_start: {EARLIEST_CLEAN_DATE.isoformat()}")
    lines.append(f"days_tracked: {days_tracked_global}")
    lines.append("last_refresh_status: ok")
    lines.append("---")
    lines.append("")
    lines.append("# Plugin / MCP / Skill Usage Dashboard")
    lines.append("")
    lines.append(
        f"**Data window**: {EARLIEST_CLEAN_DATE.isoformat()} → {today.isoformat()} "
        f"({days_tracked_global} days). "
        f"**Refreshed**: {today.isoformat()} by `/wrap` Step 5.6."
    )
    lines.append("")
    lines.append(
        "> **Threshold note**: `LIKELY-UNUSED` fires at 14 days of zero usage "
        f"(half of `TARGET_REMOVAL_DAYS={TARGET_REMOVAL_DAYS}`). `UNUSED` fires "
        "at 30 days. **Do not act on `LIKELY-UNUSED` alone** — it's an early "
        "signal, not a removal instruction. Revisit thresholds once ≥30d clean "
        f"data exists (first honest check: {next_mature_date.isoformat()})."
    )
    lines.append("")
    lines.append("**Verdict legend** (precedence top-to-bottom, first match wins):")
    lines.append("")
    lines.append("- `ACTIVE` — ≥3 invocations in past 7 days (demonstrable use)")
    lines.append("- `INFREQUENT` — at least 1 invocation in past 30 days, not active")
    lines.append("- `NEW` — installed <14 days ago AND no recent use; too young to judge")
    lines.append("- `STALE` — historic usage exists, dormant for ≥30 days")
    lines.append("- `UNUSED` — installed ≥30 days, no historic usage, zero in past 30 days → **prune candidate**")
    lines.append("- `LIKELY-UNUSED` — installed ≥14 days, zero in past 14 days → **early signal, watch**")
    lines.append("- `UNKNOWN` — no install-log entry → **backfill install-log**")
    lines.append("")
    lines.append("**Trend column**: `↑` recent 7d > prior 7d × 1.5 | `→` ±50% | `↓` recent 7d < prior 7d × 0.5 | `·` no usage either window.")
    lines.append("")

    # Recommended for Removal
    lines.append("## Recommended for Removal")
    lines.append("")
    if not is_mature:
        lines.append(
            f"_Data window < {TARGET_REMOVAL_DAYS} days "
            f"({days_tracked_global}d as of {today.isoformat()}); "
            f"first honest UNUSED check: {next_mature_date.isoformat()}._"
        )
        lines.append("")
        if removal_candidates:
            lines.append(
                "_(Items below are STALE — historic usage exists, currently "
                "dormant. STALE precedence is independent of data window maturity.)_"
            )
            lines.append("")
            lines.append(render_table(removal_candidates))
    else:
        if removal_candidates:
            lines.append(render_table(removal_candidates))
        else:
            lines.append("_(no removal candidates — all items active or recently used)_")
    lines.append("")

    # Plugins section
    lines.append(f"## Plugins ({len(plugin_rows)} application + {len(lsp_rows)} LSP)")
    lines.append("")
    lines.append("### Application plugins")
    lines.append("")
    lines.append(render_table(plugin_rows))
    lines.append("")
    lines.append("### Language Server plugins (usage not tracker-visible)")
    lines.append("")
    lines.append(
        "_LSP plugins integrate with editor language-server protocol; their "
        "invocations don't go through the Skill/Task/slash hooks that feed "
        "the trackers. Verdict will read NEW/LIKELY-UNUSED/UNUSED based on "
        "data window age — **ignore those verdicts for LSPs**. Keep based on "
        "current language usage in your editor._"
    )
    lines.append("")
    lines.append(render_table(lsp_rows))
    lines.append("")

    # MCP section
    total_mcp = len(anthropic_rows) + len(plugin_mcp_rows) + len(project_mcp_rows)
    lines.append(f"## MCP Servers ({total_mcp} visible)")
    lines.append("")
    lines.append("### Anthropic-Hosted (default disabled — re-enable via `/mcp` when needed)")
    lines.append("")
    lines.append(render_table(anthropic_rows))
    lines.append("")
    lines.append("### Plugin-Provided")
    lines.append("")
    lines.append(render_table(plugin_mcp_rows))
    lines.append("")
    lines.append("### Project-Level (`.mcp.json` files)")
    lines.append("")
    lines.append(render_table(project_mcp_rows))
    lines.append("")

    # Skills section
    total_skills = len(global_skill_rows) + len(plugin_skill_rows)
    lines.append(f"## Skills ({total_skills} total)")
    lines.append("")
    lines.append(f"### Global ({len(global_skill_rows)})")
    lines.append("")
    lines.append(render_table(global_skill_rows))
    lines.append("")
    lines.append(f"### Plugin-Contributed ({len(plugin_skill_rows)})")
    lines.append("")
    lines.append(render_table(plugin_skill_rows))
    lines.append("")

    # Cross-references
    lines.append("---")
    lines.append("")
    lines.append("**Install/remove log**: [plugin-mcp-skill-install-log.md](./plugin-mcp-skill-install-log.md)")
    lines.append("")
    lines.append("**Active task**: [usage-surveillance](../../actives/usage-surveillance/todos.md)")
    lines.append("")
    lines.append("**Regeneration script**: `~/.claude/scripts/regenerate-usage-dashboard.py` (runs in `/wrap` Step 5.6)")
    lines.append("")

    return "\n".join(lines)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true",
                   help="Render to stdout, do not write file")
    p.add_argument("--check-stale", action="store_true",
                   help="Exit 1 if dashboard older than 7 days")
    return p.parse_args()


def main():
    args = parse_args()

    if args.check_stale:
        if not DASHBOARD_PATH.is_file():
            sys.stderr.write(f"[dashboard] file missing: {DASHBOARD_PATH}\n")
            sys.exit(1)
        age_days = (date.today() - date.fromtimestamp(DASHBOARD_PATH.stat().st_mtime)).days
        if age_days > 7:
            sys.stderr.write(f"[dashboard] stale: {age_days} days old\n")
            sys.exit(1)
        sys.stderr.write(f"[dashboard] fresh: {age_days} days old\n")
        sys.exit(0)

    today = date.today()
    try:
        markdown = render_dashboard(today)
    except Exception as e:
        sys.stderr.write(f"[dashboard] render error: {e}\n")
        sys.exit(2)

    if args.dry_run:
        print(markdown)
        return

    try:
        atomic_write_text(DASHBOARD_PATH, markdown)
        sys.stderr.write(f"[dashboard] wrote {DASHBOARD_PATH}\n")
    except Exception as e:
        sys.stderr.write(f"[dashboard] write error: {e}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
