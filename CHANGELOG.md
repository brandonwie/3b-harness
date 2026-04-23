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

### `plugins/interview/`

#### Changed
- Renamed plugin identity from `ask-socratic` to `interview` to match
  the folder name and parallel the Codex variant's naming convention.
  Slash command is now `/interview:interview`.
- Updated `plugin.json` repository + homepage URLs to the new
  `brandonwie/3b-harness` location.
- SKILL.md references to `/ask-socratic:interview` updated to
  `/interview:interview`; references to `ask-socratic-ai` package
  (Phase 2) updated to `interview-ai`.

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
