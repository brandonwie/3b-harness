#!/bin/bash
# =============================================================================
# Global ~/.claude Setup Script
# =============================================================================
#
# ⚠️ WAVE 1 STATUS — NOT READY FOR PUBLIC EXECUTION.
# This script still hardcodes `${HOME}/dev/personal/3b` as the source tree.
# Wave 2 will parameterize the path so external installs work.
# Until then: read this script as reference only; do not run.
#
# =============================================================================
# This script sets up the global Claude Code configuration from 3B.
# It is idempotent - safe to run multiple times.
#
# What it does:
#   Personal profile (~/.claude → 3B):
#     1. Initializes dotfiles submodule and creates symlink
#     2. Creates ~/.claude directories
#     3. Symlinks settings.json from 3B
#     4. Symlinks commands/ from 3B
#     5. Symlinks CLAUDE.md from 3B
#     6. Symlinks CUSTOMIZATIONS.md from 3B
#     7. Symlinks statusline-wrapper.sh from 3B
#     8. Symlinks claude-hud-patches/ from 3B
#     9. Symlinks plugins/claude-hud/config.json from 3B
#    10. Symlinks task-tracker.json from 3B
#    11. Symlinks scripts/ from 3B (hook scripts)
#    12. Symlinks hooks/ from 3B
#    13. Symlinks friction-log files from 3B
#    14. Symlinks skills/ from 3B
#    15. Symlinks RTK.md from 3B
#
#   Work profile (~/.claude-work → ~/.claude chain):
#    16. Creates ~/.claude-work directories
#    17. Chains shared config through ~/.claude
#    18. Symlinks settings.local.json → work override in 3B
#
# Prerequisites:
#   - 3B repository cloned to ~/dev/personal/3b
#
# Usage:
#   ./setup.sh
#
# =============================================================================

set -e # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
THREE_B="${HOME}/dev/personal/3b"
GLOBAL_SETUP="${THREE_B}/.claude/global-claude-setup"
CLAUDE_DIR="${HOME}/.claude"
CLAUDE_WORK_DIR="${HOME}/.claude-work"

# Helper functions
info() {
	echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
	echo -e "${GREEN}[✓]${NC} $1"
}

warning() {
	echo -e "${YELLOW}[!]${NC} $1"
}

error() {
	echo -e "${RED}[✗]${NC} $1"
	exit 1
}

# Create symlink helper (handles existing files/symlinks)
create_symlink() {
	local source="$1"
	local target="$2"
	local name="$3"

	# Remove existing symlink or backup existing file/directory
	if [ -L "$target" ]; then
		rm "$target"
	elif [ -e "$target" ]; then
		mv "$target" "${target}.backup.$(date +%Y%m%d%H%M%S)"
		warning "Backed up existing $name"
	fi

	ln -sf "$source" "$target"
	success "$name symlinked"
}

# Check prerequisites
check_prerequisites() {
	if [ ! -d "$THREE_B" ]; then
		error "3B repository not found at $THREE_B"
	fi

	if [ ! -d "$GLOBAL_SETUP" ]; then
		error "Global setup directory not found at $GLOBAL_SETUP"
	fi

	success "Prerequisites verified"
}

# Setup dotfiles submodule
setup_dotfiles_submodule() {
	info "Checking dotfiles submodule..."

	# Initialize submodule if not already done
	if [ ! -f "${THREE_B}/dotfiles/bootstrap.sh" ]; then
		info "Initializing dotfiles submodule..."
		git -C "${THREE_B}" submodule update --init --recursive
		success "Dotfiles submodule initialized"
	else
		success "Dotfiles submodule already initialized"
	fi

	# Create symlink at ~/dev/personal/dotfiles
	local DOTFILES_LINK="${HOME}/dev/personal/dotfiles"
	local DOTFILES_TARGET="${THREE_B}/dotfiles"

	if [ -L "$DOTFILES_LINK" ]; then
		success "Dotfiles symlink already exists"
	elif [ -d "$DOTFILES_LINK" ]; then
		warning "~/dev/personal/dotfiles exists as directory"
		warning "MANUAL ACTION REQUIRED:"
		warning "  rm -rf ~/dev/personal/dotfiles"
		warning "  ln -s ${DOTFILES_TARGET} ${DOTFILES_LINK}"
	else
		mkdir -p "${HOME}/dev/personal"
		ln -s "$DOTFILES_TARGET" "$DOTFILES_LINK"
		success "Created dotfiles symlink"
	fi
}

# Step 1: Create ~/.claude directories
create_directories() {
	info "Creating ~/.claude directories..."

	mkdir -p "${CLAUDE_DIR}/plugins/claude-hud"

	success "Directories created"
}

