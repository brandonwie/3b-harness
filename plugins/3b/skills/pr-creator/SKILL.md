---
name: pr-creator
description: >-
  Create GitHub pull requests with bilingual notes (English + Korean) and full
  project integration. Confirms target branch, analyzes commits since
  divergence, generates structured PR body, assigns user, adds conventional
  labels, and sets GitHub Project status to "In Review". Use when user says "pr
  to dev", "pr to prod", "create pr", "open pr", "submit for review", or "push
  and pr".
metadata:
  version: "1.3.1"
---

# PR Creator Skill

## Activation Verification

When this skill activates, confirm mentally:

1. User triggered with: "pr to dev", "pr to prod", "create pr", or "open pr"
2. I will follow ALL steps including Korean translation
3. I will ASK about labels and project (not skip)
4. I will complete the execution checklist before finishing

## Purpose

Streamline PR creation with:

- Branch confirmation before proceeding
- Commit analysis for concise PR description
- **Bilingual PR notes** (English + Korean 요약)
- Auto-assignment to `@{github_user}` (configured per project)
- Smart label selection based on domain + priority
- Project selection with automatic "In Review" status
- Automated code review trigger via `@claude review` comment

## Reference Files

Load these during execution when the relevant step requires detailed reference:

| File                                                          | Use During | Contains                                                         |
| ------------------------------------------------------------- | ---------- | ---------------------------------------------------------------- |
| [korean-guide.md](./references/korean-guide.md)               | Step 3     | 합니다체 verb table, technical terms, transformation examples    |
| [labels-and-projects.md](./references/labels-and-projects.md) | Steps 4-5  | Label discovery, type mapping, project selection, error recovery |

## CRITICAL: Execution Checklist (MANDATORY)

Before completing PR creation, verify ALL items:

- [ ] Branch confirmed with user
- [ ] Korean 요약 created (합니다체 formal tone)
- [ ] Labels added (minimum: type label, priority if available)
- [ ] Project question ASKED (even if answer is "None")
- [ ] /review-pr offered (proactive review before AI review)
- [ ] @claude review triggered (or user chose to skip)

**DO NOT mark complete until checklist satisfied.**

## Step 0: Detect GitHub Configuration

```bash
# From git remote (preferred)
git remote get-url origin | sed -E 's/.*github.com[:/]([^/]+)\/([^.]+).*/\1\/\2/'
```

Optional PROJECT-CONFIG.md values: `github.org`, `github.repo`,
`github.project_id`, `github.project_name`, `github.project_number`,
`merge_strategy.develop_to_main`.

If no `merge_strategy` section exists in PROJECT-CONFIG, default to **merge
commit** for all PRs (the standard for most repositories).

## Trigger Phrases

- "pr to dev" → PR to `develop` branch
- "pr to prod" → PR to `main` branch
- "create pr" / "open pr" → Ask for target branch

## Title Convention (REQUIRED)

### Feature/Fix PRs (to `develop`)

```text
type(scope): description
```

Scope is a code area (e.g., `api`, `auth`, `calendar`), NOT an issue number.
Issue linking goes in the PR body via `Closes #N`.

### Release PRs (`develop` → `main`)

**Most projects:** Use standard `type(scope): description` format (same as
feature PRs). The PR will be merged with a **merge commit**.

**For projects with `merge_strategy.develop_to_main: squash`** (e.g.,
backend-v2): The PR title becomes the **squash commit message** on `main`.
semantic-release reads this commit to determine the version bump. Choose the
title type based on the **highest-impact change** in the release:

| Highest Impact Change | Title Type | Version Bump  | Example                                         |
| --------------------- | ---------- | ------------- | ----------------------------------------------- |
| New feature           | `feat`     | Minor (1.x.0) | `feat: calendar sync improvements and i18n`     |
| Bug fix only          | `fix`      | Patch (1.0.x) | `fix: OAuth token reset and contact dedup`      |
| Breaking change       | `feat!`    | Major (x.0.0) | `feat!: v3 API with breaking schema changes`    |
| Maintenance only      | `chore`    | None          | `chore: dependency updates and CI improvements` |

**Release PR title rules (squash projects only):**

- **Summarize the release theme** in the description (not individual issues)
- Keep under 70 characters
- The body carries the detailed changelog (see Step 3)

## Workflow

### Step 1: Confirm Branch

ALWAYS ask user to confirm current branch and target branch before proceeding.

### Step 2: Analyze Commits

```bash
git merge-base HEAD {target_branch}
git log {merge_base}..HEAD --oneline
git log {merge_base}..HEAD --pretty=format:"%s%n%b"
```

**For release PRs** (`develop` → `main`), also run:

```bash
# Count commits and unique issues to confirm release scope
git log {merge_base}..HEAD --oneline | wc -l
git log {merge_base}..HEAD --oneline | grep -oE '#[0-9]+' | sort -u
# Summarize by commit type
git log {merge_base}..HEAD --pretty=format:"%s" --no-merges \
  | sed -E 's/\(.*//' | sort | uniq -c | sort -rn | head -10
```

If commit count is high (100+) or issue count is 5+, switch to the **release PR
body template** in Step 3.

### Step 3: Generate PR Content

**Read [korean-guide.md](./references/korean-guide.md) for Korean translation
rules and verb patterns.**

**Feature/Fix PR body template:**

```markdown
## Summary

- {bullet point 1: what changed}
- {bullet point 2: why it changed}
- {bullet point 3: key implementation detail if relevant}

Closes #{issue_number}

---

## 요약 (Korean)

- {bullet point 1: 무엇이 변경되었는지}
- {bullet point 2: 왜 변경되었는지}
- {bullet point 3: 주요 구현 사항}

---

## Type of Change

- [x] {appropriate type from template}

## Merge Strategy

- **Default**: Use **"Create a merge commit"** for all PRs
- **Exception**: If PROJECT-CONFIG has `develop_to_main: squash`, use **"Squash
  and merge"** for PRs to `main`
```

