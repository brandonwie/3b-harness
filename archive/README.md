# `archive/` — superseded plugin snapshots

Read-only historical record. Preserved for documentation, not for
installation.

## What's in here

| Path | What it was | Superseded on | Why |
|---|---|---|---|
| [`plugins/interview-claude-v0.0.1/`](./plugins/interview-claude-v0.0.1/) | Claude-authored prompt-heavy snapshot of the Socratic interview skill | 2026-04-23 | Folded into [`../plugins/3b/`](../plugins/3b/) as the conversational layer (agents + SKILL.md + commands). |
| [`plugins/interview-codex-v0.1.0/`](./plugins/interview-codex-v0.1.0/) | Codex-generated portable Python extraction with numeric ambiguity scoring and 60 pytest-asyncio tests | 2026-04-23 | Python engine folded into [`../plugins/3b/engine/`](../plugins/3b/engine/) as the optional programmatic layer; `.codex-plugin/` manifest moved to [`../plugins/3b/.codex-plugin/`](../plugins/3b/.codex-plugin/); 6 shared agent prompts de-duplicated against [`../plugins/3b/agents/`](../plugins/3b/agents/). |

## Why archive rather than delete

Both snapshots were **deliberately-built design-axis experiments**:
`interview-claude` pushed interview discipline into markdown prompts
(host conversation IS the engine); `interview-codex` pushed it into a
Python engine with a pluggable `LLMAdapter`. Comparing them produced
genuine learning that informed the consolidated design. Keeping the
comparison trail visible matters more than tree tidiness.

## Cross-variant review artifacts

The audit cycle that drove consolidation lives at repo root:

- [`../review-from-claude.md`](../review-from-claude.md) — Claude
  reviewing `interview-claude` against `interview-codex`.
- [`../review-from-codex.md`](../review-from-codex.md) — Codex
  reviewing `interview-codex` against `interview-claude`.
- [`../consolidated-plan.md`](../consolidated-plan.md) — reconciliation
  plus the REVISION section noting why "keep both variants" was the
  wrong adjudication and how SSoT consolidation replaced it.

## Can I still run anything in here?

No. Manifests still exist, but:

- `interview-claude-v0.0.1/` is a README-only shell — its
  `.claude-plugin/`, `agents/`, `skills/`, and `commands/` dirs were
  `git mv`'d out.
- `interview-codex-v0.1.0/` is a README-only shell — its Python
  source, tests, pyproject.toml, and `.codex-plugin/` manifest were
  `git mv`'d out.

If you need the live plugin, use [`../plugins/3b/`](../plugins/3b/).
If you need the pre-consolidation code, `git log --follow` a file in
`plugins/3b/` back through the rename.
