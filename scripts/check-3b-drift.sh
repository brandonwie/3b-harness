#!/usr/bin/env bash
# =============================================================================
# 3b-forge Drift Check
# =============================================================================
#
# Compares each entry in plugins/3b/SOURCE-MANIFEST.yaml against the current
# 3B working tree. For every file, reports whether the 3B source has moved
# since the manifest's recorded source_sha.
#
# Exit codes:
#   0 — no drift (every entry's source is at or before its recorded sha)
#   1 — drift detected (at least one file has upstream changes)
#   2 — pre-flight failure (missing env var, missing manifest, etc.)
#
# Requirements:
#   - $FORGE_3B_ROOT must point at a valid git repo
#   - python3 with PyYAML (for manifest parsing). Install via:
#       pip install pyyaml   # or: brew install libyaml && pip install pyyaml
# =============================================================================

set -euo pipefail

# --- Flag parsing -----------------------------------------------------------
VERBOSE=0
for arg in "$@"; do
	case "$arg" in
	--verbose | -v) VERBOSE=1 ;;
	-h | --help)
		sed -n '2,18p' "$0"
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

# --- Pre-flight: 3B working tree clean? -------------------------------------
# Drift check against HEAD is only meaningful when the working tree matches HEAD.
DIRTY_COUNT=$(git -C "$FORGE_3B_ROOT" status --porcelain | wc -l | tr -d ' ')
if [ "$DIRTY_COUNT" != "0" ]; then
	echo "WARNING: \$FORGE_3B_ROOT has $DIRTY_COUNT uncommitted change(s)." >&2
	echo "  Drift detection compares against 3B HEAD; uncommitted changes" >&2
	echo "  are invisible to the check. Consider committing 3B first." >&2
	echo "" >&2
fi

# --- Parse manifest ---------------------------------------------------------
# Emit tab-separated: forge_path<TAB>source_path<TAB>source_sha
ENTRIES=$(
	python3 - <<PY
import sys
try:
    import yaml
except ImportError:
    sys.stderr.write(
        "ERROR: PyYAML is required to parse the drift manifest.\n"
        "  Install: pip install pyyaml\n"
        "  (or: brew install libyaml && pip install pyyaml)\n"
    )
    sys.exit(2)
with open("$MANIFEST") as f:
    data = yaml.safe_load(f)
for entry in data.get("entries", []):
    fp = entry["forge_path"]
    sp = entry["source_path"]
    sha = entry["source_sha"]
    print(f"{fp}\t{sp}\t{sha}")
PY
)

# --- Per-entry drift check --------------------------------------------------
total=0
drifted=0
missing=0
clean=0
drift_report=""

while IFS=$'\t' read -r forge_path source_path source_sha; do
	[ -z "$forge_path" ] && continue
	total=$((total + 1))

	# Sanity: does the source_sha exist in 3B?
	if ! git -C "$FORGE_3B_ROOT" cat-file -e "$source_sha" 2>/dev/null; then
		missing=$((missing + 1))
		drift_report="${drift_report}UNKNOWN-SHA | ${forge_path}
  manifest sha: ${source_sha} (not found in 3B repo)
"
		continue
	fi

	# Does the source file still exist in 3B HEAD?
	if ! git -C "$FORGE_3B_ROOT" cat-file -e "HEAD:${source_path}" 2>/dev/null; then
		missing=$((missing + 1))
		drift_report="${drift_report}SOURCE-GONE | ${forge_path}
  source ${source_path} no longer exists at 3B HEAD
"
		continue
	fi

	# Count commits between source_sha and HEAD that touched this source_path.
	commit_count=$(git -C "$FORGE_3B_ROOT" log --oneline "${source_sha}..HEAD" -- "$source_path" | wc -l | tr -d ' ')

	if [ "$commit_count" != "0" ]; then
		drifted=$((drifted + 1))
		drift_report="${drift_report}DRIFT ($commit_count commits) | ${forge_path}
  source: ${source_path}
  since:  ${source_sha:0:8}
"
		if [ "$VERBOSE" = "1" ]; then
			recent=$(git -C "$FORGE_3B_ROOT" log --oneline "${source_sha}..HEAD" -- "$source_path" | head -5)
			drift_report="${drift_report}  recent commits:
${recent}
"
		fi
	else
		clean=$((clean + 1))
	fi
done <<<"$ENTRIES"

# --- Report -----------------------------------------------------------------
echo "═══════════════════════════════════════════════"
echo " 3b-forge Source Drift Check"
echo "═══════════════════════════════════════════════"
echo " Total entries:   $total"
echo " In sync:         $clean"
echo " Drifted:         $drifted"
if [ "$missing" != "0" ]; then
	echo " Missing sources: $missing"
fi
echo "═══════════════════════════════════════════════"

if [ "$drifted" != "0" ] || [ "$missing" != "0" ]; then
	echo ""
	printf '%s' "$drift_report"
	echo ""
	echo "Next steps:"
	echo "  1. Review the changes in 3B for each drifted file."
	echo "  2. Re-sync the forge file, re-applying scrubs per PUBLIC-PRIVATE-SPLIT.md."
	echo "  3. Update SOURCE-MANIFEST.yaml: set source_sha to the new 3B HEAD."
	echo "  4. Re-run this script to confirm in sync."
	exit 1
fi

echo ""
echo "All forge files are in sync with their 3B sources."
exit 0
