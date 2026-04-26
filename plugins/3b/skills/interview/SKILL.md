---
name: interview
description: "Socratic interview to crystallize vague requirements into clear specifications. Cross-agent: Claude Code, Codex, Gemini CLI."
aliases: [socratic]
---

# /3b:interview

Socratic interview that turns a vague request ("build a payment module",
"add search to my app") into a concrete, actionable specification via
structured questioning. Works across Claude Code, Codex, and Gemini CLI.

## Usage

```
/3b:interview [topic]
```

**Trigger keywords:** "interview me", "clarify requirements", "socratic interview"

## Cross-agent tool mapping

This SKILL uses Claude Code tool names (`Read`, `Write`, `Edit`, `Grep`,
`Glob`, `Bash`, `AskUserQuestion`, `WebFetch`). When running on a
different platform:

- **Codex** — see [./references/codex-tools.md](./references/codex-tools.md).
  Note: Codex has no `AskUserQuestion` equivalent — use plain-text
  option blocks (see "Codex fallback" below).
- **Gemini CLI** — see [./references/gemini-tools.md](./references/gemini-tools.md).
  Use `ask_user` instead of `AskUserQuestion`.
- **Claude Code** — use the tools as named below.

## Instructions

The interview runs as an in-conversation flow driven by the
socratic-interviewer role and rotating perspectives (see step B.6). No
MCP tools, no Python runtime, no persistence — the host conversation is
the engine. For a Python-engine variant with numeric ambiguity scoring
(0–1 scale, 40/30/30 weighting) and file-locked persisted
`InterviewState`, see [`../../engine/`](../../engine/) — same `agents/`
SSoT, opt-in for programmatic integrators.

#### B.1 — Adopt the interviewer role

Read `${CLAUDE_PLUGIN_ROOT}/agents/socratic-interviewer.md` and adopt that
role for the interview.

On Codex and Gemini CLI, `${CLAUDE_PLUGIN_ROOT}` is a Claude Code
convention — substitute your platform's plugin-root path (usually the
directory containing `plugin.json`).

#### B.2 — Pre-scan the codebase (if relevant)

If the user's topic mentions an existing project, or the working directory
contains a manifest file:

1. Use `Glob` to check for common manifests: `pyproject.toml`,
   `package.json`, `go.mod`, `Cargo.toml`, `Dockerfile`, `.env.example`,
   `requirements.txt`.
2. If any are found, use `Read` on the most informative ones to extract
   language, framework, dependencies, CI/CD tool, package manager, etc.
3. Incorporate findings into early questions as **confirmation-style**
   questions rather than open-ended discovery:
   - GOOD: "I see Python 3.12 + FastAPI in pyproject.toml. Should the new
     module also use FastAPI?"
   - BAD: "What language does your project use?" (already told by the
     codebase).

#### B.3 — Ask clarifying questions

For each question, route via one of the four paths below. Track which
path each question takes (see B.5 rhythm guard).

**PATH 1a — Auto-confirm** (high-confidence factual, no user block):

When ALL of the following are true:
- The answer is found as an **exact match** in a manifest or config file
  (e.g., `pyproject.toml`, `package.json`, `Dockerfile`, `go.mod`,
  `.env.example`)
- The answer is **purely descriptive** — it describes what exists, not
  what the new feature should do
- There is **no ambiguity** — a single, clear answer

Then:
- Announce the finding to the user as a one-line note:
  "ℹ️ Auto-confirmed from pyproject.toml: Python 3.12, FastAPI framework."
- Use the fact as context for the next question.
- The user can correct at any time by saying "that's wrong" — accept the
  correction and move on.
- Counts as a non-user round for the rhythm guard (B.5).

**PATH 1b — Code Confirmation** (medium confidence — user confirms):

When the codebase has relevant information but confidence is not high
enough for auto-confirm (inferred from patterns, multiple candidates, or
no manifest match):

Present findings to the user as a **confirmation question** via
`AskUserQuestion` (or platform equivalent):

```json
{
  "questions": [{
    "question": "I see JWT-based auth in src/auth/jwt.py. Is this the auth method for the new module?",
    "header": "Auth confirm",
    "options": [
      {"label": "Yes, use JWT", "description": "Extend the existing JWT auth"},
      {"label": "No, different method", "description": "I'll specify a different auth approach"}
    ],
    "multiSelect": false
  }]
}
```

Counts as a non-user round for the rhythm guard (B.5).

**PATH 2 — Human Judgment** (decisions only humans can make):

When the question asks about goals, vision, acceptance criteria, business
logic, preferences, tradeoffs, scope, or desired behavior for new features:

