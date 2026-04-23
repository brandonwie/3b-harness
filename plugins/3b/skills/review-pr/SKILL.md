---
name: review-pr
description: >-
  Proactive PR code review using 3 specialized agents in parallel. Analyzes PR
  diff across 7 categories (Security, Code Quality, Performance, Architecture,
  Test Quality, Maintainability, Deployment Safety) and produces structured
  findings with severity-based triage. Use when user says "review pr",
  "proactive review", "code review pr", or "/review-pr". Companion to
  validate-pr-reviews (reactive). Do NOT use for responding to AI reviewer
  comments (use validate-pr-reviews instead).
metadata:
  version: "1.0.0"
---

# Proactive PR Review Skill

## Purpose

Generate proactive code review findings by spawning 3 specialized agents in
parallel, each covering 2-3 of 7 review categories. Produces a unified
`proactive-review.md` with severity-based triage.

**This is a companion to `validate-pr-reviews`:**

| Aspect     | `validate-pr-reviews` (reactive) | `review-pr` (proactive)      |
| ---------- | -------------------------------- | ---------------------------- |
| Purpose    | Classify AI reviewer comments    | Generate findings ourselves  |
| Input      | AI comments from GitHub          | PR diff + changed files      |
| Agent mode | Single session, sequential       | 3 agents in parallel         |
| Output     | `round-{N}-review.md`            | `proactive-review.md`        |
| When       | After AI reviews arrive          | Before requesting AI reviews |

## Trigger Phrases

- "review pr" / "proactive review" / "code review"
- "review-pr" / "/review-pr"
- "review pr {number}" (e.g., "review pr 700")

## Reference Files

Load during execution when the relevant phase requires detailed reference:

| File                                                          | Use During | Contains                                              |
| ------------------------------------------------------------- | ---------- | ----------------------------------------------------- |
| [categories.md](./references/categories.md)                   | Phase 1    | 7 category checklists by agent group                  |
| [agent-prompts.md](./references/agent-prompts.md)             | Phase 1    | Spawn prompt templates with placeholders              |
| [output-format.md](./references/output-format.md)             | Phase 1, 2 | Finding format contract, severity mapping             |
| [clean-review-bridge.md](./references/clean-review-bridge.md) | Phase 1    | Pointers to Clean Code/Refactoring refs               |
| [pr-review-lifecycle.md](../../rules/pr-review-lifecycle.md)  | Any        | Pipeline position, severity mapping, shared artifacts |

## 3 Agent Groups

| Agent               | Categories                                                         | Finding Prefix |
| ------------------- | ------------------------------------------------------------------ | -------------- |
| **Safety Agent**    | 1. Security Review + 7. Dependency & Deployment Safety             | F-S-           |
| **Structure Agent** | 4. Architectural Assessment + 2. Code Quality + 6. Maintainability | F-T-           |
| **Runtime Agent**   | 3. Performance Analysis + 5. Test Quality                          | F-R-           |

All agents spawn simultaneously using `subagent_type: "Explore"` (read-only).

## Optional Category Selection

- `/review-pr` → all 3 agents (default)
- `/review-pr --safety` → Safety Agent only
- `/review-pr --structure` → Structure Agent only
- `/review-pr --runtime` → Runtime Agent only

Parse args to determine which agents to spawn. Default: all 3.

---

## Workflow

### Phase 0: Context Gathering

1. **Get PR number**: From user argument, or detect via
   `gh pr view --json number`
2. **Resolve task folder** using the same algorithm as `validate-pr-reviews`
   Step 0:
   - Detect project repo root (nearest `.git/`)
   - Check/create `docs/actives/`
   - Verify gitignore for `docs/actives/`
   - Get current branch: `git branch --show-current`
   - List existing task folders in `docs/actives/`
   - Match on branch name (normalize, strip `feat/`/`fix/`/`refactor/` prefix)
   - If match → use it; if not → ask user (create or select)
3. **Get changed files**: `gh pr diff {PR} --name-only`
4. **Get full diff**: `gh pr diff {PR}`
5. **Large PR check**: If >30 changed files, warn user:
   > "This PR touches {N} files. Run full review or focus on specific paths?" If
   > user chooses to focus, filter `file_list` and `diff` to selected paths.
6. **Small PR check**: If <3 changed files, suggest single-session mode:
   > "Small PR ({N} files). Run single-session review instead of spawning
   > agents?" If user agrees, skip agent spawning and run the sequential
   > fallback prompt from `agent-prompts.md`.
