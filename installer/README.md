# 3b-forge installer payload

> **Wave 1 status — WIP.** Copied verbatim from the 3B maintainer's personal
> `global-claude-setup/` on 2026-04-24. Paths and assumptions are still
> 3B-opinionated (`setup.sh` hardcodes `${HOME}/dev/personal/3b`). This
> directory is published for **reference only**. Do not run `setup.sh` as
> a public user until Wave 2 parameterization lands.

## What's here

| Path | Purpose | Public-ready? |
| ---- | ------- | ------------- |
| `setup.sh` | Idempotent installer that wires `~/.claude/` to the source tree | No — 3B-pathed |
| `statusline-wrapper.sh` | Custom HUD statusline with profile detection | Yes |
| `templates/CLAUDE.md` | Starter global CLAUDE.md (references 3B rule paths) | No — Wave 2 strips paths |
| `templates/settings.example.json` | Permission + hook config example (uses `$HOME`) | Yes |
| `templates/AGENTS.md`, `templates/GEMINI.md` | Symlinks to templates/CLAUDE.md | Follows CLAUDE.md |
| `templates/plugins/` | `known_marketplaces.json`, `installed_plugins.json` examples | Yes |
| `claude-hud-patches/` | Overlay patches for the claude-hud statusline plugin | Yes |
| `plugins/claude-hud/config.json` | Shareable claude-hud config defaults | Yes |
| `commands/commit.md` | `/commit` — guided atomic conventional commits | Yes |
| `commands/clean-review.md`, `commands/clean-review/` | Clean Code review command pack | Yes |
| `hooks/` (21 files) | SessionStart / PreToolUse / PostToolUse / Stop hook scripts | Yes |
| `RTK.md`, `CUSTOMIZATIONS.md` | Reference docs from source repo | Yes (context-only) |
| `README.ko.md` | Korean source README (reference) | Yes (context-only) |

## What was intentionally NOT copied

- `settings.json` (maintainer's real settings — contained hardcoded personal
  paths; `templates/settings.example.json` is the sanitized template).
- `task-tracker.json` (maintainer's personal task pattern data).
- `settings.local.work.json` (work-repo-scoped permissions).
- `settings.json.bak-*` (backups).
- 3B-coupled hooks (`profile-sync-hook.py`, `friction-context-hook.py`,
  `knowledge-staleness-hook.py`) — deferred to Wave 2 after parameterization.
- `commands/init-3b.md` — tightly bound to 3B repo bootstrap; never ships here.

## Hooks inventory

All hooks are shipped as Claude Code hook scripts. Each reads the hook event
payload from stdin and emits zero-or-one line to stdout. Most are defensive
`|| true` hooks — they log advisories but never block tool use.

- `aws-safety-hook.py` — warn before destructive AWS commands
- `terraform-safety-hook.py` — warn before destructive Terraform commands
- `typescript-check-hook.py` — lightweight TS type-check on PostToolUse
- `formatter-hook.py` — run project formatter after Edit/Write
- `stop-verification-hook.py` — remind to verify success on Stop
- `correction-detector-hook.py` — detect user corrections in prompt history
- `post-implementation-review-hook.py` — prompt for post-impl review
- `implementation-tracker-hook.py` — track implementation progress
- `scope-warning-hook.py` — warn when changes exceed declared scope
- `symlink-check-hook.py` — validate symlink integrity on Bash ops
- `symlink-daily-check.sh` — daily symlink audit
- `me-md-protection-hook.py` — block edits to `*.me.md` files
- `skill-routing-diff.py` — audit skill-trigger match diffs
- `track-skill-slash.py` — count slash-invoked skills
- `track-skill-usage.py` — count PostToolUse Skill invocations
- `track-plugin-usage.py` — count plugin-scoped invocations
- `track-mcp-usage.py` — count mcp__ tool invocations
- `regenerate-usage-dashboard.py` — regenerate usage dashboard from logs
- `verify-registry.py` — sanity-check registry file integrity
- `knowledge-link-checker.py` — validate cross-references in knowledge files
- `post-impl-review-checklist.md` — checklist referenced by the post-impl hook

## Wave 2 parameterization targets

1. Replace `THREE_B="${HOME}/dev/personal/3b"` in `setup.sh` with either:
   - `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` (script-relative), or
   - `${INSTALLER_SRC:-$PWD}` (env-var overridable).
2. Strip `3b/.claude/rules/*` path references from `templates/CLAUDE.md`.
3. Split `templates/CLAUDE.md` into a "minimal universal" version + an
   optional "3B methodology extension" (so public users don't inherit the
   knowledge-pipeline rules unless they want them).
4. Audit every hook script for hardcoded 3B paths.

## License

MIT. See [`../LICENSE`](../LICENSE) at the repo root — covers this entire
directory and every file under it.

## Source lineage

- Original home: `~/dev/personal/3b/.claude/global-claude-setup/` in the
  maintainer's private 3B (Brandon's Binary Brain) repo.
- Predecessor project: `claude-forge` — a short-lived sibling project focused
  on overall Claude Code settings + plugin management. Its scope was folded
  into 3b-forge in April 2026; the `claude-forge-crosschecker` agent
  (`../plugins/3b/agents/claude-forge-crosschecker.md`) carries the name
  forward as the one surviving artifact.
