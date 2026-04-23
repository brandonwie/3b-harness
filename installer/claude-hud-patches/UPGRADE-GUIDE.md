---
tags: [devops, claude-hud]
created: 2026-03-10
updated: 2026-04-17
status: completed
---

# Claude HUD Upgrade Guide

Upstream: <https://github.com/jarrodwatts/claude-hud>

## Overview

When claude-hud plugin updates, custom patches must be re-applied. This guide
covers the full workflow: reinstall → patch → verify.

## Architecture Quick Reference

- Two profiles: `~/.claude` (Personal/Max) and `~/.claude-work` (Work/Team)
- Work profile's HUD cache is symlinked to personal
  (`~/.claude-work/plugins/cache/claude-hud` →
  `~/.claude/plugins/cache/claude-hud`). Patch once; both profiles get it.
- Plugin cache: `~/.claude/plugins/cache/claude-hud/claude-hud/{version}/`
- `statusline-wrapper.sh` picks the newest cached version directory (`ls -td`),
  so the patch script must target that same directory.
- Source of truth: `3b/.claude/global-claude-setup/claude-hud-patches/`
- HUD runs via `bun src/index.ts` — patches go in `src/`, not `dist/`

## Step 1: Check Current Version

```bash
ls ~/.claude/plugins/cache/claude-hud/claude-hud/
ls ~/.claude-work/plugins/cache/claude-hud/claude-hud/
```

## Step 2: Reinstall Plugin

```bash
# From personal profile (default)
claude plugin uninstall claude-hud
claude plugin install claude-hud@claude-hud

# From work profile (requires CLAUDE_CONFIG_DIR)
CLAUDE_CONFIG_DIR=~/.claude-work claude plugin uninstall claude-hud
CLAUDE_CONFIG_DIR=~/.claude-work claude plugin install claude-hud@claude-hud
```

Note: If `claude plugin` commands aren't available, you can manually:

1. Delete `~/.claude/plugins/cache/claude-hud/` (and work equivalent)
2. The plugin will auto-reinstall on next Claude Code launch if it's in
   `enabledPlugins`

## Step 3: Apply Custom Patches

```bash
~/.claude/claude-hud-patches/claude-hud-post-patches.sh
```

This patches BOTH profiles automatically. The script is idempotent — safe to
re-run.

## Step 4: Update Config (if needed)

Check if the new upstream version adds config fields. Our `config.json` at:

- `3b/.claude/global-claude-setup/plugins/claude-hud/config.json` (SoT)
- Symlinked to both profiles

v0.0.9 added these config fields (already supported):

- `usage.cacheTtlSeconds` (default: 60) — success cache TTL
- `usage.failureCacheTtlSeconds` (default: 15) — failure cache TTL
- `elementOrder` — configurable line ordering for expanded mode
- `display.showProject` — toggle project path display
- `display.showSessionName` — show session name from /rename

## Step 5: Verify

```bash
# Check version installed
ls ~/.claude/plugins/cache/claude-hud/claude-hud/

# Clear caches to see changes immediately
rm -f ~/.claude/plugins/claude-hud/.usage-cache.json
rm -f ~/.claude-work/plugins/claude-hud/.usage-cache.json

# Quick compile check (should produce no errors). --target=bun is required;
# without it, bun defaults to browser target and rejects Node builtins.
cd ~/.claude/plugins/cache/claude-hud/claude-hud/0.0.12
bun build src/index.ts --target=bun --outdir /tmp/hud-test 2>&1 | head -5

# Start a new Claude Code session and check statusline displays correctly
```

## Step 6: Update Documentation

After a successful upgrade:

1. Update `CUSTOMIZATIONS.md` — new sections if patches changed
2. Update `claude-hud-post-patches.sh` header comments — version + patch count
3. Update memory files if version number changed

## Troubleshooting

### Statusline shows nothing

- Check `bun` is installed: `which bun`
- Check plugin exists: `ls ~/.claude/plugins/cache/claude-hud/`
- Check wrapper runs: `echo '{}' | ~/.claude/statusline-wrapper.sh`
- Check DEBUG output:
  `DEBUG=claude-hud echo '{}' | ~/.claude/statusline-wrapper.sh`

### 429 errors persist

- Upstream v0.0.9 has proper 15s failure cache TTL. If 429 persists:
  - Increase failure TTL in config.json:
    `"usage": { "failureCacheTtlSeconds": 300 }`
  - Check if OAuth token needs refresh: `claude /login`
  - Clear cache: `rm -f ~/.claude/plugins/claude-hud/.usage-cache.json`

### Wrong profile showing

- Verify `CLAUDE_HUD_CONFIG_DIR` is set by statusline-wrapper.sh
- Check: `echo $CLAUDE_CONFIG_DIR` in each profile

### Patches fail to apply

- Check upstream file structure hasn't changed drastically
- Run with `set -x` for debug output:
  `bash -x ~/.claude/claude-hud-patches/claude-hud-post-patches.sh`
- If sed patterns don't match, templates may need updating for new upstream
  structure

## Untagged Version Bumps (2026-04-21)

Upstream bumped `main`'s `plugin.json` to **0.1.0** on commit
`4d2a023 release: bump version to 0.1.0` (2026-04-20 21:08 +1000) without
tagging, cutting a GitHub Release, or updating the marketplace metadata
(`marketplace.json` still pinned `metadata.version: 0.0.12`). Because Claude
Code's marketplace auto-update follows `main` (not tags), the updater pulled
HEAD on 2026-04-21 and cached vanilla 0.1.0 source at
`cache/claude-hud/claude-hud/0.1.0/`. `statusline-wrapper.sh`'s `ls -td` picked
the newer directory, silently replacing the patched 0.0.12 code path with
vanilla upstream — losing Sesh./Week. labels, the pace indicator, the plan
label, branch truncation, env label, customLine separation, neon palette, and
compact model display.

