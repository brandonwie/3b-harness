#!/usr/bin/env python3
"""Stop hook: triggers post-implementation review when significant code was written.

Reads the accumulated edit state from implementation-tracker-hook.py,
scores the session's implementation significance, and if above threshold,
prints a [POST-IMPLEMENTATION-REVIEW] advisory to stdout.

Claude reads this advisory and spawns an Explore subagent with the review
checklist. The review is report-only — findings are reported with severity
levels, and the user decides what to fix.

Design principles:
  - Advisory pattern: print a tagged advisory to stdout → Claude reads + acts
  - Same Stop hook structure as stop-verification-hook.py (no stdin)
  - Fail-open: any exception → sys.exit(0)
  - Anti-triggers prevent review fatigue (md-only, 3B project, skill dedup)
"""
import glob
import json
import os
import sys
from datetime import date

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Minimum score to trigger review advisory
SCORE_THRESHOLD = 8

# Env var to disable entirely
ENABLED = os.environ.get("CLAUDE_POST_IMPL_REVIEW", "1").lower() not in (
    "0", "false", "no",
)

# Paths
THREE_B_PATH = os.path.expanduser("~/dev/personal/3b")
SKILL_USAGE_PATH = os.path.expanduser("~/.claude/skill-usage.json")
CHECKLIST_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "post-impl-review-checklist.md",
)

# Skills that indicate review was already done this session
REVIEW_SKILLS = {"review-pr", "clean-review", "simplify"}

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

# Points per file type (with caps)
SCORING = {
    "source": {"points": 2, "cap": 20},
    "test": {"points": 1, "cap": 5},
    "config": {"points": 0, "cap": 0},
    "docs": {"points": 0, "cap": 0},
    "other": {"points": 1, "cap": 5},
}

# Bonus for Write operations (new files)
WRITE_BONUS = 2
WRITE_CAP = 10

# Bonus for directory breadth
DIR_BONUS = 1  # per directory beyond the first
DIR_CAP = 5

# Volume bonus
VOLUME_DIVISOR = 5  # 1 point per 5 edit operations
VOLUME_CAP = 10


def score_session(state):
    """Calculate significance score from accumulated edit state."""
    files = state.get("files_edited", [])
    if not files:
        return 0, {}

    # Count unique files by type
    file_types = {}
    write_count = 0
    directories = set()

    for entry in files:
        path = entry.get("path", "")
        ftype = entry.get("type", "other")
        operation = entry.get("operation", "Edit")

        # Track unique files per type
        if path not in file_types:
            file_types[path] = ftype
        if operation == "Write":
            write_count += 1
        if path:
            directories.add(os.path.dirname(path))

    # Calculate score components
    breakdown = {}
    total = 0

    # File type scoring
    type_counts = {}
    for ftype in file_types.values():
        type_counts[ftype] = type_counts.get(ftype, 0) + 1

    for ftype, count in type_counts.items():
        cfg = SCORING.get(ftype, SCORING["other"])
        points = min(count * cfg["points"], cfg["cap"])
        if points > 0:
            total += points
            breakdown[f"{ftype}_files ({count})"] = points

    # Write bonus (new files)
    if write_count > 0:
        write_pts = min(write_count * WRITE_BONUS, WRITE_CAP)
        total += write_pts
        breakdown[f"new_files ({write_count})"] = write_pts

    # Directory breadth
    dir_count = len(directories)
    if dir_count > 1:
        dir_pts = min((dir_count - 1) * DIR_BONUS, DIR_CAP)
        total += dir_pts
        breakdown[f"directories ({dir_count})"] = dir_pts

    # Volume bonus
    total_ops = len(files)
    if total_ops >= VOLUME_DIVISOR:
        vol_pts = min(total_ops // VOLUME_DIVISOR, VOLUME_CAP)
        total += vol_pts
        breakdown[f"edit_volume ({total_ops})"] = vol_pts

    return total, breakdown


# ---------------------------------------------------------------------------
# Anti-triggers
# ---------------------------------------------------------------------------

def is_docs_only(state):
    """Check if only documentation files were edited."""
    files = state.get("files_edited", [])
    return all(f.get("type") == "docs" for f in files)


def is_3b_project():
    """Check if CWD is the 3B knowledge management project."""
    cwd = os.getcwd()
    try:
        real_cwd = os.path.realpath(cwd)
        real_3b = os.path.realpath(THREE_B_PATH)
        return real_cwd == real_3b or real_cwd.startswith(real_3b + "/")
    except Exception:
        return False


def review_skill_invoked_today():
    """Check if a review skill was already invoked today."""
    try:
        if not os.path.exists(SKILL_USAGE_PATH):
            return False
        with open(SKILL_USAGE_PATH, "r") as f:
            usage = json.load(f)
        today = date.today().isoformat()
        for skill_name in REVIEW_SKILLS:
            entries = usage.get(skill_name, [])
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict) and entry.get("date") == today:
                        return True
            elif isinstance(entries, dict):
                if entries.get("lastUsed", "") == today:
                    return True
    except Exception:
        pass
    return False


