#!/usr/bin/env bash
# 3B Symlink Audit — checks all symlinks from 3B to profiles and project repos
# Compatible with bash 3.2+ (no associative arrays). Path resolution uses
# `realpath` when present (coreutils/macOS brew) and falls back to python3
# so this works on stock macOS without a Homebrew-installed coreutils.
# Exit codes: 0 = all healthy, 1 = issues found

set -eo pipefail

THREE_B="${FORGE_3B_ROOT:?FORGE_3B_ROOT must be set — export it before running}"

# ─── realpath fallback ─────────────────────────────────────────
# Stock macOS bash 3.2 ships without `realpath`; brew-installed
# coreutils provides it but isn't guaranteed. python3 is already
# a project-wide dependency (see installer/README.md), so it is
# the safe fallback.
_realpath() {
	if command -v realpath >/dev/null 2>&1; then
		realpath "$1"
	else
		python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$1"
	fi
}
GLOBAL="$THREE_B/.claude/global-claude-setup"
PC="$THREE_B/.claude/project-claude"
CLAUDE="$HOME/.claude"
WORK="$HOME/.claude-work"

total=0
ok_count=0
issue_count=0
issues=""

# ─── Core check function ───────────────────────────────────────
# Args: $1=symlink_path  $2=expected_target  $3=category  $4=optional
check() {
	local path="$1" expected="$2" category="$3" optional="${4:-}"

	# Skip truly optional links (neither side exists)
	if [ "$optional" = "optional" ] && [ ! -e "$path" ] && [ ! -L "$path" ] && [ ! -e "$expected" ]; then
		return
	fi

	total=$((total + 1))

	# MISSING: path doesn't exist at all
	if [ ! -e "$path" ] && [ ! -L "$path" ]; then
		issue_count=$((issue_count + 1))
		issues="${issues}MISSING|${category}|${path}|${expected}|
"
		return
	fi

	# REPLACED: exists but not a symlink
	if [ ! -L "$path" ]; then
		issue_count=$((issue_count + 1))
		issues="${issues}REPLACED|${category}|${path}|${expected}|
"
		return
	fi

	# It's a symlink — resolve both sides to compare
	local actual expected_resolved
	actual=$(_realpath "$path" 2>/dev/null || echo "UNRESOLVABLE")
	expected_resolved=$(_realpath "$expected" 2>/dev/null || echo "UNRESOLVABLE")

	# BROKEN: symlink can't resolve or target missing
	if [ "$actual" = "UNRESOLVABLE" ] || [ ! -e "$path" ]; then
		local raw
		raw=$(readlink "$path")
		issue_count=$((issue_count + 1))
		issues="${issues}BROKEN|${category}|${path}|${expected}|points to: ${raw}
"
		return
	fi

	# WRONG_TARGET: resolves but to the wrong place
	if [ "$actual" != "$expected_resolved" ]; then
		local raw
		raw=$(readlink "$path")
		issue_count=$((issue_count + 1))
		issues="${issues}WRONG_TARGET|${category}|${path}|${expected}|actual: ${raw}
"
		return
	fi

	# OK
	ok_count=$((ok_count + 1))
}

# ─── Project helper ────────────────────────────────────────────
# Args: $1=sot_name  $2=repo_path  $3=docs_target
check_project() {
	local name="$1" repo="$2" docs_target="$3"

	if [ ! -d "$repo" ]; then
		echo "  SKIP: $name — repo not found ($repo)"
		return
	fi

	# CLAUDE.md
	if [ -f "$PC/$name.md" ]; then
		check "$repo/CLAUDE.md" "$PC/$name.md" "Project:$name"
	fi

	# .mcp.json
	if [ -f "$PC/$name.mcp.json" ]; then
		check "$repo/.mcp.json" "$PC/$name.mcp.json" "Project:$name"
	fi

	# docs/
	if [ -n "$docs_target" ]; then
		check "$repo/docs" "$docs_target" "Docs:$name"
	fi
}

# ═══════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════"
echo " 3B Symlink Audit"
echo "═══════════════════════════════════════════════"
echo ""

# ─── Category A: Personal Profile (~/.claude → 3B) ─────────────
echo "▸ Personal (~/.claude → 3B)"

