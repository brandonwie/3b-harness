# interview plugin

Socratic interview that turns vague requests into concrete specifications.
Cross-agent: Claude Code, Codex, Gemini CLI.

> **Status:** `v0.1.0-alpha` — Path B (agent fallback) only. Path A (MCP
> server via `interview-ai` package) arriving in `v0.2.0`.

Part of the [3b-harness](../../README.md) workspace. A Codex-generated
alternative lives at [`../interview-codex/`](../interview-codex/) for
cross-analysis — the two approaches will be compared and merged.

## What it does

Takes a vague topic ("build a payment module", "add search to my app")
and guides you through a structured Socratic interview until the
requirements are concrete enough to act on. Outputs a YAML-frontmatter
+ markdown summary (goal / constraints / acceptance criteria / non-goals
/ open questions).

## How it works (short version)

- 7 internal perspectives rotate based on interview state: researcher,
  simplifier, architect, breadth-keeper, seed-closer, ontologist, plus
  the outer socratic-interviewer role.
- **Dialectic Rhythm Guard**: at most 3 consecutive rounds without
  direct user judgment; the next one must route to the user.
- **Seed-ready Acceptance Guard**: before closing, the main session
  checks canonical criteria (scope, non-goals, outputs, verification
  explicit? material blockers resolved?) and refuses premature closure.
- On Claude Code uses `AskUserQuestion` for structured input; Gemini
  uses `ask_user`; Codex falls back to plain-text option blocks.

## Install

### Claude Code

```bash
claude plugin marketplace add brandonwie/3b-harness
claude plugin install interview@3b-harness
```

Trigger with `/interview:interview "your topic"` or natural language
trigger `"interview me about <topic>"`.

### Codex CLI

Install method depends on how your Codex install discovers plugins.
Either:

```bash
git clone https://github.com/brandonwie/3b-harness ~/.codex/plugins/3b-harness
```

…and the `interview` plugin is discovered under
`3b-harness/plugins/interview/`. Or follow your Codex docs for mounting
a plugin from a subdirectory.

Note: Codex has no native `AskUserQuestion` equivalent. The skill falls
back to plain-text option blocks — functional, slightly rougher UX than
Claude Code.

### Gemini CLI

Clone into your Gemini CLI plugins directory (or configure `GEMINI.md`
with a skill reference — check your Gemini CLI docs for the current
preferred install path). Skill activates via `activate_skill` for the
`interview` skill name.

## Usage

```
/interview:interview Build a payment module that integrates with Stripe
```

The interview runs for 5–15 rounds depending on how complete your
initial context is. At the end you get a YAML+markdown summary ready
to paste into a design doc, PR description, ticket, or spec.

## File layout

```
plugins/interview/
├── .claude-plugin/plugin.json       # Claude Code manifest
├── commands/interview.md            # slash-command entry
├── skills/interview/
│   ├── SKILL.md                     # dual-path playbook (Path B only in alpha)
│   └── references/
│       ├── codex-tools.md           # Claude→Codex tool mapping
│       └── gemini-tools.md          # Claude→Gemini tool mapping
├── agents/                          # 7 role prompts
│   ├── socratic-interviewer.md      # outer role
│   ├── seed-closer.md               # closure audit
│   ├── researcher.md
│   ├── simplifier.md
│   ├── architect.md
│   ├── breadth-keeper.md
│   └── ontologist.md
└── README.md                        # this file
```

## Design reference

The full analysis that informed this plugin is in
[`../../docs/interview-skill/`](../../docs/interview-skill/). Start with
[`README.md`](../../docs/interview-skill/README.md) and the fork
decision tree.

Key decision doc:
[`09-plugin-build-decisions.md`](../../docs/interview-skill/09-plugin-build-decisions.md)
(English) or
[`09-plugin-build-decisions.ko.md`](../../docs/interview-skill/09-plugin-build-decisions.ko.md)
(Korean).

## Upstream

Forked from the `interview` skill in
[Q00/ouroboros](https://github.com/Q00/ouroboros). Upstream carries the
original Socratic methodology, five-perspective model, and numerical
ambiguity-scoring design. This fork narrows scope (interview-only),
adds cross-agent portability (Codex, Gemini), and adds the ontologist
perspective.

## Changelog

See the top-level [CHANGELOG.md](../../CHANGELOG.md) for both
harness-level and plugin-level entries.

## License

MIT. See [LICENSE](../../LICENSE).
