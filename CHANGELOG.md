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
