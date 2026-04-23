---
tags: [plan, ouroboros, interview, plugin, multi-agent, decisions]
created: 2026-04-23
updated: 2026-04-23
status: in-progress
related:
  - /Users/brandonwie/dev/personal/ouroboros/docs/interview-skill/README.md
  - /Users/brandonwie/dev/personal/ouroboros/docs/interview-skill/08-customization-guide.md
  - ./09-plugin-build-decisions.ko.md
---

> 한국어판: [./09-plugin-build-decisions.ko.md](./09-plugin-build-decisions.ko.md)

> **Name update (post-doc, two rounds):**
>
> 1. Repo renamed `ask-socratic` → `3b-harness` (repo = harness
>    containing multiple plugins).
> 2. Plugin snapshot's own name settled as **`interview-claude`** (NOT
>    `ask-socratic`, NOT `interview`) to pair visibly with the sibling
>    Codex-generated snapshot at `plugins/interview-codex/`. Version
>    demoted to `v0.0.1` — this plugin is a **not-for-use snapshot**
>    held for cross-analysis against `interview-codex`, not a
>    distribution-ready build.
>
> When reading the rest of this doc: where it says `ask-socratic` read
> the consolidated plugin at `plugins/3b/` (manifest `name: 3b`); where
> it says `ask-socratic-ai` (Phase 2 PyPI package) read `interview-ai`
> (deprecated — see Phase 2 note below). Slash command is
> `/3b:interview` (previously `/interview-claude:interview`, earlier
> still `ask-socratic` flavored names). See the root CHANGELOG for the
> full rename record.
>
> **Phase 2 / MCP note (2026-04-23 consolidation):** the dual-path
> design (Path A = MCP via `interview-ai` PyPI package, Path B = agent
> fallback) was collapsed. The consolidated `plugins/3b/` ships two
> **layers** (not two plugins):
>
> - Conversational layer — SKILL.md + agents, prompt-heavy, zero deps.
> - Programmatic layer — `plugins/3b/engine/` Python package, optional,
>   loads prompts from the same `plugins/3b/agents/` via filesystem
>   SSoT. Provides numeric ambiguity scoring, file-locked state
>   persistence, and `LLMAdapter` protocol for integrators.
>
> The `interview-ai` package referenced below was never built and is
> no longer planned. The originally-paired sibling variants
> (`interview-claude` and `interview-codex`) are archived under
> `archive/plugins/` as historical snapshots.

# Plugin build decisions — cross-agent interview skill fork

## Revision — 2026-04-23

Original MVP was "agent-only / Path B only / drop MCP / drop PM / drop
brownfield / skip tests." After reviewing the MCP handler implementation,
we reversed: **full port + fresh tests**. All three open questions resolved:

- **R1 — Ontologist:** YES, add as the 6th `InterviewPerspective`.
- **R2 — PM variant:** YES, include in MVP.
- **R3 — Brownfield exploration:** YES, include in MVP.
- **Testing:** rewrite fresh (do NOT port upstream fixture-coupled tests).

New open decision introduced: **D13 — plugin-mode subagent dispatch**
(keep / drop / abstract). Recommendation: **drop** (D13b).

Implementation split into **three phases** across ~9–13 hours total. See
§7 for the phase breakdown.

## Why this doc exists

Your goal: take the `interview` skill from Ouroboros and ship it as **your own**
plugin runnable on Claude Code, Codex, and Gemini CLI. After the revision
above, this is a **full, renamed port** of the interview subsystem — the
entire pipeline for interviews (including PM variant and brownfield
exploration) but decoupled from Ouroboros's seed/execute/evaluate stages,
cross-agent portable, and under your maintenance.

This document surfaces every meaningful decision with options + tradeoffs so
you can pick before we start building. Reference: all claims below
reference the analysis docs in `ouroboros/docs/interview-skill/`
(`01-overview.md` … `08-customization-guide.md`).

---

## 1. Target agent matrix

Capability table — what each platform supports and how that affects the fork.

| Capability | Claude Code | Codex | Gemini CLI |
|---|---|---|---|
| Skill format | `skills/{name}/SKILL.md` via `Skill` tool | Auto-loaded; follow instructions directly | `activate_skill` tool loads on demand |
| Subagents / parallel dispatch | `Task` tool, named agents | `spawn_agent` (requires `multi_agent=true` in `~/.codex/config.toml`), **no named registry** — must read agent md and dispatch as generic worker | **None** — single-session only |
| Structured user input | `AskUserQuestion` (native) | No direct equivalent — plain-text prompt fallback | `ask_user` (native) |
| Task tracking | `TodoWrite` | `update_plan` | `write_todos` |
| MCP support | First-class (servers configured via `.mcp.json`) | Supported via config.toml | Supported (standard protocol) |
| Plan mode | `EnterPlanMode` / `ExitPlanMode` | No equivalent | `enter_plan_mode` / `exit_plan_mode` |
| Memory / persistence | Project CLAUDE.md + file writes | File writes + optional MCP | `save_memory` → GEMINI.md + file writes |
| Web | `WebFetch` / `WebSearch` | Native equivalents | `web_fetch` / `google_web_search` |

