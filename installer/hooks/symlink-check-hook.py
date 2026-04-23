#!/usr/bin/env python3
"""PostToolUse hook: check for broken symlinks after git commit.

Only fires when:
  - Bash command contains 'git commit' (not just any Bash command)
  - Commit succeeded (exit code 0)
  - Repo contains symlinks (quick find check, maxdepth 2)

Reports broken symlinks via stdout so Claude sees them. Never blocks (exit 0).
"""
import json
import os
import subprocess
import sys


def get_git_root(cwd):
    """Get the git repository root, or None."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=cwd,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


try:
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")

    # Quick exit: only care about git commit commands
    if "git commit" not in command:
        sys.exit(0)

    # Check if commit actually succeeded
    exit_code = data.get("tool_result", {}).get("exitCode")
    if exit_code is None:
        # Try alternate field name
        exit_code = data.get("tool_result", {}).get("exit_code")
    if exit_code is not None and exit_code != 0:
        sys.exit(0)

    cwd = data.get("cwd", os.getcwd())
    repo_root = get_git_root(cwd)
    if not repo_root:
        sys.exit(0)

    # Quick check: does this repo have symlinks? (maxdepth 2 for speed)
    result = subprocess.run(
        ["find", ".", "-maxdepth", "2", "-type", "l", "-not", "-path", "./.git/*"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=repo_root,
    )

    symlinks = [ln.strip() for ln in result.stdout.strip().split("\n") if ln.strip()]
    if not symlinks:
        sys.exit(0)

    # Check each symlink for broken targets
    broken = []
    outside_repo = []
    for link in symlinks:
        full_path = os.path.join(repo_root, link)
        if os.path.islink(full_path):
            target = os.readlink(full_path)
            # Resolve relative to the symlink's directory
            if not os.path.isabs(target):
                target_abs = os.path.normpath(
                    os.path.join(os.path.dirname(full_path), target)
                )
            else:
                target_abs = target

            if not os.path.exists(target_abs):
                broken.append(f"  {link} -> {target} (BROKEN - target missing)")

    if broken:
        print("[symlink-hook] Broken symlinks detected after commit:")
        for b in broken:
            print(b)
        print(
            "\nConsider fixing or removing these symlinks before pushing."
        )

    sys.exit(0)

except Exception:
    sys.exit(0)  # Never block on errors
