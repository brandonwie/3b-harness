# ARCHIVED — `interview-claude` v0.0.1

> **Not installable.** This snapshot was superseded by
> [`plugins/3b/`](../../../plugins/3b/) on **2026-04-23**.

## What this was

The Claude-authored, prompt-heavy variant of the Socratic interview
skill. Zero Python deps. Pure markdown: a SKILL.md playbook + seven
agent role prompts (socratic-interviewer, seed-closer, researcher,
simplifier, architect, breadth-keeper, ontologist — the last was a
Claude-original contribution beyond the Ouroboros upstream).

Slash command was `/interview-claude:interview`, then renamed to
`/3b:interview` a few hours before consolidation.

## What happened to it

| Component | Moved to |
|---|---|
| `agents/` (7 role prompts) | [`plugins/3b/agents/`](../../../plugins/3b/agents/) — now SSoT shared with the Python engine |
| `skills/interview/SKILL.md` | [`plugins/3b/skills/interview/SKILL.md`](../../../plugins/3b/skills/interview/SKILL.md) |
| `skills/interview/references/` | [`plugins/3b/skills/interview/references/`](../../../plugins/3b/skills/interview/references/) (augmented with `claude-code-tools.md`) |
| `commands/interview.md` | [`plugins/3b/commands/interview.md`](../../../plugins/3b/commands/interview.md) |
| `.claude-plugin/plugin.json` | [`plugins/3b/.claude-plugin/plugin.json`](../../../plugins/3b/.claude-plugin/plugin.json) (name updated: `3b`) |

Only this README remains as a historical marker.

## Why it was superseded

The cross-variant review cycle produced three documents at repo root —
`review-from-claude.md`, `review-from-codex.md`, and
`consolidated-plan.md` — that initially adjudicated "keep both
variants as siblings" (hybrid). The user corrected that: the real goal
was a **Single Source of Truth** plugin working across any AI agent
host, not two sibling design-axis experiments.

The revised architecture keeps both the prompt-heavy conversational
layer AND the engine-heavy programmatic layer, but inside **one
plugin** (`plugins/3b/`). Agents live once in
[`plugins/3b/agents/`](../../../plugins/3b/agents/) and are referenced
by both layers.

See the REVISION section of
[`../../../consolidated-plan.md`](../../../consolidated-plan.md) for
the full rationale.

## Pre-consolidation git history

To see this plugin's history before the move, `git log --follow` a
relocated file:

```bash
git log --follow plugins/3b/agents/socratic-interviewer.md
git log --follow plugins/3b/skills/interview/SKILL.md
```
