#!/usr/bin/env bash
# =============================================================================
# 3b-forge Wave 3 Symlink Flip
# =============================================================================
#
# Flips the 18 Wave 2 manifest entries in the 3B repo from real files to
# relative symlinks pointing into this forge repo's plugins/3b/ (or
# installer/hooks/) tree. After flip, forge is the Single Source of Truth for
# those entries; 3B consumes via symlink.
#
# Modes (exclusive):
#   --dry-run   (default) Print planned actions only. No filesystem changes.
#   --execute            Perform the flip. Writes .flip-state.json alongside
#                        this script for rollback reproducibility.
#   --rollback           Read .flip-state.json and restore each entry from
#                        the recorded baseline SHA via `git checkout`.
#   --help, -h           Show header comment.
#
# Exit codes:
#   0 — success (dry-run planned cleanly, or execute/rollback completed)
#   1 — operation failed (aborted mid-run; filesystem may be partially changed
#       if --execute, consult .flip-state.json or rerun with --rollback)
#   2 — pre-flight failure (missing env var, dirty tree, manifest not found,
#       unknown flag, etc.). No filesystem changes made.
#
# Requirements:
#   - $FORGE_3B_ROOT must point at a clean 3B git repo.
#   - python3 with PyYAML (same dep as check-3b-drift.sh).
#   - forge repo's plugins/3b/ + installer/hooks/ files must exist.
#
# Safety:
#   - Hard allowlist: script refuses any path outside the 18-entry manifest.
#   - 3B working tree must be clean (no uncommitted changes).
#   - Each entry must currently be a real file (not already a symlink).
#   - Each forge target must exist before symlinking.
#   - Baseline SHA captured before any write; stored in .flip-state.json.
# =============================================================================

set -euo pipefail

# --- Flag parsing -----------------------------------------------------------
MODE="dry-run"
for arg in "$@"; do
	case "$arg" in
	--dry-run) MODE="dry-run" ;;
	--execute) MODE="execute" ;;
	--rollback) MODE="rollback" ;;
	-h | --help)
		sed -n '2,37p' "$0"
		exit 0
		;;
	*)
		echo "Unknown flag: $arg" >&2
		echo "Usage: $0 [--dry-run|--execute|--rollback|--help]" >&2
		exit 2
		;;
	esac
done

# --- Resolve paths ----------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORGE_HOME="$(cd "${SCRIPT_DIR}/.." && pwd)"
MANIFEST="${FORGE_HOME}/plugins/3b/SOURCE-MANIFEST.yaml"
STATE_FILE="${SCRIPT_DIR}/.flip-state.json"

if [ -z "${FORGE_3B_ROOT:-}" ]; then
	echo "ERROR: FORGE_3B_ROOT must be set." >&2
	echo "  Example: export FORGE_3B_ROOT=/path/to/your/3b" >&2
	exit 2
fi

if ! git -C "$FORGE_3B_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
	echo "ERROR: \$FORGE_3B_ROOT ($FORGE_3B_ROOT) is not a git repo." >&2
	exit 2
fi

if [ ! -f "$MANIFEST" ]; then
	echo "ERROR: manifest not found at $MANIFEST" >&2
	exit 2
fi

# --- Rollback mode (branches off early) -------------------------------------
if [ "$MODE" = "rollback" ]; then
	if [ ! -f "$STATE_FILE" ]; then
		echo "ERROR: no flip state at $STATE_FILE; nothing to roll back." >&2
		exit 2
	fi

	BASELINE_SHA=$(python3 -c "import json; print(json.load(open('$STATE_FILE'))['baseline_sha'])")
	if [ -z "$BASELINE_SHA" ]; then
		echo "ERROR: .flip-state.json missing baseline_sha." >&2
		exit 2
	fi

	if ! git -C "$FORGE_3B_ROOT" cat-file -e "$BASELINE_SHA" 2>/dev/null; then
		echo "ERROR: baseline SHA $BASELINE_SHA not found in \$FORGE_3B_ROOT." >&2
		echo "  Has the 3B repo been re-cloned or garbage-collected?" >&2
		exit 2
	fi

	echo "Rollback mode. Baseline: $BASELINE_SHA"
	echo ""

	# Env-var + quoted heredoc prevents shell-into-python interpolation
	# hazards when paths contain single quotes or other special characters.
	ENTRIES=$(
		STATE_FILE="$STATE_FILE" python3 - <<'PY'
import json
import os
with open(os.environ["STATE_FILE"]) as f:
    data = json.load(f)
for e in data["entries"]:
    print(e["source_path"])
PY
	)

	restored=0
	failed=0
	while IFS= read -r source_path; do
		[ -z "$source_path" ] && continue
		if git -C "$FORGE_3B_ROOT" checkout "$BASELINE_SHA" -- "$source_path" 2>/dev/null; then
			echo "  restored: $source_path"
			restored=$((restored + 1))
		else
			echo "  FAILED:   $source_path" >&2
			failed=$((failed + 1))
		fi
	done <<<"$ENTRIES"

	echo ""
	echo "Restored $restored entr(ies); $failed failure(s)."
	if [ "$failed" != "0" ]; then
		exit 1
	fi

	# Archive state file so check-3b-drift.sh reverts to pre-flip mode.
	# Without this, the drift checker reads the stale state file and reports
	# all 18 entries as A. NOT-A-SYMLINK after a successful rollback.
	ARCHIVE="${STATE_FILE}.rolled-back-$(date -u +%Y%m%dT%H%M%SZ)"
	mv "$STATE_FILE" "$ARCHIVE"
	echo "Archived state file → $ARCHIVE"
	echo "Rollback complete. Review 'git -C \$FORGE_3B_ROOT status' and commit."
	exit 0