**Key consequences for this fork:**

- **Gemini has no subagents.** The interview skill doesn't use `Task` in its
  hot path, so this is fine — but if you ever want parallel exploration (e.g.,
  a "research the user's codebase" step), it will be serial on Gemini.
- **Codex has no `AskUserQuestion` equivalent.** The skill's routing uses
  `AskUserQuestion` heavily in PATH 1b / 2 / 3 / 4. Codex fork must fall back
  to plain-text prompts (`"Please answer: ..."`).
- **Named agent dispatch is Claude-only.** The five perspective agents
  (researcher, simplifier, architect, breadth-keeper, seed-closer) are
  currently loaded server-side by Python (interview.py:62–87). In an
  agent-only fork (your chosen MVP), they become prompt-data files referenced
  inline by the skill. Claude can `Task`-dispatch them if wanted; Codex must
  read + `spawn_agent` with filled content; Gemini cannot dispatch at all.

---

## 2. Inventory — what the source skill contains (revised for full port)

After R1–R3 YES: almost everything is ported. Rename-and-adapt is the
dominant workload; only tests are genuinely new.

| Part | Source | Full-port action |
|---|---|---|
| SKILL.md dual-path playbook (338 lines) | `skills/interview/SKILL.md` | **Port whole file.** Rename "Ouroboros" → your plugin brand; rename MCP tool refs to `{plugin}_interview`; retain both Path A + Path B |
| Command entry stub | `commands/interview.md` | **Port**, rename prefix |
| Socratic interviewer (outer role) | `src/ouroboros/agents/socratic-interviewer.md` | **Keep; adapt** — prefix contract (`[from-code]` etc.) stays since MCP is included; only minor rename of references to Ouroboros |
| Closure audit (canonical) | `src/ouroboros/agents/seed-closer.md` | **Copy verbatim** |
| 5 perspective agents (researcher, simplifier, architect, breadth-keeper, seed-closer) | `src/ouroboros/agents/*.md` | **Copy verbatim** (loaded via ported `agents/loader.py`) |
| Ontologist | `src/ouroboros/agents/ontologist.md` | **Port as 6th `InterviewPerspective`** — add enum value + map it in `_load_interview_perspective_strategies()` + 1-line trigger in engine |
| `InterviewEngine` + `InterviewState` + `InterviewRound` + `InterviewStatus` + `InterviewPerspective` | `src/ouroboros/bigbang/interview.py` (31.6K) | **Port whole file.** Rename package refs; drop plugin-mode subagent dispatch per D13b |
| `AmbiguityScorer` + threshold + floors + milestones + `qualifies_for_seed_completion` | `src/ouroboros/bigbang/ambiguity.py` (28.4K) | **Port whole file** — full numerical gate restored |
| Events | `src/ouroboros/events/interview.py` (74 lines) + `events/base.py` | **Port.** Consider prefixing type names with plugin namespace (`{plugin}.interview.*`) to avoid event-store collisions |
| MCP handler (InterviewHandler only) | `src/ouroboros/mcp/tools/authoring_handlers.py:694–1150` | **Port handler class + helpers.** Drop plugin-mode branch per D13b. Rename tool name `ouroboros_interview` → `{plugin}_interview` |
| PM variant (6 files) | `pm_interview.py` + `pm_handler.py` + `pm_seed.py` + `pm_document.py` + `pm_completion.py` + `question_classifier.py` | **Port all six** (Phase 3). ~80K Python |
| Downstream `Seed` dataclass | `src/ouroboros/core/seed.py:155–229` | **Port.** Keep as Python immutable model (~75 lines); reference from handler's completion path |
| Brownfield exploration | `src/ouroboros/bigbang/brownfield.py` (14.6K) + `explore.py` (17.4K) | **Port both** (Phase 3). Used by `InterviewEngine.start_interview(cwd=...)` for auto-detect |
| Secondary dependencies | See §13 | **Port** (~50K) — types, errors, file_lock, security, providers, config, event_store, MCP types, subagent adapter, initial_context, agent loader |
| Tests | `tests/unit/bigbang/test_interview.py` + `test_pm_interview.py` | **Do NOT port. Rewrite fresh** — property tests for scorer, integration tests for engine, contract tests for handler |
| Plugin-mode subagent dispatch | `handle()` lines 980–1108 in `authoring_handlers.py` | **Drop per D13b** — subprocess mode only. Removes ~130 lines of Claude-specific code |

---

## 3. What the MVP looks like end-to-end (revised)

Full port. Dual-path (MCP + fallback). Cross-agent. The plugin ships as
**two coordinated artifacts**: a Claude Code plugin (skill + manifest)
and a Python package (engine + MCP server). Users install both for Path
A; plugin only for Path B.

