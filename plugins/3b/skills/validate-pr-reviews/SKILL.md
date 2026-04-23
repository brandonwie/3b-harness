---
name: validate-pr-reviews
description: >-
  Validate AI-generated PR review comments from Claude, Copilot, and Codex.
  Fetches unresolved comments, classifies each as
  valid/invalid/good-to-have/controversial, applies user-approved fixes, and
  logs agent confusion patterns. Use when user says "validate reviews", "check
  pr comments", "handle review feedback", "address pr reviews", or "process
  copilot/claude/codex comments". Do NOT use for writing self-review comments
  (use add-pr-self-reviews instead).
metadata:
  version: "1.11.0"
  changelog:
    - "1.11.0: Phase 6.4 Cascade Decision (NEW) — AskUserQuestion gates whether
      the round summary appends `@claude review`. Removes unconditional trigger.
      Users pick Trigger / Trigger+Wait / Skip per round. Wait duration asked on
      first Trigger+Wait run and cached in `{task_folder}/cascade-config.json`."
    - "1.10.0: Deferred items now persist to project docs/todos.md (Phase 3
      Defer flow). Execution checklist, Phase 5.5 verification, Phase 6.5
      summary, and Quick Reference all updated. Prevents orphan deferrals when
      PR merges before re-addressing."
---

# Validate PR Reviews Skill

## Purpose

Validate AI-generated pull request reviews with:

- Fetch ONLY latest, unresolved comments (skip stale/resolved/hidden)
- **Persist reviews locally** to `docs/actives/{task}/` in the project repo
- Classify each comment (VALID BUG | VALID IMPROVEMENT | GOOD-TO-HAVE |
  CONTROVERSIAL | INVALID)
- **Cross-round dedup**: read previous round files to detect repeated reviews
- Always ask user for GOOD-TO-HAVE and CONTROVERSIAL items
- For INVALID: infer WHY agent was wrong → add code comments to prevent
  recurrence
- Track INVALID patterns in validation file with reinforcing comments
- **MUST update tests when changing source files**
- Support 5+ iteration rounds

## GitHub Comment Policy

**Two levels of GitHub interaction:**

1. **Per-thread replies** (during Phase 3): Reply to each review thread with
   `Dismissed: {Pattern} — {reason}.` or `Fixed in {commit_hash}`, then resolve.
2. **Round summary comment** (Phase 6.5, after push): Post ONE consolidated
   issue comment summarizing all findings — what was fixed, dismissed, and
   deferred. This gives human reviewers a single place to see all changes.

Detailed round-level tracking stays in the local `round-{N}-review.md` file.

## CRITICAL: Execution Checklist (MANDATORY)

Before marking a round complete, verify ALL items:

- [ ] Per-thread replies posted (Phase 3: "Fixed in {hash}" / "Dismissed: ...")
- [ ] Per-thread resolves executed (Phase 3: GraphQL `resolveReviewThread`)
- [ ] **Deferred items appended to project `docs/todos.md`** (Phase 3: under "PR
      Review Deferrals" section — one row per DEFER decision, with PR#, Round,
      Item ID, File:Line, description, date, `[ ]` status)
- [ ] Reinforcement verification passed (Phase 5.5)
- [ ] Commits pushed (Phase 6)
- [ ] Cascade decision captured (Phase 6.4) — Trigger / Trigger+Wait / Skip,
      user-approved via `AskUserQuestion`
- [ ] Round summary comment posted; `@claude review` trailer included **only
      if** Phase 6.4 said Trigger or Trigger+Wait (Phase 6.5)
- [ ] Bot comments + trigger commands minimized (Phase 7.5)

**DO NOT mark complete until checklist satisfied.** The round summary is NOT a
substitute for per-thread cleanup — both must happen.

## Reference Files

Load these during execution when the relevant phase requires detailed reference:

| File                                                         | Use During   | Contains                                                        |
| ------------------------------------------------------------ | ------------ | --------------------------------------------------------------- |
| [api-reference.md](./references/api-reference.md)            | Phase 1, 7.5 | All `gh api` and GraphQL commands, `minimizeComment` mutation   |
| [patterns.md](./references/patterns.md)                      | Phase 3      | 8 confusion patterns, comment templates, 5W1H template          |
| [templates.md](./references/templates.md)                    | Phase 1, 7   | Round file template, Comment Registry format                    |
| [examples.md](./references/examples.md)                      | Any phase    | Full example session, 4 INVALID + 3 CONTROVERSIAL flow examples |
| [pr-review-lifecycle.md](../../rules/pr-review-lifecycle.md) | Phase 1.5    | Canonical severity ↔ classification mapping, pipeline position  |

