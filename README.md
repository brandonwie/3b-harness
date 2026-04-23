# 3b-harness

Personal workspace for the **`3b`** cross-agent plugin — built and
maintained for Claude Code, Codex, Gemini CLI, and (in principle) any
future AI agent host that can read markdown-based skills.

> Single Source of Truth layout: the plugin's agent prompts, skill
> playbooks, and (optional) Python engine live once, and are shared
> across every host via per-host manifests. No sibling duplication.

## What ships today

| Path | Purpose | Status |
|---|---|---|
| [`plugins/3b/`](./plugins/3b/) | The consolidated `3b` plugin. Ships `/3b:interview` (Socratic requirement interview) with a conversational layer (SKILL.md + 7 agent prompts) AND an optional Python engine (`engine/`) for programmatic integrators. | `v0.0.1` — pre-release |
| [`archive/plugins/`](./archive/plugins/) | Historical snapshots of the two design-axis experiments (`interview-claude-v0.0.1`, `interview-codex-v0.1.0`) that informed the consolidation. Not installable. | reference |
| [`docs/interview-skill/`](./docs/interview-skill/) | 10 markdown files analyzing the upstream Ouroboros interview skill — overview, routing decision tree, rhythm guard, ambiguity scoring, persistence, agents/perspectives, PM variant, customization, plugin build decisions (EN + KO) | reference |
| [`consolidated-plan.md`](./consolidated-plan.md) | Executable v0.0.1 → v0.1.0 plan. See the ⚠️ REVISION banner at top for the adjudication trail. | active |
| [`review-from-claude.md`](./review-from-claude.md), [`review-from-codex.md`](./review-from-codex.md) | Cross-variant self-reviews that seeded the consolidation. | reference |

## Layout

```
3b-harness/
├── plugins/
│   └── 3b/                          # the consolidated cross-agent plugin
│       ├── .claude-plugin/          # Claude Code manifest
│       ├── .codex-plugin/           # Codex manifest
│       ├── skills/interview/        # /3b:interview SKILL.md + tool mappings
│       ├── agents/                  # SSoT role prompts (7)
│       ├── commands/                # slash-command stubs
│       ├── engine/                  # optional Python layer (interview_plugin_core)
│       └── README.md
├── archive/
│   ├── README.md
│   └── plugins/
│       ├── interview-claude-v0.0.1/ # prompt-heavy variant (README-only marker)
│       └── interview-codex-v0.1.0/  # engine-heavy variant (README-only marker)
├── docs/interview-skill/            # 10 analysis docs (EN + KO where applicable)
├── consolidated-plan.md             # v0.0.1 → v0.1.0 roadmap + REVISION trail
├── review-from-claude.md            # cross-variant self-reviews
├── review-from-codex.md
├── todos.md                         # near-term backlog + adjudication block
├── CHANGELOG.md
├── LICENSE                          # MIT
└── README.md                        # this file
```

## Why ONE plugin with two layers, not two sibling plugins

The harness previously held two parallel variants (`interview-claude`
authored as a prompt-heavy markdown skill, `interview-codex` as a
Python-engine extraction). A full cross-variant review cycle produced
an initial adjudication — "keep both as canonical siblings" — that was
wrong. The real goal: **one plugin users can install that works
wherever their agent host runs**.

The revised architecture keeps both surfaces (prompt-heavy + engine-
heavy) but inside **one** plugin as two **layers**:

- **Conversational layer** — `skills/interview/SKILL.md` + the 7
  prompts under `agents/`. Zero runtime deps. Works on any AI agent
  host that reads markdown skills. This is the default path.
- **Programmatic layer** — `engine/` holds a Python package
  (`interview_plugin_core`) for CLI / server / automation integrators
  who need numeric ambiguity scoring (0–1 scale, 40/30/30 weighting),
  file-locked `InterviewState` persistence, and a pluggable
  `LLMAdapter` protocol. 60+ pytest-asyncio tests. Loads prompts
  from the shared `agents/` directory — no duplication.

The two archived variants live at `archive/plugins/` with explanatory
READMEs so the design-journey context stays visible.

## Roadmap

### v0.0.1 → v0.1.0 (current focus)

Graduation criteria documented in
[`plugins/3b/README.md`](./plugins/3b/README.md). Outstanding items
(from [`consolidated-plan.md`](./consolidated-plan.md) Workstreams B + D):

- [ ] Validate perspective-rotation decision table in SKILL.md §B.6 via
  golden transcripts (greenfield + brownfield).
- [ ] Add per-dimension observable-signal rubric to `seed-closer.md`.
- [ ] Document session-continuity transcript convention (path under
  `projects/*/actives/` + frontmatter schema).
- [ ] Write `docs/interview-skill/10-variant-comparison.md` describing
  the two-layer architecture (why one plugin, not two).
- [ ] Write `docs/interview-skill/11-direction-decision.md` as the
  formal ADR for the SSoT consolidation.
- [ ] 2+ golden transcript fixtures under
  `docs/interview-skill/fixtures/`.
- [ ] Cross-host install flow verified end-to-end on Claude Code + Codex.

### Post-v0.1.0 (speculative)

- [ ] Additional `/3b:<skill>` members as they emerge from practice —
  candidates: `/3b:simplify`, `/3b:wrap`, `/3b:review`, `/3b:brainstorm`.
  Each new skill joins `plugins/3b/skills/<name>/`, reuses the
  existing `agents/` where relevant.
- [ ] Publish `interview_plugin_core` wheel to PyPI with `force-include`
  bundling `agents/` into the wheel so pip-installed users don't need
  the filesystem SSoT path.
- [ ] Optional MCP wrapper around `engine/` for Claude Code plugin
  hosts that want server-side persistence; would load the same
  engine, no new code.

## Install

> Pre-release. Install paths below are the intended shape; verify
> before publishing.

Claude Code users:

```bash
claude plugin marketplace add brandonwie/3b-harness
claude plugin install 3b
```

Codex users: discovery via `.codex-plugin/plugin.json` inside
`plugins/3b/`. Concrete command varies by Codex CLI version.

Gemini CLI: plugin format still evolving; best-effort support via the
portable SKILL.md format.

Programmatic (Python) integrators:

```bash
cd plugins/3b/engine
uv sync --extra dev
uv run python -m pytest -q
```

See [`plugins/3b/engine/README.md`](./plugins/3b/engine/README.md) for
the `LLMAdapter` contract and the round-driving loop.

## Upstream

The `interview` skill forks from
[Q00/ouroboros](https://github.com/Q00/ouroboros). Upstream carries
the original Socratic methodology, five-perspective model, and
numerical ambiguity-scoring design. The 3b consolidation adds the
`ontologist` perspective, the cross-agent manifest layer, and the
two-layer architecture.

## Contributing

Personal workspace. Issues welcome for discussion; direct PRs are not
the expected contribution pattern.

## License

MIT. See [LICENSE](./LICENSE).

## See also

- [Ouroboros](https://github.com/Q00/ouroboros) — upstream source.
- [3b](https://github.com/brandonwie/3b) (private, personal) — the
  knowledge system this harness is adjacent to.