```
ask-socratic/                          # Claude plugin side
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── interview.md
├── skills/
│   └── interview/
│       ├── SKILL.md                   # Full dual-path: Path A + Path B
│       └── references/
│           ├── codex-tools.md
│           └── gemini-tools.md
├── agents/                            # 7 files (6 + ontologist)
│   ├── socratic-interviewer.md
│   ├── seed-closer.md
│   ├── researcher.md
│   ├── simplifier.md
│   ├── architect.md
│   ├── breadth-keeper.md
│   └── ontologist.md                  # NEW 6th perspective
├── LICENSE
└── README.md                          # Install for all three agents

ask-socratic-ai/                       # Python package (PyPI)
├── pyproject.toml
├── src/ask_socratic/
│   ├── __init__.py
│   ├── config.py                      # simplified get_clarification_model
│   ├── core/
│   │   ├── types.py                   # Result
│   │   ├── errors.py
│   │   ├── file_lock.py
│   │   ├── security.py                # InputValidator
│   │   ├── initial_context.py
│   │   └── seed.py                    # ported Seed dataclass
│   ├── providers/
│   │   ├── base.py                    # LLMAdapter, Message, CompletionConfig
│   │   └── litellm_adapter.py
│   ├── agents/
│   │   └── loader.py                  # load_persona_prompt_data
│   ├── interview/
│   │   ├── state.py                   # InterviewState/Round/Status/Perspective
│   │   ├── engine.py                  # InterviewEngine
│   │   ├── ambiguity.py               # AmbiguityScorer + threshold + floors
│   │   └── brownfield.py + explore.py # Phase 3 brownfield auto-detect
│   ├── pm/                            # Phase 3
│   │   ├── engine.py                  # PMInterviewEngine
│   │   ├── seed.py                    # PMSeed + UserStory
│   │   ├── document.py
│   │   ├── completion.py
│   │   └── question_classifier.py
│   ├── events/
│   │   ├── base.py                    # BaseEvent
│   │   └── interview.py               # event factories
│   ├── persistence/
│   │   └── event_store.py
│   └── mcp/
│       ├── __init__.py                # server registration
│       ├── types.py
│       ├── errors.py
│       ├── subagent.py                # build_interview_subagent (still needed for PM plugin transcript)
│       └── tools/
│           ├── interview.py           # InterviewHandler
│           └── pm.py                  # PMInterviewHandler
└── tests/
    ├── unit/
    │   ├── test_ambiguity.py          # property tests
    │   ├── test_engine.py             # integration with mock LLM
    │   ├── test_handler.py            # contract tests
    │   └── test_pm.py
    └── smoke/
        └── test_end_to_end.py         # real LLM, manual-invocation only
```

End-user flow (same across all three agents):

1. User types `/ask-socratic:interview "topic"` (or platform equivalent).
2. SKILL.md Step 0.5 runs `ToolSearch "+ask-socratic interview"`.
3. If `ask-socratic-ai` package installed with MCP registered → **Path A**
   (persistent, numerical gate, session_id handoff).
4. Otherwise → **Path B** (in-conversation, qualitative closure). Works on
   Gemini even without Python package.
5. Interview completes → agent outputs structured summary (YAML + markdown
   per D5) referencing `session_id` when Path A is active.

End-user flow (same across all three agents):

1. User types `/your-plugin:interview "topic"` (or equivalent slash / skill
   invocation on each platform).
2. Agent loads SKILL.md, adopts socratic-interviewer role.
3. Interview proceeds with routing paths + rhythm guard + closure audit, all
   in-conversation.
4. On close, agent outputs a structured "interview summary" block (markdown)
   with goal / constraints / success criteria / non-goals / ambiguity ledger.
5. User can pass that summary into whatever downstream step they want (seed
   generation, ticket writing, PR draft, etc.) — either via another skill in
   this plugin or any external tool.

---

## 4. The decisions

Numbered. Each has a **recommendation** (first option) but you pick.

### D1 — Plugin name + command prefix

Drives everything downstream (slash commands, MCP tool names if you add one
later, GitHub repo name).

- **D1a. `ask-socratic`** — descriptive, tool-first, agent-agnostic
- **D1b. `interview-ooo`** — keeps heritage to Ouroboros
- **D1c. `socratic-spec`** — emphasizes the output is a spec
- **D1d. Your own pick**

**Recommendation:** D1a. "socratic" is the distinguishing methodology;
"ask" reads well as a verb slash-command (`/ask-socratic:interview`).

### D2 — Repo location + git origin

Where does the plugin live on disk and on GitHub?

- **D2a. New standalone public GitHub repo** — e.g., `github.com/brandonwie/ask-socratic`. Publishable via Claude marketplace. Clean boundary.
- **D2b. Subfolder under `~/dev/personal/3b/plugins/`** — private-only, tight integration with your 3B stack. No marketplace publish.
- **D2c. Subfolder under a new `brandonwie-plugins` monorepo** — if you plan more plugins later, start the monorepo now.

**Recommendation:** D2a. Standalone repo maximizes reusability + visibility.
Adding a second plugin later is cheap (another repo). Monorepo doesn't pay
off until 3+ plugins.

### D3 — Persistence model (agent-only MVP)

MVP is agent-only (no MCP, no Python engine). But you can still write
interview state to disk via each agent's native file tools.

- **D3a. No persistence** — interview lives entirely in conversation; closing the session loses it. Simplest; truly portable.
- **D3b. Filesystem-only** — SKILL.md writes a markdown transcript to `~/.{plugin}/sessions/{id}.md` after each round. Resumable if session dies.
- **D3c. Filesystem + structured JSON** — markdown for humans + JSON sidecar with routing metadata for programmatic consumption.