## DEFAULT BEHAVIOR: Infer + Reinforce (Always Active)

When ANY review is classified as **INVALID**, this workflow is **MANDATORY**:

1. **INFER WHY** - What confused the reviewer? Which pattern does it match?
2. **DOCUMENT PATTERN** - Match to known pattern (8) or create NEW pattern
3. **ADD REINFORCING COMMENT** - Code comment at location prevents future
   confusion. If the pattern template says N/A or doesn't fit, use generic
   fallback: `// NOTE: [claim] is incorrect because [reality]`
4. **LOG TO TRACKING** - Record in local round file with Why Analysis
5. **REPLY & RESOLVE ON GITHUB** - Close the loop on the original comment:
   - For **review threads** (Copilot/Codex): Reply to thread with dismissal
     reason, then **resolve the thread** via GraphQL mutation
   - For **issue comments** (Claude): Post a new issue comment referencing the
     original
   - Reply template:
     `Dismissed: {Pattern Name} — {one-sentence reason}. Reinforcing comment added at {file:line}.`

**This is NOT optional.** Every INVALID review triggers all 5 steps.

### Anti-Escape-Hatch Clause

The following are **NOT valid reasons** to skip reinforcing comments:

- **"Self-evident from code"** → If it were self-evident, the AI reviewer would
  not have flagged it. The comment makes the intent machine-readable.
- **"Already documented elsewhere"** → The flag happened HERE, the comment goes
  HERE. AI reviewers don't cross-reference docs.
- **"Codebase pattern"** → Patterns must be explicit to AI reviewers who have no
  institutional memory. An inline comment costs nothing.
- **"No comment needed"** → Contradicts the mandatory 5-step workflow.

**Only valid skip:** Explicit user-approved skip (user says "skip this one"
during the session). User skips are recorded in the verification table.

## Trigger Phrases

- "validate pr reviews" / "validate reviews"
- "check pr comments" / "review pr reviews"
- "validate-pr-reviews" / "/validate-pr-reviews"
- "pr review {number}" (e.g., "pr review 605")

## AI Agents Tracked

| Agent                  | Identifier                             | Arrival             | Notes                               |
| ---------------------- | -------------------------------------- | ------------------- | ----------------------------------- |
| Claude (GitHub Action) | `claude[bot]` or `github-actions[bot]` | On `@claude review` | Posts as issue comments             |
| GitHub Copilot         | `copilot-pull-request-reviewer`        | 1-5 min after push  | **Async** — may arrive mid-workflow |
| Codex                  | `chatgpt-codex-connector[bot]`         | Variable            | OpenAI code reviewer                |

## GitHub PR Comment Types (CRITICAL)

GitHub has **TWO distinct comment types** on PRs. You MUST fetch BOTH:

| Type                       | API Endpoint                                      | Who Uses It                     |
| -------------------------- | ------------------------------------------------- | ------------------------------- |
| **Issue Comments**         | `/issues/{PR}/comments`                           | `claude[bot]`, human reviewers  |
| **Review Thread Comments** | GraphQL `reviewThreads` or `/pulls/{PR}/comments` | `copilot-pull-request-reviewer` |

If you only fetch review threads, you'll miss Claude's reviews entirely.

## Step 0: Resolve Local Task Folder

Round files are stored **locally in the project repo**, not in 3B.

**Convention:** `{project_repo}/docs/actives/{task_name}/`

### Folder Resolution Algorithm

1. **Detect project repo root** from cwd (find nearest `.git/`)
2. **Check `docs/actives/`** exists. If not, create it.
3. **Gitignore check**: Verify `docs/actives/` is in `.gitignore`. If not, warn
   user: "docs/actives/ is not gitignored — round files are process artifacts
   and should not be committed."
4. **Get current branch**: `git branch --show-current`
5. **List existing task folders** in `docs/actives/`
6. **Match on branch name**: Normalize the branch (e.g.,
   `feat/656-block-ids-sync-payload-v2-endpoint` → extract issue number and key
   words) and compare against existing folder names
7. **If match found** → use that folder
8. **If no match** → ask user: create new folder (suggest name from branch) or
   select an existing one
9. **Count existing `round-*-review.md`** files → next round = count + 1

**Task folder naming**: Use issue number + descriptive kebab-case (e.g.,
`block-ids-sync-656`). Branch prefixes like `feat/`, `fix/` are stripped.

**Store result as `{task_folder}`** — All subsequent references use this
resolved path.

### Project Config (Optional)