Present the question directly to the user via `AskUserQuestion` (or
platform equivalent) with contextually suggested options where relevant.

Resets the rhythm-guard counter to 0.

**PATH 3 — Code + Judgment** (facts exist but interpretation needed):

When code contains relevant facts BUT the question also requires judgment
(e.g., "I see a saga pattern in `orders/`. Should payments use the same?"):

1. Read relevant code first.
2. Present BOTH the code findings AND the question to the user.
3. Prefix the answer mentally with `[from-user]` (human made the decision).

Resets the rhythm-guard counter to 0.

**PATH 4 — Research Interlude** (external knowledge needed):

When the question asks about third-party APIs, pricing models, library
capabilities, version compatibility, security advisories, or industry
standards that are NOT answerable from the local codebase:

1. Use `WebFetch` or `WebSearch` to gather external information.
2. Present findings as a confirmation question to the user (same pattern
   as PATH 1b).

**Facts, not decisions:** "Stripe rate limit is 100 req/s" is research.
"We should use Stripe" is a DECISION — route that to PATH 2.

Counts as a non-user round for the rhythm guard (B.5).

**When in doubt, use PATH 2.** It is safer to ask the user than to guess.

#### B.4 — Maintain the ambiguity ledger

Track independent ambiguity threads: scope, constraints, outputs,
verification, non-goals. Do NOT let the interview collapse onto one
subtopic — even if the user goes deep on one thread, the ledger forces
you to come back to the others before closing.

Every ~3 rounds, run a **breadth check**: ask yourself "which of the
open threads have I not touched in 3+ rounds?" If any are stale, next
question should surface them.

#### B.5 — Dialectic Rhythm Guard

Track consecutive non-user answers (PATH 1a auto-confirms, PATH 1b code
confirmations, and PATH 4 research confirmations).

If **3 consecutive questions** were answered without direct user judgment
(PATH 1a, 1b, or PATH 4), the next question MUST be routed to **PATH 2**
(directly to user), even if it appears code- or research-answerable.

This preserves the Socratic dialectic rhythm — the interview is with the
human, not the codebase or external docs. Auto-confirmed answers
especially need this guard: if the AI answers too many questions on its
own, the user loses awareness of what the AI is assuming about their
project.

Reset the counter whenever the user answers directly (PATH 2 or PATH 3).

#### B.6 — Rotate perspectives

At each round, pick the perspective that best matches the current state:

| Perspective | File | When to use |
|---|---|---|
| researcher | `${CLAUDE_PLUGIN_ROOT}/agents/researcher.md` | Early rounds with low context; investigation needed |
| simplifier | `${CLAUDE_PLUGIN_ROOT}/agents/simplifier.md` | When scope is creeping or the user is over-specifying |
| architect | `${CLAUDE_PLUGIN_ROOT}/agents/architect.md` | When the problem surface suggests structural issues |
| breadth-keeper | `${CLAUDE_PLUGIN_ROOT}/agents/breadth-keeper.md` | When recent rounds have collapsed onto one thread |
| seed-closer | `${CLAUDE_PLUGIN_ROOT}/agents/seed-closer.md` | When the interview is nearing readiness for closure |
| ontologist | `${CLAUDE_PLUGIN_ROOT}/agents/ontologist.md` | When the user's stated problem seems symptomatic rather than root-cause |

Read the relevant perspective file and apply its `YOUR APPROACH` +
`YOUR QUESTIONS` sections to shape the next question. Do NOT load all
perspectives at once — pick one per round based on need.

#### B.7 — Seed-ready Acceptance Guard

Before suggesting closure, apply the canonical criteria from
`${CLAUDE_PLUGIN_ROOT}/agents/seed-closer.md`:

- Are scope, non-goals, outputs, and verification expectations already
  explicit?
- For brownfield or system-level work: are ownership/SSoT, protocol or
  API contract, lifecycle/recovery, migration, cross-client impact, and
  verification clear enough to execute?
- Did code or research reveal an alternative path that would change
  implementation and needs a human decision?
- Would another question change execution, or just polish wording?

If any material decision remains unresolved, do NOT close. Ask the
single highest-impact follow-up question instead. Only when all criteria
pass does the interview qualify for closure.

#### B.8 — Write the summary on closure

When closure criteria pass and the user confirms, produce a structured
summary with YAML frontmatter + markdown body. Write this directly in
the conversation (not to a file — the user decides where to file it):