7. **Detect domain context**: If any changed files match `src/blocks/`,
   `src/queue/` (block events), or `src/sync/` (block sync), read `BLOCKS.md`
   from `.claude/prompts/`. Include as `{project_context}`.
8. **Store variables**: `{pr_number}`, `{branch}`, `{file_list}`, `{diff}`,
   `{task_folder}`, `{project_context}`

### Phase 1: Agent Dispatch

**Read [agent-prompts.md](./references/agent-prompts.md) for spawn templates.**
**Read [categories.md](./references/categories.md) for agent-specific
checklists.** **Read [output-format.md](./references/output-format.md) for
finding format.**

1. **Build agent prompts**: For each agent to spawn:
   - Extract the agent-specific category checklist from `categories.md`
   - Fill placeholders in the agent prompt template from `agent-prompts.md`
   - Include the output format contract from `output-format.md`
   - Include `{project_context}` (CLAUDE.md rules, BLOCKS.md if relevant)
2. **Spawn agents**: Use the Agent tool to spawn all agents in a single message
   (parallel dispatch):

   ```text
   Agent(
     name: "Safety Agent",
     subagent_type: "Explore",
     prompt: {filled_safety_prompt}
   )
   Agent(
     name: "Structure Agent",
     subagent_type: "Explore",
     prompt: {filled_structure_prompt}
   )
   Agent(
     name: "Runtime Agent",
     subagent_type: "Explore",
     prompt: {filled_runtime_prompt}
   )
   ```

   If `--safety` / `--structure` / `--runtime` flag was passed, spawn only the
   corresponding agent.

3. **Fallback**: If agent spawning fails (error, no tmux, plan mode
   restriction):
   - Notify user: "Agent spawning unavailable. Running sequential review."
   - Use the sequential fallback prompt from `agent-prompts.md`
   - Run all 7 categories in the lead session sequentially

### Phase 2: Collect & Merge

1. **Wait for all agents** to complete and return findings
2. **Parse findings**: Extract all `F-{agent}-{N}` blocks from each agent's
   output using the structured format from `output-format.md`
3. **Cross-agent dedup**: Check for overlapping findings across agents:
   - Same file + overlapping line range (±5 lines) → keep higher severity
   - Same file + similar claim (normalized text) → keep higher severity
   - Conflicting recommendations → keep both, flag for user decision
4. **Build unified Finding Registry**: Sort by severity (CRITICAL → INFO), then
   by file path
5. **If any agent failed**: Log the failure, mark those categories as
   "INCOMPLETE — agent failed", proceed with other agents' findings

### Phase 3: Triage with User

Present findings grouped by severity. User decides action for each.

#### CRITICAL / HIGH Findings

Present each finding individually with full detail:

```text
F-S-1 [CRITICAL] Security Review — Missing @UseGuards on POST endpoint
  File: src/auth/auth.controller.ts:42-45
  What: POST /auth/reset endpoint has no authentication guard
  Why:  Unauthenticated users can trigger password resets for any account
  Suggestion: Add @UseGuards(JwtAuthGuard) decorator
  Confidence: High

  Action? [FIX / SKIP / DEFER]
```

- **FIX** → Queue for Phase 5 fix application
- **SKIP** → Record as SKIPPED with reason
- **DEFER** → Record as DEFERRED (stays open for next review)

#### MEDIUM Findings

Batch presentation. Show all MEDIUM findings as a numbered list:

```text
MEDIUM findings (3):
  1. F-T-2: Long method in BlocksService.syncEvents (42 lines)
  2. F-R-3: Missing pagination on getBlocksByUser query
  3. F-T-4: Magic number 86400 should be named constant

  Review individually? [YES / SKIP ALL]
```

If YES → present each individually (same FIX/SKIP/DEFER flow). If SKIP ALL →
mark all as SKIPPED.

**NEEDS CLARIFICATION tag**: If a MEDIUM finding's ambiguity stems from unclear
intent (not implementation quality), tag it as "NEEDS CLARIFICATION" in the
proactive-review.md output with a recommendation: "Consider running
`/clarify vague` on the original requirement before deciding FIX/SKIP/DEFER."

#### LOW / INFO Findings

Summary only:

```text
LOW/INFO findings (5):
  - F-T-5: Consider renaming `tmp` variable (LOW)
  - F-R-4: Test uses hardcoded date string (LOW)
  - F-S-2: Consider adding rate limiting to public endpoint (INFO)
  - F-T-6: Unused import detected (LOW)
  - F-R-5: Test factory available but not used (INFO)

  Expand any? [numbers / SKIP ALL]
```

### Phase 4: Persist & Report

**Read [output-format.md](./references/output-format.md) for proactive-review.md
template.**

