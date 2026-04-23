#!/usr/bin/env python3
"""PostToolUse hook: run TypeScript type check after editing .ts/.tsx files.

Only fires when:
  - Edited file has .ts or .tsx extension
  - tsconfig.json exists at the git repo root
  - Cooldown (60s) has elapsed since last check

Surfaces errors via stdout so Claude sees them. Never blocks (exit 0).

Dry-run mode: set CLAUDE_TSC_DRY_RUN=1 to log without running tsc.
"""
import json
import os
import subprocess
import sys
import time

DRY_RUN = os.environ.get("CLAUDE_TSC_DRY_RUN", "1").lower() in (
    "1",
    "true",
    "yes",
)

COOLDOWN_SECONDS = 60
COOLDOWN_FILE = "/tmp/.claude-tsc-last-run"

TS_EXTS = frozenset({".ts", ".tsx"})


def get_git_root(path):
    """Get the git repository root for a path, or None."""
    try:
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def cooldown_elapsed():
    """Check if enough time has passed since last tsc run."""
    try:
        if os.path.exists(COOLDOWN_FILE):
            last_run = os.path.getmtime(COOLDOWN_FILE)
            if time.time() - last_run < COOLDOWN_SECONDS:
                return False
    except Exception:
        pass
    return True


def touch_cooldown():
    """Update the cooldown timestamp."""
    try:
        with open(COOLDOWN_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass


try:
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")

    if not file_path:
        sys.exit(0)

    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in TS_EXTS:
        sys.exit(0)

    # Resolve symlinks for repo detection
    real_file = os.path.realpath(file_path)
    file_dir = os.path.dirname(real_file)
    repo_root = get_git_root(file_dir)

    if not repo_root:
        sys.exit(0)

    # Only run if tsconfig.json exists
    tsconfig = os.path.join(repo_root, "tsconfig.json")
    if not os.path.exists(tsconfig):
        sys.exit(0)

    # Cooldown check
    if not cooldown_elapsed():
        sys.exit(0)

    if DRY_RUN:
        print(
            f"[tsc-hook dry-run] would run: npx tsc --noEmit (repo: {os.path.basename(repo_root)})",
            file=sys.stderr,
        )
        sys.exit(0)

    touch_cooldown()

    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--pretty"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=repo_root,
    )

    if result.returncode != 0 and result.stdout.strip():
        # Surface errors so Claude sees them
        error_lines = result.stdout.strip().split("\n")
        # Limit output to avoid flooding
        if len(error_lines) > 30:
            shown = "\n".join(error_lines[:30])
            print(
                f"[tsc-hook] TypeScript errors detected ({len(error_lines)} lines, showing first 30):\n{shown}",
            )
        else:
            print(
                f"[tsc-hook] TypeScript errors detected:\n{result.stdout.strip()}",
            )

    sys.exit(0)

except Exception:
    sys.exit(0)  # Never block on errors