# ---------------------------------------------------------------------------
# Advisory output
# ---------------------------------------------------------------------------

def load_checklist(project_cwd=None):
    """Load global + project-specific review checklists.

    Global checklist always loads from the companion markdown file.
    If {project_cwd}/.claude/review-checklist.md exists, its contents
    are appended as project-specific checks.
    """
    # Global checklist
    try:
        with open(CHECKLIST_PATH, "r") as f:
            checklist = f.read()
    except OSError:
        checklist = """Review checklist:
1. Error handling — no swallowed exceptions
2. Edge cases — null/undefined, empty collections
3. Type safety — no unguarded `any` or assertions
4. Naming — variables/functions reveal intent
5. Function size — single responsibility, <30 lines
6. Side effects — mutations explicit
7. Test coverage — new public methods tested
8. Security — no hardcoded secrets, input validation"""

    # Project-specific checklist (optional)
    if project_cwd:
        project_checklist_path = os.path.join(
            project_cwd, ".claude", "review-checklist.md"
        )
        try:
            if os.path.isfile(project_checklist_path):
                with open(project_checklist_path, "r") as f:
                    project_checklist = f.read().strip()
                if project_checklist:
                    checklist += (
                        "\n\n## Project-Specific Checks\n\n"
                        + project_checklist
                    )
        except OSError:
            pass

    return checklist


def format_advisory(score, breakdown, state):
    """Format the review advisory for Claude to consume."""
    files = state.get("files_edited", [])

    # Deduplicate file list
    seen = set()
    unique_files = []
    for f in files:
        path = f.get("path", "")
        if path not in seen:
            seen.add(path)
            unique_files.append(f)

    # Build file list for the advisory
    source_files = [f for f in unique_files if f["type"] in ("source", "other")]
    test_files = [f for f in unique_files if f["type"] == "test"]

    project_cwd = state.get("project_cwd")
    checklist = load_checklist(project_cwd)

    lines = [
        "[POST-IMPLEMENTATION-REVIEW]",
        "Implementation review recommended before ending this session.",
        f"Score: {score} (threshold: {SCORE_THRESHOLD})",
        "",
        "Score breakdown:",
    ]

    for label, pts in breakdown.items():
        lines.append(f"  {label}: +{pts}")

    lines.append("")
    lines.append("Files to review:")
    for f in source_files[:15]:  # Cap at 15 to avoid context bloat
        op = "NEW" if f.get("operation") == "Write" else "MOD"
        lines.append(f"  [{op}] {f['path']}")
    if test_files:
        lines.append("Test files:")
        for f in test_files[:5]:
            lines.append(f"  [TST] {f['path']}")

    lines.append("")
    lines.append(
        "INSTRUCTION: Spawn an Explore subagent to review the modified files."
    )
    lines.append("The review is REPORT-ONLY — report findings, do not auto-fix.")
    lines.append("")
    lines.append("Agent(")
    lines.append('  subagent_type: "Explore",')
    lines.append('  name: "impl-reviewer",')
    lines.append('  prompt: "You are an implementation reviewer. Check the '
                 'following files for quality issues.')
    lines.append("")
    lines.append("    FILES TO REVIEW:")
    for f in source_files[:15]:
        lines.append(f"    - {f['path']}")
    lines.append("")
    lines.append("    " + checklist.replace("\n", "\n    "))
    lines.append("")
    lines.append('    For each issue found, report:')
    lines.append('      FILE: {path}')
    lines.append('      LINE: {approximate line range}')
    lines.append('      ISSUE: {checklist category}')
    lines.append('      WHAT: {what the code does wrong}')
    lines.append('      FIX: {specific fix suggestion}')
    lines.append('      SEVERITY: CRITICAL | HIGH | MEDIUM | LOW')
    lines.append("")
    lines.append('    Read each file fully. Only flag issues in CHANGED code.')
    lines.append('    End with a summary count by severity."')
    lines.append(")")
    lines.append("")
    lines.append('To skip this review, say "skip review".')
    lines.append("[/POST-IMPLEMENTATION-REVIEW]")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

try:
    if not ENABLED:
        sys.exit(0)

    # Find the most recent tracker state file
    state_files = glob.glob("/tmp/.claude-impl-tracker-*.json")
    if not state_files:
        sys.exit(0)

    # Use the most recently modified state file
    state_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    state_path = state_files[0]

    with open(state_path, "r") as f:
        state = json.load(f)

    # Check if review was already triggered for this state
    if state.get("review_triggered", False):
        sys.exit(0)

    # Anti-triggers
    if is_docs_only(state):
        sys.exit(0)
    if is_3b_project():
        sys.exit(0)
    if review_skill_invoked_today():
        sys.exit(0)

    # Score the session
    score, breakdown = score_session(state)

    if score < SCORE_THRESHOLD:
        sys.exit(0)

    # Mark as triggered so we don't re-fire
    state["review_triggered"] = True
    try:
        with open(state_path, "w") as f:
            json.dump(state, f)
    except OSError:
        pass

    # Print the advisory
    print(format_advisory(score, breakdown, state))

except Exception:
    sys.exit(0)  # Never block on errors
