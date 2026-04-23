# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-alpha] — 2026-04-23

### Added
- Initial release — Path B (agent fallback) only.
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
- MIT license + upstream Ouroboros credit.

### Known limitations
- No persistence (Path B only — conversation-only state).
- No numerical ambiguity score — qualitative closure via `seed-closer.md`
  criteria.
- No PM variant.
- No brownfield auto-detection (user must describe the codebase
  themselves if relevant).
- Codex users get plain-text prompt fallback for structured input
  (no `AskUserQuestion` equivalent exists on Codex).

## [Unreleased]

### Planned for v0.2.0
- `ask-socratic-ai` PyPI package with MCP server.
- Full numerical ambiguity gate (threshold 0.2 + per-dimension floors +
  completion streak).
- Filesystem persistence of interview state.
- Session ID handoff for downstream tooling.
- Property / integration / contract tests.

### Planned for v0.3.0
- PM variant (product-requirement interviews).
- Brownfield auto-detection (auto-scan `pyproject.toml`, `package.json`,
  etc. on interview start).
- End-to-end smoke tests on all three agents.