**Policy from 2026-04-21 onward:** `claude-hud` marketplace auto-update is
**disabled** in `~/.claude/plugins/known_marketplaces.json`
(`autoUpdate: false`). The marketplace git HEAD is pinned to `6e146239`
(pre-bump detached HEAD), and `installed_plugins.json` is pinned to version
`0.0.12`.

Re-enable auto-update only after upstream publishes a real 0.1.x release with a
Git tag + GitHub Release + CHANGELOG entry. Until then, updates are manual:

```bash
cd ~/.claude/plugins/marketplaces/claude-hud
git fetch origin
git log --oneline origin/main ^HEAD  # review what would change
# If safe, fast-forward — otherwise stay pinned:
git checkout main
claude plugin update claude-hud@claude-hud
~/.claude/claude-hud-patches/claude-hud-post-patches.sh
```

Patches 7, 8, 9 will need rewriting when upstream 0.1.x lands — see
`Patch History` table below.

## Registry Native v0.0.12 (2026-04-17)

As of 2026-04-16, the claude-hud registry publishes **v0.0.12 natively**. The
earlier "registry hijack" workaround (v0.0.12 source inside a v0.0.9 folder) is
retired. The patch script now targets `0.0.12/` directly.

**Stale cache directories** (`0.0.9/`, `0.0.6/`) can be safely removed:

```bash
rm -rf ~/.claude/plugins/cache/claude-hud/claude-hud/0.0.6
rm -rf ~/.claude/plugins/cache/claude-hud/claude-hud/0.0.9
```

The wrapper uses `ls -td` and only reads the newest directory, so leaving them
in place is harmless but wastes ~2 MB.

**Work profile sync**: `~/.claude-work/plugins/cache/claude-hud` is symlinked to
personal, so patching once reaches both profiles automatically.

## Compile Check Target

When running a manual build-verify:

```bash
cd ~/.claude/plugins/cache/claude-hud/claude-hud/0.0.12
bun build src/index.ts --target=bun --outdir /tmp/hud-test
```

The `--target=bun` flag is required — without it, bun defaults to the `browser`
target and rejects Node.js builtins (`readline`, `fs`, etc.) that HUD uses.

## Patch History

| Version            | Patches | Notes                                                                                                                             |
| ------------------ | ------- | --------------------------------------------------------------------------------------------------------------------------------- |
| v0.0.6             | 30      | Original patching target. Many workarounds for missing features.                                                                  |
| v0.0.9             | 9       | 22 patches absorbed by upstream. Major simplification.                                                                            |
| v0.0.12 (hijack)   | 5       | Source copied into 0.0.9/ folder; registry still capped at 0.0.9.                                                                 |
| v0.0.12 (native)   | 5       | Registry publishes v0.0.12 directly. Hijack retired 2026-04-17.                                                                   |
| v0.0.12 (restored) | 7       | Restored colors.ts neon palette + usage.ts pace indicator lost on 2026-04-05.                                                     |
| v0.0.12 (+8,+9)    | 9       | Added compact model display (patch 8) + force-combine/no-wrap (patch 9).                                                          |
| v0.1.0 (vanilla)   | —       | Untagged main-branch bump (`4d2a023`, 2026-04-20). Pulled silently by autoUpdate. Rolled back 2026-04-21; autoUpdate now `false`. |

## Custom Patches (v0.0.12)

| #   | File                      | Method   | Purpose                                              |
| --- | ------------------------- | -------- | ---------------------------------------------------- |
| 1   | `render/lines/project.ts` | sed      | Plan label from `CLAUDE_HUD_PLAN_LABEL` env var      |
| 2   | `render/lines/project.ts` | sed      | Branch name truncation to 7 chars + `...`            |
| 3   | `render/lines/project.ts` | sed      | Env label + version from wrapper env vars (green)    |
| 4   | `render/lines/project.ts` | sed      | Remove inline `customLine` (moved to separate line)  |
| 5   | `render/index.ts`         | awk      | Insert `customLine` block after `gitFilesLine` block |
| 6   | `render/colors.ts`        | awk      | Midnight Aurora 256-color neon constants (7 swaps)   |
| 7   | `render/lines/usage.ts`   | template | Compact Sesh./Week. labels + pace indicator          |
| 8   | `render/lines/project.ts` | awk      | Compact model display `Opus4.7 1M, Max`              |
| 9   | `render/index.ts`         | awk      | Force-combine context+usage, disable auto-wrap       |

### Notes on Patch 7 (template-based)

`templates/usage.ts` fully replaces the upstream file. Upstream may refactor
`usage.ts` between HUD releases — diff
`~/.claude/plugins/cache/claude-hud/claude-hud/{version}/src/render/lines/usage.ts`
against `templates/usage.ts` after each upgrade and port any new upstream
features into the template before re-running the script.

The template delivers:

- Labels `Sesh.` (5-hour) / `Week.` (7-day) instead of upstream's `5h` /
  `weekly`
- Compact reset times (`1.2h`, `2.3d`, `45m`) instead of upstream's `1h 30m`
- Pace indicator: appends `, 50%` where `50%` is the elapsed window fraction,
  colored by how far usage is ahead of or behind pace — green (under pace,
  headroom), amber (0–15% over), red (>15% over, burning too fast)