Load `3b/.claude/prompts/{project}/PROJECT-CONFIG.md` for GitHub org/repo info
needed by `gh api` commands. The `actives_path` and `todos_path` values in that
config are used by other skills (`/wrap`, `/archive-task`) but are **not used**
for round file resolution.

## Workflow

### Phase 1: Fetch & Persist Reviews

**Read [api-reference.md](./references/api-reference.md) for all fetch
commands.**

1. Get PR number and repo info. **For Round 2+:** read the most recent
   `round-*-review.md` header to get its date — use as `since` parameter in Step
   1A to skip already-processed issue comments (see
   [api-reference.md](./references/api-reference.md) § "Round 2+ Fetch
   Optimization").
2. **STEP 1A**: Fetch Issue Comments (claude[bot], human reviewers)
3. **STEP 1B**: Fetch Review Thread Comments (Copilot inline comments)
4. **STEP 1C**: Parse Claude's Structured Review - extract actionable items from
   "Issues & Recommendations" section (CRITICAL, HIGH → VALID; MEDIUM →
   CONTROVERSIAL; LOW → GOOD-TO-HAVE)
5. **STEP 1D**: Merge and Deduplicate both comment types
6. **STEP 1E**: Identify Trigger Commands — scan fetched issue comments for
   user-typed review invocations (body matches `@claude review`). Capture their
   `node_id` for Phase 7.5 minimization. These are NOT classified — they're UI
   noise to clean up later.
7. **STEP 1F**: Agent Inventory — Report which tracked agents have posted
   reviews. Present: `Agents seen: Claude ✓/✗, Copilot ✓/✗, Codex ✓/✗`. If
   Copilot is missing and the branch was recently pushed (<10 min), note:
   "Copilot reviews may still be arriving (typical: 1-5 min after push)."

**Read [templates.md](./references/templates.md) for round file format.**

Create round file and save to: `{task_folder}/round-{N}-review.md`

### Phase 1.5: Cross-Round Dedup Check

**Before classifying**, check all fetched comments against previous rounds.

**Severity ↔ Classification mapping** (for dedup against proactive review):

| Proactive Severity | Reactive Classification | Dedup Behavior                              |
| ------------------ | ----------------------- | ------------------------------------------- |
| CRITICAL           | VALID BUG               | Auto-mark DUPLICATE if same file ±5 lines   |
| HIGH               | VALID IMPROVEMENT       | Auto-mark DUPLICATE if same claim           |
| MEDIUM             | CONTROVERSIAL           | Flag for user — proactive triage may differ |
| LOW                | GOOD-TO-HAVE            | Flag for user — low severity ≠ invalid      |
| INFO               | (no equivalent)         | Not matched against AI comments             |

See `.claude/rules/pr-review-lifecycle.md` for canonical reference.

1. **Read all existing `round-*-review.md`** files in `{task_folder}` Also read
   `proactive-review.md` if it exists in `{task_folder}`. Findings from the
   proactive review are treated as prior round items for dedup purposes.
2. **Build Seen Registry** from each file's Comment Registry table — collect all
   items with their ID, agent, file:line, and claim summary
3. **Compare each new comment** against the registry using these match rules:

| Match Type         | Criteria                                         | Example                                   |
| ------------------ | ------------------------------------------------ | ----------------------------------------- |
| **Exact location** | Same agent + same file + same/adjacent line (±5) | Copilot flags `sync.ts:142` again         |
| **Same claim**     | Same agent + similar core claim (normalized)     | Claude re-raises "missing error handling" |
| **Pattern repeat** | Same confusion pattern on same file              | Cross-File Blindness on same service      |

1. **For duplicates**:
   - Auto-classify as `DUPLICATE` with reference: `Dup Of: R{M}-{K}`
   - Copy the previous round's classification and Why Analysis
   - No new reinforcing comment needed (previous round added one)
   - Still reply+resolve on GitHub per-thread:
     `Duplicate of Round {M} finding. Already addressed — see reinforcing comment at {file:line}.`
2. **For new items** — proceed to Phase 2 classification as normal
3. **Populate Comment Registry** table in the round file with all items (both
   new and duplicates)

### Phase 2: Present & Classify Each Comment

For each **new** (non-duplicate) comment, determine:

| Classification        | Criteria                                            | Action                        |
| --------------------- | --------------------------------------------------- | ----------------------------- |
| **VALID BUG**         | Real bug, security issue, will cause failure        | Fix immediately               |
| **VALID IMPROVEMENT** | Correct suggestion, improves code quality           | Fix immediately               |
| **GOOD-TO-HAVE**      | Clearly correct but minor, stylistic, not urgent    | **ASK USER** (Fix/Skip/Defer) |
| **CONTROVERSIAL**     | Uncertain correctness, context-dependent, debatable | **DISCUSS → RE-CLASSIFY**     |
| **INVALID**           | Wrong, misunderstood context, doesn't apply         | Document WHY + prevent        |

**Classification Judgment Rule:** When in doubt between GOOD-TO-HAVE and
CONTROVERSIAL, classify as CONTROVERSIAL. Better to discuss unnecessarily than
to skip a discussion that was needed.

**Backward Compatibility:** Old round files using OPTIONAL are process
artifacts. In Phase 1.5 dedup, treat `OPTIONAL` from old rounds as
`GOOD-TO-HAVE` for matching purposes.

**Update round file** with each classification decision.

### Phase 3: Handle Classifications

**Processing Order:** VALID BUG/IMPROVEMENT → CONTROVERSIAL → GOOD-TO-HAVE →
INVALID

#### For VALID BUG / VALID IMPROVEMENT

1. Read affected file
2. Make minimal fix (no scope creep)
3. **MUST update corresponding test file** (see Phase 5)
4. Queue for commit
5. **Reply & resolve on GitHub** — After committing the fix:
   - For **review threads** (Copilot/Codex): Reply with
     `Fixed in {commit_hash}`, then resolve the thread
   - For **issue comments** (Claude): Post a new issue comment referencing the
     fix commit

#### For CONTROVERSIAL (DISCUSS → RE-CLASSIFY)

**Requirement Ambiguity Detection**: Before presenting the For/Against analysis,
check whether the disagreement is about implementation (engineering opinion) or
about intent (requirement ambiguity). If both "For" and "Against" arguments
hinge on different interpretations of a requirement, flag as "REQUIREMENT
AMBIGUITY" and recommend: "This controversy stems from requirement ambiguity,
not code quality. Consider running `/clarify vague` to resolve before
re-classifying."

Present a discussion analysis for each CONTROVERSIAL item:

```text
### CONTROVERSIAL: R{N}-{X} [Agent: {name}]
**File**: `{path}:{line}`
**Suggestion**: "{quoted review text}"

**Analysis**:
- **For**: {why this suggestion could be correct}
- **Against**: {why it might not apply here}
- **Context**: {under what conditions is it right vs wrong}
- **Confidence**: {High / Medium / Low}

Options: → VALID IMPROVEMENT | → INVALID | Fix | Skip | Defer
```

**Re-classification outcomes after discussion:**

| Outcome             | What Happens                                                                                                                     | Round File Records                  |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| → VALID IMPROVEMENT | Fix immediately, update tests                                                                                                    | `CONTROVERSIAL → VALID IMPROVEMENT` |
| → INVALID           | Full 5-step INVALID workflow                                                                                                     | `CONTROVERSIAL → INVALID`           |
| → Fix               | Apply suggestion, queue for commit, reply+resolve                                                                                | `CONTROVERSIAL → FIX (reasoning)`   |
| → Skip              | Add reinforcing comment with discussion reasoning                                                                                | `CONTROVERSIAL → SKIP (reasoning)`  |
| → Defer             | Leave for next round, no reinforcing comment + **append to project `docs/todos.md`** (see "Persistence of Deferred Items" below) | `CONTROVERSIAL → DEFER`             |

#### For GOOD-TO-HAVE (ALWAYS ASK)

Present options to user:

- **Fix** — Apply the suggestion now. Queue for commit. After committing, reply
  `Fixed in {commit_hash}` and resolve the GitHub thread.
- **Skip** — Reject the suggestion. Add reinforcing comment so AI doesn't flag
  it again. Reply+resolve on GitHub.
- **Defer** — Acknowledge but postpone. Record as DEFERRED in round file AND
  **append an entry to the project's `docs/todos.md`** (see "Persistence of
  Deferred Items" below). Do NOT add reinforcing comment (issue remains open for
  next round). Do NOT resolve the GitHub thread (it stays unresolved so the next
  fetch picks it up). The deferred item auto-surfaces in the next validation
  round AND is captured in the persistent project backlog.