```yaml
---
topic: {user's original topic, one line}
goal: {primary objective, 1–2 sentences}
constraints:
  - {hard constraint 1}
  - {hard constraint 2}
acceptance_criteria:
  - {specific measurable criterion 1}
  - {specific measurable criterion 2}
non_goals:
  - {what this explicitly will NOT do}
open_questions:
  - {question explicitly deferred for later}
---

# Interview Summary — {topic}

{2–3 paragraph narrative capturing the interview's key decisions and
rationale. Mention which perspective drove which decision when notable.}
```

## Codex fallback — no `AskUserQuestion`

On Codex, there is no native equivalent to `AskUserQuestion`. For any
step that calls for it, fall back to a plain-text prompt:

```
I have a question:

{question text}

Options:
(1) {option 1 label} — {option 1 description}
(2) {option 2 label} — {option 2 description}
(3) {option 3 label} — {option 3 description}
Other: type your own answer.

Please reply with a number or your own answer.
```

This loses the clean option-list UX but is otherwise functionally
equivalent.

## Gemini fallback — `ask_user`

On Gemini CLI, use `ask_user` in place of `AskUserQuestion`. The argument
shapes are slightly different — consult Gemini CLI docs for the current
spec.

## Example Session

```
User: /3b:interview Add payment module to existing project

(Perspective: researcher)
Q1: "Is this a greenfield or brownfield project? If brownfield, what's
the working directory?"

→ PATH 1a after Glob found pyproject.toml:
ℹ️ Auto-confirmed: Brownfield, Python 3.12 / FastAPI (pyproject.toml)
(rhythm counter: 1)

(Perspective: researcher)
Q2: "What payment provider will you use?"

→ PATH 2 (human decision — no code can answer this)
User: "Stripe"
(rhythm counter reset to 0)

(Perspective: breadth-keeper — noting we've locked in stack + provider
but haven't touched failure modes, auth, or acceptance criteria)
Q3: "How should payment failures affect order state?"

→ PATH 2 (design decision)
User: "Saga pattern — rollback the order if charge fails"
(counter stays at 0)

(Perspective: architect — probing structural fit)
Q4: "I see src/auth/jwt.py. Should the Stripe webhook endpoint also
sit behind JWT, or is it a public endpoint with signature verification?"

→ PATH 1b (found auth; needs decision on how to apply)
User: "Public endpoint, Stripe signature verification only"
(counter: 1 — but user answered so resets)

(Perspective: seed-closer — scope + failure + auth + provider clear)
Q5: "What are the acceptance criteria for this feature — specifically,
what must be verifiable at merge time?"

→ PATH 2
User: "Successful Stripe charge end-to-end, webhook signature validated,
refund endpoint works, order state transitions correctly on both paths"
(counter: 0)

(Seed-ready Acceptance Guard: scope / outputs / verification all
explicit; no open material decisions.)

Q6: "Ready to finalize the interview summary?"

→ User: "yes"

---
topic: Add payment module to existing project (Python 3.12 / FastAPI brownfield)
goal: Integrate Stripe payments into the existing FastAPI service with
  saga-pattern rollback on charge failure and a public webhook endpoint
  verified by Stripe signatures.
constraints:
  - Must integrate with existing FastAPI / Python 3.12 stack
  - Webhook endpoint must be public (no JWT) but signature-verified
  - Order state must rollback on charge failure (saga pattern)
acceptance_criteria:
  - End-to-end successful Stripe charge flow
  - Webhook signature validation working
  - Refund endpoint functional
  - Order state transitions correct on both success and failure paths
non_goals:
  - Multi-currency support (v1 US only)
  - Subscription billing (one-time charges only in v1)
open_questions:
  - Exact error-retry policy on failed webhook delivery — to be decided
    at implementation time
---

# Interview Summary — Add payment module

The user is adding Stripe-based payments to an existing FastAPI (Python
3.12) service. The design uses a saga pattern for order/charge
consistency: if the Stripe charge fails, the order is rolled back.

The Stripe webhook endpoint is intentionally public (not behind JWT) but
guarded by Stripe signature verification — standard pattern. Existing
JWT auth in `src/auth/jwt.py` is preserved for user-facing endpoints
but not applied to the webhook.

Acceptance is end-to-end: real Stripe charge, webhook validation, refund
flow, and correct order-state transitions on both success and failure.
Subscription billing and multi-currency are explicitly out of scope for
v1. Retry policy on webhook delivery failures is deferred to
implementation.
```

## Next Steps

After the summary is written, it's yours — paste it into a design doc,
PR description, ticket, or spec template. The skill's job ends at the
summary; downstream workflows are up to you.
