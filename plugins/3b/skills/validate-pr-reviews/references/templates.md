# Round File Templates

Templates for creating and managing local round files during Phase 1 (Fetch &
Persist) and Phase 7 (Update Tracking & Report).

## Round File Template

Save to: `{task_folder}/round-{N}-review.md`

Where `{task_folder}` is `{project_repo}/docs/actives/{task_name}/`, resolved by
the folder resolution algorithm in SKILL.md Step 0.

```markdown
# PR Review — Round {N}

- **PR**: #{pr_number}
- **Branch**: {branch_name}
- **Date**: {YYYY-MM-DD}
- **Task**: {task_folder_name}
- **Previous Rounds**: {N-1}
- **Status**: In Progress

---

## Comment Registry

| ID     | Agent | File:Line | Claim Summary | Classification | Dup Of |
| ------ | ----- | --------- | ------------- | -------------- | ------ |
| R{N}-1 |       |           |               |                | —      |

---

## Duplicates from Previous Rounds

Items below were seen in earlier rounds and auto-resolved:

| ID     | Original        | Resolution                        | GitHub Thread    |
| ------ | --------------- | --------------------------------- | ---------------- |
| R{N}-X | R{M}-Y: {claim} | Already reinforced at {file:line} | Replied+Resolved |

_(If no duplicates, write: "No duplicates detected.")_

---

## New Items

### Item R{N}-1 [Agent: {name}]

**File**: `{path}:{line}` **Body**:

> {quoted review text}

**Classification**: {VALID BUG | VALID IMPROVEMENT | GOOD-TO-HAVE |
CONTROVERSIAL | INVALID} **Decision**: {description} **Action**: {what was done}

---

## Why Analysis (INVALID items)

### R{N}-X: {claim summary}

| Field            | Content                            |
| ---------------- | ---------------------------------- |
| What (comment)   | {exact flagged text}               |
| What (issue)     | {what reviewer thought was wrong}  |
| What (reality)   | {what code actually does}          |
| Why (pattern)    | {pattern name or NEW: description} |
| Why (root cause) | {why reviewer couldn't see truth}  |
| How (prevention) | {reinforcing comment at file:line} |
| Who (agent)      | {Claude/Copilot/Codex}             |
| Where            | {file:line}                        |
| When             | Round {N}, {date}                  |

---

## Discussion Log (CONTROVERSIAL items)

### R{N}-X: {claim summary}

| Field              | Content                                                |
| ------------------ | ------------------------------------------------------ |
| Reviewer's Claim   | {what the reviewer suggested}                          |
| For                | {why this suggestion could be correct}                 |
| Against            | {why it might not apply here}                          |
| Context Dependency | {under what conditions is it right vs wrong}           |
| Confidence         | {High / Medium / Low}                                  |
| User Decision      | {→ VALID IMPROVEMENT / → INVALID / Fix / Skip / Defer} |
| Action Taken       | {what was done after discussion}                       |

---

## Fixes Applied

### R{N}-X: {description}

- **File**: {path}
- **Change**: {what changed}
- **Test updated**: {test file} — {what was added}
- **Commit message**: `{type}(#{issue}): {descriptive summary}`

_Internal IDs (R{N}-{X}, CR-{X}, F-{cat}-{X}) are session-internal only — they
belong in round files, NOT in commit messages._

---

## Reinforcing Comment Verification

| ID     | Classification | Comment Added | File:Line | GitHub Reply | Status |
| ------ | -------------- | ------------- | --------- | ------------ | ------ |
| R{N}-1 |                |               |           |              |        |

- INVALID items: {count}
- Comments added: {count}
- CONTROVERSIAL resolved: {count} (→VALID: {N}, →INVALID: {N}, →Fix: {N}, →Skip:
  {N}, →Defer: {N})
- GOOD-TO-HAVE decided: {count} (Fix: {N}, Skip: {N}, Defer: {N})
- GitHub replies: {count} (per-thread only)
- Threads resolved: {count}
- Duplicates resolved: {count}
- User skips: {count}
- Comments minimized: {count} (bot reviews: {N}, triggers: {N})
- **Status**: PASS / FAIL

---

## Status: {In Progress | Completed}
```

### Key Template Conventions

**Comment Registry** is the machine-readable index at the top of each round
file. It enables cross-round dedup in Phase 1.5:

- **ID format**: `R{round}-{item}` (e.g., `R3-1` = Round 3, Item 1)
- **Claim Summary**: Normalized 10-word-max summary of the reviewer's claim
- **Dup Of**: Reference to previous round item (e.g., `R2-4`), or `—` if new

**Duplicates section** separates auto-resolved repeats from new items. This
keeps the "New Items" section focused on fresh reviews only.

**No GitHub summary comment**: Round files replace what was previously posted as
round summary comments on the PR. All tracking stays local.

## Pattern Aggregation Tracking Format

Location: `knowledge/ai-ml/ai-code-review-confusion-patterns.md` (in 3B repo)

Update after validation sessions with 2+ INVALID reviews.

```markdown
## AI Code Review Confusion Patterns

Last Updated: YYYY-MM-DD

### Pattern Frequency

| Pattern               | Count | Last Seen  | Common Triggers            |
| --------------------- | ----- | ---------- | -------------------------- |
| Stale Diff            | 5     | 2026-01-26 | Long-running PRs, rebases  |
| Cross-File Blindness  | 8     | 2026-01-26 | Multi-service changes      |
| Variable Reassignment | 3     | 2026-01-25 | Destructuring + reassign   |
| Cascade Ignorance     | 2     | 2026-01-24 | TypeORM cascade operations |
| Feature Exists        | 6     | 2026-01-26 | Large files (500+ lines)   |
| Intentional Design    | 4     | 2026-01-26 | Trade-off decisions        |
| Webhook Flow          | 2     | 2026-01-23 | External service handlers  |
| YAGNI Suggestion      | 7     | 2026-01-26 | Low-traffic paths          |

### Insights

- **High frequency patterns** → Need better code documentation
- **Reviewer-specific patterns** → Claude vs Copilot tendencies
- **File structure patterns** → Certain architectures confuse reviewers
```

### When to Update

- After each validation session with 2+ INVALID reviews
- When discovering a NEW pattern not in the 8 known
- Weekly aggregation of all validation files

### Benefits

1. Identify systemic documentation gaps
2. Track which code structures confuse AI reviewers
3. Compare Claude vs Copilot confusion patterns
4. Inform code style guide updates