fi

# --- Pre-flight: 3B tree clean ---------------------------------------------
# Dirty tree is fatal for --execute (rollback can't restore uncommitted work)
# but only a warning for --dry-run (planning is read-only).
DIRTY_COUNT=$(git -C "$FORGE_3B_ROOT" status --porcelain | wc -l | tr -d ' ')
if [ "$DIRTY_COUNT" != "0" ]; then
	if [ "$MODE" = "execute" ]; then
		echo "ERROR: \$FORGE_3B_ROOT has $DIRTY_COUNT uncommitted change(s)." >&2
		echo "  --execute records a baseline SHA for rollback; uncommitted" >&2
		echo "  changes would not be restorable. Commit or stash first." >&2
		exit 2
	else
		echo "WARNING: \$FORGE_3B_ROOT has $DIRTY_COUNT uncommitted change(s)." >&2
		echo "  --execute will require a clean tree; plan below is advisory." >&2
		echo "" >&2
	fi
fi

BASELINE_SHA=$(git -C "$FORGE_3B_ROOT" rev-parse HEAD)

# --- Parse manifest ---------------------------------------------------------
# Emit tab-separated: forge_path<TAB>source_path
ENTRIES=$(
	MANIFEST="$MANIFEST" python3 - <<'PY'
import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "ERROR: PyYAML is required to parse the manifest.\n"
        "  Install: pip install pyyaml\n"
        "  (or: brew install libyaml && pip install pyyaml)\n"
    )
    sys.exit(2)
with open(os.environ["MANIFEST"]) as f:
    data = yaml.safe_load(f)
for entry in data.get("entries", []):
    print(f"{entry['forge_path']}\t{entry['source_path']}")
PY
)

# --- Plan phase: validate + compute relative targets ------------------------
# Build a plan array: lines of
#   source_abs<TAB>forge_abs<TAB>relative_target
PLAN=""
total=0
errors=0

REAL_FORGE_HOME=$(HOME_ABS="$FORGE_HOME" python3 -c 'import os; print(os.path.realpath(os.environ["HOME_ABS"]))')
REAL_3B_ROOT=$(ROOT_ABS="$FORGE_3B_ROOT" python3 -c 'import os; print(os.path.realpath(os.environ["ROOT_ABS"]))')

