<!--
⚠️ WAVE 1 STATUS — 3B-opinionated reference template.
This file references `3b/.claude/rules/*` paths that only exist inside the
maintainer's private 3B repo. Wave 2 will strip those references and split
this file into a minimal universal CLAUDE.md plus an optional 3B-methodology
extension. For now, treat this as reference, not as a ready-to-install template.
-->

# Global Claude Instructions

These instructions apply to ALL projects.

---

## Universal Principles (CRITICAL)

### 1. YAML Frontmatter

Every markdown file MUST have YAML frontmatter. Minimum: `tags:`, `created:`,
`updated:`, `status:` (values: not-started / in-progress / completed). Full 3B
schema with optional fields (`source`, `projects`, `related`, `when_used`,
`references`, `confidence`, `blog`) in
`3b/.claude/rules/yaml-frontmatter-schema.md` — auto-loads when editing `.md`.

### 2. Cross-Referencing

- **Forward links only** — maintain `related:` + `when_used:` in frontmatter.
- **Backlinks are computed, NEVER stored** — do NOT add `backlinks:` to any
  file.
- **Use relative markdown paths**, not wiki-style `[[links]]`.

### 3. 5W1H Documentation

Knowledge entries answer **Who / When / Where / What / Why / How**. Full
template + required sections in `3b/.claude/rules/knowledge-creation.md` —
auto-loads when editing `knowledge/`.

### 4. Decision Documentation Protocol

For every non-trivial decision, evaluate options **before** implementation and
document the outcome:

1. **Problem** — what decision is needed
2. **Feasible options** (aim for 3; minimum 2; present 1 only when genuinely no
   alternative exists) with pros/cons:

   | Option   | Pros         | Cons         |
   | -------- | ------------ | ------------ |
   | Option A | Pro 1, Pro 2 | Con 1        |
   | Option B | Pro 1        | Con 1, Con 2 |
   | Option C | Pro 1, Pro 2 | Con 1, Con 2 |