check "$CLAUDE/settings.json" "$GLOBAL/settings.json" "Personal"
check "$CLAUDE/commands" "$GLOBAL/commands" "Personal"
check "$CLAUDE/CLAUDE.md" "$GLOBAL/templates/CLAUDE.md" "Personal"
check "$CLAUDE/CUSTOMIZATIONS.md" "$GLOBAL/CUSTOMIZATIONS.md" "Personal"
check "$CLAUDE/statusline-wrapper.sh" "$GLOBAL/statusline-wrapper.sh" "Personal"
check "$CLAUDE/claude-hud-patches" "$GLOBAL/claude-hud-patches" "Personal"
check "$CLAUDE/plugins/claude-hud/config.json" "$GLOBAL/plugins/claude-hud/config.json" "Personal"
check "$CLAUDE/task-tracker.json" "$GLOBAL/task-tracker.json" "Personal"
check "$CLAUDE/scripts" "$GLOBAL/scripts" "Personal"
check "$CLAUDE/hooks" "$GLOBAL/hooks" "Personal"
check "$CLAUDE/friction-log.json" "$THREE_B/.claude/friction-log.json" "Personal"
check "$CLAUDE/friction-log-archive.json" "$THREE_B/.claude/friction-log-archive.json" "Personal"
check "$CLAUDE/skills" "$THREE_B/.claude/skills" "Personal"
check "$CLAUDE/RTK.md" "$GLOBAL/RTK.md" "Personal"

# ─── Category B: Work Profile (~/.claude-work → chain) ─────────
echo "▸ Work (~/.claude-work → chain)"

check "$WORK/CLAUDE.md" "$CLAUDE/CLAUDE.md" "Work"
check "$WORK/CUSTOMIZATIONS.md" "$CLAUDE/CUSTOMIZATIONS.md" "Work"
check "$WORK/commands" "$CLAUDE/commands" "Work"
check "$WORK/hooks" "$CLAUDE/hooks" "Work"
check "$WORK/scripts" "$CLAUDE/scripts" "Work"
check "$WORK/claude-hud-patches" "$CLAUDE/claude-hud-patches" "Work"
check "$WORK/statusline-wrapper.sh" "$CLAUDE/statusline-wrapper.sh" "Work"
check "$WORK/task-tracker.json" "$CLAUDE/task-tracker.json" "Work"
check "$WORK/settings.json" "$CLAUDE/settings.json" "Work"
check "$WORK/RTK.md" "$CLAUDE/RTK.md" "Work"
check "$WORK/friction-log.json" "$CLAUDE/friction-log.json" "Work"
check "$WORK/friction-log-archive.json" "$CLAUDE/friction-log-archive.json" "Work"
check "$WORK/plugins/claude-hud/config.json" "$CLAUDE/plugins/claude-hud/config.json" "Work"
check "$WORK/skills" "$CLAUDE/skills" "Work"
check "$WORK/agents" "$CLAUDE/agents" "Work" "optional"
check "$WORK/ide" "$CLAUDE/ide" "Work" "optional"
check "$WORK/settings.local.json" "$GLOBAL/settings.local.work.json" "Work"

# ─── Category C: Project Repos ─────────────────────────────────
# Add your own `check_project` calls below. Each entry follows:
#   check_project "<sot_name>" "<repo_path>" "<docs_target>"
#
# Example:
#   PROJECT_DOCS="$THREE_B/projects/myproject"
#   check_project "myproject" "$HOME/dev/personal/myproject" "$PROJECT_DOCS"
#
# Replace the commented example below with your own repo entries.
echo "▸ Projects (repos → 3B)"

# (example — uncomment and customize for your own repos)
# check_project "myproject" "$HOME/dev/personal/myproject" "$THREE_B/projects/myproject"

# Dotfiles submodule (optional — skipped if $THREE_B/dotfiles doesn't exist)
if [ -L "$HOME/dev/personal/dotfiles" ] || [ -d "$THREE_B/dotfiles" ]; then
	check "$HOME/dev/personal/dotfiles" "$THREE_B/dotfiles" "Dotfiles"
fi

# ─── Report ────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════"
echo " Results: $total checked, $ok_count OK, $issue_count issues"
echo "═══════════════════════════════════════════════"

if [ "$issue_count" -gt 0 ]; then
	echo ""
	echo "$issues" | while IFS='|' read -r status category path expected detail; do
		[ -z "$status" ] && continue
		echo "  $status  [$category]"
		echo "    Path:     $path"
		echo "    Expected: $expected"
		[ -n "$detail" ] && echo "    Detail:   $detail"
		echo ""
	done
	exit 1
else
	echo ""
	echo "All symlinks healthy."
	exit 0
fi
