---
name: issue-creator
description: >-
  Create GitHub issues with conventional commit title format, bilingual body
  (English + Korean), proper labels, assignee, and project integration. Enforces
  Issue Type selection, required labels, and project assignment. Use when user
  says "create issue", "new issue", "open issue", "file issue", "report bug",
  "request feature", or "track task".
metadata:
  version: "1.2.0"
---

# Issue Creator Skill

## Purpose

Standardize GitHub issue creation with:

- Conventional commit title format (required scope)
- **Bilingual issue body** (English + Korean 요약)
- GitHub Issue Type (Bug/Feature/Task)
- Automatic label selection based on domain + priority
- Auto-assignment to `@{github_user}` (configured per project; see the skill's
  Reference Files section for how to set this)
- Project selection prompt before creation

## Reference Files

Load these during execution when the relevant step requires detailed reference:

| File                                                          | Use During | Contains                                                          |
| ------------------------------------------------------------- | ---------- | ----------------------------------------------------------------- |
| [labels-types-scopes.md](./references/labels-types-scopes.md) | Steps 1-6  | Type tables, scope table, GraphQL for issue types, label strategy |
| [korean-guide.md](./references/korean-guide.md)               | Step 5     | 합니다체 verb table, technical terms, transformation examples     |

## CRITICAL: Execution Checklist (MANDATORY)

Before completing issue creation, verify ALL items:

- [ ] Korean 요약 created (합니다체 formal tone)
- [ ] Labels added (minimum: domain label + priority)
- [ ] Issue Type set (Bug/Feature/Task)
- [ ] Project question ASKED (even if answer is "None")

**DO NOT mark complete until checklist satisfied.**

## Pre-Check: Ambiguous Issue Description

If the issue description is too ambiguous to generate specific acceptance
criteria (cannot distinguish scope, behavior, or success conditions), invoke
`/clarify` (mode: vague, context: issue description, scope_limit: 4) first. Use
the clarified Goal, Scope, Constraints, and Success Criteria to populate the
issue body.

## Step 0: Detect GitHub Configuration

```bash
# From git remote (preferred)
git remote get-url origin | sed -E 's/.*github.com[:/]([^/]+)\/([^.]+).*/\1\/\2/'
```

Optional PROJECT-CONFIG.md values: `github.org`, `github.repo`,
`github.project_id`, `github.project_name`, `github.project_number`.

## Trigger Phrases

- "create issue" / "new issue" / "open issue" / "file issue"
- "track this as issue"
- "make an issue for this"

## Title Convention (REQUIRED)

```text
type(scope): short description
```

**Read [labels-types-scopes.md](./references/labels-types-scopes.md) for type
table, scope table, and examples.**

- Description should be lowercase (except proper nouns)
- No period at the end
- Keep under 72 characters

**Examples:**

```text
feat(subscription): add yearly subscription support
fix(recurrence): relatedBlocks query includes deleted blocks
security(auth): hardcoded redirect URLs in auth-legacy
```

## Workflow

### Step 1: Gather Information

If not provided, ask:

1. What type of issue? (feat/fix/perf/security/etc.)
2. What scope/area? (sync/queue/auth/etc.)
3. Brief description

### Step 2: Determine Priority

From context clues:

- **priority:high**: "urgent", "production", "blocking", "ASAP", security
- **priority:medium**: Default for most features and bugs
- **priority:low**: "eventually", "nice to have", "when possible", "minor"

If unclear, ask the user.

### Step 3: Compose Title

Format: `type(scope): description`

### Step 4: Ask About Project

ALWAYS ask before creating:

```text
Which project should this issue be added to?
1. {project_name from config} (default)
2. None
```

### Step 5: Create Issue

**Read [korean-guide.md](./references/korean-guide.md) for Korean translation
rules and verb patterns.**

```bash
gh issue create \
  --title "type(scope): description" \
  --body "$(cat <<'EOF'
## Description

{Clear description of the issue}

## Context

{Why this is needed, background information}

## Acceptance Criteria

- [ ] {Criterion 1}
- [ ] {Criterion 2}

## Related

- Related to #{issue_number} (if applicable)

---

## 요약 (Korean)

### 설명

{Description을 합니다체로 번역}

### 맥락

{Context를 합니다체로 번역}
EOF
)" \
  --assignee "{github_user}" \
  --label "domain-label,priority:level"
```

### Step 6: Set Issue Type

**Read [labels-types-scopes.md](./references/labels-types-scopes.md) for GraphQL
commands to fetch type IDs and set issue type.**

### Step 7: Add to Project (if selected)

```bash
gh issue edit {number} --add-project "{project_name}"
```

## Output

```text
Issue created successfully!
URL: {issue_url}
Title: {title}
Type: {Bug|Feature|Task}
Labels: {labels}
Assignee: @{github_user}
Project: {project_name or "None"}
```

## Quick Reference

```text
TITLE:    type(scope): description
KOREAN:   요약 section with 합니다체 endings (MANDATORY)
TYPE:     Bug | Feature | Task (GitHub Issue Type, NOT a label)
LABELS:   [domain-label] + [priority:level]
ASSIGNEE: Always @{github_user}
PROJECT:  Always ask user
```