3. **Chosen option** — which one and WHY, citing specific pros/cons that drove
   the choice (e.g., "Option B because [Pro 1] outweighs [Con 1] given
   [constraint]")
4. **Constraints** — what influenced the choice

A decision is non-trivial if it affects architecture, is hard to reverse,
involves trade-offs, or costs significant time.

### 5. Zettelkasten Methodology

- **Atomic notes** — one concept per file, small and reusable.
- **Rich connections** — `related:` forward links in frontmatter (not inline).
- **Unique identity** — clear titles, kebab-case filenames.
- **Own words** — restate concepts; don't copy-paste sources.
- **Progressive layers** — journal → knowledge → guide → architecture → blog.

Frontmatter connects notes; connections turn isolated notes into a networked
brain. Templates in `3b/.claude/rules/knowledge-creation.md`.

### 6. Git Commit Discipline

**Atomic commits + Conventional Commits.** Stage specific files by name (never
`git add -A`). One logical change per commit. Format `type(scope): subject`;
issue refs in the footer (`Closes #N`). Common types: `feat`, `fix`, `refactor`,
`chore`, `docs`, `test`, `perf`. Use `/commit` for guided atomic staging. Full
rules: `3b/.claude/rules/change-discipline.md` § Commit Scope.

**Branch cleanup** — on "cleanup branch" after merge:

1. `git branch -d <branch>`
2. `git push origin --delete <branch>` (if not auto-deleted)
3. `git remote prune origin`

If uncertain whether a branch should be deleted, ask first.

**Plan → implementation transition** — on exiting plan mode:

1. **MUST** invoke `/task-starter` BEFORE any edits (handles branch, context,
   scaffolding).
2. Only after `/task-starter` completes, proceed with code changes.

**Post-implementation workflow:**

1. **Mid-session commits stay user-initiated.** Use `/commit` for atomic
   staging; do NOT auto-commit code you just wrote unless the user asks.
2. **Session-end is the exception.** `/wrap` auto-commits (stage by name, atomic
   Conventional Commit) and auto-pushes on feature/task branches; asks once on
   `main`/`master`. Overrides: `no-commit`, `no-push`, `+pr`.
3. **Safety confirms required for destructive ops** — force-push,
   `git reset --hard`, amending published commits.
4. PR creation stays opt-in — `/wrap` does NOT invoke `/pr-creator` unless `+pr`
   is passed.

### 7. Scientific Thinking

Reason from evidence, not assumptions. Before making claims, recommending
solutions, or drawing conclusions, apply hypothesis-driven reasoning.

**Pre-claim checklist (apply before asserting or recommending):**

| Step                    | Action                                          |
| ----------------------- | ----------------------------------------------- |
| 1. State hypothesis     | "I believe X because Y" — make it falsifiable   |
| 2. List assumptions     | What am I taking for granted?                   |
| 3. Check for bias       | Am I anchored, confirming, or sunk-cost biased? |
| 4. Seek disconfirmation | What evidence would prove me wrong?             |
| 5. Rate confidence      | High / Medium / Low / Unverified                |

**When to apply:**

- Diagnosing bugs or unexpected behavior (complements Root Cause Verification)
- Choosing between approaches (complements Decision Documentation #4)
- Making claims about what code does or why something fails
- Writing knowledge entries or investigation reports
- Any time you catch yourself saying "probably" or "I think"

**When NOT to apply:**

- Trivial operations (renaming, formatting, mechanical edits)
- Executing an already-approved plan
- Tasks with no ambiguity

**Cognitive biases to watch for:**

| Bias         | Symptom                                          |
| ------------ | ------------------------------------------------ |
| Confirmation | Only seeking evidence that supports your idea    |
| Anchoring    | Over-weighting the first piece of info found     |
| Sunk cost    | Continuing a failing approach because of effort  |
| Availability | Assuming recent/memorable patterns are universal |
| Bandwagon    | Preferring popular tools without evaluating fit  |

**Integration with existing principles:**

- **Decision Documentation (#4)** handles WHAT was decided and WHY. Scientific
  Thinking adds: state the hypothesis first, document assumptions, seek
  disconfirming evidence.
- **Root Cause Verification** (3B Change Discipline) IS causal analysis.
  Scientific Thinking adds: what would disprove this root cause?
- **Prototype-first** (3B Change Discipline) IS hypothesis testing. Scientific
  Thinking adds: state expected outcome before prototyping.
- **`/investigate` skill** already uses hypothesis + confidence. This principle
  extends that reasoning to ALL tasks, not just investigations.
- **Friction Capture** IS empirical observation. Scientific Thinking adds:
  distinguish correlation from causation in pattern detection.

### 8. Context Efficiency

Context window is the scarcest resource. Prefer pointers over inline content.

**Strategies (priority order):**

1. **Path pointers** — reference `.claude/rules/*.md`, templates, or docs by
   path instead of duplicating content in CLAUDE.md
2. **Fetch on demand** — use WebFetch for external docs (official APIs, best
   practices) instead of memorizing them; URLs belong in project CLAUDE.md or
   rules files
3. **Subagent delegation** — offload file-heavy research to subagents so
   findings return as summaries, not raw file contents
4. **Lazy-loaded skills** — domain knowledge belongs in `.claude/skills/`, not
   CLAUDE.md; skills load only when invoked

**During compaction:** preserve file paths, URLs, decision rationale, and
modified file lists. Drop fetched web content, verbose tool output, and
exploratory dead ends.

### 9. Execution Integrity

Session diagnostics across 1200+ sessions reveal four recurring anti-patterns
that account for most user frustration. Each has a concrete countermeasure.

| Anti-Pattern         | Diagnostic Signal   | Countermeasure                                         |
| -------------------- | ------------------- | ------------------------------------------------------ |
| Edit thrashing       | 3+ edits, same file | Full read → plan all changes → single edit pass        |
| Error loops          | Retrying same fix   | 2 consecutive failures = mandatory strategy change     |
| Drift from request   | Output ≠ what asked | Re-read original request every 3–5 turns               |
| Shallow verification | Rapid corrections   | Verify every instruction was met before reporting done |

**Edit once:** Read the full target file before touching it. Plan all intended
changes, then make one comprehensive edit. If you have already edited the same
file 3+ times in a task, stop — re-read the user's original request and batch
remaining changes into a single pass.

**Fail fast, pivot faster:** After 2 consecutive tool errors or failed fix
attempts on the same issue, do not retry the same approach. Summarize what you
tried, what failed, and why. Then either try a fundamentally different strategy
or surface the blocker to the user.

**Stay anchored:** In multi-turn tasks, periodically re-read the original
request to verify current work still addresses what was asked. Before reporting
a task as complete, walk through every instruction in the request and confirm
each one was addressed — not just the most recent exchange.

**Accept corrections cleanly:** When corrected, re-read the original message
before responding. Identify what was missed or misread. Confirm the revised
understanding before continuing — do not apply a surface-level fix to a
misunderstood requirement.

### .me.md Files (Read-Only)

Files ending in `.me.md` are human-authored seed documents. **NEVER edit a
`.me.md` file.** Read for context only.

### Buffer (Cross-Session Memory)

Write to buffer IMMEDIATELY when something important happens.

**Location:** `~/dev/personal/3b/.claude/buffer.md`

**Format:**

```text
## YYYY-MM-DD HH:MM - {project}
**What:** {one line summary}
**Why it matters:** {why worth remembering}
**Details:** {context with 5W1H}
```

**When to write:** Decisions made, problems solved, patterns discovered, useful
references found, non-obvious learnings.

### Active Work Status (Cross-Session Dashboard)

Auto-generated dashboards track in-progress tasks, todos, and recently completed
work. Check at session start for cross-session continuity.

**Location:** `~/dev/personal/3b/ACTIVE-STATUS.md`

Generated by `/wrap` Step 5.7. Read by `/project-context-loader` and
`/task-starter` automatically. Contains work tasks, personal goals, stale
alerts, and per-category recently completed items.

### Communication Style

| DO                             | DO NOT                           |
| ------------------------------ | -------------------------------- |
| Acknowledge and correct        | Say "I'm sorry" or "I apologize" |
| Present facts objectively      | Give excessive praise            |
| Cool-headed, professional tone | Emotional responses              |

### 3B (Brandon's Binary Brain)

All repos share a centralized knowledge system called **3B**
(`~/dev/personal/3b`). It is the **single source of truth** for:

| What              | SoT Location in 3B                         | Symlinked As         |
| ----------------- | ------------------------------------------ | -------------------- |
| Project CLAUDE.md | `.claude/project-claude/{name}.md`         | `CLAUDE.md`          |
| Project .mcp.json | `.claude/project-claude/{name}.mcp.json`   | `.mcp.json`          |
| Project config    | `.claude/prompts/{name}/PROJECT-CONFIG.md` | (read by skills)     |
| Project docs/     | `projects/{name}/`                         | `docs/` (gitignored) |
| Global settings   | `.claude/global-claude-setup/`             | `~/.claude/*`        |

**Key behaviors:**

- **Verify before use:** Before any `docs/`-related work, run `ls -la docs/` to
  check if it exists and whether it is a symlink. If the symlink is broken or
  missing, ask the user before proceeding — do NOT create a local `docs/`.
- `docs/` in 3B-connected repos is a **symlink** — gitignored because it points
  to personal content. Do NOT delete or overwrite the symlink.
- Not all repos have `docs/` (e.g., forked or experimental repos). When
  docs-related work is needed in a repo without `docs/`, ask the user whether to
  connect it to 3B (`/init-3b`) or keep docs local.
- `CLAUDE.md` in repos is a **symlink** to 3B — edit the source in
  `3b/.claude/project-claude/`, not the symlink target.
- `projects/{name}/` holds both docs AND task tracking (`todos.md`, `actives/`,
  `PROGRESS.md`). Skills like `/wrap` and `/task-starter` read
  `PROJECT-CONFIG.md` to locate these files.
- Use `/init-3b` to connect a new repo to this system.

---

## Diagrams in Markdown

Use Mermaid (`flowchart`, `sequenceDiagram`, `stateDiagram-v2`) for
architecture, data flow, pipeline, and state diagrams. Never use ASCII box art
(`┌`, `│`, `└`, `─`). Directory trees (`├──`) and inline arrows in prose are
fine as plain text.

---

## Runtime Environment

**Strategy:** asdf for dev language runtimes (version pinning per-project),
Homebrew for apps and tools. Never use `nvm`, `pyenv`, `rustup`, or other
single-language managers.

Full version tables (asdf runtimes + brew-managed languages) live in
`3b/.claude/rules/runtime-environment.md` — auto-loaded when working with
`.tool-versions`, `Brewfile`, `package.json`, or other runtime config files.

---

## Repeating Task Tracker

After completing any non-trivial task, check if it's a recurring pattern worth
automating. Invoke the `/task-tracker` skill (or it runs automatically via
`/wrap` Step 4.7). Full logic, thresholds, and suggestion flow live in
`~/.claude/skills/task-tracker/SKILL.md`.

---

## Friction Capture

Write `[FRICTION]` tagged entries to the buffer when Claude hits config-related
friction (wrong assumption, missing rule, permission block). Extraction, pattern
detection, and improvement proposals run during `/wrap` Step 4.7. Storage:
`~/.claude/friction-log.json` (active) + `friction-log-archive.json` (resolved).
Lifecycle rules in `3b/.claude/rules/change-discipline.md` § Friction Lifecycle.

---

## External Tool Routing

Policies for installed external tools available across all projects:

- **Firecrawl** (web scraping/search/interact, free tier 1,175 credits) — see
  `~/dev/personal/3b/.claude/rules/firecrawl-usage.md` for decision matrix
  (WebFetch vs firecrawl-\* vs playwright vs chrome-devtools) and credit
  discipline. Default to free tools first; explicit user confirmation required
  before `firecrawl-crawl` or `firecrawl-download`.

---

## Compact Instructions

When compaction runs, preserve:

- File paths touched (edits, creates, deletes)
- Decision rationale (ADRs, `/investigate` hypotheses, plan.md approvals)
- Skill invocations with arguments (`/wrap`, `/task-starter`, etc.)
- Commit hashes, PR numbers, issue numbers
- Friction-log entries and corrections
- Knowledge file paths created or updated (`knowledge/{cat}/{file}.md`)
- Active task folder state (`projects/*/actives/*/todos.md` progress)

Drop:

- Verbose tool output (full file contents re-read, long test logs)
- Exploratory grep/glob results once the target was found
- Rejected approach branches (keep only the chosen path + why)

---

## Update Log

| Date       | Rule Added                                               | Reason                                                           |
| ---------- | -------------------------------------------------------- | ---------------------------------------------------------------- |
| 2026-04-19 | Compressed principles #1, #2, #3, #5, #6 to pointers     | CLAUDE.md lazy-load SSoT (#17) — ~73 lines/~1K tok/session saved |
| 2026-04-18 | Diet: Runtime Env → scoped rule, Task Tracker → skill    | Token usage reduction (#13) — ~1,800 tok/session saved           |
| 2026-04-18 | Friction Capture compressed to 6-line pointer            | Full logic in change-discipline.md § Friction Lifecycle          |
| 2026-04-18 | Compact Instructions section                             | Smarter auto-compact — preserve file paths, decisions, hashes    |
| 2026-04-17 | Removed Parallel Task Advisory + Agent Teams (old #7/#8) | ~800–1300 tokens/session saved; `Agent` tool covers parallelism  |
| 2026-04-16 | Execution Integrity (#9)                                 | claude-doctor diagnostics: edit-thrashing, error-loops, drift    |
| 2026-04-15 | External Tool Routing section (Firecrawl pointer)        | User opted in to global rule application across all repos        |
| 2026-04-03 | Plan→impl transition + post-impl workflow (#6)           | Skipped /task-starter and branch creation during F.1 impl        |
| 2026-03-31 | 3B awareness section                                     | Cross-repo friction: Claude didn't know why docs/ gitignored     |
| 2026-03-22 | Decision Documentation (#4): planning gate + aim-for-3   | Was retrospective-only; now evaluates options before impl        |
| 2026-03-12 | Agent Teams: clarify TeamCreate vs Agent tool            | Subagents never split panes; TeamCreate is the only path         |
| 2026-03-09 | Context Efficiency (#8), compaction instructions         | Pointer-over-inline strategy; fetch-on-demand for docs           |
| 2026-03-02 | Scientific Thinking (#7), `confidence:` field            | Hypothesis-driven reasoning gaps across all projects             |
| 2026-02-25 | Git Commit Discipline, Parallel Task Advisory            | Atomic commit gap in global; hook-based team detection           |
| 2026-02-23 | Universal Principles (8 items), markdownlint compressed  | Promote 5W1H/frontmatter/cross-ref/decisions/Zettelkasten        |
| 2026-02-12 | Friction Capture                                         | Self-improving config via friction pattern detection             |
| 2026-02-04 | Repeating Task Tracker                                   | Auto-detect recurring tasks, suggest skills/hooks/commands       |
| 2026-03-09 | Removed markdownlint table, compressed Mermaid section   | Tooling enforces lint; ~125 lines saved from context load        |

## graphify

- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge
  graph. Trigger: `/graphify` When the user types `/graphify`, invoke the Skill
  tool with `skill: "graphify"` before doing anything else.

@RTK.md
