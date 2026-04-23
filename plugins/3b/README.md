# 3b — the consolidated 3b-harness plugin

Single Source of Truth for the harness. One plugin, many skills. Works
across Claude Code, Codex, Gemini CLI, and any future AI agent host
that can read markdown-based skills.

> **Status:** `v0.0.1` — **pre-release**. Lifted from the cross-variant
> review cycle (see [`/archive/plugins/`](../../archive/plugins/) for
> the superseded `interview-claude-v0.0.1` and `interview-codex-v0.1.0`
> snapshots plus the adjudication that led here).

## Current skills

| Slash | What it does | File |
|---|---|---|
| `/3b:interview` | Socratic interview that turns a vague request into a concrete spec via rotating-perspective questioning | [`skills/interview/SKILL.md`](./skills/interview/SKILL.md) |

More skills will join under `/3b:<name>` as the harness grows.

## Two layers, one plugin

### Conversational layer (default)

The primary skill runs as a pure-markdown playbook. The host
conversation IS the engine. Zero runtime dependencies. Any agent host
that can read this plugin's files can run the skill.

**Entry points:**

- [`skills/interview/SKILL.md`](./skills/interview/SKILL.md) — the
  playbook itself. Hosts read this and follow it step-by-step.
- [`agents/`](./agents/) — the seven role prompts loaded per round
  (socratic-interviewer, seed-closer, researcher, simplifier,
  architect, breadth-keeper, ontologist).
- [`skills/interview/references/`](./skills/interview/references/) —
  per-host tool-name mappings (what Claude Code calls `Read` and
  `Write`, Codex and Gemini call something slightly different).

### Programmatic layer (optional)

For integrators building CLIs, servers, or automations on top of this
skill, the [`engine/`](./engine/) subdir ships a Python package
(`interview_plugin_core`) that wraps the same agents + playbook as an
async engine with:

- Pluggable `LLMAdapter` protocol (runtime-agnostic).
- Numeric ambiguity scoring (0–1 scale, 40/30/30 weights across goal /
  constraints / criteria).
- File-locked `InterviewState` persistence.
- 60+ pytest-asyncio tests.

The engine loads its prompts from the same [`agents/`](./agents/)
directory used by the conversational layer — there is no duplication.

**If you don't need programmatic access, ignore the `engine/` folder
entirely.**

## Per-host manifests

| Host | Manifest | Discovery |
|---|---|---|
| Claude Code | [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json) | Standard plugin marketplace |
| Codex | [`.codex-plugin/plugin.json`](./.codex-plugin/plugin.json) | Codex skill loader |
| Gemini CLI | (future) | TBD — plugin format evolving |

All manifests declare the same plugin `name: "3b"` and point to the
same `skills/` directory. The only per-host difference is the manifest
schema itself.

## Graduation criterion (v0.0.1 → v0.1.0)

Bump to `v0.1.0` when ready-to-use-out-of-the-box as a harness library:

1. Perspective-rotation decision table in SKILL.md is empirically
   validated (golden transcripts produce expected agent activations).
2. `seed-closer.md` has per-dimension observable-signal rubric.
3. Session continuity convention (transcript path under
   `projects/*/actives/`) is documented and exercised.
4. Cross-host install flow tested end-to-end on Claude Code + Codex
   (Gemini support remains best-effort until its plugin format
   stabilizes).
5. At least 2 golden transcript fixtures under
   `docs/interview-skill/fixtures/` (greenfield + brownfield).
6. Python engine's ontologist perspective lands and its tests pass.

## File layout

```
plugins/3b/
├── .claude-plugin/plugin.json        # Claude Code manifest
├── .codex-plugin/plugin.json         # Codex manifest
├── commands/
│   └── interview.md                  # /3b:interview slash stub
├── skills/
│   └── interview/
│       ├── SKILL.md                  # playbook
│       └── references/               # per-host tool mappings
│           ├── claude-code-tools.md
│           ├── codex-tools.md
│           └── gemini-tools.md
├── agents/                           # SSoT role prompts (7)
│   ├── socratic-interviewer.md
│   ├── seed-closer.md
│   ├── researcher.md
│   ├── simplifier.md
│   ├── architect.md
│   ├── breadth-keeper.md
│   └── ontologist.md
├── engine/                           # optional Python engine
│   ├── pyproject.toml
│   ├── src/interview_plugin_core/
│   └── tests/
└── README.md                         # this file
```

## Upstream

Forked from the `interview` skill in
[Q00/ouroboros](https://github.com/Q00/ouroboros). Upstream carries
the original Socratic methodology, five-perspective model, and
numerical ambiguity-scoring design. The 3b consolidation adds the
ontologist perspective and the cross-agent manifest layer.

## License

MIT. See [../../LICENSE](../../LICENSE).
