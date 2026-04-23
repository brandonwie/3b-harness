#!/usr/bin/env python3
"""PostToolUse hook: auto-format files after Write/Edit.

Detects the project's formatter based on config files at the git repo root:
  - pyproject.toml  → ruff format (for .py files)
  - package.json    → npx prettier --write (for web/md/yaml files)
  - *.tf files      → terraform fmt
  - *.sh files      → shfmt -w (if shfmt available)
  - Fallback        → no formatting

Dry-run mode: set CLAUDE_FORMATTER_DRY_RUN=1 to log without formatting.
"""
import json
import os
import subprocess
import sys

DRY_RUN = os.environ.get("CLAUDE_FORMATTER_DRY_RUN", "1").lower() in (
    "1",
    "true",
    "yes",
)

# File extensions handled by each formatter
PRETTIER_EXTS = frozenset(
    {
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".json",
        ".md",
        ".yaml",
        ".yml",
        ".css",
        ".scss",
        ".html",
        ".svelte",
    }
)
RUFF_EXTS = frozenset({".py"})
TERRAFORM_EXTS = frozenset({".tf", ".tfvars"})
SHFMT_EXTS = frozenset({".sh", ".bash", ".zsh"})


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


def has_command(cmd):
    """Check if a command is available on PATH."""
    try:
        result = subprocess.run(
            ["which", cmd], capture_output=True, text=True, timeout=3
        )
        return result.returncode == 0
    except Exception:
        return False


def detect_formatter(repo_root, file_ext):
    """Detect formatter based on repo config and file extension.

    Returns (formatter_name, command_list) or (None, []).
    """
    if not repo_root:
        return None, []

    # Python files → ruff (if pyproject.toml exists)
    if file_ext in RUFF_EXTS:
        if os.path.exists(os.path.join(repo_root, "pyproject.toml")):
            return "ruff", ["ruff", "format", "--quiet"]
        return None, []

    # Terraform files → terraform fmt (no config check needed)
    if file_ext in TERRAFORM_EXTS:
        return "terraform", ["terraform", "fmt"]

    # Web/markdown/yaml files → prettier (if package.json exists)
    if file_ext in PRETTIER_EXTS:
        if os.path.exists(os.path.join(repo_root, "package.json")):
            return "prettier", ["npx", "prettier", "--write"]
        return None, []

    # Shell files → shfmt (if available)
    if file_ext in SHFMT_EXTS:
        if has_command("shfmt"):
            return "shfmt", ["shfmt", "-w"]
        return None, []

    return None, []


try:
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")

    if not file_path or not os.path.isfile(file_path):
        sys.exit(0)

    file_ext = os.path.splitext(file_path)[1].lower()
    if not file_ext:
        sys.exit(0)

    # Resolve symlinks for repo detection
    real_file = os.path.realpath(file_path)
    file_dir = os.path.dirname(real_file)
    repo_root = get_git_root(file_dir)

    formatter_name, cmd = detect_formatter(repo_root, file_ext)
    if not formatter_name:
        sys.exit(0)

    full_cmd = cmd + [file_path]

    if DRY_RUN:
        print(
            f"[formatter-hook dry-run] {formatter_name}: {' '.join(full_cmd)}",
            file=sys.stderr,
        )
        sys.exit(0)

    subprocess.run(full_cmd, capture_output=True, timeout=30, cwd=repo_root)
    sys.exit(0)

except Exception:
    sys.exit(0)  # Never block on errors
