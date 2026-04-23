#!/bin/bash
# ============================================================================
# Claude HUD Patches — v0.0.12 (native registry release)
# ============================================================================
# Run this script after updating the claude-hud plugin to re-apply patches.
#
# ARCHITECTURE:
#   - Registry publishes v0.0.12 natively (since ~2026-04-16). The old
#     "registry hijack" strategy (v0.0.12 source inside a v0.0.9 folder) is
#     retired — stale 0.0.6/ and 0.0.9/ directories are safe to delete.
#   - Work profile's HUD cache is symlinked to personal (patch once, both get it).
#   - statusline-wrapper.sh uses `ls -td` to pick the newest version directory,
#     so this script must target whichever directory the wrapper will actually
#     load — currently 0.0.12/.
#
# USAGE:
#   ~/.claude/claude-hud-patches/claude-hud-post-patches.sh
#
# PATCHES (7 total):
#   1: render/lines/project.ts — Plan label from CLAUDE_HUD_PLAN_LABEL (sed)
#   2: render/lines/project.ts — Branch name truncation to 7 chars (sed)
#   3: render/lines/project.ts — Env label from wrapper env vars (sed)
#   4: render/lines/project.ts — Remove inline customLine (sed)
#   5: render/index.ts          — CustomLine as separate line (awk)
#   6: render/colors.ts         — Midnight Aurora 256-color neon palette (awk)
#   7: render/lines/usage.ts    — Compact labels (Sesh./Week.) + pace indicator (template)
#   8: render/lines/project.ts  — Compact model display "Opus4.7 1M, Max" (awk)
#   9: render/index.ts           — Force-combine context+usage, disable wrap (awk)
#
# All patches are idempotent — safe to re-run at any time.
#
# UPGRADE HISTORY:
#   v0.0.6  → 30 patches (many workarounds for missing features)
#   v0.0.9  → 9 patches  (22 absorbed upstream; +NBSP, +quote, +colors)
#   v0.0.12 → 5 patches  (OAuth removed, customLine, colors config, modelFormat,
#                          smart auto-split. Added: plan label, branch truncation)
#   v0.0.12 native → 7 patches — restored neon palette + pace indicator that were
#                          lost during 5→7 drop on 2026-04-05 (db0b305). Hijack
#                          retired 2026-04-17.
#
# See UPGRADE-GUIDE.md for the full reinstall + patch workflow.
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TOTAL=9

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Claude HUD Patch Script (9 patches for v0.0.12)         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Find HUD path — registry now publishes v0.0.12 natively
HUD_PATH="$HOME/.claude/plugins/cache/claude-hud/claude-hud/0.0.12"

if [ ! -d "$HUD_PATH" ]; then
	echo -e "${RED}ERROR: HUD not found at ${HUD_PATH}${NC}"
	echo "Run: claude plugin install claude-hud@claude-hud"
	exit 1
fi

# Verify it's actually v0.0.12 code
ACTUAL_VERSION=$(grep '"version"' "$HUD_PATH/package.json" 2>/dev/null | head -1 | sed 's/.*"version": *"//;s/".*//')
echo "  Directory: v0.0.12"
echo "  Actual code: v${ACTUAL_VERSION}"

if [ "$ACTUAL_VERSION" != "0.0.12" ]; then
	echo -e "  ${RED}⚠ Expected v0.0.12, got v${ACTUAL_VERSION}. Re-install the plugin.${NC}"
	exit 1
fi

# Check work profile symlink
if [ -L "$HOME/.claude-work/plugins/cache/claude-hud" ]; then
	echo -e "  Work profile: ${GREEN}symlinked${NC}"
else
	echo -e "  Work profile: ${YELLOW}independent (not symlinked)${NC}"
fi
echo ""

# File paths
PROJECT_TS="${HUD_PATH}/src/render/lines/project.ts"
RENDER_INDEX="${HUD_PATH}/src/render/index.ts"
COLORS_TS="${HUD_PATH}/src/render/colors.ts"
USAGE_TS="${HUD_PATH}/src/render/lines/usage.ts"

# Templates directory (for full-file replacements)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="${SCRIPT_DIR}/templates"

# ── Patch 1: Plan label from wrapper ── project.ts ──────────────────

echo -e "  ${YELLOW}[1/${TOTAL}] Plan label from CLAUDE_HUD_PLAN_LABEL${NC}"
if grep -q "CLAUDE_HUD_PLAN_LABEL" "$PROJECT_TS" 2>/dev/null; then
	echo -e "        ${GREEN}✓ Already patched${NC}"
else
	sed -i '' 's/const modelQualifier = providerLabel ?? undefined;/\/\/ PATCHED: Plan label from wrapper env var (Max\/Team for multi-account)\
    const planLabel = process.env.CLAUDE_HUD_PLAN_LABEL?.trim();\
    const modelQualifier = providerLabel ?? planLabel ?? undefined;/' "$PROJECT_TS"
	echo -e "        ${GREEN}✓ Patched${NC}"