#### Persistence of Deferred Items (MANDATORY for any Defer decision)

**Why:** Deferred items are real follow-ups that outlive the PR lifecycle. If
the PR merges before the deferred review is re-addressed, the item orphans in
the round file + GitHub summary comment — neither surfaces in triage or /wrap
workflows. Writing to `docs/todos.md` makes deferred items first-class active
tasks that `/project-context-loader` and `/wrap` both pick up naturally.

**When:** Every time a review item gets `CONTROVERSIAL → DEFER` or
`GOOD-TO-HAVE → Defer` in Phase 3, BEFORE proceeding to the next item.

**Where:** Project repo's `docs/todos.md` (the authoritative active-tasks file;
typically a symlink to `3b/projects/{project}/todos.md`). If no `docs/todos.md`
exists, fall back to `docs/actives/{task}/todos.md` and surface a warning.

**How:**

1. **Check for an existing `## PR Review Deferrals` section.** If absent, create
   it near the top of the file (after the Status Legend / Current Goal header,
   before the first phase section).

2. **Append a table row** with this schema:

   | Column            | Content                                                                                                                                     |
   | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
   | **PR**            | `#{pr_number}`                                                                                                                              |
   | **Round**         | `{N}` (the validation round that deferred it)                                                                                               |
   | **Item ID**       | `R{N}-{X}` (matches the round file Comment Registry ID)                                                                                     |
   | **File:Line**     | The flagged location, or "out of scope" if the review was non-code                                                                          |
   | **Deferred Item** | One-sentence description of the suggestion + WHY it was deferred. Reference the round file for detail: `Ref: round-{N}-review.md R{N}-{X}.` |
   | **Added**         | Today's date in `YYYY-MM-DD`                                                                                                                |
   | **Status**        | `[ ]` initially. Switches to `[x]` when the follow-up is done, or `[-]` if superseded.                                                      |