while IFS=$'\t' read -r forge_path source_path; do
	[ -z "$forge_path" ] && continue
	total=$((total + 1))

	forge_abs="${FORGE_HOME}/${forge_path}"
	source_abs="${FORGE_3B_ROOT}/${source_path}"

	# Path-safety: reject manifest entries whose realpath escapes the
	# intended repo roots. Prevents rm/ln -s from operating on arbitrary
	# files if a manifest entry contains `../` segments.
	real_forge=$(FORGE_ABS="$forge_abs" python3 -c 'import os; print(os.path.realpath(os.environ["FORGE_ABS"]))')
	real_source=$(SOURCE_ABS="$source_abs" python3 -c 'import os; print(os.path.realpath(os.environ["SOURCE_ABS"]))')
	if [[ "$real_forge" != "$REAL_FORGE_HOME"/* ]]; then
		echo "  UNSAFE-PATH: $forge_path escapes FORGE_HOME" >&2
		errors=$((errors + 1))
		continue
	fi
	if [[ "$real_source" != "$REAL_3B_ROOT"/* ]]; then
		echo "  UNSAFE-PATH: $source_path escapes FORGE_3B_ROOT" >&2
		errors=$((errors + 1))
		continue
	fi

	if [ ! -f "$forge_abs" ]; then
		echo "  MISSING-FORGE-TARGET: $forge_path" >&2
		errors=$((errors + 1))
		continue
	fi

	if [ -L "$source_abs" ]; then
		echo "  ALREADY-SYMLINK: $source_path" >&2
		errors=$((errors + 1))
		continue
	fi

	if [ ! -f "$source_abs" ]; then
		echo "  MISSING-3B-SOURCE: $source_path" >&2
		errors=$((errors + 1))
		continue
	fi

	# Compute relative target: from dir-of-source to forge_abs.
	# Env-var passing keeps paths out of shell-interpolated Python source.
	rel_target=$(FORGE_ABS="$forge_abs" SOURCE_ABS="$source_abs" python3 -c '
import os
print(os.path.relpath(os.environ["FORGE_ABS"], os.path.dirname(os.environ["SOURCE_ABS"])))
')

	PLAN="${PLAN}${source_abs}	${forge_abs}	${rel_target}
"
done <<<"$ENTRIES"

echo "═══════════════════════════════════════════════"
echo " 3b-forge Wave 3 Symlink Flip — ${MODE}"
echo "═══════════════════════════════════════════════"
echo " Baseline SHA:  $BASELINE_SHA"
echo " Total entries: $total"
echo " Plan errors:   $errors"
echo "═══════════════════════════════════════════════"

if [ "$errors" != "0" ]; then
	echo ""
	echo "ABORTED: $errors precondition failure(s). No changes made."
	exit 2
fi

# --- Dry-run prints plan only -----------------------------------------------
if [ "$MODE" = "dry-run" ]; then
	echo ""
	echo "Planned actions:"
	while IFS=$'\t' read -r source_abs forge_abs rel_target; do
		[ -z "$source_abs" ] && continue
		echo "  ${source_abs#"$FORGE_3B_ROOT"/}"
		echo "    → $rel_target"
	done <<<"$PLAN"
	echo ""
	echo "No changes made. Re-run with --execute to apply."
	exit 0
fi

# --- Execute phase ----------------------------------------------------------
# MODE=execute reaches here. Perform flip + emit .flip-state.json.

if [ -f "$STATE_FILE" ]; then
	echo "ERROR: $STATE_FILE already exists." >&2
	echo "  A prior flip is recorded. Roll back with --rollback first, or" >&2
	echo "  move the file aside if you are intentionally re-flipping." >&2
	exit 2
fi

# ── Write .flip-state.json BEFORE the flip loop. ────────────────────────────
# The plan is already fully validated at this point; the state file is the
# rollback contract. Writing it first guarantees rollback availability even
# if the flip loop aborts mid-way (disk full, permission error, signal, etc.).
# Pass $PLAN via tempfile to avoid shell-into-python string-interpolation
# fragility on paths containing special characters.
PLAN_FILE=$(mktemp -t flip-plan.XXXXXX)
trap 'rm -f "$PLAN_FILE"' EXIT
printf '%s' "$PLAN" >"$PLAN_FILE"

BASELINE_SHA="$BASELINE_SHA" \
	FORGE_HOME="$FORGE_HOME" \
	FORGE_3B_ROOT="$FORGE_3B_ROOT" \
	STATE_FILE="$STATE_FILE" \
	PLAN_FILE="$PLAN_FILE" \
	python3 - <<'PY'
import datetime
import json
import os

state = {
    "baseline_sha": os.environ["BASELINE_SHA"],
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "forge_home": os.environ["FORGE_HOME"],
    "forge_3b_root": os.environ["FORGE_3B_ROOT"],
    "entries": [],
}
with open(os.environ["PLAN_FILE"]) as f:
    for line in f.read().strip().splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        source_abs, forge_abs, rel_target = parts
        state["entries"].append({
            "source_path": os.path.relpath(source_abs, os.environ["FORGE_3B_ROOT"]),
            "forge_path": os.path.relpath(forge_abs, os.environ["FORGE_HOME"]),
            "relative_target": rel_target,
            "original_mode": "regular-file",
        })
with open(os.environ["STATE_FILE"], "w") as f:
    json.dump(state, f, indent=2)
    f.write("\n")
PY

# ── Perform the flip. ───────────────────────────────────────────────────────
# If this loop aborts mid-way, .flip-state.json already exists and a
# subsequent --rollback will restore all 18 entries (git restores files that
# were never flipped just as cleanly as ones that were).
flipped=0
while IFS=$'\t' read -r source_abs forge_abs rel_target; do
	[ -z "$source_abs" ] && continue
	rm "$source_abs"
	ln -s "$rel_target" "$source_abs"
	flipped=$((flipped + 1))
done <<<"$PLAN"

echo ""
echo "Flipped $flipped entr(ies)."
echo "State recorded: $STATE_FILE"
echo ""
echo "Next steps (DO NOT commit symlinks until verified):"
echo "  1. cd \$FORGE_3B_ROOT"
echo "  2. git status  # confirm 18 paths show mode change regular → symlink"
echo "  3. Spot-check: cat a few paths, confirm forge content returned"
echo "  4. git add <paths> && git commit (Wave 3 3B-side PR)"
echo "  5. Copy $STATE_FILE into the PR body for reproducibility."
echo ""
echo "Rollback (safe before OR after commit — git tracks the baseline tree):"
echo "  bash $0 --rollback"
exit 0
