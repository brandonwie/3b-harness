# ask-socratic

Socratic interview to crystallize vague requirements into clear specifications.
Cross-agent: works on Claude Code, Codex, and Gemini CLI.

> **Status:** `v0.1.0-alpha` — Path B (agent fallback) only. MCP server
> (`ask-socratic-ai` package) arriving in `v0.2.0`.

## What it does

Takes a vague topic ("build a payment module", "add search to my app") and
guides you through a structured Socratic interview until the requirements are
concrete enough to act on. Outputs a YAML-frontmatter + markdown summary
(goal / constraints / acceptance criteria / non-goals / open questions).

Forks the `interview` skill from [Q00/ouroboros](https://github.com/Q00/ouroboros)
with cross-agent portability and a narrowed scope (interview-only — no
downstream seed/execute/evaluate stages).

## How it works (short version)

- 7 internal perspectives (researcher, simplifier, architect, breadth-keeper,
  seed-closer, ontologist, plus the outer socratic-interviewer role) rotate
  based on interview state.
- **Dialectic Rhythm Guard**: at most 3 consecutive rounds without direct
  user judgment; the next one must route to the user.
- **Seed-ready Acceptance Guard**: before closing, the main session checks
  canonical criteria (scope, non-goals, outputs, verification explicit?
  material blockers resolved?) and refuses premature closure.
- On Claude Code uses `AskUserQuestion` for structured input; Gemini uses
  `ask_user`; Codex falls back to plain-text option blocks.

## Install

### Claude Code

```bash
claude plugin marketplace add brandonwie/ask-socratic
claude plugin install ask-socratic@ask-socratic
```

Then trigger with `/ask-socratic:interview "your topic"` or the natural
language trigger `"interview me about <topic>"`.

### Codex CLI

1. Clone this repo somewhere:
   ```bash
   git clone https://github.com/brandonwie/ask-socratic ~/.codex/plugins/ask-socratic
   ```
2. Codex auto-discovers the skill on next start.
3. Trigger: `/ask-socratic:interview "your topic"`.

Note: Codex has no native `AskUserQuestion` equivalent. The skill falls
back to plain-text option blocks — functional, slightly rougher UX than
Claude Code.

### Gemini CLI

1. Clone into your Gemini CLI plugins directory (or configure `GEMINI.md`
   with a skill reference — check your Gemini CLI docs for the current
   preferred install path).
2. Trigger: the skill activates via `activate_skill` for the `interview`
   skill name.

## Usage

```
/ask-socratic:interview Build a payment module that integrates with Stripe
```

The interview runs for 5–15 rounds depending on how complete your initial
context is. At the end you get a YAML+markdown summary you can paste into
a design doc, PR description, or ticket system.

### Example interview flow

```
User: /ask-socratic:interview Add search to my app

Round 1 — perspective: researcher
"What kind of data are you searching, and what is the current storage
backend (Postgres, ElasticSearch, files, etc.)?"

Round 2 — perspective: breadth-keeper
...

...

Round 8 — closure audit
"Scope, non-goals, outputs, and verification are all explicit. Ready to
finalize the summary?"

→ User: "yes"

---
topic: Add search to my app
goal: Introduce full-text search across the product-catalog Postgres table
  with <200ms p99 latency, typo tolerance, and faceted filtering.
constraints:
  - Must use existing Postgres (no new service for v1)
  - Must preserve existing admin CRUD latency budget
  ...
acceptance_criteria:
  - p99 search latency < 200ms on 100k records
  - Typos up to edit distance 2 return the intended result
  ...
non_goals:
  - Semantic/vector search (considered for v2)
  - Personalization
open_questions:
  - Exact faceting fields — deferred until UX review
---

# Interview Summary — Add search to my app

(narrative...)
```

## File structure

```
ask-socratic/
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
│   ├── researcher.md                # perspective 1
│   ├── simplifier.md                # perspective 2
│   ├── architect.md                 # perspective 3
│   ├── breadth-keeper.md            # perspective 4
│   └── ontologist.md                # perspective 5 (added vs upstream)
├── LICENSE
├── CHANGELOG.md
└── README.md
```

## Roadmap

- **v0.1.0-alpha** (current) — Path B only. Works everywhere, no persistence, qualitative closure.
- **v0.2.0** — Path A (MCP) via `ask-socratic-ai` PyPI package. Filesystem state, numerical ambiguity gate, session_id handoff.
- **v0.3.0** — PM variant + brownfield auto-detection. Full feature parity with upstream Ouroboros interview subsystem.

## Credits

Forked from the `interview` skill in
[Q00/ouroboros](https://github.com/Q00/ouroboros). Upstream carries the
original Socratic methodology, five-perspective model, and numerical
ambiguity-scoring design. This fork narrows scope (interview-only) and
adds cross-agent portability (Codex, Gemini) plus the ontologist
perspective.

## License

MIT. See [LICENSE](./LICENSE).