3. **Template for the section header** (use when creating for the first time):

   ```markdown
   ## PR Review Deferrals

   > Items deferred during `/validate-pr-reviews` that need follow-up after the
   > originating PR merges. Sourced from round file Comment Registry entries
   > with Final classification `CONTROVERSIAL → DEFER` or
   > `GOOD-TO-HAVE → Defer`.

   | PR  | Round | Item ID | File:Line | Deferred Item | Added | Status |
   | --- | ----- | ------- | --------- | ------------- | ----- | ------ |
   ```

4. **Record the todos.md write in the round file's Verification table** — add a
   column "todos.md appended?" so Phase 5.5 can check it.

**Skip conditions:** The project has no `docs/todos.md` AND no equivalent
active-tasks file — in that case, warn the user and rely on the round summary
comment (Phase 6.5) alone. Do not silently drop the defer.

#### For INVALID (MANDATORY: Infer Why + Add Reinforcing Comment)

**Read [patterns.md](./references/patterns.md) for confusion patterns, comment
templates, and 5W1H Why Analysis template.**

Every INVALID review MUST trigger the full analysis workflow to prevent the same
false positive in future reviews.

### Phase 4: Fix Valid Issues

Group fixes by file for **editing efficiency** (read once, apply multiple
fixes). Update round file with planned fixes. Commit scope is determined
separately in Phase 6 — do NOT bundle all fixes into one commit here.

### Phase 5: Test Update Rule (CRITICAL)

**RULE: If a source file is changed, its corresponding test file MUST be
updated.**

```text
Source File Changed          → Test File to Update
─────────────────────────────────────────────────────
<path>/<name>.<ext>          → <path>/<name>.<test-suffix>
```

Substitute the project's own test-file-naming convention for
`<test-suffix>` (e.g. `.spec.ts`, `.test.ts`, `.unit.spec.ts`,
`_test.py`). If the project declares its convention in `CLAUDE.md` /
`TESTING.md`, follow that; otherwise match existing test files in the
repository.

### Phase 5.5: Reinforcement Verification Checkpoint

**Before committing**, verify enforcement:

1. Count all INVALID + user-SKIPPED + CONTROVERSIAL resolved + VALID fixed items
   from Phase 2-3
2. Count reinforcing comments actually added (from git diff or round file)
3. Count GitHub per-thread replies/resolves actually posted
4. Count duplicates auto-resolved from Phase 1.5
5. If **any mismatch** → go back and add missing comments/replies/resolves
6. Fill in the **Reinforcing Comment Verification** table in the round file
7. Present verification summary to user:

```text
Reinforcement Verification:
  INVALID items:         {N}
  Comments added:        {N} ✓/✗
  VALID items fixed:     {N}
  CONTROVERSIAL resolved:{N} (→VALID: {N}, →INVALID: {N}, →Fix: {N}, →Skip: {N}, →Defer: {N})
  GOOD-TO-HAVE decided:  {N} (Fix: {N}, Skip: {N}, Defer: {N})
  GitHub replies:        {N} ✓/✗  (per-thread only)
  Threads resolved:      {N} ✓/✗
  Duplicates resolved:   {N}
  User skips:            {N}
  Deferred:              {N}
  todos.md appended:     {N} ✓/✗   (must equal Deferred count, unless docs/todos.md is absent)
  Status:                PASS / FAIL (go back and fix)
```