1. **Create `proactive-review.md`** in `{task_folder}` using the document
   template from `output-format.md`:
   - Header with PR number, branch, date, file count
   - Finding Registry table (all findings with decisions)
   - Findings by Agent (full detail for each finding)
   - Triage Decisions table
   - Fix Log (populated in Phase 5)
2. **Present final summary**:

   ```text
   Proactive Review Summary — PR #{pr_number}
     Total findings:  {N}
     CRITICAL:        {N} ({N} FIX, {N} SKIP, {N} DEFER)
     HIGH:            {N} ({N} FIX, {N} SKIP, {N} DEFER)
     MEDIUM:          {N} ({N} FIX, {N} SKIP, {N} DEFER)
     LOW:             {N}
     INFO:            {N}
     Cross-agent dups removed: {N}
     Saved to: {task_folder}/proactive-review.md
   ```

3. **Ask**: "Apply fixes now? (FIX items: {N})"

### Phase 5: Apply Fixes (Optional)

If user chose FIX on any findings:

1. **Group fixes by file** for efficiency (multiple findings on same file →
   single edit session)
2. **Apply each fix** in the lead session:
   - Read the affected file
   - Make minimal, targeted fix (no scope creep)
   - If the fix changes a source file → update its corresponding test
     file, following the project's test-location and test-file-naming
     convention (same rule as `validate-pr-reviews` Phase 5). Example
     mapping (substitute your project's own convention):

     ```text
     src/foo/foo.service.ts → src/foo/foo.service.{test-suffix}
     ```

3. **Run affected tests**: `npx jest {test_file} --no-coverage` for each changed
   test file
4. **Atomic commit**: Group related fixes, commit with message:

   ```text
   fix(#{issue}): address proactive review findings F-S-1, F-T-2
   ```

5. **Update proactive-review.md**: Fill in the Fix Log table with commit hashes
   and changed files
6. **Update Finding Registry**: Change Decision from FIX to FIXED for completed
   items

---

## Edge Cases

| Scenario                   | Handling                                                |
| -------------------------- | ------------------------------------------------------- |
| Large PR (>30 files)       | Warn user, offer path-focused review                    |
| Small PR (<3 files)        | Suggest single-session mode (skip agent spawning)       |
| Empty category             | Agent states "No issues found" — logged as clean signal |
| Agent failure/timeout      | Log failure, proceed with other agents, mark categories |
| No tmux                    | Fall back to sequential single-session mode             |
| Cross-agent duplicate      | Same file + overlapping lines → keep higher severity    |
| Conflicting findings       | Both preserved, user decides                            |
| No PR open                 | Error: "No open PR found. Push and create PR first."    |
| proactive-review.md exists | Warn: "Previous review exists. Overwrite or create v2?" |

## PR Lifecycle Integration

See `.claude/rules/pr-review-lifecycle.md` for the full pipeline diagram,
severity ↔ classification mapping, and shared artifact table.

**This skill's position:** After `/pr-creator`, before requesting AI reviews.
`/validate-pr-reviews` Phase 1.5 reads `proactive-review.md` for cross-dedup.

## Quick Reference

```text
TRIGGER:     "review pr" | "proactive review" | "/review-pr"
FOLDER:      {project_repo}/docs/actives/{task_name}/
OUTPUT:      proactive-review.md
AGENTS:      Safety (F-S), Structure (F-T), Runtime (F-R)

CATEGORY SELECTION:
  /review-pr              → all 3 agents (default)
  /review-pr --safety     → Safety Agent only
  /review-pr --structure  → Structure Agent only
  /review-pr --runtime    → Runtime Agent only

PHASES:
  0. Context     — PR number, branch, diff, task folder
  1. Dispatch    — Spawn 3 agents (or sequential fallback)
  2. Merge       — Collect, dedup, build registry
  3. Triage      — User decides FIX/SKIP/DEFER per severity
  4. Persist     — Create proactive-review.md, summary
  5. Fix         — Apply fixes, update tests, commit

SEVERITY → ACTION:
  CRITICAL → Must fix    (maps to VALID BUG)
  HIGH     → Should fix  (maps to VALID IMPROVEMENT)
  MEDIUM   → User decides (maps to CONTROVERSIAL)
  LOW      → User decides (maps to GOOD-TO-HAVE)
  INFO     → Logged only

FALLBACK:    Sequential single-session if agents unavailable
DEDUP:       Cross-agent (same file ±5 lines → keep higher severity)
INTEGRATION: validate-pr-reviews Phase 1.5 reads proactive-review.md
```