**Recommendation:** D3a for MVP, D3b as v0.2. Persistence adds complexity
that doesn't pay off until users are running interviews longer than one
session, which requires validation first.

### D4 — Closure mechanism

Ouroboros uses numerical ambiguity scoring (≤ 0.2 gate + per-dimension floors
+ streak). MVP drops the scorer — so closure becomes a judgment call.

- **D4a. Pure qualitative via `seed-closer.md`** — agent reads seed-closer criteria, asks the closure questions, user decides.
- **D4b. In-conversation self-score** — agent produces a self-rated score (0–1) each round using the same 4 dimensions, but as a prompt-level self-assessment, not a separate LLM call. User sees the score.
- **D4c. Checklist-based** — agent tracks the 4 dimensions explicitly (goal / constraints / success / context) and shows the user which dimensions are "clear" vs "fuzzy" each round. User closes when all clear.

**Recommendation:** D4c. Checklist is concrete, visible, cross-agent
portable (no LLM-specific scoring prompts). Keeps the spirit of the
4-dimension model without pretending to be a numerical gate.

### D5 — Downstream handoff shape

When the interview closes, what does the agent output?

- **D5a. Plain-markdown summary** — headings: Goal / Constraints / Success Criteria / Non-Goals / Open Questions. Human-readable. No downstream tool contract.
- **D5b. YAML frontmatter + markdown body** — machine-parseable plus human-readable. Downstream scripts can load it.
- **D5c. Full `Seed`-shaped JSON** — matches the Ouroboros Seed dataclass for compat if user ever uses real Ouroboros downstream.

**Recommendation:** D5b. YAML frontmatter (`goal`, `constraints`,
`acceptance_criteria`, `non_goals`, `open_questions`) + markdown narrative
below. Good for humans; cheap to parse; trivial to map to Ouroboros Seed
later if ever needed. No dependency on a Python model.

### D6 — AskUserQuestion fallback for Codex

Codex has no native structured-input tool. The interview skill uses
`AskUserQuestion` in PATH 1b / 2 / 3 / 4.

- **D6a. Plain-text prompt** — "Please answer: <question>. Options: (1) X, (2) Y, (3) other." User responds in free text. Simplest. Loses the clean option-list UX.
- **D6b. Fenced option block** — agent outputs a code-fenced option list the user can copy. Slightly richer but still plain text.
- **D6c. Skip Codex support initially** — Claude + Gemini only; add Codex later when their CLI ships an `ask_user` equivalent.

**Recommendation:** D6a. Cleanest portability. Claude users get native
`AskUserQuestion` experience; Codex users get plain-text fallback; Gemini
users get `ask_user`. The SKILL.md gives a single instruction
("ask the user with these options") and each platform renders it in its
own way.

### D7 — Perspective rotation without the Python loader

In Ouroboros, `InterviewEngine` rotates through 5 perspectives based on
milestone + breadth state. Without Python, rotation must live in SKILL.md
instructions.

- **D7a. Milestone-driven rotation described in SKILL.md** — "On round 1–2 use researcher, on round 3–4 simplifier, …". Simple mapping.
- **D7b. Trigger-driven rotation** — "Use breadth-keeper if the last N rounds stayed on one thread; use seed-closer if the ledger shows scope/success/constraints all explicit; …". Closer to original.
- **D7c. No rotation — agent picks the best perspective per round** — trust the LLM to pick from the 5 files based on round context.

**Recommendation:** D7b. It's what the Python engine actually does; the
triggers are already documented in the 5 agent md files; portable to any
agent that can read instructions. Slightly higher prompt-engineering risk
than D7a but better fidelity to the original behaviour.

### D8 — Cross-agent skill format strategy

How do you ship ONE skill runnable in three agents with different tool names?

- **D8a. Canonical Claude Code tool names + platform mapping refs** — SKILL.md uses `Read` / `Write` / `Bash` / `AskUserQuestion` (Claude names). Include `references/codex-tools.md` + `references/gemini-tools.md` inside the skill with mapping tables. Each agent reads the mapping file on invocation. (Superpowers pattern.)
- **D8b. Per-agent skill variants** — maintain `skills/interview/claude/SKILL.md`, `skills/interview/codex/SKILL.md`, `skills/interview/gemini/SKILL.md`. Each uses native tool names. Triplicate maintenance.
- **D8c. Abstract instructions only** — never name specific tools ("use your file-reading tool", "ask the user"). Sloppier but platform-neutral.

**Recommendation:** D8a. Pattern is proven (superpowers). Maintenance stays
O(1). New platforms only need a new mapping file, not a rewrite.

### D9 — Distribution

How do users install the plugin?

- **D9a. Claude plugin marketplace + manual install instructions for Codex/Gemini** — `claude plugin install ...` for Claude; README docs for the other two.
- **D9b. Single git-clone install across all three** — each platform's CLI has a way to install skills from git. Unified install story.
- **D9c. Defer distribution — ship for Claude first, solve portability later**