**Do NOT proceed to Phase 5.7 until verification passes.**

### Phase 5.7: Pre-Commit Re-Fetch (Late Arrivals)

**Before committing**, re-fetch unresolved review threads to catch reviews that
arrived during the workflow (especially Copilot, which posts 1-5 min after
push).

1. Re-run Phase 1 STEP 1B (fetch unresolved review threads via GraphQL)
2. Compare against the Phase 1 fetch — identify NEW threads not in the round
   file
3. If new threads found:
   - Append to the round file's Comment Registry as "Late Arrival" items
   - Classify and handle per Phase 2-3 rules (same round, not a new round)
   - Re-run Phase 5.5 verification with updated counts
4. If no new threads → proceed to Phase 6

**CRITICAL:** Do NOT skip this step. Copilot reviews routinely arrive 1-5
minutes after push, which falls within the typical Phase 1-5.5 execution window.

### Phase 6: Commit & Push

**One fix = one commit.** Each finding gets its own atomic commit containing the
source fix + corresponding test update. The only merge exception: multiple
reinforcing NOTEs added to the same file in one round may share a commit.

**Commit message format:**

```text
{type}(#{issue}): {descriptive summary of what changed and why}
```

**No internal IDs in commit messages.** IDs like R{N}-{X}, CR-{X}, F-{cat}-{X}
are session-internal tracking — they belong in round files and reinforcing code
comments, NOT in git history.

Good:

```text
fix(#708): add operation context to IntegrationCredentialsExpiredException
fix(#708): add WARNING JSDoc for undefined calendarRepo parameter
docs(#708): convert narrative JSDoc to inline WHY comment in helper
```

Bad:

```text
fix(#708): address round-1 review findings R1-1, R1-6, CR-1, CR-4
fix(#708): address Round 2 AI review findings R2-1 through R2-5
```

Push after all commits pass verification (Phase 5.5).

### Phase 6.4: Cascade Decision (MANDATORY)

Before posting the round summary, ask the user whether to trigger the next
review cycle on the just-pushed commits. This replaces the previous
unconditional `@claude review` trailer — the user controls cascade per round.

**Tool:** `AskUserQuestion` — one question, three options, `multiSelect: false`.

**Question:** "Trigger next review round on these commits?"

| Label            | Description                                                                                    |
| ---------------- | ---------------------------------------------------------------------------------------------- |
| `Trigger Claude` | Append `@claude review` to the round summary. Claude (bot) re-reviews in ~2–5 min. No wait.    |
| `Trigger + Wait` | Append `@claude review` AND pause the skill for the cached wait duration before offering next. |
| `Skip trigger`   | Post summary WITHOUT `@claude review`. Round ends; user manually re-invokes when ready.        |

Store the answer as `cascade_decision`. Phase 6.5 reads it to decide whether the
trailer is emitted.

**Wait-duration sub-question (first Trigger+Wait run per task folder only):**

1. Check for `{task_folder}/cascade-config.json`. If present and it contains
   `wait_minutes`, reuse that value — skip the sub-question.
2. Otherwise fire a second `AskUserQuestion`: "How long to wait before offering
   the next round?" with options `2 min`, `3 min`, `5 min`, `7 min` (multiSelect
   `false`).
3. Persist the chosen value to `{task_folder}/cascade-config.json` as
   `{ "wait_minutes": <N> }`. Create the file if missing.
4. `cascade-config.json` is a task-folder-scoped cache. It SHOULD be gitignored
   by the consumer project's `docs/actives/` gitignore (the task folder is
   already ignored per `pr-review-lifecycle.md`).

Do NOT write `cascade-config.json` when the answer is `Trigger Claude` (no wait)
or `Skip trigger` — only `Trigger + Wait` caches a duration.

### Phase 6.5: Post Round Summary Comment

After Phase 6.4, post ONE consolidated issue comment on the PR summarizing the
round's outcomes. This is the human-readable audit trail.

**Command:**

```bash
gh api repos/{owner}/{repo}/issues/{PR}/comments \
  -f body="{summary}"
```

**Format (trailer is conditional on Phase 6.4):**

