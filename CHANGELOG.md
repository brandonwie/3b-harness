# Changelog

All notable changes to this repo will be documented here. Harness-level
(repo structure, cross-plugin changes) and plugin-level entries are
both tracked; plugin-level entries are scoped by `plugins/<name>/`.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
per plugin.

## [Unreleased]

### Harness-level

#### Added
- 2026-04-24 — **Wave 1 copy-only migration from 3B `.claude/`**. Copied
  (not moved) portable Tier-A content from `~/dev/personal/3b/.claude/` into
  `3b-forge/plugins/3b/` and new `installer/` directory. No source files in
  3B were touched — verified by pre/post `git status` SHA match. Detailed
  tier classification in [`tmp/migration-analysis.md`](./tmp/migration-analysis.md).
  Locked decisions: single consolidated plugin at `plugins/3b/`; every skill
  invokable as `/3b:{skill_name}`; 3B-bounded items inside `plugins/3b/`
  gitignored (policy at [`plugins/3b/PUBLIC-PRIVATE-SPLIT.md`](./plugins/3b/PUBLIC-PRIVATE-SPLIT.md));
  `installer/` is a sibling to `plugins/`, not a plugin itself and carries a
  Wave 1 WIP banner on `setup.sh` and `templates/CLAUDE.md` because both
  still hardcode `${HOME}/dev/personal/3b` paths (parameterization deferred
  to Wave 2).

### `plugins/3b/` v0.0.1 → v0.0.2 (2026-04-24)

#### Added
- 11 new portable skills under `skills/`, all invokable as `/3b:{name}`:
  `clarify`, `investigate`, `review-pr`, `pr-creator`, `issue-creator`,
  `add-pr-self-reviews`, `validate-pr-reviews`, `doc-audit`, `graphify`,
  `translate-ko`, `task-tracker`. All scraped with coupling count ≤ 5 against
  3B-specific path/file patterns — safe to ship as-is.
- 13 new methodology rules under `rules/` (new directory). Covers universal
  load (`change-discipline.md`, `pr-review-lifecycle.md`,
  `yaml-frontmatter-schema.md`, `tag-taxonomy.md`) and path-gated load
  (`knowledge-creation.md`, `tmp-files.md`, `reference-credibility.md`,
  `runtime-environment.md`, `firecrawl-usage.md`,
  `claude-settings-lookup.md`, `task-starter-post-plan.md`,
  `blog-publishing.md`, `dotfiles-management.md`).
- 1 new agent: `claude-forge-crosschecker.md` — renamed on copy from the
  original `forge-crosschecker.md`. New name carries the lineage of the
  `claude-forge` sibling project (short-lived effort focused on global Claude
  Code settings + plugin management, folded into 3b-forge April 2026).
- `PUBLIC-PRIVATE-SPLIT.md` — maintainer policy doc describing the gitignore
  rubric that separates public Tier-A content from locally-staged 3B-bounded
  items.

#### Changed
- `plugin.json` — version bump, description expanded to enumerate the new
  skills, keywords extended (`skills`, `rules`, `methodology`,
  `yaml-frontmatter`, `pr-review`, `zettelkasten`), explicit `agents` and
  `commands` paths registered.
- `README.md` — rewritten Current skills table, added Methodology rules and
  Agents tables, updated File layout and Graduation criterion to reflect
  Wave 1 state.

### `installer/` (new directory, 2026-04-24)

Sibling to `plugins/` at repo root. Not a Claude Code plugin — this is the
shell-installer payload (eventually the `curl … | sh` target for external
users). Wave 1 status: **reference only, do not execute**.

#### Added
- `setup.sh` (WIP banner: hardcoded 3B path; Wave 2 will parameterize).
- `statusline-wrapper.sh` — portable statusline helper.
- `templates/` — starter `CLAUDE.md` (WIP banner, 3B-referenced),
  `settings.example.json` (clean, uses `$HOME`), `AGENTS.md` and `GEMINI.md`
  symlinks, example plugin manifests.