**Recommendation:** D9a. Start with Claude marketplace (lowest friction
for your primary user base); keep the skill+agent structure portable so
Codex/Gemini users can clone and symlink. Marketplace publish for
Codex/Gemini once those ecosystems mature.

### D10 — MCP is Phase 2 core (REVISED)

Previously deferred. Now **primary** after R2/R3 resolution.

- ~~D10a. Yes — reserve design space for it~~ (superseded)
- ~~D10b. Maybe — write the door open~~ (superseded)
- ~~D10c. No — agent-only forever~~ (rejected)
- **D10 (revised).** MCP is Phase 2 (see §7). Full `InterviewEngine` +
  `AmbiguityScorer` + `InterviewHandler` ported to `ask-socratic-ai` PyPI
  package. SKILL.md Step 0.5 activates MCP automatically when the package
  is installed; Path B fallback used when it isn't.

**Consequences:**
- Two distribution artifacts (Claude marketplace plugin + PyPI package)
- Gemini users without Python package → Path B only (works)
- Claude / Codex users who install both → Path A (full numerical gate,
  session_id handoff, resumable state)

### D11 — Which files to copy verbatim vs rewrite

From the six agent md files the MVP keeps:

- `socratic-interviewer.md` — **rewrite**. Source mentions `[from-code]` / `[from-user]` / `[from-research]` prefixes; MVP drops them because there's no MCP to receive prefixed answers. Simplify role description to pure questioning.
- `seed-closer.md` — **copy verbatim**. Criteria are universal.
- `researcher.md`, `simplifier.md`, `architect.md`, `breadth-keeper.md` — **copy verbatim**. Role prompts are universal.

**Recommendation:** as listed. Rewriting only the one file where the MCP
assumption shows through.

### D12 — Testing / validation approach (REVISED — expanded for full port)

Fresh tests (not ports). Three tiers:

- **Property tests** for `AmbiguityScorer` (deterministic math given stubbed LLM): threshold, floors, streak, milestones, brownfield weight flip. No LLM needed.
- **Integration tests** for `InterviewEngine` with a mock `LLMAdapter` returning fixed responses: start → record → ask flow, state persistence, save/load round-trip, perspective rotation trigger.
- **Contract tests** for `InterviewHandler` (and `PMInterviewHandler`): MCP schema validation, action dispatch, gate refusal messages, completion meta shape, event emission.
- **Smoke tests** with real LLM (manual, not CI): one full interview per agent (Claude Code / Codex / Gemini CLI) per release.

Target coverage: ≥80% line coverage on `interview/` + `pm/` modules via
unit + integration. Smoke tests are pass/fail manual checkpoints per
release — do not gate CI on them.

### D13 — Plugin-mode subagent dispatch (NEW)

`InterviewHandler.handle()` has a branch at line 980
(`should_dispatch_via_plugin`) that delegates actual question generation
to an OpenCode Task pane (child subagent). This is a Claude Code
performance optimization — avoids re-priming LLM context each turn on
long sessions — but adds ~300 lines and one Claude-specific code path.

- **D13a.** Keep plugin-mode dispatch, Claude-only — detect runtime; dispatch to Task pane on Claude Code, subprocess on Codex/Gemini.
- **D13b. Drop plugin-mode entirely (Recommended)** — subprocess mode always. Handler owns its own LLM adapter. Simpler.
- **D13c.** Abstract over a "subagent dispatcher" — handler asks its runtime host for dispatch; falls back to subprocess.

**Recommendation:** D13b. Simplest; cross-agent. Lose the OpenCode
perf bonus, but gain one unified code path. Each MCP call costs the
~3–8s LLM question-generation latency — same as Path B.

**Consequences of D13b:**
- Handler always creates its own `LLMAdapter` (`create_llm_adapter()`)
- `ask-socratic-ai` package always imports litellm (~50 transitive deps)
- No "plugin-only install" flavor
- Drop `build_interview_subagent` + `emit_subagent_dispatched_event` helpers from the port (exception: PM handler's transcript-passing `last_question` pattern is kept because it's also used for continuity, not just dispatch)

---

## 5. Additional open questions (not blocking MVP)

These are worth thinking about but not decide-now:

- **Q1.** Who is the intended user? (You personally / your team at work /
  public OSS users.) Drives documentation tone + install friction tolerance.
- **Q2.** Multi-language support? (English-only MVP, add Korean prompts in
  agent md files later?) Easy to bolt on once the skeleton works.
- **Q3.** Interview session replay / sharing? (Export markdown transcript +
  share link / gist integration.) Depends on D3.
- **Q4.** Integration with your 3B knowledge system? (Auto-save interview
  transcripts to `3b/projects/{name}/` or `knowledge/process/`.) Natural fit
  but adds 3B dependency.

---

## 6. Recommended MVP profile — "Full port + fresh tests" (REVISED)

After R1–R3 YES + D13b recommendation:

- **D1:** `ask-socratic`
- **D2:** Standalone repo `github.com/brandonwie/ask-socratic` + PyPI package `ask-socratic-ai`
- **D3:** **Filesystem persistence** via MCP state files (`~/.ask-socratic/data/interview_{id}.json`) — matches upstream; Path B fallback is in-conversation only
- **D4:** **Numerical gate** — full `AmbiguityScorer` ported (supersedes checklist-only D4c); Path B still uses `seed-closer.md` qualitative audit as secondary
- **D5:** YAML frontmatter + markdown body summary — plus `session_id` reference when Path A is active
- **D6:** Plain-text fallback for Codex; native widget on Claude + Gemini
- **D7:** Trigger-driven perspective rotation — enforced by ported `InterviewEngine._load_interview_perspective_strategies()`
- **D8:** Canonical Claude tool names + mapping references (unchanged)
- **D9:** Claude marketplace + PyPI dual distribution
- **D10:** **MCP is Phase 2 core** (flipped from "deferred")
- **D11:** Expanded rewrite list — see §12 rename map (multiple files, not just `socratic-interviewer.md`)
- **D12:** Property + integration + contract + smoke tests (fresh, not ports)
- **D13:** **Drop** plugin-mode subagent dispatch (subprocess mode only)

Total deliverable across three phases:

- Plugin side: 1 `plugin.json` + 1 command + 1 SKILL.md + 2 tool-mapping refs + 7 agent md + README + LICENSE
- Package side: `pyproject.toml` + ~185–265K Python (depending on PM completion) + test suite
- Documentation: install guide (per agent) + example transcripts + CHANGELOG

Estimated total effort: **~9–13 hours across 3 focused sessions**. See §7.

---

## 7. Phase split — what happens after you decide (REVISED)

Three focused sessions. Each ends with a tag + push so you can pause
without losing momentum.

### Phase 1 — foundation + Path B (2–3 hours) → `v0.1.0-alpha`

Goal: the skill runs end-to-end on all three agents using the Path B
(agent-only) fallback. No Python yet.

1. `gh repo create brandonwie/ask-socratic --public` + clone locally.
2. Scaffold: `plugin.json`, `LICENSE`, `README.md`, `CHANGELOG.md`.
3. Copy the 7 agent md files (6 existing + ontologist.md) into
   `agents/`. Adapt `socratic-interviewer.md` only (drop Ouroboros
   self-references; `[from-code]` prefix wording stays — Path A will
   need it).
4. Author `SKILL.md` with full dual-path structure but Step 0.5 hardcoded
   to "no MCP yet, use Path B" (tombstone for Phase 2).
5. Add `skills/interview/references/codex-tools.md` +
   `gemini-tools.md` copied from superpowers with `ask-socratic`
   rebranding.
6. Write `commands/interview.md` entry stub.
7. Smoke-test: run one interview on Claude Code, Codex, Gemini CLI.
   Fix any Path B blockers.
8. `git tag v0.1.0-alpha && git push`.

### Phase 2 — Path A engine (4–6 hours) → `v0.1.0-beta`

Goal: MCP server exists, `ask-socratic-ai` package installable from
PyPI (or git), Path A activates automatically when Step 0.5 finds it.

1. Scaffold `pyproject.toml` for `ask-socratic-ai` package in a
   sibling dir or subfolder (`python/` inside the same repo, or
   separate repo `ask-socratic-ai` — open sub-question).
2. Port secondary deps (see §13): `core/types.py`, `core/errors.py`,
   `core/file_lock.py`, `core/security.py`, `core/initial_context.py`.
3. Port `providers/base.py` + one LLM adapter (litellm). Port
   simplified `config.py` (`get_clarification_model`).
4. Port `agents/loader.py`.
5. Port `interview/state.py` (`InterviewState`, `InterviewRound`,
   `InterviewStatus`, `InterviewPerspective`).
6. Port `interview/engine.py` (`InterviewEngine`).
7. Port `interview/ambiguity.py` (`AmbiguityScorer` + all constants).
8. Port `events/base.py` + `events/interview.py`.
9. Port `persistence/event_store.py` (simplify if upstream has moba
   coupling).
10. Port `mcp/types.py`, `mcp/errors.py`.
11. Port `mcp/tools/interview.py` (`InterviewHandler`, dropping
    plugin-mode branch per D13b).
12. Register MCP server in package entry point; document
    `claude mcp add ask-socratic uv tool run ask-socratic-ai`.
13. Un-tombstone SKILL.md Step 0.5 — ToolSearch actually activates
    Path A now.
14. Fresh tests: property (ambiguity.py), integration (engine.py with
    mock LLM), contract (handler.py).
15. `git tag v0.1.0-beta && git push`.

### Phase 3 — PM + brownfield + ontologist perspective (3–4 hours) → `v0.1.0`

Goal: feature-complete vs upstream interview subsystem.

1. Port brownfield: `brownfield.py` + `explore.py`. Wire into
   `InterviewEngine.start_interview(cwd=...)` for auto-detect.
2. Port PM core: `pm_seed.py` (PMSeed + UserStory), `pm_document.py`,
   `pm_completion.py`, `question_classifier.py`.
3. Port `pm/engine.py` (`PMInterviewEngine` composition wrapper).
4. Port `mcp/tools/pm.py` (`PMInterviewHandler` with
   decide-later diff computation; last_question continuity stays).
5. Register PM MCP tool `ask-socratic_pm_interview` alongside the main
   one.