```markdown
## Addressed {agent} review findings (Round {N})

**{total} items from {agent}** — {fixed} fixed, {dismissed} dismissed,
{deferred} deferred.

### Fixed

- **R{N}-X** `file:line` — {description} (`{commit_hash}`)

### Dismissed (INVALID)

- **R{N}-X** `file:line` — {claim}: {reason for dismissal}. Reinforcing NOTE
  added.

### Deferred

- **R{N}-X** `file:line` — {description}. Tracked as follow-up in
  `docs/todos.md` § PR Review Deferrals.

**Commits:** `{hash1}`, `{hash2}`, ...

---

{TRAILER}
```

**TRAILER rules (gated by Phase 6.4 `cascade_decision`):**

| `cascade_decision` | Trailer emitted                                                                          |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `Trigger Claude`   | `@claude review` on its own line after the `---` separator                               |
| `Trigger + Wait`   | `@claude review` on its own line after the `---` separator                               |
| `Skip trigger`     | No trailer line — omit `@claude review` entirely (and the `---` if nothing else follows) |

The `@claude review` trailer is no longer unconditional. Emitting it without a
Phase 6.4 decision is a skill-contract violation.

**Rules:**

- One comment per round (not per item)
- Include commit hashes for fixed items
- Brief dismissal reasons (1 sentence)
- Deferred items get explanation of why deferred
- Skip sections with zero items (e.g., no "Deferred" heading if nothing
  deferred)

### Phase 7: Update Tracking & Report

**Read [templates.md](./references/templates.md) for aggregation tracking
format.**

Update local round file status to Completed. Present summary report showing:
Fixed items, GOOD-TO-HAVE decisions, CONTROVERSIAL discussion outcomes, Invalid
reviews documented, Duplicates auto-resolved, Tests updated, Commit hash, Push
status.

**Pattern aggregation** still goes to 3B:
`knowledge/ai-ml/ai-code-review-confusion-patterns.md` — update when 2+ INVALID
reviews occur in a round.

Ask if ready for next review round.

**Post-push cascade (gated by Phase 6.4):**

- `Trigger Claude` → summary comment includes `@claude review`. Claude (bot)
  responds in ~2–5 min on the new commits. No forced wait.
- `Trigger + Wait` → summary comment includes `@claude review` AND the skill
  pauses for the cached `wait_minutes` (from
  `{task_folder}/cascade-config.json`) before offering the next round. Copilot
  may also re-review during the wait window.
- `Skip trigger` → summary comment omits `@claude review`. Round ends. Next
  round requires manual re-invocation of `/validate-pr-reviews`.

### Phase 7.5: Minimize Processed Comments

After the round report, clean up the PR conversation by minimizing addressed
comments. This replaces the manual "Hide comment → Resolved" workflow.

**Read [api-reference.md](./references/api-reference.md) § "Minimizing Issue
Comments" for all commands.**

**What gets minimized (with `RESOLVED` classifier):**

1. **AI bot review comments** — `claude[bot]` / `github-actions[bot]` issue
   comments that were processed in this round (matched by date/content against
   round file)
2. **Trigger commands** — user-typed `@claude review` comments captured in Phase
   1 Step 1E
3. **Only unminimized** — skip comments where `is_minimized` is already true

**What stays visible:**

