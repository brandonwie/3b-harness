---
tags: [ouroboros, interview, customization, fork-guide, matrix]
created: 2026-04-23
updated: 2026-04-23
status: in-progress
related:
  - ./01-overview.md
  - ./02-routing-decision-tree.md
  - ./03-dialectic-rhythm.md
  - ./04-ambiguity-scoring.md
  - ./05-state-and-persistence.md
  - ./06-agents-and-roles.md
  - ./07-pm-variant.md
when_used: "Use this doc as your index when planning a change. Every row points to the single file + location where that change lives, and to the explainer doc that covers the theory."
---

# 08 — Customization guide

This is the operational companion to the rest of this folder. The
theory lives in docs 01–07; this one is the lookup table: you decide
what behaviour to change, find the row, and go edit.

## How to use this doc

1. Pick the change you want in the **goal** column.
2. Open the listed file at the listed location.
3. Skim the listed related doc for context if you need it.
4. Make the change, then run the verification steps at the bottom
   of this doc.

All file paths are absolute. Line numbers are accurate as of
2026-04-23; if source has moved, grep the shown constant or header to
relocate.

## Fork matrix — behaviour → source

### Numerical gates (most common change)

| Goal | File | Location | Related doc |
|------|------|----------|-------------|
| Change the seed-ready threshold (0.2) | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/bigbang/ambiguity.py` | `AMBIGUITY_THRESHOLD` at line 30 | [./04-ambiguity-scoring.md](./04-ambiguity-scoring.md) |
| Change when the seed-closer starts running (0.25) | same | `SEED_CLOSER_ACTIVATION_THRESHOLD` at line 31 | 04 |
| Require more consecutive seed-ready rounds before auto-complete | same | `AUTO_COMPLETE_STREAK_REQUIRED` at line 32 | 04 |
| Raise/lower any per-dimension clarity floor | same | Lines 35–38 (`GOAL_CLARITY_FLOOR` etc.) | 04 |
| Change the greenfield weights (40/30/30) | same | Lines 41–43 | 04 |
| Change the brownfield weights (35/25/25/15) | same | Lines 46–49 | 04 |
| Tighten scorer determinism | same | `SCORING_TEMPERATURE` at line 52 | 04 |
| Allow scoring to use more tokens | same | `MAX_TOKEN_LIMIT` at line 55 | 04 |
| Change default scorer retry count (10) | same | `AmbiguityScorer.max_retries` at line 282 | 04 |

### Routing behaviour

| Goal | File | Location | Related doc |
|------|------|----------|-------------|
| Change what makes a question PATH 1a auto-confirmable | `/Users/brandonwie/dev/personal/ouroboros/skills/interview/SKILL.md` | Section `### Path A: MCP Mode (Preferred)` → `PATH 1a — Auto-confirm` (lines 118–139) | [./02-routing-decision-tree.md](./02-routing-decision-tree.md) |
| Change confirmation question template | same | `PATH 1b` template at lines 143–156 | 02 |
| Add a new answer-provenance prefix | same | PATH sections 108–198 + prefix table | 02 |
| Change the "when in doubt" default (PATH 2) | same | Line 198 | 02 |
| Change retry count or fallback trigger | same | `#### Retry on Failure` (lines 253–261) | 02 |
| Change the Path B pre-scan file list | same | `### Path B: Plugin Fallback` (lines 265–282) | 02 |

### Rhythm guard

| Goal | File | Location | Related doc |
|------|------|----------|-------------|
| Change the "3 consecutive non-user" threshold | `/Users/brandonwie/dev/personal/ouroboros/skills/interview/SKILL.md` | `#### Dialectic Rhythm Guard` at lines 238–251 | [./03-dialectic-rhythm.md](./03-dialectic-rhythm.md) |
| Change which prefixes reset the counter | same | Same section (rhythm rules) | 03 |
| Change how the counter handles PATH 3 | same | Same section | 03 |

### Closure audit

| Goal | File | Location | Related doc |
|------|------|----------|-------------|
| Override the Seed-ready Acceptance Guard behaviour | `/Users/brandonwie/dev/personal/ouroboros/skills/interview/SKILL.md` | Lines 218–231 (accept guard + override wording) | [./03-dialectic-rhythm.md](./03-dialectic-rhythm.md) |
| Change the canonical closure criteria | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/agents/seed-closer.md` | Whole file (affects **both** the LLM perspective and the session-level audit — see [./06-agents-and-roles.md](./06-agents-and-roles.md)) | 03, 06 |
| Add/remove closure audit questions | same | `## YOUR QUESTIONS` section (lines 46–54) | 03 |

### Question generation behaviour

