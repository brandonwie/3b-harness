# 3b-harness

Personal workspace for AI-agent extensions — **plugins**, **skills**,
**agents**, and (soon) **MCP servers** — built and maintained for
Claude Code, Codex, and Gemini CLI.

> Not a single plugin. A harness: the container where the primary
> implementations, alternate variants, analysis docs, and shared
> tooling all live together so one can be compared against another and
> the best design promoted.

## Layout

```
3b-harness/
├── plugins/                         # one subdir per plugin
│   ├── interview-claude/            # Claude-session authored snapshot (v0.0.1, not-for-use)
│   └── interview-codex/             # Codex-generated snapshot (v0.1.0, not-for-use)
├── docs/                            # design analysis + cross-variant reports
│   └── interview-skill/             # 10 analysis docs informing the interview plugins
├── CHANGELOG.md                     # harness + plugin changes
├── LICENSE                          # MIT
└── README.md                        # this file
```

## What's inside right now

| Path | Purpose | Status |
|---|---|---|
| [`plugins/interview-claude/`](./plugins/interview-claude/) | Claude-session authored snapshot — cross-agent (Claude / Codex / Gemini), Path B only, no scoring core | `v0.0.1` — snapshot, not-for-use pending comparison |
| [`plugins/interview-codex/`](./plugins/interview-codex/) | Codex-generated snapshot — portable interview with Python scoring core, skills, tests | `v0.1.0` — snapshot, not-for-use pending comparison |
| [`docs/interview-skill/`](./docs/interview-skill/) | 10 markdown files analyzing the upstream Ouroboros interview skill — overview, routing decision tree, rhythm guard, ambiguity scoring, state persistence, agents/perspectives, PM variant, customization guide, plugin build decisions (EN + KO) | reference |

Both plugin snapshots are deliberately un-released. Neither is the
"winner" yet — they exist side-by-side so the two approaches can be
diffed and the best features merged. See the Roadmap below.

## Why a harness, not separate repos?

- **Cross-analysis.** Two implementations of the "same" skill — one
  hand-built from analysis, one LLM-generated — side by side. Easier
  to compare, diff, and learn from differences.
- **Shared context.** The analysis docs under `docs/` inform every
  plugin here; keeping them in-repo means they are always current with
  the implementations.
- **Future MCP servers.** Planned: `mcp/` directory for Python MCP
  servers that back the richer plugin modes (e.g., `interview-ai`
  package backing `plugins/interview/` Path A).
- **One install surface.** Users can clone one thing, pick what they
  want.

## Roadmap

### Cross-variant work (current focus)
- [x] `plugins/interview-claude/` **v0.0.1** snapshot — not-for-use.
- [x] `plugins/interview-codex/` **v0.1.0** snapshot — not-for-use.
- [ ] **Comparison report** — diff both snapshots across design axes
  (cross-agent portability, scoring, persistence, prompt rotation, test
  strategy). Land in `docs/interview-skill/10-variant-comparison.md`.
- [ ] Merge best features into a single promoted plugin (new name TBD
  post-comparison); keep the other as reference.

### Post-comparison roadmap (applies to whichever plugin wins)
- [ ] **v0.1.0** — first usable release (cross-agent, Path B).
- [ ] **v0.2.0** — Path A (MCP) via an `interview-ai` PyPI package.
  Full numerical ambiguity gate, filesystem persistence, session_id
  handoff. See
  [docs/interview-skill/09-plugin-build-decisions.md](./docs/interview-skill/09-plugin-build-decisions.md).
- [ ] **v0.3.0** — PM variant (product-requirement interviews) +
  brownfield auto-detection.

### Additional plugins (TBD)
- [ ] Potential candidates: skill for /edit workflow, /simplify post-PR
  review, codebase summary, custom /ralph loop, /wrap variants, etc.

## Install (per plugin)

Each plugin under `plugins/` is independently installable. See its
`README.md` for per-agent instructions:

- [plugins/interview-claude/README.md](./plugins/interview-claude/README.md)
- [plugins/interview-codex/README.md](./plugins/interview-codex/README.md)

Claude Code users can install the marketplace (single `claude plugin
marketplace add brandonwie/3b-harness`) and then pick per-plugin
installs.

## Contributing

This is a personal harness. Issues welcome for discussion, but direct
PRs are not the expected contribution pattern — the harness evolves as
the maintainer's understanding of the agent landscape evolves.

## License

MIT. See [LICENSE](./LICENSE).

Each plugin may credit its upstream separately. `plugins/interview/`
credits [Q00/ouroboros](https://github.com/Q00/ouroboros).
`plugins/interview-codex/` credits the same upstream via its own
README.

## See also

- [Ouroboros](https://github.com/Q00/ouroboros) — upstream source of
  the interview skill analyzed and ported here.
- [3b](https://github.com/brandonwie/3b) (private, personal) — the
  knowledge system this harness is adjacent to.
