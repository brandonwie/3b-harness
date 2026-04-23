#!/usr/bin/env python3
"""PreToolUse hook: warn when Write/Edit targets a file outside the CWD repo.

Resolves symlinks before comparing to avoid false positives (e.g., symlinked
settings.json pointing back into the same repo).

Returns "ask" decision when repos differ, allowing the user to proceed or cancel.
Silently allows when: same repo, whitelisted repo, no git repo found, or any
error occurs.
"""
import json
import os
import subprocess
import sys

# Repos that are always allowed for cross-repo writes (basename of repo root).
# Default includes `3b` — the 3B knowledge base, where Claude frequently writes
# buffer, journals, and knowledge entries from any project. Override or extend
# via the SCOPE_WARNING_WHITELIST env var (comma-separated repo basenames).
_default_whitelist = {"3b"}
_env_whitelist = os.environ.get("SCOPE_WARNING_WHITELIST", "")
WHITELISTED_REPOS = _default_whitelist | {
    name.strip() for name in _env_whitelist.split(",") if name.strip()
}


def get_git_root(path):
    """Get the git repository root for a path, or None."""
    try:
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def find_existing_parent(path):
    """Walk up from path until an existing directory is found."""
    check = path
    while not os.path.exists(check) and check != "/":
        check = os.path.dirname(check)
    return check


try:
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")
    cwd = data.get("cwd", "")

    if not file_path or not cwd:
        sys.exit(0)

    # Resolve symlinks on both paths
    real_cwd = os.path.realpath(cwd)
    real_file = os.path.realpath(file_path)

    # For new files (Write), walk up to find existing parent
    existing = find_existing_parent(real_file)
    file_dir = existing if os.path.isdir(existing) else os.path.dirname(existing)

    # Get git repo roots
    cwd_repo = get_git_root(real_cwd)
    file_repo = get_git_root(file_dir)

    # Skip check if either path isn't in a git repo
    if not cwd_repo or not file_repo:
        sys.exit(0)

    # Resolve symlinks on repo roots themselves
    real_cwd_repo = os.path.realpath(cwd_repo)
    real_file_repo = os.path.realpath(file_repo)

    if real_cwd_repo != real_file_repo:
        # Allow writes to whitelisted repos without prompting
        target_repo_name = os.path.basename(real_file_repo)
        if target_repo_name in WHITELISTED_REPOS:
            sys.exit(0)

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    f"Scope warning: editing {file_path} "
                    f"(repo: {os.path.basename(real_file_repo)}) "
                    f"but cwd is in {os.path.basename(real_cwd_repo)}"
                ),
            }
        }
        json.dump(result, sys.stdout)

    sys.exit(0)

except Exception:
    sys.exit(0)  # Never block on errors
