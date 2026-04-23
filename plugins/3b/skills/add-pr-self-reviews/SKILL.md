---
name: add-pr-self-reviews
description: >-
  Add self-review inline comments to GitHub PR diff pages explaining key
  implementation decisions. Posts comments in Korean (default) or English on
  specific diff lines. Use when user says "add self review", "self review
  comments", "annotate pr", "explain my changes", or "add review notes".
  Typically run after /validate-pr-reviews iterations are complete.
metadata:
  version: "1.1.0"
---

# Add PR Self-Reviews Skill

## Purpose

Add explanatory inline comments to PR diff pages that:

- Prove self-review was conducted
- Help new developers understand implementation patterns
- Explain the "why" behind non-obvious decisions
- Document edge case handling and design trade-offs

## Reference Files

Load these during execution when the relevant phase requires detailed reference:

| File                                                         | Use During | Contains                                                    |
| ------------------------------------------------------------ | ---------- | ----------------------------------------------------------- |
| [comment-templates.md](./references/comment-templates.md)    | Phase 4    | 5 category templates (Korean+English), writing guidelines   |
| [api-format.md](./references/api-format.md)                  | Phase 5    | JSON format guide, error handling, lessons learned          |
| [pr-review-lifecycle.md](../../rules/pr-review-lifecycle.md) | Phase 6    | Pipeline position, task folder convention, shared artifacts |

## Trigger Phrases

- "add pr self reviews" / "/add-pr-self-reviews"
- "add self-review comments"
- "self review the pr"
- "add implementation comments to pr"

## Language Selection

**Default: Korean (합니다체)**

Ask user on first invocation: Korean (Recommended) or English.

## Workflow

### Phase 1: Identify PR and Changed Files

```bash
# Get current PR number
PR_NUMBER=$(gh pr view --json number --jq '.number')

# Get repo info
REPO=$(gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"')

# Get changed files with line counts
gh pr diff $PR_NUMBER --name-only

# Get commit SHA for review API
COMMIT_SHA=$(gh pr view $PR_NUMBER --json headRefOid --jq '.headRefOid')
```

### Phase 2: Analyze Changed Files for Key Points

Read each changed file and identify:

| Category                  | What to Look For                          | Comment Priority |
| ------------------------- | ----------------------------------------- | ---------------- |
| Core Functions            | New utility functions, main logic         | HIGH             |
| Edge Case Handling        | Null checks, error handling, DST handling | HIGH             |
| Design Decisions          | Pattern choices, trade-offs               | MEDIUM           |
| Performance Optimizations | Caching, micro-optimizations              | MEDIUM           |
| Integration Points        | Where code connects to other systems      | LOW              |
| Validation Logic          | Input validation, boundary checks         | MEDIUM           |

**Target: 5-10 comments per PR** (enough to be helpful, not overwhelming)

**Skip test files** (`*.spec.ts`, `*.test.ts`) unless the test contains a
critical insight (e.g., non-obvious mock setup, testing pitfall, or a pattern
that future developers would misunderstand). Focus comments on source files
where the implementation decisions live.

### Phase 3: Determine Comment Locations (CRITICAL)

Comments MUST be placed on the TARGET LINE in the diff.

1. **Read the actual file** using Read tool to get current line numbers
2. **Verify line is in the PR diff** (changed/added lines only, not context)
3. **Use the NEW file line number** (right side of diff, `side: "RIGHT"`)

```bash
# Get the PR diff to see which lines are actually changed
gh pr diff {PR_NUMBER} -- {file_path}

# Lines starting with '+' are added (commentable)
# Lines starting with '-' are removed (not commentable)
# Lines starting with ' ' are context (may not be commentable)
```

### Phase 4: Generate Comment Content

**Read [comment-templates.md](./references/comment-templates.md) for the 5
category templates and writing guidelines.**

### Phase 5: Create PR Review with Inline Comments

**Read [api-format.md](./references/api-format.md) for the correct JSON
submission approach.**

## Output

After creating the review:

```text
Self-review comments added to PR #{number}

Language: Korean / English
Comments: {count} inline comments

Files commented:
  - src/utils/calendar.ts (3 comments)
  - src/services/block.ts (2 comments)

Review URL: {url}
```

## Quick Reference

```text
TRIGGER:     "/add-pr-self-reviews" | "add pr self reviews"
LANGUAGE:    Korean (default, 합니다체) | English
TARGET:      5-10 inline comments per PR

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: LINE NUMBERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Read file to get CURRENT line numbers
  2. Verify line is IN the PR diff (not context)
  3. Use "side": "RIGHT" for new/changed lines

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: JSON FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❌ WRONG: gh api -f "comments[0][path]=..."
  ✅ RIGHT: Write JSON file + gh api --input /path/to/file

SKIP:        Test files (*.spec.ts, *.test.ts) unless critical insight

COMMENT TYPES:
  1. Core Function    - Why function exists, key patterns
  2. Edge Case        - Problem → Solution → Reasoning
  3. Design Decision  - Choice + Alternatives + Why
  4. Performance      - Before → After → Improvement
  5. Integration      - Connection points + Critical info
```

## Phase 6: Task Folder Tracking (Optional)

If a task folder exists at `{project_repo}/docs/actives/{task_name}/` (created
by `/review-pr` or `/validate-pr-reviews`):

1. Save a `self-review-comments.md` summary to the task folder containing:
   - PR number, date, language used
   - List of files commented with comment count per file
   - Review URL
2. If no task folder exists → skip silently (self-reviews work independently)

See `.claude/rules/pr-review-lifecycle.md` for pipeline position and shared
artifacts.

## Example Session

**User says:** "self-review" (after completing /validate-pr-reviews)

**Flow:**

1. Ask language preference → User selects "Korean"
2. Get PR #644, repo info
3. Get changed files
4. Read files, identify 8 key implementation points
5. Generate Korean comments (합니다체)
6. Create PR review with inline comments via API
7. Report success with review URL