# Step 2: Setup settings.json
setup_settings() {
	info "Setting up settings.json..."

	# Check if settings.json exists in 3B (the real one, gitignored)
	if [ -f "${GLOBAL_SETUP}/settings.json" ]; then
		create_symlink "${GLOBAL_SETUP}/settings.json" "${CLAUDE_DIR}/settings.json" "settings.json"
	elif [ ! -f "${CLAUDE_DIR}/settings.json" ]; then
		# No real settings.json in 3B yet, copy template
		cp "${GLOBAL_SETUP}/templates/settings.example.json" "${CLAUDE_DIR}/settings.json"
		warning "Created settings.json from template (not symlinked)"
		warning "MANUAL ACTION REQUIRED: Edit ~/.claude/settings.json"
		warning "  - Replace YOUR_GITHUB_TOKEN_HERE with your actual GitHub token"
		warning "  - Then move to 3B: mv ~/.claude/settings.json ${GLOBAL_SETUP}/settings.json"
		warning "  - Re-run this script to create symlink"
	else
		success "settings.json already exists (skipped)"
	fi
}

# Step 3: Symlink commands directory
setup_commands() {
	info "Setting up commands symlink..."
	create_symlink "${GLOBAL_SETUP}/commands" "${CLAUDE_DIR}/commands" "commands/"
}

# Step 4: Symlink CLAUDE.md
setup_claude_md() {
	info "Setting up CLAUDE.md symlink..."
	create_symlink "${GLOBAL_SETUP}/templates/CLAUDE.md" "${CLAUDE_DIR}/CLAUDE.md" "CLAUDE.md"
}

# Step 5: Symlink CUSTOMIZATIONS.md
setup_customizations() {
	info "Setting up CUSTOMIZATIONS.md symlink..."
	create_symlink "${GLOBAL_SETUP}/CUSTOMIZATIONS.md" "${CLAUDE_DIR}/CUSTOMIZATIONS.md" "CUSTOMIZATIONS.md"
}

# Step 6: Symlink statusline-wrapper.sh
setup_statusline() {
	info "Setting up statusline-wrapper.sh symlink..."
	create_symlink "${GLOBAL_SETUP}/statusline-wrapper.sh" "${CLAUDE_DIR}/statusline-wrapper.sh" "statusline-wrapper.sh"
}

# Step 7: Symlink claude-hud-patches/
setup_hud_patches() {
	info "Setting up claude-hud-patches symlink..."
	create_symlink "${GLOBAL_SETUP}/claude-hud-patches" "${CLAUDE_DIR}/claude-hud-patches" "claude-hud-patches/"
}

# Step 8: Symlink plugins/claude-hud/config.json
setup_hud_config() {
	info "Setting up HUD config symlink..."
	create_symlink "${GLOBAL_SETUP}/plugins/claude-hud/config.json" "${CLAUDE_DIR}/plugins/claude-hud/config.json" "plugins/claude-hud/config.json"
}

# Step 9: Symlink task-tracker.json
setup_task_tracker() {
	info "Setting up task-tracker.json symlink..."
	create_symlink "${GLOBAL_SETUP}/task-tracker.json" "${CLAUDE_DIR}/task-tracker.json" "task-tracker.json"
}

# Step 10: Symlink scripts/ (hook scripts)
setup_scripts() {
	info "Setting up scripts symlink..."
	create_symlink "${GLOBAL_SETUP}/scripts" "${CLAUDE_DIR}/scripts" "scripts/"
}

# Step 11: Symlink hooks/
setup_hooks() {
	info "Setting up hooks symlink..."
	create_symlink "${GLOBAL_SETUP}/hooks" "${CLAUDE_DIR}/hooks" "hooks/"
}

# Step 12: Symlink friction-log files
setup_friction_logs() {
	info "Setting up friction-log symlinks..."
	local THREE_B_CLAUDE="${THREE_B}/.claude"
	if [ -f "${THREE_B_CLAUDE}/friction-log.json" ]; then
		create_symlink "${THREE_B_CLAUDE}/friction-log.json" "${CLAUDE_DIR}/friction-log.json" "friction-log.json"
	fi
	if [ -f "${THREE_B_CLAUDE}/friction-log-archive.json" ]; then
		create_symlink "${THREE_B_CLAUDE}/friction-log-archive.json" "${CLAUDE_DIR}/friction-log-archive.json" "friction-log-archive.json"
	fi
}

# Step 13: Symlink skills/
setup_skills() {
	info "Setting up skills symlink..."
	create_symlink "${THREE_B}/.claude/skills" "${CLAUDE_DIR}/skills" "skills/"
}

# Step 14: Symlink RTK.md
setup_rtk() {
	info "Setting up RTK.md symlink..."
	create_symlink "${GLOBAL_SETUP}/RTK.md" "${CLAUDE_DIR}/RTK.md" "RTK.md"
}