fi

# ── Patch 2: Branch name truncation ── project.ts ────────────────────

echo -e "  ${YELLOW}[2/${TOTAL}] Branch name truncation (7 chars)${NC}"
if grep -q "truncatedBranch" "$PROJECT_TS" 2>/dev/null; then
	echo -e "        ${GREEN}✓ Already patched${NC}"
else
	sed -i '' 's/const branchText = ctx.gitStatus.branch + ((gitConfig?.showDirty/\/\/ PATCHED: Truncate branch name to 7 chars for narrow terminals\
    const rawBranch = ctx.gitStatus.branch;\
    const truncatedBranch = rawBranch.length > 7 ? rawBranch.slice(0, 7) + '\''...'\'' : rawBranch;\
    const branchText = truncatedBranch + ((gitConfig?.showDirty/' "$PROJECT_TS"
	echo -e "        ${GREEN}✓ Patched${NC}"
fi

# ── Patch 3: Env label from wrapper ── project.ts ────────────────────

echo -e "  ${YELLOW}[3/${TOTAL}] Env label from statusline-wrapper.sh${NC}"
if grep -q "CLAUDE_HUD_ENV_LABEL" "$PROJECT_TS" 2>/dev/null; then
	echo -e "        ${GREEN}✓ Already patched${NC}"
else
	sed -i '' '/parts\.push(label(ctx\.extraLabel, colors));/a\
\  }\
\
\  // PATCHED: Env label from statusline-wrapper.sh (VIOLET label, green version)\
\  const envLabel = process.env.CLAUDE_HUD_ENV_LABEL;\
\  const envVersion = process.env.CLAUDE_HUD_ENV_VERSION;\
\  if (envLabel \&\& envVersion) {\
\    const VIOLET = '\''\\x1b[38;5;141m'\'';\
\    parts.push(`${VIOLET}${envLabel}\\x1b[0m ${green(envVersion)}`);' "$PROJECT_TS"
	echo -e "        ${GREEN}✓ Patched${NC}"
fi

# ── Patch 4: Remove inline customLine ── project.ts ──────────────────

echo -e "  ${YELLOW}[4/${TOTAL}] Remove inline customLine (moved to separate line)${NC}"
if grep -q "customLine moved to render/index.ts" "$PROJECT_TS" 2>/dev/null; then
	echo -e "        ${GREEN}✓ Already patched${NC}"
else
	sed -i '' '/const customLine = display?.customLine;/{
N;N;N
s|const customLine = display?.customLine;\n  if (customLine) {\n    parts.push(customColor(customLine, colors));\n  }|// PATCHED: customLine moved to render/index.ts as a separate line|
}' "$PROJECT_TS"
	echo -e "        ${GREEN}✓ Patched${NC}"
fi

# ── Patch 5: CustomLine as separate line ── render/index.ts ──────────

echo -e "  ${YELLOW}[5/${TOTAL}] CustomLine as separate line${NC}"
if grep -q "Custom line as separate line" "$RENDER_INDEX" 2>/dev/null; then
	echo -e "        ${GREEN}✓ Already patched${NC}"
else
	# Add import for custom color (idempotent — only matches the un-patched form)
	sed -i '' "s/import { dim, RESET } from '.\/colors.js';/import { dim, custom, RESET } from '.\/colors.js';/" "$RENDER_INDEX"
	# Add customLine rendering after the if(gitFilesLine) block (awk is more
	# robust than BSD sed's multi-line pattern space; upstream formatting
	# changes to the blank line between blocks broke the old sed pattern)
	awk '
		/^  if \(gitFilesLine\) \{/ { in_block=1 }
		in_block && /^  \}/ {
			print
			print ""
			print "  // PATCHED: Custom line as separate line (moved from project.ts inline)"
			print "  const customLineText = ctx.config?.display?.customLine;"
			print "  if (customLineText) {"
			print "    lines.push({ line: custom(customLineText, ctx.config?.colors), isActivity: false });"
			print "  }"
			in_block=0
			next
		}
		{ print }
	' "$RENDER_INDEX" >"$RENDER_INDEX.tmp" && mv "$RENDER_INDEX.tmp" "$RENDER_INDEX"
	echo -e "        ${GREEN}✓ Patched${NC}"
fi

# ── Patch 6: Midnight Aurora neon palette ── colors.ts ───────────────

echo -e "  ${YELLOW}[6/${TOTAL}] Midnight Aurora 256-color neon palette${NC}"
if grep -q "Midnight Aurora neon palette" "$COLORS_TS" 2>/dev/null; then
	echo -e "        ${GREEN}✓ Already patched${NC}"
else
	# Replace the 7 raw ANSI constants with 256-color escapes.
	# awk is used so we can match each "const X = " line exactly and rewrite
	# it without fighting BSD sed's escaping rules for \x1b.
	awk '
		/^export const RESET / && !marker_printed {
			print
			print ""
			print "// PATCHED: Midnight Aurora neon palette (256-color)"
			marker_printed=1
			next
		}
		/^const RED = / { print "const RED = '\''\\x1b[38;5;203m'\'';           // CORAL (#ff5f5f)"; next }
		/^const GREEN = / { print "const GREEN = '\''\\x1b[38;5;85m'\'';          // MINT (#5fffaf)"; next }
		/^const YELLOW = / { print "const YELLOW = '\''\\x1b[38;5;215m'\'';        // WARM_AMBER (#ffaf5f)"; next }
		/^const MAGENTA = / { print "const MAGENTA = '\''\\x1b[38;5;211m'\'';       // SOFT_ROSE (#ff87af)"; next }
		/^const CYAN = / { print "const CYAN = '\''\\x1b[38;5;117m'\'';          // SOFT_CYAN (#87d7ff)"; next }
		/^const BRIGHT_BLUE = / { print "const BRIGHT_BLUE = '\''\\x1b[38;5;141m'\'';   // VIOLET (#af87ff)"; next }
		/^const BRIGHT_MAGENTA = / { print "const BRIGHT_MAGENTA = '\''\\x1b[38;5;135m'\''; // NEON_VIOLET (#af5fff)"; next }
		{ print }
	' "$COLORS_TS" >"$COLORS_TS.tmp" && mv "$COLORS_TS.tmp" "$COLORS_TS"
	echo -e "        ${GREEN}✓ Patched${NC}"
fi

# ── Patch 7: Compact labels + pace indicator ── usage.ts (template) ──

echo -e "  ${YELLOW}[7/${TOTAL}] Compact labels (Sesh./Week.) + pace indicator${NC}"
if grep -q "Window formatter with pace" "$USAGE_TS" 2>/dev/null; then
	echo -e "        ${GREEN}✓ Already patched${NC}"
else
	if [ ! -f "${TEMPLATES_DIR}/usage.ts" ]; then
		echo -e "        ${RED}✗ Template missing at ${TEMPLATES_DIR}/usage.ts${NC}"
		exit 1
	fi
	cp "${TEMPLATES_DIR}/usage.ts" "$USAGE_TS"
	echo -e "        ${GREEN}✓ Patched (from template)${NC}"
fi

# ── Patch 8: Compact model display ── project.ts ────────────────────

echo -e "  ${YELLOW}[8/${TOTAL}] Compact model display (Opus4.7 1M, Max)${NC}"
if grep -q "Compact model display" "$PROJECT_TS" 2>/dev/null; then
	echo -e "        ${GREEN}✓ Already patched${NC}"
else
	awk '
		/const modelDisplay = modelQualifier \? `\$\{model\} \| \$\{modelQualifier\}` : model;/ {
			print "    // PATCHED: Compact model display — \"Opus4.7 1M, Max\" (strip space, shorten context suffix, comma separator)"
			print "    const compactModel = model"
			print "      .replace(/([A-Za-z])\\s+(\\d)/, '"'"'$1$2'"'"')"
			print "      .replace(/\\s*\\(1M context\\)/i, '"'"' 1M'"'"')"
			print "      .replace(/\\s*\\([^)]*context[^)]*\\)/i, '"'"''"'"');"
			print "    const modelDisplay = modelQualifier ? `${compactModel}, ${modelQualifier}` : compactModel;"
			next
		}
		{ print }
	' "$PROJECT_TS" >"$PROJECT_TS.tmp" && mv "$PROJECT_TS.tmp" "$PROJECT_TS"
	echo -e "        ${GREEN}✓ Patched${NC}"
fi

# ── Patch 9: Force-combine context+usage, disable wrap ── render/index.ts ─

echo -e "  ${YELLOW}[9/${TOTAL}] Force-combine context+usage, disable wrap${NC}"
if grep -q "Always combine context+usage" "$RENDER_INDEX" 2>/dev/null; then
	echo -e "        ${GREEN}✓ Already patched${NC}"
else
	awk '
		/const combinedLine = `\$\{firstLine\} \u2502 \$\{secondLine\}`;/ && !combine_done {
			print "        // PATCHED: Always combine context+usage; skip width check"
			print "        const combinedLine = `${firstLine} \u2502 ${secondLine}`;"
			print "        lines.push({ line: combinedLine, isActivity: false });"
			combine_done=1
			skip_count=7
			next
		}
		skip_count > 0 { skip_count--; next }
		/const visibleLines = physicalLines\.flatMap\(line => wrapLineToWidth\(line, terminalWidth\)\);/ {
			print "  // PATCHED: Disable auto-wrap — keep logical lines intact"
			print "  const visibleLines = physicalLines;"
			next
		}
		{ print }
	' "$RENDER_INDEX" >"$RENDER_INDEX.tmp" && mv "$RENDER_INDEX.tmp" "$RENDER_INDEX"
	echo -e "        ${GREEN}✓ Patched${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  All patches applied successfully!                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Restart Claude Code to see changes."
