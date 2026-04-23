# Interview Codex

Portable Socratic interview extraction from Ouroboros.

## What is included

- `skills/interview/SKILL.md`
  - A Codex-facing portable interview skill with no Ouroboros-specific MCP boot flow.
- `src/interview_plugin_core/`
  - A reusable Python core for interview state, question generation, prompt loading, brownfield detection, and ambiguity scoring.
- `tests/`
  - Ported unit coverage for the extracted portable subset.

## What is intentionally excluded from v1

- Ouroboros plugin version checks and self-update flow
- Deferred-tool loading and MCP handler glue
- Seed generation pipeline coupling
- PM interview variant

## Runtime model

The package keeps the original `LLMAdapter` protocol so other runtimes can wrap their own model client. The default model string is read from `INTERVIEW_CODEX_MODEL` and otherwise falls back to `"default"`.

Prompt overrides are supported through `INTERVIEW_CODEX_PROMPTS_DIR`. State persistence defaults to `~/.interview-codex/data` and can be overridden with `INTERVIEW_CODEX_STATE_DIR`.

## Running tests

```bash
cd plugins/interview-codex
python -m pytest -q
```