# Step 15-17: Setup work profile (~/.claude-work)
setup_work_profile() {
	info "Setting up work profile (~/.claude-work)..."

	# Create directories
	mkdir -p "${CLAUDE_WORK_DIR}/plugins/claude-hud"

	# Chain shared config through ~/.claude (not directly to 3B)
	local CHAIN_ITEMS=(
		"CLAUDE.md"
		"CUSTOMIZATIONS.md"
		"commands"
		"hooks"
		"scripts"
		"claude-hud-patches"
		"statusline-wrapper.sh"
		"task-tracker.json"
		"settings.json"
		"RTK.md"
		"friction-log.json"
		"friction-log-archive.json"
	)

	for item in "${CHAIN_ITEMS[@]}"; do
		create_symlink "${CLAUDE_DIR}/${item}" "${CLAUDE_WORK_DIR}/${item}" "work: ${item}"
	done

	# HUD config chains through personal
	create_symlink "${CLAUDE_DIR}/plugins/claude-hud/config.json" \
		"${CLAUDE_WORK_DIR}/plugins/claude-hud/config.json" \
		"work: plugins/claude-hud/config.json"

	# Skills symlink (chain through personal, consistent with other items)
	create_symlink "${CLAUDE_DIR}/skills" "${CLAUDE_WORK_DIR}/skills" "work: skills/"

	# agents and ide directories (chain through personal)
	if [ -d "${CLAUDE_DIR}/agents" ]; then
		create_symlink "${CLAUDE_DIR}/agents" "${CLAUDE_WORK_DIR}/agents" "work: agents/"
	fi
	if [ -d "${CLAUDE_DIR}/ide" ]; then
		create_symlink "${CLAUDE_DIR}/ide" "${CLAUDE_WORK_DIR}/ide" "work: ide/"
	fi

	# Work-specific settings.local.json (overrides statusLine + enabledMcpjsonServers)
	create_symlink "${GLOBAL_SETUP}/settings.local.work.json" \
		"${CLAUDE_WORK_DIR}/settings.local.json" \
		"work: settings.local.json (work overrides)"

	success "Work profile setup complete"
}

# Print summary
print_summary() {
	echo ""
	echo "=============================================="
	echo -e "${GREEN}Setup Complete!${NC}"
	echo "=============================================="
	echo ""
	echo "Dotfiles submodule:"
	echo "  - ~/dev/personal/dotfiles → 3b/dotfiles/"
	echo ""
	echo "Personal profile (~/.claude → 3B):"
	echo "  - settings.json (shared base)"
	echo "  - commands/ scripts/ hooks/ skills/"
	echo "  - CLAUDE.md CUSTOMIZATIONS.md RTK.md"
	echo "  - statusline-wrapper.sh claude-hud-patches/"
	echo "  - plugins/claude-hud/config.json task-tracker.json"
	echo "  - friction-log.json friction-log-archive.json"
	echo ""
	echo "Work profile (~/.claude-work → ~/.claude chain):"
	echo "  - All shared config chained through personal"
	echo "  - settings.local.json → work overrides (statusLine, MCP)"
	echo ""

	echo -e "${YELLOW}Next steps:${NC}"
	echo ""
	echo "  1. Login to Claude Code:"
	echo "     claude"
	echo ""
	echo "  2. Install plugins:"
	echo "     claude plugin install context7"
	echo "     claude plugin install github"
	echo "     claude plugin install claude-hud"
	echo ""
	echo "  3. Apply HUD patches (for multi-account support):"
	echo "     ~/.claude/claude-hud-patches/claude-hud-post-patches.sh"
	echo ""
	echo "  4. Login to work profile:"
	echo "     CLAUDE_CONFIG_DIR=~/.claude-work claude"
	echo ""

	echo "Commands available:"
	echo "  /commit, /wrap, /clean-review, /validate-pr-reviews, ..."
	echo ""

	echo "Documentation:"
	echo "  - README.md - Setup overview"
	echo "  - CUSTOMIZATIONS.md - Detailed patch documentation"
	echo ""
}

# Main execution
main() {
	echo ""
	echo "=============================================="
	echo "Global ~/.claude Setup"
	echo "=============================================="
	echo ""

	check_prerequisites
	setup_dotfiles_submodule
	create_directories
	setup_settings
	setup_commands
	setup_claude_md
	setup_customizations
	setup_statusline
	setup_hud_patches
	setup_hud_config
	setup_task_tracker
	setup_scripts
	setup_hooks
	setup_friction_logs
	setup_skills
	setup_rtk
	setup_work_profile
	print_summary
}

# Run main
main "$@"
