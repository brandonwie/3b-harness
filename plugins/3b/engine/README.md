# 3b Engine (`interview_plugin_core`)

Optional Python layer inside [`plugins/3b/`](../README.md) for
programmatic integrators. The conversational `/3b:interview` skill
(markdown-only) does NOT require this engine — ignore this folder if
you only consume the plugin through Claude Code, Codex, or Gemini CLI.

## When to use

Use the engine when you need:

- Async interview orchestration under your own LLM client
  (`LLMAdapter` protocol).
- Numeric ambiguity scoring (0–1 scale, 40/30/30 weighting across
  goal / constraints / criteria).
- Persisted `InterviewState` (file-locked, resume across process
  restarts).
- Programmatic access to perspectives, rounds, closure signals.

## Source of truth

Agent prompts live at [`../agents/`](../agents/) — one SSoT shared
with the conversational skill. The engine's `prompt_loader` resolves
in three tiers:

1. `INTERVIEW_CODEX_PROMPTS_DIR` env var override.
2. `plugins/3b/agents/` filesystem (default in repo checkouts).
3. `importlib.resources` bundle (fallback for pip-installed wheels
   when `force-include` bundles the prompts).

## Install

```bash
cd plugins/3b/engine
uv sync
```

## Test

```bash
cd plugins/3b/engine
uv run python -m pytest -q
```

## Runtime integration

See [`../README.md`](../README.md) "Programmatic layer" for the full
`LLMAdapter` contract, engine construction, round-driving loop, and
enriched answer prefixes (`[from-code]`, `[from-user]`,
`[from-research]`).

## Scope (intentional exclusions)

- Ouroboros plugin version checks and self-update flow.
- Deferred-tool loading and MCP handler glue.
- Seed generation pipeline coupling.
- PM interview variant.
