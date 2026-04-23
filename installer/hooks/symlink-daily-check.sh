#!/usr/bin/env bash
# SessionStart hook: daily symlink health check
# Runs check-symlinks.sh at most once per 24 hours.
# Zero context overhead — only prints on failure.
# Throttle file: ~/.claude/.symlink-check-timestamp

THROTTLE_FILE="$HOME/.claude/.symlink-check-timestamp"
THROTTLE_SECONDS=86400 # 24 hours
SCRIPT="$HOME/dev/personal/3b/.claude/skills/check-symlinks/scripts/check-symlinks.sh"

# Skip if script doesn't exist
[ -x "$SCRIPT" ] || exit 0

# Throttle: skip if checked within last 24h
if [ -f "$THROTTLE_FILE" ]; then
	last_check=$(cat "$THROTTLE_FILE" 2>/dev/null || echo 0)
	now=$(date +%s)
	elapsed=$((now - last_check))
	if [ "$elapsed" -lt "$THROTTLE_SECONDS" ]; then
		exit 0
	fi
fi

# Run the check (capture output, suppress if all healthy)
output=$("$SCRIPT" 2>&1)
exit_code=$?

# Update throttle timestamp regardless of result
date +%s >"$THROTTLE_FILE"

# Only print if issues found (exit code 1)
if [ "$exit_code" -ne 0 ]; then
	# Extract just the summary line (ISSUES count)
	summary=$(echo "$output" | grep -E "^(ISSUES|REPLACED|BROKEN|MISSING|WRONG)" | head -5)
	if [ -n "$summary" ]; then
		echo "[SYMLINK-CHECK] Issues detected — run /check-symlinks for details:"
		echo "$summary"
	else
		echo "[SYMLINK-CHECK] Issues detected — run /check-symlinks for full audit"
	fi
fi

exit 0
