# ARCHIVED — `interview-codex` v0.1.0

> **Not installable.** This snapshot was superseded by
> [`plugins/3b/`](../../../plugins/3b/) on **2026-04-23**.

## What this was

The Codex-generated, engine-heavy variant of the Socratic interview
skill. A portable Python extraction from Ouroboros:

- `src/interview_plugin_core/` — async interview orchestrator with
  `LLMAdapter` Protocol, file-locked state persistence, and numeric
  ambiguity scoring (0–1 scale, 40/30/30 weighting across goal /
  constraints / criteria).
- `tests/` — 60 pytest-asyncio tests covering state transitions,
  persistence, brownfield detection, prompt behavior.
- `.codex-plugin/plugin.json` — Codex host manifest.
- `skills/interview/SKILL.md` — portable Codex-facing skill.
- `src/interview_plugin_core/assets/` — bundled copies of 6 agent
  prompts (did not include `ontologist.md`).

## What happened to it

| Component | Moved to |
|---|---|
| `src/interview_plugin_core/` (Python engine) | [`plugins/3b/engine/src/interview_plugin_core/`](../../../plugins/3b/engine/src/interview_plugin_core/) |
| `tests/` | [`plugins/3b/engine/tests/`](../../../plugins/3b/engine/tests/) — 60 tests still pass |
| `pyproject.toml`, `uv.lock` | [`plugins/3b/engine/`](../../../plugins/3b/engine/) |
| `.codex-plugin/plugin.json` | [`plugins/3b/.codex-plugin/plugin.json`](../../../plugins/3b/.codex-plugin/plugin.json) (name updated: `3b`) |
| `skills/` | absorbed into [`plugins/3b/skills/`](../../../plugins/3b/skills/) |
| `src/interview_plugin_core/assets/` | **deleted** — de-duplicated against [`plugins/3b/agents/`](../../../plugins/3b/agents/) via filesystem SSoT; the prompt loader now reads from `plugins/3b/agents/` (Tier 2) with `importlib.resources` kept as Tier 3 wheel fallback. |

Only this README remains as a historical marker.

## Consolidation-time engine changes

Applied during the move (not in the original snapshot):

1. `prompt_loader._SSOT_AGENTS_DIR` added — default resolves to
   `plugins/3b/agents/` via `Path(__file__).resolve().parents[3]`.
2. `assets/` directory deleted; engine now requires either the env
   override, the filesystem SSoT, or (future) a build-time
   `force-include` that bundles agents into the wheel.
3. `InterviewPerspective.ONTOLOGIST` added to the enum and wired into
   `_load_interview_perspective_strategies()` — closes the gap flagged
   by both cross-variant reviews.
4. `start_interview()` docstring corrected to remove the false auto-
   exploration claim (landed pre-consolidation, preserved through
   move).

## Why it was superseded

See [`../../README.md`](../../README.md) and the REVISION section of
[`../../../consolidated-plan.md`](../../../consolidated-plan.md).

## Pre-consolidation git history

```bash
git log --follow plugins/3b/engine/src/interview_plugin_core/interview.py
git log --follow plugins/3b/engine/tests/test_interview.py
```
