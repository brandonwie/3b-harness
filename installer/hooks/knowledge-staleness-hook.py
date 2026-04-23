#!/usr/bin/env python3
"""Knowledge staleness warning hook for Claude Code.

UserPromptSubmit hook that scans knowledge entries for staleness:
entries with `updated:` dates older than 90 days that have recent
`when_used:` entries (indicating active use of potentially stale knowledge).

Inspired by Vasilopoulos's "context drift detector" (arXiv:2602.20478,
Section 5.2) — simplified for 3B: checks YAML frontmatter dates instead
of cross-repo Git analysis.

Prints a warning listing the top 3 stale-but-active entries.
Only runs once per session (checks a timestamp file to avoid re-running).
"""
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

# Configuration
_forge_3b_root = os.environ.get("FORGE_3B_ROOT")
if not _forge_3b_root:
    # No 3B configured — staleness check is a no-op.
    sys.exit(0)
KNOWLEDGE_DIR = os.path.join(_forge_3b_root, "knowledge")
STALENESS_DAYS = 90
RECENT_USE_DAYS = 60
MAX_WARNINGS = 3
SESSION_MARKER = os.path.expanduser("~/.claude/.staleness-check-ts")


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


def parse_date(date_str):
    """Parse YYYY-MM-DD date string."""
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        parts = date_str.strip().split("-")
        if len(parts) == 3:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        pass
    return None


def extract_frontmatter(filepath):
    """Extract YAML frontmatter fields from a markdown file.

    Simple regex-based extraction — avoids requiring PyYAML dependency.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(4096)  # Only read first 4KB for frontmatter
    except (OSError, UnicodeDecodeError):
        return None

    # Match YAML frontmatter between --- delimiters
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    fm = match.group(1)

    # Extract updated: date
    updated_match = re.search(r"^updated:\s*(.+)$", fm, re.MULTILINE)
    updated = parse_date(updated_match.group(1)) if updated_match else None

    # Extract when_used: dates (look for date: fields within when_used block)
    when_used_dates = []
    in_when_used = False
    for line in fm.split("\n"):
        if re.match(r"^when_used:", line):
            in_when_used = True
            continue
        if in_when_used:
            if re.match(r"^\S", line) and not line.startswith(" "):
                break  # New top-level key
            date_match = re.search(r"date:\s*(.+)", line)
            if date_match:
                d = parse_date(date_match.group(1))
                if d:
                    when_used_dates.append(d)

    return {"updated": updated, "when_used": when_used_dates}


def find_stale_entries():
    """Find knowledge entries that are stale but actively used."""
    today = date.today()
    staleness_threshold = today - timedelta(days=STALENESS_DAYS)
    recent_use_threshold = today - timedelta(days=RECENT_USE_DAYS)

    stale_entries = []

    knowledge_path = Path(KNOWLEDGE_DIR)
    if not knowledge_path.exists():
        return []

    for md_file in knowledge_path.rglob("*.md"):
        # Skip index and category files
        if md_file.name.startswith("_"):
            continue

        fm = extract_frontmatter(str(md_file))
        if not fm or not fm["updated"]:
            continue

        # Check if stale (updated > 90 days ago)
        if fm["updated"] >= staleness_threshold:
            continue

        # Check if actively used (when_used within last 60 days)
        recent_uses = [d for d in fm["when_used"] if d >= recent_use_threshold]
        if not recent_uses:
            continue

        # This entry is stale but actively used
        days_stale = (today - fm["updated"]).days
        last_used = max(recent_uses)
        rel_path = md_file.relative_to(knowledge_path.parent)

        stale_entries.append(
            {
                "path": str(rel_path),
                "days_stale": days_stale,
                "last_used": last_used.isoformat(),
                "use_count": len(recent_uses),
            }
        )

    # Sort by staleness (most stale first)
    stale_entries.sort(key=lambda x: x["days_stale"], reverse=True)
    return stale_entries[:MAX_WARNINGS]


try:
    # Read hook input (UserPromptSubmit provides user_prompt)
    data = json.load(sys.stdin)

    # Only check once per day
    if already_checked_today():
        sys.exit(0)

    stale = find_stale_entries()
    mark_checked()

    if stale:
        print("\n[KNOWLEDGE-STALENESS] Active entries with stale content:")
        for entry in stale:
            print(
                f"  ⚠ {entry['path']} — {entry['days_stale']}d stale, "
                f"last used {entry['last_used']} "
                f"({entry['use_count']} recent uses)"
            )
        print(
            "  Consider updating these entries or running /doc-audit.\n"
        )

except Exception:
    pass  # Never fail — hooks must be non-blocking
