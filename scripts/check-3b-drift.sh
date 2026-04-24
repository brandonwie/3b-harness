#!/usr/bin/env bash
# =============================================================================
# 3b-forge Drift Check (Wave 3+)
# =============================================================================
#
# Post-flip topology check. Validates that forge's SOURCE-MANIFEST.yaml
# entries are intact on the 3B side and detects integrity problems.
#
# Back-compat: runs cleanly on the pre-flip state (regular files), producing
# only advisory output from Checks C/D. Symlink-oriented checks (A/B/E)
# activate only when scripts/.flip-state.json is present.
#
# Checks:
#   A. Symlink integrity    manifest entry in 3B is -L and target exists     (fail=1)
#   B. Wrong target         readlink does not resolve to computed forge path (fail=1)
#   C. Untracked candidates new Tier-A-looking files in 3B .claude/          (advisory=2)
#   D. Reintroduced paths   forge Tier-A files contain ~/dev/personal/3b/    (advisory=2)
#   E. Plugin-reinstall     entry recorded as symlink is now a regular file  (fail=1)
#
# Exit codes:
#   0 — all critical checks pass (advisories may still print)
#   1 — at least one critical check (A/B/E) failed
#   2 — pre-flight failure (missing env var, manifest not found, etc.)
#       OR only advisory findings (C/D) — script still warns, but returns 2
#       so callers can distinguish clean/advisory/critical.
#
# Requirements:
#   - $FORGE_3B_ROOT must point at a valid git repo
#   - python3 with PyYAML (pip install pyyaml)
#
# Emergency fallback: the pre-Wave-3 drift script is recoverable via
#   git show wave2-backup:scripts/check-3b-drift.sh
# =============================================================================

set -euo pipefail

# --- Flag parsing -----------------------------------------------------------
VERBOSE=0
for arg in "$@"; do
	case "$arg" in
	--verbose | -v) VERBOSE=1 ;;
	-h | --help)
		sed -n '2,33p' "$0"
		exit 0
		;;
	*)
		echo "Unknown flag: $arg" >&2
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

# --- Mode detection ---------------------------------------------------------
# POST_FLIP=1 means .flip-state.json exists → Checks A/B/E active.
# POST_FLIP=0 means pre-flip state → Checks A/B/E skip (regular files expected).
if [ -f "$STATE_FILE" ]; then
	POST_FLIP=1
	MODE_LABEL="post-flip"
else
	POST_FLIP=0
	MODE_LABEL="pre-flip"
fi

# --- Parse manifest ---------------------------------------------------------
# Emit tab-separated: forge_path<TAB>source_path
ENTRIES=$(
	python3 - <<PY
import sys
try:
    import yaml
except ImportError:
    sys.stderr.write(
        "ERROR: PyYAML is required to parse the manifest.\n"
        "  Install: pip install pyyaml\n"
    )
    sys.exit(2)
with open("$MANIFEST") as f:
    data = yaml.safe_load(f)
for entry in data.get("entries", []):
    print(f"{entry['forge_path']}\t{entry['source_path']}")
PY
)

# --- Per-entry checks -------------------------------------------------------
total=0
ok=0
fail_a=0
fail_b=0
fail_e=0
critical_report=""

while IFS=$'\t' read -r forge_path source_path; do
	[ -z "$forge_path" ] && continue
	total=$((total + 1))

	forge_abs="${FORGE_HOME}/${forge_path}"
	source_abs="${FORGE_3B_ROOT}/${source_path}"

	# Check E — plugin-reinstall damage: was recorded as symlink but now regular.
	# Only active in POST_FLIP mode.
	if [ "$POST_FLIP" = "1" ]; then
		if [ -f "$source_abs" ] && [ ! -L "$source_abs" ]; then
			fail_e=$((fail_e + 1))
			critical_report="${critical_report}E. REINSTALL-DAMAGE | ${source_path}
  Expected symlink (per .flip-state.json) but found regular file.
  Likely cause: plugin reinstall or atomic-rename overwrote the symlink.
  Fix: bash scripts/flip-to-forge.sh --rollback && --execute, OR
       manually recreate symlink: ln -s <target> \$FORGE_3B_ROOT/${source_path}
"
			continue
		fi
	fi

	# Check A — symlink integrity (POST_FLIP only).
	if [ "$POST_FLIP" = "1" ]; then
		if [ ! -L "$source_abs" ]; then
			fail_a=$((fail_a + 1))
			critical_report="${critical_report}A. NOT-A-SYMLINK | ${source_path}
  Expected symlink, got: $(stat -f '%HT' "$source_abs" 2>/dev/null || echo 'missing')
"
			continue
		fi
		if [ ! -e "$source_abs" ]; then
			fail_a=$((fail_a + 1))
			critical_report="${critical_report}A. BROKEN-SYMLINK | ${source_path}
  Target does not exist: $(readlink "$source_abs")