6. Add `ontologist.md` as 6th `InterviewPerspective` — enum value +
   loader mapping entry + trigger logic in engine (e.g., activate when
   user explicitly asks "why" or when root-cause signals appear).
7. Update SKILL.md for PM variant hook + brownfield auto-detect.
8. Fresh tests: brownfield detection, PM classifier, PM seed
   extraction, ontologist rotation trigger.
9. Full end-to-end smoke on all three agents: greenfield interview,
   brownfield interview (cwd=repo with pyproject.toml), PM interview.
10. `git tag v0.1.0 && git push`. Claude marketplace submission +
    PyPI publish (`uv publish` or `twine`).

**Total estimated effort:** 9–13 hours (3 focused sessions). Each phase
ships something runnable. Drop any phase if a deadline bites — v0.1.0-alpha
already delivers Path B on three agents.

---

## 8. Decisions that can change later (low risk)

D3, D6, D10 are all easy to revisit after MVP — they don't affect
skill structure. Decisions worth getting right first time:

- **D1 (name)** — renaming the plugin later is cheap but annoying if
  anyone has installed it.
- **D2 (repo)** — moving a repo loses stars/history; pick correctly.
- **D8 (format strategy)** — switching strategies is a significant
  rewrite.
- **D11 (what to rewrite vs copy)** — stacking tech debt in
  `socratic-interviewer.md` rewrite would hurt; spend time on it.

Everything else can evolve with releases.

---

## 9. What this plan does NOT decide

- The actual rewritten `socratic-interviewer.md` content (Phase 1).
- Full SKILL.md copy (Phase 1 — derives from upstream with rename map in §12).
- Exact `pyproject.toml` contents (Phase 2).
- `plugin.json` schema details (Phase 1 — boilerplate).
- Test assertion specifics (Phase 2 — derives from ported behavior).
- Smoke-test transcripts (captured during each phase).
- Open sub-question: is `ask-socratic-ai` a subfolder of the plugin repo
  (`python/`) or a separate repo? Resolve at start of Phase 2.
- Open sub-question: event-store SQLite schema — keep upstream's or
  simplify? Resolve when porting `persistence/event_store.py`.

---

## 10. Verification before execution (REVISED — per phase)

**Phase 1 exit criteria:**

- All 7 agent md files exist under `agents/` and parse as valid markdown.
- SKILL.md frontmatter has `name`, `description`, optional `aliases`.
- `plugin.json` validates against Claude plugin manifest schema.
- Tool-mapping references match the superpowers originals (cache:
  `~/.claude/plugins/cache/temp_git_*/skills/using-superpowers/references/`).
- Running `/ask-socratic:interview "build a task CLI"` in Claude Code
  produces a first question within 2 rounds of SKILL.md instructions.
- Codex (`multi_agent=false`) and Gemini CLI produce comparable behavior.
- `v0.1.0-alpha` tag pushed.

**Phase 2 exit criteria:**

- `ask-socratic-ai` package installs cleanly: `uv tool install ask-socratic-ai`.
- MCP tool discoverable via `claude mcp list | grep ask-socratic`.
- Property tests for `AmbiguityScorer` pass (score math + floors + streak
  + milestones + brownfield weight switch).
- Integration tests for `InterviewEngine` pass with mock LLM adapter
  (start → record → ask → save/load round-trip).
- Contract tests for `InterviewHandler` pass (schema validation,
  action dispatch, gate refusal message, completion meta).
- SKILL.md Step 0.5 `ToolSearch` finds the tool and routes to Path A.
- Coverage ≥80% on `interview/` module.
- `v0.1.0-beta` tag pushed.

**Phase 3 exit criteria:**

- Brownfield auto-detect works: running with `cwd=<repo with pyproject.toml>`
  sets `state.is_brownfield=True` and populates `codebase_paths`.
- PM interview separately callable via `/ask-socratic:pm-interview`.
- PMSeed extraction produces expected JSON schema
  (product_name / goal / user_stories / constraints / success_criteria /
  deferred_items / decide_later_items / assumptions).
- Ontologist perspective triggers on root-cause-style user responses.
- Full end-to-end smoke on all 3 agents (greenfield + brownfield + PM).
- `v0.1.0` tag pushed, marketplace submission + PyPI publish done.

---

## 11. Rename map — every `ouroboros` reference (NEW)

Before porting any file, know exactly what changes. Use `rg` / `sed` for
each row when porting.

