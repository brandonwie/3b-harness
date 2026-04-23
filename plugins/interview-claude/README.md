# interview-claude

Snapshot of a Socratic-interview plugin built from analysis of the upstream
[Ouroboros](https://github.com/Q00/ouroboros) `interview` skill.

> **Status:** `v0.0.1` — **not-for-use snapshot**. Held side-by-side with
> [`../interview-codex/`](../interview-codex/) pending a cross-variant
> analysis. After that comparison one of the two (or a merged best-of)
> will be promoted. Do not install this yet.

## Snapshot intent

This folder captures one interpretation of "how to extract and port the
interview skill":

- Claude-session-authored, analysis-driven.
- Cross-agent (Claude Code / Codex / Gemini CLI) skill format from day
  one.
- Path B (agent fallback) only in this snapshot — Path A (MCP) deferred
  until after the cross-variant decision.
- Seven agent prompts: six inherited (socratic-interviewer, seed-closer,
  researcher, simplifier, architect, breadth-keeper) plus the ontologist
  (added beyond upstream's default five).

The alternate in [`../interview-codex/`](../interview-codex/) is a
Codex-generated portable extraction that already ships a Python scoring
core and its own skill. The two are deliberately different in scope so
we can compare approaches.

## Why you can't use it yet

1. Slash command name `/interview-claude:interview` is a placeholder —
   final naming decided post-comparison.
2. No numerical ambiguity gate (scoring lives in the `interview-codex`
   variant's Python core, not ported here yet).
3. No persistence — Path B only; every interview is conversation-only.
4. Docs reference `interview-ai` as the Phase 2 package name, but that
   package is not yet written.

After cross-analysis, the chosen direction will get a real v0.1.0
release and install instructions.

## How to read this snapshot

- [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json) —
  manifest; note the `keywords: [..., "snapshot", "not-for-use"]` flag.
- [`skills/interview/SKILL.md`](./skills/interview/SKILL.md) — dual-path
  playbook (Path A tombstoned, Path B primary). Start here for how the
  skill actually behaves.
- [`agents/`](./agents/) — the seven role prompts loaded per round.
- [`commands/interview.md`](./commands/interview.md) — slash-command
  entry stub.

## Design reference

The full analysis that informed this snapshot is in
[`../../docs/interview-skill/`](../../docs/interview-skill/). Start with
[`README.md`](../../docs/interview-skill/README.md) and the fork
decision tree.

Key decision doc:
[`09-plugin-build-decisions.md`](../../docs/interview-skill/09-plugin-build-decisions.md)
(English) or
[`09-plugin-build-decisions.ko.md`](../../docs/interview-skill/09-plugin-build-decisions.ko.md)
(Korean).

Note: the docs were written when the plugin name was `ask-socratic` and
later `interview`. The final name here is `interview-claude` to pair
visibly with `interview-codex`.

## File layout

```
plugins/interview-claude/
├── .claude-plugin/plugin.json       # manifest (name: interview-claude, v0.0.1)
├── commands/interview.md            # slash-command entry stub
├── skills/interview/
│   ├── SKILL.md                     # dual-path playbook
│   └── references/
│       ├── codex-tools.md           # Claude→Codex tool mapping
│       └── gemini-tools.md          # Claude→Gemini tool mapping
├── agents/                          # 7 role prompts
│   ├── socratic-interviewer.md
│   ├── seed-closer.md
│   ├── researcher.md
│   ├── simplifier.md
│   ├── architect.md
│   ├── breadth-keeper.md
│   └── ontologist.md
└── README.md                        # this file
```

## Upstream

Forked from the `interview` skill in
[Q00/ouroboros](https://github.com/Q00/ouroboros). Upstream carries the
original Socratic methodology, five-perspective model, and numerical
ambiguity-scoring design.

## Changelog

See the root [CHANGELOG.md](../../CHANGELOG.md) for both harness-level
and plugin-level entries.

## License

MIT. See [LICENSE](../../LICENSE).