- Human discussion comments (non-bot, non-trigger)
- **Our own replies** posted during Phase 3-7 ("Fixed in {hash}", "Dismissed:
  {Pattern}...", "Addressed in {hash}") — these are the validation trail and
  must remain visible
- Fix confirmation replies on resolved threads (already collapsed)
- DEFERRED items (not yet addressed — stay visible for next round)
- The PR description

**Steps:**

1. Collect `node_id`s from Phase 1 fetch: bot review comments + trigger commands
2. Filter out already-minimized (`is_minimized: true`)
3. Filter out any comments tied to DEFERRED items (not yet addressed)
4. For each remaining `node_id`: call `minimizeComment` mutation
5. Report: "Minimized {N} comments ({M} bot reviews, {K} triggers)"

**Skip conditions** (do NOT minimize):

- Round has DEFERRED items that reference the AI review → the review body is
  still needed for the next round
- User explicitly says "don't minimize" or "keep visible"

## File Structure

```text
{project_repo}/
└── docs/
    └── actives/                       # Gitignored — process artifacts
        └── {task_name}/               # e.g., block-ids-sync-656
            ├── round-1-review.md      # Round 1 validation
            ├── round-2-review.md      # Round 2 validation
            ├── round-3-review.md      # Round 3 validation
            └── ...                    # Up to 5+ rounds
```

## Iteration Support

Track round number via files in the local task folder:

- Count existing `round-*-review.md` files
- Next iteration = count + 1
- Show progress: "Round 3 of ~5 typical iterations"

## Quick Reference

```text
STEP 0:      Resolve local task folder in project repo
FOLDER:      {project_repo}/docs/actives/{task_name}/
FILE:        round-{N}-review.md
TRIGGER:     "validate pr reviews" | "pr review {number}"

FOLDER RESOLUTION (Step 0):
  1. Find repo root (nearest .git/)
  2. Check docs/actives/ for existing task folders
  3. Match on branch name (normalize, strip prefix)
  4. No match → ASK USER (create or select)

FETCH (BOTH TYPES - Phase 1):
  1. Issue Comments:  gh api repos/{owner}/{repo}/issues/{PR}/comments
     → claude[bot], human reviewers (general PR comments)
  2. Review Threads:  GraphQL reviewThreads (filter isResolved=false)
     → copilot-pull-request-reviewer (inline code comments)

DEDUP (Phase 1.5):
  Read all round-*-review.md → build Seen Registry from Comment Registry
  tables → mark duplicates as DUPLICATE (R{M}-{K}) → auto-resolve

PERSIST:     Save all comments to local round file FIRST
CLASSIFY:    VALID BUG | VALID IMPROVEMENT | GOOD-TO-HAVE | CONTROVERSIAL | INVALID | DUPLICATE
GOOD-TO-HAVE:   ALWAYS ask user (Fix/Skip/Defer)
CONTROVERSIAL:   DISCUSS first (For/Against/Context/Confidence) → RE-CLASSIFY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVALID or SKIPPED HANDLING (MANDATORY - All 5 Steps, 5W1H)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. INFER WHY      - Complete 5W1H Why Analysis Template
  2. DOCUMENT       - Match to pattern or create NEW
  3. REINFORCE      - Add code comment at flagged location
  4. LOG            - Record in round file
  5. REPLY+RESOLVE  - Reply on GitHub thread + resolve (Copilot)
                      or post issue comment (Claude)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VALID FIXED:  Reply "Fixed in {hash}" + resolve thread on GitHub
DUPLICATE:    Reply "Duplicate of Round {M}. Already addressed." + resolve
DEFERRED:     Append row to project docs/todos.md § "PR Review Deferrals"
              (MANDATORY — deferred items orphan without this; leave GitHub
              thread unresolved so next round still picks it up)
VERIFY (Phase 5.5): Count INVALID + VALID + DUPLICATE + DEFERRED items vs
                     comments/replies/resolves/todos.md rows. Mismatch → go
                     back. Do NOT proceed to COMMIT until PASS.

GITHUB POLICY: Per-thread replies/resolves (Phase 3) +
               ONE round summary comment after push (Phase 6.5).

MINIMIZE (Phase 7.5):
  Bot reviews + trigger commands → minimizeComment(RESOLVED)
  Skip: already minimized, DEFERRED-linked, user opt-out

TESTS:       MUST update tests when source files change
COMMIT:      One fix = one commit (source + test). No IDs in messages.
ITERATE:     Support 5+ rounds
AGGREGATE:   Update knowledge/ai-ml/ai-code-review-confusion-patterns.md
```

## Troubleshooting

| Problem                                         | Cause                                              | Fix                                                                               |
| ----------------------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------- |
| No comments found                               | All resolved, or wrong PR number                   | Verify PR number with `gh pr view`; check if comments are already resolved        |
| Missing Claude reviews                          | Only fetched review threads, not issue comments    | Fetch BOTH: issue comments (`/issues/{PR}/comments`) AND review threads (GraphQL) |
| GraphQL query fails                             | Token lacks `read:org` or `project` scope          | Run `gh auth status`; re-auth with required scopes if needed                      |
| `docs/actives/` not gitignored                  | Missing `.gitignore` entry                         | Add `docs/actives/` to project `.gitignore`; warn user                            |
| No matching task folder                         | Branch name doesn't match any existing folder      | Ask user: create new folder or select existing; suggest name from branch          |
| Test file doesn't exist                         | New source file without test, or non-standard path | Ask user: create new test file or skip test update with justification             |
| Claude review format changed                    | Bot updated its output structure                   | Adapt parsing; look for "Issues & Recommendations" or similar heading             |
| INVALID pattern doesn't match any known pattern | New type of AI confusion                           | Create NEW pattern entry; assign next number in the confusion patterns list       |
| Round count wrong                               | Stale `round-*-review.md` files from previous PR   | Verify files match current PR; clean up stale files or reset count                |
| Reinforcing comment causes lint error           | Comment syntax conflicts with linter rules         | Use `// eslint-disable-next-line` or adjust comment format to pass linting        |
| Duplicate detection false positive              | Different claim at adjacent line                   | Review manually; override by classifying as new item                              |
