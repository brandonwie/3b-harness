#!/usr/bin/env python3
"""PostToolUse hook: silently tracks Edit/Write operations for post-implementation review.

Accumulates file edit metadata into a session-scoped state file at /tmp/.
The companion Stop hook (post-implementation-review-hook.py) reads this state
to decide whether to trigger a review advisory.

Design principles:
  - Zero stdout output (no context overhead on every edit)
  - <10ms per invocation (JSON file I/O only, no subprocesses)
  - Fail-open: any exception → sys.exit(0)
  - Session-isolated via hash of (cwd, date)
  - 24h cleanup of stale state files
"""
import hashlib
import json
import os
import sys
from datetime import date, datetime

# ---------------------------------------------------------------------------
# File classification
# ---------------------------------------------------------------------------

SOURCE_EXTS = frozenset({
    ".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java", ".kt",
    ".swift", ".rb", ".php", ".c", ".cpp", ".h", ".hpp", ".cs", ".scala",
    ".svelte", ".vue",
})

TEST_PATTERNS = frozenset({
    ".spec.ts", ".test.ts", ".spec.js", ".test.js", ".spec.tsx", ".test.tsx",
    "_test.go", "_test.py",
})

CONFIG_EXTS = frozenset({
    ".json", ".yaml", ".yml", ".toml", ".env", ".tf", ".tfvars",
})

DOC_EXTS = frozenset({".md", ".txt", ".rst", ".adoc"})


def classify_file(file_path):
    """Classify a file as source, test, config, docs, or other."""
    basename = os.path.basename(file_path).lower()
    ext = os.path.splitext(file_path)[1].lower()

    # Test detection (check before source — test files have source extensions)
    for pattern in TEST_PATTERNS:
        if basename.endswith(pattern):
            return "test"
    if basename.startswith("test_") and ext == ".py":
        return "test"
    if "/test/" in file_path.lower() or "/__tests__/" in file_path.lower():
        return "test"

    # Source code
    if ext in SOURCE_EXTS:
        return "source"

    # Config files
    if ext in CONFIG_EXTS:
        return "config"
    if basename in ("dockerfile", "docker-compose.yml", "docker-compose.yaml",
                    "makefile", ".gitignore", ".eslintrc", ".prettierrc"):
        return "config"

    # Documentation
    if ext in DOC_EXTS:
        return "docs"

    # Anything else treated as "other" (scored as source for safety)
    return "other"


# ---------------------------------------------------------------------------
# State file management
# ---------------------------------------------------------------------------

def get_state_path():
    """Generate a session-scoped state file path."""
    cwd = os.getcwd()
    today = date.today().isoformat()
    key = f"{cwd}:{today}"
    session_hash = hashlib.md5(key.encode()).hexdigest()[:12]
    return f"/tmp/.claude-impl-tracker-{session_hash}.json"


def read_state(path):
    """Read existing state or return empty state."""
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {
        "session_start": datetime.now().isoformat(),
        "project_cwd": os.getcwd(),
        "files_edited": [],
        "review_triggered": False,
    }


def write_state(path, state):
    """Atomic write: write to temp file then rename."""
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w") as f:
            json.dump(state, f)
        os.replace(tmp_path, path)
    except OSError:
        pass


def cleanup_stale_files():
    """Remove state files older than 24 hours."""
    try:
        now = datetime.now().timestamp()
        for name in os.listdir("/tmp"):
            if name.startswith(".claude-impl-tracker-") and name.endswith(".json"):
                path = f"/tmp/{name}"
                if now - os.path.getmtime(path) > 86400:
                    os.unlink(path)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

try:
    data = json.load(sys.stdin)

    # Extract file path from tool input
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    # Determine operation type (Edit vs Write = existing vs new)
    tool_name = data.get("tool_name", "")
    operation = "Write" if tool_name == "Write" else "Edit"

    # Classify the file
    file_type = classify_file(file_path)

    # Read/update/write state
    state_path = get_state_path()
    state = read_state(state_path)

    state["files_edited"].append({
        "path": file_path,
        "type": file_type,
        "operation": operation,
        "timestamp": datetime.now().isoformat(),
    })

    write_state(state_path, state)

    # Periodic cleanup (only on first edit of session)
    if len(state["files_edited"]) == 1:
        cleanup_stale_files()

    sys.exit(0)

except Exception:
    sys.exit(0)  # Never block on errors