**Release PR body template** (`develop` → `main`):

The squash commit body becomes the **permanent git history** on `main`. Write a
categorized changelog, not a raw commit dump.

```markdown
## Release Summary

{1-2 sentence overview of this release's theme/scope}

### Features

- {grouped by domain, not by individual commit}

### Fixes

- {critical fixes, grouped by domain}

### Performance

- {perf improvements, if any}

### Infrastructure / CI

- {infra, CI, build changes, if any}

### Related Issues

{comma-separated list: #111, #222, #333 — do NOT use "Closes" since issues were
already closed when merged into develop}

---

## 릴리스 요약 (Korean)

{1-2 sentence overview in Korean}

### 기능

- {features in Korean, 합니다체}

### 수정

- {fixes in Korean, 합니다체}

### 성능

- {perf in Korean, 합니다체, if any}

---

## Merge Strategy

- **Default**: Use **"Create a merge commit"**
- **If PROJECT-CONFIG has `develop_to_main: squash`**: Use **"Squash and
  merge"**
  - The PR title becomes the single commit message on `main`
  - semantic-release reads this commit to determine the version bump
```

### Issue Linking

**Feature/Fix PRs**: ALWAYS include `Closes #{issue_number}` in Summary section.
Extract issue number from branch name, commit messages, or ask user.

**Release PRs**: List related issues without `Closes` — issues were already
closed when merged into `develop`. Use `Related Issues: #111, #222, ...`
instead.

### Step 4: Select Labels (REQUIRED)

**Read [labels-and-projects.md](./references/labels-and-projects.md) for label
discovery, type mapping, and graceful degradation.**

### Step 5: Ask About Project (MANDATORY)

**Read [labels-and-projects.md](./references/labels-and-projects.md) for project
discovery and selection workflow.**

**CRITICAL:** Even if there's an obvious default, ASK the user.

### Step 6: Create PR

```bash
gh pr create \
  --base {target} \
  --title "type(scope): description" \
  --body "$(cat <<'EOF'
{generated body with Korean section}
EOF
)" \
  --assignee "{github_user}" \
  --label "{labels}"
```

### Step 7: Add to Project & Set Status (if selected)

```bash
gh pr edit {number} --add-project "{project_name}"
```

Set project status to "In Review" using GraphQL.

### Step 8: Review & Automated Code Review

Before triggering Claude AI review, ask:

> "Run /review-pr (proactive review) before triggering @claude review?"
>
> Options: **Yes** | **Skip (trigger @claude review now)** | **Neither**

- **Yes** → Inform user to invoke `/review-pr` separately (different skill,
  needs interactive triage). After proactive review is done, user can re-trigger
  this step or manually post `@claude review`.
- **Skip** → Post `@claude review` comment immediately:

  ```bash
  gh pr comment {number} --body "@claude review"
  ```

- **Neither** → Skip both (user will trigger reviews manually later)

**Note:** `/review-pr` is recommended but optional — small/trivial PRs don't
need 3-agent proactive review. See `.claude/rules/pr-review-lifecycle.md` for
the full post-creation workflow.

## Target Branch Rules

| Command      | Target    | Typical Labels                       |
| ------------ | --------- | ------------------------------------ |
| "pr to dev"  | `develop` | domain + priority labels             |
| "pr to prod" | `main`    | `release` + domain + priority labels |

## Quick Reference

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY (Must complete or document failure)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRANCH:   Confirm with user before proceeding
TITLE:    type(scope): description
          scope = code area (api, auth, etc.), NOT issue number
          Issue linking: "Closes #N" in PR body (not title)
KOREAN:   요약 section with 합니다체 endings
PROJECT:  ASK user (even if answer is "None")
REVIEW:   Offer /review-pr first, then trigger @claude review

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEST EFFORT (Apply if available, skip with warning if not)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LABELS:   Type label required, priority if available
STATUS:   Set to "In Review" when adding to project

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALWAYS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ASSIGNEE: @{github_user}
ISSUE:    Feature/Fix PR: "Closes #xxx"
          Release PR: "Related Issues: #x, #y, ..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MERGE STRATEGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Default: merge commit (--merge) for all PRs
Exception: if PROJECT-CONFIG has develop_to_main: squash →
  - PR title → squash commit message (semantic-release)
  - Title type must match highest-impact change in release
```

## Troubleshooting

| Problem                          | Cause                                  | Fix                                                                          |
| -------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------- |
| Empty diff (no commits)          | Branch matches target or not pushed    | Run `git log {target}..HEAD`; push local commits first                       |
| Branch not on remote             | Forgot to push before PR creation      | Run `git push -u origin {branch}` before `gh pr create`                      |
| Korean 요약 missing              | Step 3 skipped or translation failed   | Re-read korean-guide.md; manually add 요약 section via `gh pr edit --body`   |
| Labels not found in repo         | Label doesn't exist on this repository | Run `gh label list` to verify; create missing labels or skip with warning    |
| Project not found                | Wrong project name or no access        | Run `gh project list` to verify; ask user to confirm project name            |
| `gh` CLI not authenticated       | Token expired or not logged in         | Run `gh auth status`; if expired, run `gh auth login`                        |
| Issue number not found           | Branch name doesn't contain issue ref  | Ask user for issue number directly; check recent issues with `gh issue list` |
| Merge conflict with target       | Target branch has diverged             | Ask user to rebase or merge target into feature branch first                 |
| `@claude review` comment ignored | GitHub Action not configured for repo  | Log warning; this is a non-blocking step                                     |