- `claude-hud-patches/` — claude-hud overlay patches.
- `commands/commit.md`, `commands/clean-review/` — portable slash commands.
- `hooks/` — 21 portable hook scripts (AWS / Terraform safety, TS check,
  formatter, stop-verification, symlink check, skill/plugin/MCP usage
  tracking, …).
- `README.md` — public-facing inventory + Wave 1 WIP status banner.

#### Not copied (stays private)
- `settings.json` (maintainer's personal paths).
- `task-tracker.json` (personal data).
- `settings.local.work.json` (work-repo permissions).
- `init-3b.md` command (bootstraps 3B itself, tightly bound).
- 3B-coupled hooks: `profile-sync-hook.py`, `friction-context-hook.py`,
  `knowledge-staleness-hook.py`. Deferred to Wave 2 after parameterization.

### Harness-level (continued)
- 2026-04-23 — **Repo renamed `brandonwie/3b-harness` → `brandonwie/3b-forge`.**
  Continues the `ask-socratic` → `3b-harness` → `3b-forge` chain. Brand taxonomy
  locked: **3B** (umbrella) / **3B Brain** (knowledge repo at `~/dev/personal/3b/`) /
  **3B Forge** (this repo — build + packaging layer for cross-agent plugin
  distribution) / **3B Plugin** (`plugins/3b/`, slash namespace `/3b:*`) /
  **3B Runtime** (Python engine). GitHub repo renamed via `gh repo rename`
  (301 redirects cover old URL). Local dir `3b-harness/` → `3b-forge/`. Claude
  memory dir + all Brain path refs migrated. Historical entries below preserved.
- 2026-04-23 — **SSoT consolidation** — the harness now ships a single
  plugin [`plugins/3b/`](./plugins/3b/) with two layers (conversational
  SKILL.md + agents; optional Python engine) instead of two sibling
  variants. Old dirs moved to [`archive/plugins/`](./archive/plugins/)
  with explanatory READMEs. See the ⚠️ REVISION banner at the top of
  [`consolidated-plan.md`](./consolidated-plan.md) for the rationale.
- 2026-04-23 — Cross-variant self-review cycle + consolidated plan.
  `review-from-claude.md` (Claude reviewing `interview-claude`),
  `review-from-codex.md` (Codex reviewing `interview-codex`), and
  `consolidated-plan.md` (reconciliation) committed at repo root. CA1
  resolved; CA3 direction chosen: **Hybrid** — keep both variants as
  canonical for their respective deploy targets. See `todos.md`
  Adjudication block.
- Renamed repository `brandonwie/ask-socratic` → `brandonwie/3b-harness`
  to reflect the expanded scope (harness for multiple plugins / skills
  / future MCP servers).
- Restructured layout: plugin content moved from repo root into
  `plugins/interview/`; top-level README rewritten to describe the
  harness.
- Added `plugins/interview-codex/` — a Codex-generated variant of the
  interview skill with its own Python core, pulled in for side-by-side
  comparison with `plugins/interview/`.
- Added `docs/interview-skill/` — 10 analysis markdown files (EN + KO)
  copied from the Ouroboros fork prep work. Includes overview, routing
  decision tree, rhythm guard, ambiguity scoring, state persistence,
  agents/perspectives, PM variant, customization guide, and plugin
  build decisions.
- Added root `.gitignore` covering Python, virtualenvs, test caches,
  IDE/OS files (needed because `plugins/interview-codex/` is a real
  Python project).
- Top-level README rewritten to describe 3b-harness as a workspace.

### `plugins/interview-claude/` (was `plugins/interview/`)

#### Changed
- 2026-04-23 — Plugin manifest `name` renamed `interview-claude` → `3b`.
  Slash command is now `/3b:interview`. Directory stays
  `plugins/interview-claude/` (paired with `interview-codex/`). This is
  a manifest-only rename; the plugin is the lead skill of the 3b-harness
  plugin set.
- 2026-04-23 — `skills/interview/SKILL.md`: Path A (future MCP mode)
  references deleted along with `interview-ai` PyPI package mentions.
  The skill is now single-path (in-conversation, prompt-heavy). A
  future numerical-scoring variant is the separate `interview-codex`
  plugin.
- 2026-04-23 — README rewritten: added explicit **graduation
  criterion** (0.0.1 → 0.1.0) documenting the four conditions under
  which `not-for-use` keyword lifts.
- Renamed folder `plugins/interview/` → `plugins/interview-claude/`
  for visible symmetry with `plugins/interview-codex/`. Pairing makes
  the "snapshot / not-yet-shipping / pending comparison" stance clear.
- Plugin identity renamed `interview` → `interview-claude`. Slash
  command was `/interview-claude:interview` (later renamed to
  `/3b:interview` on 2026-04-23 — see entry above).
- Version demoted `0.1.0-alpha` → `0.0.1` to reflect not-for-use
  status. Paired with `plugins/interview-codex/`'s `v0.1.0` snapshot,
  the lower number signals "earlier, less mature" which is accurate —
  `interview-codex` ships a Python scoring core whereas
  `interview-claude` is skill+agents only.
- plugin.json `description` + `keywords` updated to include
  `"snapshot"` + `"not-for-use"` flags.
- README rewritten as a **snapshot intent** document explaining why
  it is deliberately un-released pending cross-analysis.

#### Earlier history (during initial build, pre-rename)
- Plugin was `ask-socratic` at `v0.1.0-alpha`. See the v0.1.0-alpha
  entry below for the original scope. That version number was retired
  before any distribution channel saw it — internal-only churn.

---

## [plugins/interview/ v0.1.0-alpha] — 2026-04-23

### Added
- Initial release (pre-rename, under `ask-socratic` plugin name and
  `brandonwie/ask-socratic` repo) — Path B (agent fallback) only.
- `skills/interview/SKILL.md` dual-path playbook (Step 0.5 MCP load
  tombstoned until v0.2.0).
- Seven agent prompts under `agents/`:
  - `socratic-interviewer.md` (outer role, adapted from Ouroboros)
  - `seed-closer.md` (closure audit, copied verbatim)
  - `researcher.md`, `simplifier.md`, `architect.md`, `breadth-keeper.md`
    (perspectives 1–4, copied verbatim)
  - `ontologist.md` (perspective 5 — added beyond upstream)
- Cross-agent tool mapping references:
  - `skills/interview/references/codex-tools.md`
  - `skills/interview/references/gemini-tools.md`
- `commands/interview.md` slash-command entry.
- `.claude-plugin/plugin.json` Claude Code manifest.

### Known limitations
- No persistence (Path B only — conversation-only state).
- No numerical ambiguity score — qualitative closure via `seed-closer.md`
  criteria.
- No PM variant.
- No brownfield auto-detection (user must describe the codebase
  themselves if relevant).
- Codex users get plain-text prompt fallback for structured input
  (no `AskUserQuestion` equivalent exists on Codex).

### Planned for v0.2.0
- `interview-ai` PyPI package with MCP server.
- Full numerical ambiguity gate (threshold 0.2 + per-dimension floors +
  completion streak).
- Filesystem persistence of interview state.
- Session ID handoff for downstream tooling.
- Property / integration / contract tests.

### Planned for v0.3.0
- PM variant (product-requirement interviews).
- Brownfield auto-detection.
- End-to-end smoke tests on all three agents.

---

## [plugins/interview-codex/ v0.1.0] — (Codex-generated, date unknown)

Not authored in this repo; imported from a local Codex session. See
[plugins/interview-codex/README.md](./plugins/interview-codex/README.md)
for its own notes. Pending cross-analysis against `plugins/interview/`.
