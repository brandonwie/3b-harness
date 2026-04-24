# 3b-forge installer payload

Wave 2 parameterization landed 2026-04-24: `setup.sh` now runs on any machine
that has a 3B-structured knowledge repo, configured via the `FORGE_3B_ROOT`
environment variable. The `templates/CLAUDE.md` split separates universal
guidance from the opt-in 3B methodology extension.

## Supported platforms

| Platform | Status | Notes |
| -------- | ------ | ----- |
| macOS | **Supported** | Primary test platform. Stock bash 3.2 is handled; `realpath` falls back to `python3` when missing. |
| Linux | Untested | Expected to work — scripts are bash + POSIX tools, no macOS-specific binaries — but not in the current test matrix. Report issues. |
| Windows | **Not supported** | Installer requires bash, `ln -s` symlinks, and `$HOME/.claude` layout. No `.ps1` / junction equivalents ship. WSL may work by proxy (untested). |

Prerequisites on any supported platform: `bash` (3.2+), `python3` (+ `PyYAML`
for `scripts/check-3b-drift.sh`), `git`, `coreutils` (optional — improves
`realpath` behaviour).

## Quick start

```bash
# 1. Point the installer at your 3B-structured knowledge repo.
export FORGE_3B_ROOT=/path/to/your/3b

# 2. Dry-run first (prints every action; no filesystem writes).
./installer/setup.sh --dry-run

# 3. Real run.
./installer/setup.sh
```

## Environment variables

| Var                          | Required? | Default                              | Purpose                                                  |
| ---------------------------- | --------- | ------------------------------------ | -------------------------------------------------------- |
| `FORGE_3B_ROOT`              | **Yes**   | — (fail-fast if unset)               | Path to your 3B knowledge repo.                          |
| `FORGE_HOME`                 | No        | Script's parent dir (`../`)          | Forge repo root — only needed if you relocate the script.|
| `FORGE_DOTFILES_LINK`        | No        | `$HOME/dev/personal/dotfiles`        | Symlink target for the dotfiles submodule. Skipped if `$FORGE_3B_ROOT/dotfiles` doesn't exist. |
| `FORGE_INSTALL_WORK_PROFILE` | No        | `0`                                  | Set to `1` to also wire `~/.claude-work` (secondary profile). |
| `FORGE_DRY_RUN`              | No        | `0`                                  | Set to `1` (or pass `--dry-run`) to print actions without writing. |

Hooks in `installer/hooks/` that read 3B content (`profile-sync-hook.py`,
`knowledge-staleness-hook.py`, `knowledge-link-checker.py`, etc.) also read
`FORGE_3B_ROOT` and fail-open (exit 0) when the variable is unset, so
non-3B users can install the hook payload without noisy errors.

## What's here

| Path | Purpose | Public-ready? |
| ---- | ------- | ------------- |
| `setup.sh` | Idempotent installer, parameterized via `FORGE_3B_ROOT` | Yes |
| `statusline-wrapper.sh` | Custom HUD statusline with profile detection | Yes |
| `templates/CLAUDE.md` | Universal global CLAUDE.md (Principles #1–#9, generic) | Yes |
| `templates/CLAUDE-3b-extension.md` | Opt-in addon: Buffer, ACTIVE-STATUS, 3B directory layout | Yes |
| `templates/settings.example.json` | Permission + hook config example (uses `$HOME`) | Yes |
| `templates/AGENTS.md`, `templates/GEMINI.md` | Symlinks to templates/CLAUDE.md | Follows CLAUDE.md |
| `templates/plugins/` | `known_marketplaces.json`, `installed_plugins.json` examples | Yes |
| `claude-hud-patches/` | Overlay patches for the claude-hud statusline plugin | Yes |
| `plugins/claude-hud/config.json` | Shareable claude-hud config defaults | Yes |
| `commands/commit.md` | `/commit` — guided atomic conventional commits | Yes |
| `commands/clean-review.md`, `commands/clean-review/` | Clean Code review command pack | Yes |
| `hooks/` (24 files) | SessionStart / PreToolUse / PostToolUse / Stop hook scripts, all `FORGE_3B_ROOT`-aware | Yes |
| `RTK.md`, `CUSTOMIZATIONS.md` | Reference docs from source repo | Yes (context-only) |
| `README.ko.md` | Korean source README (reference) | Yes (context-only) |

## What was intentionally NOT copied

- `settings.json` (maintainer's real settings — contained hardcoded personal
  paths; `templates/settings.example.json` is the sanitized template).
- `task-tracker.json` (maintainer's personal task pattern data).
- `settings.local.work.json` (work-repo-scoped permissions).
- `settings.json.bak-*` (backups).
- `commands/init-3b.md` — tightly bound to 3B repo bootstrap; never ships here.

(Wave 2 2026-04-24: `profile-sync-hook.py`, `friction-context-hook.py`, and
`knowledge-staleness-hook.py` were parameterized via `FORGE_3B_ROOT` and now
ship with the Tier-A hook set.)

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

## Drift detection (forge ← 3B)

Forge files derived from the maintainer's 3B repo are tracked in
`plugins/3b/SOURCE-MANIFEST.yaml` with their 3B source path and commit SHA
at sync time. To check for upstream drift:

```bash
export FORGE_3B_ROOT=/path/to/your/3b
./scripts/check-3b-drift.sh           # summary
./scripts/check-3b-drift.sh --verbose # show per-file commit history
```

Exit codes: `0` = all in sync, `1` = drift detected, `2` = pre-flight failure
(missing env var, manifest, etc.). When drift is reported, re-sync the
affected file(s), re-apply scrubs per
[`../plugins/3b/PUBLIC-PRIVATE-SPLIT.md`](../plugins/3b/PUBLIC-PRIVATE-SPLIT.md),
and update `SOURCE-MANIFEST.yaml` with the new 3B HEAD SHA.

The `claude-forge-crosschecker` agent can perform this audit in structured-
report form — see `plugins/3b/agents/claude-forge-crosschecker.md` § Mode 2.

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