| Goal | File | Location | Related doc |
|------|------|----------|-------------|
| Change core interviewer identity / tone | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/agents/socratic-interviewer.md` | Whole file | [./06-agents-and-roles.md](./06-agents-and-roles.md) |
| Change breadth-check behaviour | same | Lines 39–44 (breadth control) | 06 |
| Change stop conditions | same | Lines 46–49 | 03, 06 |
| Tune the researcher perspective | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/agents/researcher.md` | Whole file — `system_prompt`, `## YOUR APPROACH`, `## YOUR QUESTIONS` are all loaded | 06 |
| Tune the simplifier perspective | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/agents/simplifier.md` | Whole file | 06 |
| Tune the architect perspective | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/agents/architect.md` | Whole file | 06 |
| Tune the breadth-keeper perspective | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/agents/breadth-keeper.md` | Whole file | 06 |
| Tune the seed-closer perspective | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/agents/seed-closer.md` | Whole file (same file, both perspective and audit usage) | 03, 06 |
| Add a new perspective to the rotation | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/bigbang/interview.py` | `InterviewPerspective` enum at lines 42–49 + mapping at lines 70–76 + create agent md file | 06 |
| Swap the perspective loader | same | `_load_interview_perspective_strategies` at lines 62–87 | 06 |

### State and persistence

| Goal | File | Location | Related doc |
|------|------|----------|-------------|
| Change the interview state storage directory | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/bigbang/interview.py` | `InterviewEngine.state_dir` default at line 234 | [./05-state-and-persistence.md](./05-state-and-persistence.md) |
| Change the interview state filename pattern | same | `_state_file_path` at lines 243–252 (`f"interview_{interview_id}.json"`) | 05 |
| Add a field to persisted state | same | `InterviewState` Pydantic model at lines 114–143 | 05 |
| Change seed-ready mirror threshold | same | `_SEED_READY_THRESHOLD` at line 150 (must match `ambiguity.py`'s `AMBIGUITY_THRESHOLD`) | 04, 05 |
| Change `MIN_ROUNDS_BEFORE_EARLY_EXIT` (3) | same | Line 35 | 05 |
| Change `DEFAULT_INTERVIEW_ROUNDS` (10) | same | Line 36 | 05 |
| Change event types emitted | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/events/interview.py` | Whole file (four event factories) | 05 |

### MCP surface

| Goal | File | Location | Related doc |
|------|------|----------|-------------|
| Change the MCP tool input schema | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/mcp/tools/authoring_handlers.py` | `InterviewHandler.definition` at lines 887–942 | 05 |
| Change the action dispatch logic | same | `InterviewHandler.handle` at lines 944–968 | 05 |
| Change the "seed-ready refusal" message | same | `_ambiguity_gate_response` at lines 793–824 (`Cannot complete yet — …`) | 05 |
| Change the completion response / meta | same | `_complete_interview_response` at lines 826–885 | 05 |
| Change what gets cached after each scoring call | same | `_score_interview_state` at lines 761–791 | 04, 05 |
| Change plugin-mode subagent behaviour | same | Subagent dispatch in `handle()` | 05 |

### PM variant (fork template)

| Goal | File | Location | Related doc |
|------|------|----------|-------------|
| Change the PM system prompt prefix | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/bigbang/pm_interview.py` | `_PM_SYSTEM_PROMPT_PREFIX` at lines 55–60 | [./07-pm-variant.md](./07-pm-variant.md) |
| Change the PM opening question | same | `_OPENING_QUESTION` at lines 62–66 | 07 |
| Change the PMSeed extraction schema | same | `_EXTRACTION_SYSTEM_PROMPT` at lines 68–85 | 07 |
| Change the PM seed output directory | same | `_SEED_DIR` at line 54 | 07 |
| Change classification categories | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/bigbang/question_classifier.py` | `ClassifierOutputType` enum | 07 |
| Change PM metadata storage path | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/mcp/tools/pm_handler.py` | `_meta_path` at lines 71–74 (`pm_meta_{session_id}.json`) | 07 |
| Change PM completion gate | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/bigbang/pm_completion.py` | Whole file | 07 |
| Change PM document renderer | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/bigbang/pm_document.py` | Whole file | 07 |

### Command surface

| Goal | File | Location | Related doc |
|------|------|----------|-------------|
| Change the `/ouroboros:interview` entry stub | `/Users/brandonwie/dev/personal/ouroboros/commands/interview.md` | Whole file (7 lines) | [./01-overview.md](./01-overview.md) |
| Change the `ooo interview` routing | `/Users/brandonwie/dev/personal/ouroboros/CLAUDE.md` | `## ooo Commands (Dev Mode)` table | 01 |
| Change top-level SKILL.md description / trigger keywords | `/Users/brandonwie/dev/personal/ouroboros/skills/interview/SKILL.md` | Frontmatter at lines 1–8 + `**Trigger keywords:**` at line 21 | 01 |

### Downstream contract

| Goal | File | Location | Related doc |
|------|------|----------|-------------|
| Change the shape of what interview hands off | `/Users/brandonwie/dev/personal/ouroboros/src/ouroboros/core/seed.py` | `Seed` model at lines 155–229 and `SeedMetadata` above | 01 |
| Change default ambiguity score on the seed | same | `SeedMetadata.ambiguity_score` default 0.15 | 01, 04 |

## Minimal fork checklist — standalone extraction

If you are copying the skill out of Ouroboros into your own
plugin/repo, this is the minimum set of files you need. It assumes
you keep Path A (MCP). For Path B only (no MCP server), drop the
handler and scorer files.

**Must copy** (skill definition + entry):

- `skills/interview/SKILL.md`
- `commands/interview.md`

**Must copy** (agents used as prompt data):

- `src/ouroboros/agents/socratic-interviewer.md`
- `src/ouroboros/agents/seed-closer.md`
- `src/ouroboros/agents/researcher.md`
- `src/ouroboros/agents/simplifier.md`
- `src/ouroboros/agents/architect.md`
- `src/ouroboros/agents/breadth-keeper.md`
- `src/ouroboros/agents/loader.py` (the loader used by `_load_interview_perspective_strategies`)

**Must copy if keeping Path A**:

- `src/ouroboros/bigbang/interview.py`
- `src/ouroboros/bigbang/ambiguity.py`
- `src/ouroboros/events/interview.py`
- `src/ouroboros/events/base.py`
- `src/ouroboros/mcp/tools/authoring_handlers.py` (at minimum, the
  `InterviewHandler` class + its dependencies)
- `src/ouroboros/mcp/types.py`, `mcp/errors.py`
- `src/ouroboros/providers/base.py`, the provider factory you want,
  and the `LLMAdapter` you use
- `src/ouroboros/core/errors.py`, `core/types.py`,
  `core/file_lock.py`, `core/security.py`, `core/seed.py`
- `src/ouroboros/config.py` (`get_clarification_model`)
- `src/ouroboros/persistence/event_store.py`
- `src/ouroboros/bigbang/brownfield.py` + `explore.py` (only if you
  want brownfield support)

**Can leave behind** (not used by interview):

- `ontologist.md`, `contrarian.md`, `advocate.md`,
  `consensus-reviewer.md`, `judge.md`, `evaluator.md`,
  `qa-judge.md`, `hacker.md`, `semantic-evaluator.md`,
  `codebase-explorer.md`, `code-executor.md`,
  `analysis-agent.md`, `research-agent.md`, `ontology-analyst.md`,
  `seed-architect.md`
- `pm_interview.py`, `pm_seed.py`, `pm_document.py`,
  `pm_completion.py`, `pm_handler.py`,
  `question_classifier.py` (the PM variant) — unless you want it as
  a fork template (see [./07-pm-variant.md](./07-pm-variant.md))
- All skills other than `interview`

## Test touchpoints

When you change something, these are the canonical tests to run:

- `/Users/brandonwie/dev/personal/ouroboros/tests/unit/bigbang/test_interview.py`
- `/Users/brandonwie/dev/personal/ouroboros/tests/unit/bigbang/test_pm_interview.py`
- `tests/unit/bigbang/test_ambiguity.py` (if present) — for scorer
  changes
- `tests/unit/mcp/...` — for handler changes

Run with `pytest tests/unit/bigbang/ -k interview` from the project
root.

## Verification after a change

1. Run the relevant unit tests above.
2. `ooo interview "test request"` in a throwaway cwd — check the
   first question reflects your change.
3. If you changed scoring, `ooo status <session_id>` (if the skill
   supports it) or inspect `~/.ouroboros/data/interview_{id}.json`
   and confirm `ambiguity_score` shape is what you expect.
4. If you changed the closure audit, run an interview to seed-ready
   and check both the MCP `meta.seed_ready` and the session-level
   acceptance language.
5. If you changed a perspective md file, delete the process and
   re-run — the loader is `@lru_cache(maxsize=1)` so a hot reload
   won't pick it up mid-process.

## Open questions for full fork

When you move from "customise inside Ouroboros" to "fork into my
own repo", decide these explicitly:

- **Keep the MCP path or ship agent-only?** MCP is richer but adds
  Python runtime, state file, scorer LLM call. Agent-only is
  simpler but loses session_id + persistence.
- **Keep the PM variant or start greenfield-only?** PM is large
  (~1200 lines). If your fork's audience is developers, skip it.
- **Fork target directory — separate repo, or subfolder?** Separate
  repo is cleaner; subfolder keeps everything in a known place.
- **Package manager — match upstream (uv/pipx/pip) or start fresh?**
  Matching simplifies the update step
  (see [./02-routing-decision-tree.md](./02-routing-decision-tree.md))
  but couples you to upstream's choices.

None of these are decided here — they belong in whatever design doc
kicks off the actual fork.