| Category | Before | After |
|---|---|---|
| Python package name | `ouroboros` | `ask_socratic` |
| PyPI distribution name | `ouroboros-ai` | `ask-socratic-ai` |
| MCP tool — main | `ouroboros_interview` | `ask-socratic_interview` (MCP prefers `-`, but check Claude's MCP tool naming rules — may need `ask_socratic_interview`) |
| MCP tool — PM | `ouroboros_pm_interview` | `ask-socratic_pm_interview` |
| Data directory | `~/.ouroboros/data/` | `~/.ask-socratic/data/` |
| Seed output directory | `~/.ouroboros/seeds/` | `~/.ask-socratic/seeds/` |
| State filename pattern | `interview_{id}.json` | unchanged (already generic) |
| Module paths | `src/ouroboros/…` | `src/ask_socratic/…` |
| Event type prefix | `interview.started` (flat) | **open decision:** keep flat OR namespace to `ask-socratic.interview.started` |
| Config class | `OuroborosConfig` | `AskSocraticConfig` (or simplify to module-level functions) |
| Command / CLI entry | `ooo interview` | `ask-socratic interview` (or keep `/ask-socratic:interview` slash only) |
| README / docstring mentions | "Ouroboros" | "ask-socratic" with upstream credit |
| Skill frontmatter | `mcp_tool: ouroboros_interview` | `mcp_tool: ask-socratic_interview` |
| Agent file cross-refs in SKILL.md | `src/ouroboros/agents/…` | `agents/…` (plugin-relative) |

**Execution tip:** after Phase 2 port is done, run
`rg -i 'ouroboros' src/ask_socratic/ docs/` and verify every hit is
either a credit line in README/docstrings or an intentional cross-
reference back to this analysis.

---

## 12. Secondary dependency graph (NEW)

Porting the primary items drags in these utilities. Know the full
footprint before committing to Phase 2.

### Primary (~185K if PM included)

| File | Size | Role |
|---|---|---|
| `src/ouroboros/bigbang/interview.py` | 31.6K | Engine + state + perspective enum + loader |
| `src/ouroboros/bigbang/ambiguity.py` | 28.4K | Scorer + threshold + floors + milestones |
| `src/ouroboros/mcp/tools/authoring_handlers.py` (InterviewHandler slice) | ~15K | MCP wrapping of engine |
| `src/ouroboros/bigbang/brownfield.py` + `explore.py` | 14.6K + 17.4K | Brownfield detection + codebase scan |
| `src/ouroboros/bigbang/pm_interview.py` | 45.8K | PM composition wrapper |
| `src/ouroboros/mcp/tools/pm_handler.py` | ~40K | PM MCP wrapper |
| `src/ouroboros/bigbang/pm_seed.py` + `pm_document.py` + `pm_completion.py` + `question_classifier.py` | ~40K | PM seed + document + completion + classifier |

### Secondary drag-ins (~50K)

| File | Size | Why ported |
|---|---|---|
| `src/ouroboros/core/types.py` | ~1K | `Result` type (used everywhere) |
| `src/ouroboros/core/errors.py` | ~2K | `ProviderError`, `ValidationError` |
| `src/ouroboros/core/security.py` | ~3K | `InputValidator` (used in handler) |
| `src/ouroboros/core/file_lock.py` | ~2K | Safe state-file writes |
| `src/ouroboros/core/initial_context.py` | ~2K | `resolve_initial_context_input` |
| `src/ouroboros/core/seed.py` | ~10K | `Seed` immutable dataclass (completion output) |
| `src/ouroboros/providers/base.py` + litellm adapter | ~10K | `LLMAdapter`, `Message`, `CompletionConfig` |
| `src/ouroboros/config.py` (simplified) | ~5K | `get_clarification_model` |
| `src/ouroboros/events/base.py` + existing `events/interview.py` | ~2K | Event typing |
| `src/ouroboros/persistence/event_store.py` | ~8K | SQLite event store (simplify if moba-coupled) |
| `src/ouroboros/mcp/types.py` + `errors.py` | ~5K | MCP protocol types |
| `src/ouroboros/mcp/tools/subagent.py` | ~3K | `build_interview_subagent` (kept for PM last_question continuity even without D13) |
| `src/ouroboros/agents/loader.py` | 7.3K | `load_persona_prompt_data` (reads agent md → prompt data) |

### Tertiary risks (things that may expand the port scope)

| Risk | Mitigation |
|---|---|
| `config.py` pulls in `OuroborosConfig` hierarchy beyond `get_clarification_model` | Replace with minimal `get_clarification_model()` function that reads from env + single YAML if needed |
| `providers/base.py` references litellm directly | Keep the coupling — litellm is ubiquitous; abstracting adds nothing now |
| `event_store.py` has SQLite schema tied to moba / other projects | Port only the interview-related event types; simplify schema to one table if upstream's is over-designed |
| `subagent.py` has Claude-specific OpenCode assumptions | Keep `build_*_subagent` for PM transcript continuity; ignore emission helpers (D13b drops them) |
| `agents/loader.py` assumes a specific markdown parser | Trivial; port as-is |

**Total port if R1/R2/R3 all YES:** ~265K Python, 7 agent md, SKILL.md,
plugin.json, pyproject.toml, tests, docs.

---

## 13. Next action

**R1–R3 resolved YES. D13 recommendation stands (D13b drop plugin-mode).**
Ready to start Phase 1.

When you want to begin:

1. Say "start Phase 1" — I'll run `gh repo create`, scaffold, copy
   agents, draft SKILL.md, smoke-test.
2. Or override any of D1–D13 / R1–R3 / D13 recommendation first.
3. Or ask for a deeper dive on any piece (event_store simplification,
   MCP tool naming rules, SKILL.md Step 0.5 rewrite, etc.) before
   starting.

The task list has been updated to reflect the 3-phase plan.