"
			continue
		fi

		# Check B — wrong target.
		actual_resolved=$(cd "$(dirname "$source_abs")" && cd "$(dirname "$(readlink "$source_abs")")" && pwd)/$(basename "$(readlink "$source_abs")")
		expected_resolved="$forge_abs"
		if [ "$actual_resolved" != "$expected_resolved" ]; then
			fail_b=$((fail_b + 1))
			critical_report="${critical_report}B. WRONG-TARGET | ${source_path}
  expected: $expected_resolved
  actual:   $actual_resolved
"
			continue
		fi
	fi

	ok=$((ok + 1))
done <<<"$ENTRIES"

# --- Check C: untracked Tier-A candidates in 3B ----------------------------
# Scan 3B .claude/{skills,rules,agents,global-claude-setup/scripts}/ for real
# files not in the manifest whose content contains no Tier-C markers.
advisory_c=0
advisory_c_report=""
MANIFEST_PATHS=$(echo "$ENTRIES" | cut -f2)

SCAN_DIRS=(
	".claude/skills"
	".claude/rules"
	".claude/agents"
	".claude/global-claude-setup/scripts"
)

TIER_C_PATTERN='~/dev/personal/3b/|3b/knowledge|3b/journals|3b/projects/|buffer\.md|ACTIVE-STATUS|project-claude|prompts/.*PROJECT-CONFIG'

for sd in "${SCAN_DIRS[@]}"; do
	scan_root="$FORGE_3B_ROOT/$sd"
	[ -d "$scan_root" ] || continue
	# Real files only (exclude symlinks).
	while IFS= read -r f; do
		rel="${f#$FORGE_3B_ROOT/}"
		# Skip entries already in manifest.
		if echo "$MANIFEST_PATHS" | grep -qxF "$rel"; then
			continue
		fi
		# Tier-A heuristic: no Tier-C marker hits.
		if ! grep -qE "$TIER_C_PATTERN" "$f" 2>/dev/null; then
			advisory_c=$((advisory_c + 1))
			advisory_c_report="${advisory_c_report}  ${rel}
"
		fi
	done < <(find "$scan_root" -type f \( -name '*.md' -o -name '*.py' -o -name '*.sh' \) 2>/dev/null)
done

# --- Check D: reintroduced hardcoded 3B paths in forge Tier-A files --------
# Grep the 18 forge files for ~/dev/personal/3b/ — these should be scrubbed.
advisory_d=0
advisory_d_report=""

while IFS=$'\t' read -r forge_path source_path; do
	[ -z "$forge_path" ] && continue
	forge_abs="${FORGE_HOME}/${forge_path}"
	[ -f "$forge_abs" ] || continue
	if grep -q '~/dev/personal/3b/' "$forge_abs" 2>/dev/null; then
		advisory_d=$((advisory_d + 1))
		hits=$(grep -c '~/dev/personal/3b/' "$forge_abs")
		advisory_d_report="${advisory_d_report}  ${forge_path} (${hits} hit(s))
"
	fi
done <<<"$ENTRIES"

# --- Report -----------------------------------------------------------------
critical_fails=$((fail_a + fail_b + fail_e))
advisories=$((advisory_c + advisory_d))

echo "═══════════════════════════════════════════════"
echo " 3b-forge Drift Check — ${MODE_LABEL}"
echo "═══════════════════════════════════════════════"
echo " Total entries:         $total"
echo " Passed:                $ok"
if [ "$POST_FLIP" = "1" ]; then
	echo " A (symlink integrity): $fail_a fail(s)"
	echo " B (wrong target):      $fail_b fail(s)"
	echo " E (reinstall damage):  $fail_e fail(s)"
fi
echo " C (untracked cands):   $advisory_c advisory"
echo " D (reintroduced refs): $advisory_d advisory"
echo "═══════════════════════════════════════════════"

if [ "$critical_fails" != "0" ]; then
	echo ""
	echo "── Critical findings ──"
	printf '%s' "$critical_report"
fi

if [ "$advisory_c" != "0" ]; then
	echo ""
	echo "── C. Untracked Tier-A candidates ──"
	echo "These files look Tier-A but are not in SOURCE-MANIFEST.yaml."
	echo "Consider adding them to the manifest and migrating to forge:"
	printf '%s' "$advisory_c_report"
fi

if [ "$advisory_d" != "0" ]; then
	echo ""
	echo "── D. Reintroduced hardcoded 3B paths ──"
	echo "Forge Tier-A files that contain ~/dev/personal/3b/ — should be"
	echo "scrubbed (use \$FORGE_3B_ROOT or placeholders):"
	printf '%s' "$advisory_d_report"
fi

if [ "$critical_fails" != "0" ]; then
	exit 1
fi

if [ "$advisories" != "0" ]; then
	echo ""
	echo "Advisories present; no critical failures. Review and groom as needed."
	exit 2
fi

echo ""
echo "All checks pass."
exit 0
