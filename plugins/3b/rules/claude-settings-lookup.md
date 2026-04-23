---
tags: [claude-code, configuration, multi-profile]
created: 2026-03-03
updated: 2026-04-17
status: completed
paths:
  - "**/settings.json"
  - "**/settings.local*.json"
  - ".claude/global-claude-setup/**"
---

# Claude Settings Lookup Guide

When asked to check, fix, or investigate Claude Code settings, use this
quick-reference to find the right files.

## Profile Architecture

```text
~/.claude        → Personal profile (Max plan, default)
~/.claude-work   → Work profile (Team plan)
```

All config is **shared via symlinks** from 3B, including `settings.json`.
Work-specific overrides (`statusLine.command`, `enabledMcpjsonServers`) live in
`settings.local.work.json`, symlinked as `~/.claude-work/settings.local.json`.
Claude Code deep-merges `settings.local.json` over `settings.json`.

## Quick Lookup Table

| What to Check              | File Location                                                                  | Shared? |
| -------------------------- | ------------------------------------------------------------------------------ | ------- |
| **Settings (permissions)** | `3b/.claude/global-claude-setup/settings.json` (SoT, symlinked to both)        | Yes     |
| **Work overrides**         | `3b/.claude/global-claude-setup/settings.local.work.json` → `~/.claude-work/`  | N/A     |
| **HUD display config**     | `3b/.claude/global-claude-setup/plugins/claude-hud/config.json`                | Yes     |
| **HUD source (patches)**   | `~/.claude/plugins/cache/claude-hud/claude-hud/{ver}/src/`                     | No      |
| **Statusline wrapper**     | `3b/.claude/global-claude-setup/statusline-wrapper.sh`                         | Yes     |
| **Global CLAUDE.md**       | `3b/.claude/global-claude-setup/templates/CLAUDE.md` → `~/.claude`             | Yes     |
| **Global AGENTS.md**       | `templates/AGENTS.md` → `CLAUDE.md` (symlink) → `~/.claude/AGENTS.md`          | Yes     |
| **Global GEMINI.md**       | `templates/GEMINI.md` → `CLAUDE.md` (symlink) → `~/.claude/GEMINI.md`          | Yes     |
| **Commands**               | `3b/.claude/global-claude-setup/commands/` → `~/.claude/`                      | Yes     |
| **Hooks (directory)**      | `3b/.claude/global-claude-setup/hooks/` → `~/.claude/`                         | Yes     |
| **Hook scripts**           | `3b/.claude/global-claude-setup/scripts/` → `~/.claude/`                       | Yes     |
| **Friction log (active)**  | `3b/.claude/friction-log.json` → `~/.claude/`                                  | Yes     |
| **Friction log (archive)** | `3b/.claude/friction-log-archive.json` → `~/.claude/`                          | Yes     |
| **Account credentials**    | `~/.claude/.claude.json` / `~/.claude-work/.claude.json`                       | No      |
| **Session history**        | `~/.claude/history.jsonl` / `~/.claude-work/history.jsonl`                     | No      |
| **Usage cache**            | `~/.claude/plugins/claude-hud/.usage-cache.json`                               | No      |
| **Output style**           | Global `settings.json` (`outputStyle` key) — applies everywhere                | Yes     |
| **Project CLAUDE.md SoT**  | `3b/.claude/project-claude/{name}.md` → each repo's `CLAUDE.md`                | Yes     |
| **Project .mcp.json SoT**  | `3b/.claude/project-claude/{name}.mcp.json` → each repo's `.mcp.json`          | Yes     |
| **MCP strategy**           | `3b/.claude/rules/mcp-strategy.md`                                             | N/A     |
| **Patch documentation**    | `3b/.claude/global-claude-setup/CUSTOMIZATIONS.md`                             | N/A     |
| **Patch script**           | `3b/.claude/global-claude-setup/claude-hud-patches/claude-hud-post-patches.sh` | Yes     |

## Permission Model

Global `settings.json` uses a **catch-all allow with deny/ask guardrails**:

```text
deny  → empty (nothing hard-blocked)
ask   → prompted (terraform, git push, rm, sudo, etc.)
allow → Bash(*) catch-all — everything else auto-approved
```

Precedence: **deny > ask > allow**. The `Bash(*)` catch-all auto-approves all
Bash commands except those matching `ask` patterns. `deny` is kept empty — all
dangerous commands go in `ask` so they can still be approved when needed.

`defaultMode` is `"plan"` — Claude starts in plan mode and must be explicitly
switched to implementation. Combined with the `Bash(*)` catch-all and explicit
tool allow list, all non-destructive tools run without prompts.
(`"allowedTools"` was used previously but is no longer a valid value.)

### No Per-Project settings.local.json Needed

As of 2026-03-07, per-project `settings.local.json` files and symlinks were
consolidated into global `settings.json`. Projects no longer need their own
permission files — the global `Bash(*)` catch-all covers all non-destructive
commands.

**Remaining project-level settings.local.json files:**

| File                                        | Purpose                                           |
| ------------------------------------------- | ------------------------------------------------- |
| `3b/.claude/settings.local.json`            | Voice hooks only (curl to localhost, 3b-specific) |
| `work/frontend/.claude/settings.local.json` | Managed by frontend team (not our SoT)            |
| `work/mobile/.claude/settings.local.json`   | Managed by mobile team (not our SoT)              |

## Key Rules

1. **3B is the SoT** — edit `3b/.claude/global-claude-setup/settings.json`
   directly; both profiles read it via symlinks (no manual sync needed).
   Work-specific overrides go in `settings.local.work.json`
2. **HUD binaries are per-profile** — patches must be applied to BOTH
   `~/.claude` and `~/.claude-work` plugin caches
3. **Statusline command differs** — work profile embeds
   `CLAUDE_CONFIG_DIR=~/.claude-work` in the command itself (Claude Code does
   not pass env vars to statusline subprocesses)
4. **Plugin updates overwrite patches** — after HUD update, re-run
   `~/.claude/claude-hud-patches/claude-hud-post-patches.sh`
5. **Bun runs source TS** — the wrapper calls `bun src/index.ts`, NOT compiled
   `dist/`. Patches go in `src/` files
6. **No PermissionRequest hook** — removed 2026-03-07. Was auto-approving
   non-Bash tools even in plan mode (short-circuit bug). The `Bash(*)`
   catch-all + deny/ask lists now handle all permission logic natively
