#!/bin/bash

# Unified statusline wrapper - detects profile from CLAUDE_CONFIG_DIR
# WHAT: Single statusline script shared by claude (personal) and cwork
# WHY: DRY principle - avoid maintaining duplicate scripts
#
# Profile structure:
#   ~/.claude      → Personal (default)
#   ~/.claude-work → Work
#
# DATA FLOW:
#   1. Detect profile → determine config dir
#   2. Detect project env (node/python/etc)
#   3. Pass env vars to HUD
#   4. HUD renders everything (project line, bars, custom line)
#
# v0.0.12: Usage data now comes from Claude Code stdin (rate_limits).
#          No more OAuth tokens, keychain reads, or usage cache.

# Detect profile from CLAUDE_CONFIG_DIR (set by cpers/cwork aliases)
# Default to ~/.claude if not set
CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CONFIG_DIR="${CONFIG_DIR/#\~/$HOME}" # Expand tilde

# Detect project type and show appropriate version
ENV_LABEL=""
ENV_VERSION=""

# Check for Python project (pyproject.toml, requirements.txt, .python-version, Pipfile)
if [[ -f "pyproject.toml" || -f "requirements.txt" || -f ".python-version" || -f "Pipfile" ]]; then
	PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2)
	if [[ -n "$PYTHON_VERSION" ]]; then
		ENV_LABEL="py"
		ENV_VERSION="v${PYTHON_VERSION}"
	fi
# Check for Node project (package.json, .nvmrc, .node-version)
elif [[ -f "package.json" || -f ".nvmrc" || -f ".node-version" ]]; then
	NODE_VERSION=$(node -v 2>/dev/null)
	if [[ -n "$NODE_VERSION" ]]; then
		ENV_LABEL="node"
		ENV_VERSION="${NODE_VERSION}"
	fi
# Check for Go project (go.mod)
elif [[ -f "go.mod" ]]; then
	GO_VERSION=$(go version 2>/dev/null | awk '{print $3}' | sed 's/go//')
	if [[ -n "$GO_VERSION" ]]; then
		ENV_LABEL="go"
		ENV_VERSION="v${GO_VERSION}"
	fi
# Check for Rust project (Cargo.toml)
elif [[ -f "Cargo.toml" ]]; then
	RUST_VERSION=$(rustc --version 2>/dev/null | awk '{print $2}')
	if [[ -n "$RUST_VERSION" ]]; then
		ENV_LABEL="rust"
		ENV_VERSION="v${RUST_VERSION}"
	fi
# Check for Ruby project (Gemfile, .ruby-version)
elif [[ -f "Gemfile" || -f ".ruby-version" ]]; then
	RUBY_VERSION=$(ruby --version 2>/dev/null | awk '{print $2}')
	if [[ -n "$RUBY_VERSION" ]]; then
		ENV_LABEL="ruby"
		ENV_VERSION="v${RUBY_VERSION}"
	fi
# Check for Java project (pom.xml, build.gradle)
elif [[ -f "pom.xml" || -f "build.gradle" || -f "build.gradle.kts" ]]; then
	JAVA_VERSION=$(java --version 2>/dev/null | head -1 | awk '{print $2}')
	if [[ -n "$JAVA_VERSION" ]]; then
		ENV_LABEL="java"
		ENV_VERSION="v${JAVA_VERSION}"
	fi
fi

# Run claude-hud with profile-aware settings
# CLAUDE_HUD_CONFIG_DIR: explicit override for config/cache dir
# CLAUDE_HUD_ENV_LABEL/ENV_VERSION: wrapper-detected project env info
#
# Version selection:
#   1. HUD_VERSION (pinned) — pinned version ALWAYS wins when the directory
#      exists. Ignores `.orphaned_at` marker because Claude Code's internal
#      plugin reconcile writes that marker to whichever version it considers
#      non-canonical (i.e. our pinned one, once it upgrades the registry to
#      0.1.0). Treating our explicit pin as authoritative is the whole point.
#      See 2026-04-23 investigation in 3b/.claude/global-claude-setup/
#      claude-hud-patches/UPGRADE-GUIDE.md § Orphan Marker Inversion.
#   2. Fallback — newest non-orphaned directory by mtime (`ls -td`). Used only
#      when the pinned dir is missing (e.g. fresh machine, dir deleted).
HUD_VERSION="0.0.12"
HUD_PATH=""
PINNED_DIR="$HOME/.claude/plugins/cache/claude-hud/claude-hud/${HUD_VERSION}/"
if [[ -d "$PINNED_DIR" ]]; then
	HUD_PATH="$PINNED_DIR"
else
	for dir in $(ls -td "$HOME/.claude/plugins/cache/claude-hud/claude-hud"/*/ 2>/dev/null); do
		if [[ ! -f "${dir}.orphaned_at" ]]; then
			HUD_PATH="$dir"
			break
		fi
	done
fi
if [[ -n "$HUD_PATH" ]]; then
	# Determine config dir and plan label for HUD
	case "$CONFIG_DIR" in
	*claude-work*)
		HUD_CONFIG_DIR="$HOME/.claude-work"
		PLAN_LABEL="Team"
		;;
	*)
		HUD_CONFIG_DIR="$HOME/.claude"
		PLAN_LABEL="Max"
		;;
	esac

	CLAUDE_HUD_CONFIG_DIR="$HUD_CONFIG_DIR" \
		CLAUDE_HUD_PLAN_LABEL="$PLAN_LABEL" \
		CLAUDE_HUD_ENV_LABEL="$ENV_LABEL" \
		CLAUDE_HUD_ENV_VERSION="$ENV_VERSION" \
		"${BUN_BIN:-$(command -v bun)}" "${HUD_PATH}src/index.ts"
fi
