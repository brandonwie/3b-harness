# Output Format — Proactive Review Findings

This file defines the **contract** between review agents and the lead session.
All agents MUST return findings in this exact format. The lead session parses
this structure to merge, dedup, and triage findings.

## Finding Format

Each finding is one markdown block:

```markdown
#### F-{agent}-{N}: {title}

| Field      | Value                                 |
| ---------- | ------------------------------------- |
| Category   | {category name}                       |
| Severity   | CRITICAL / HIGH / MEDIUM / LOW / INFO |
| File       | {path}:{line_start}-{line_end}        |
| Confidence | High / Medium / Low                   |
| What       | {what code does or fails to do}       |
| Why        | {why this is a problem}               |
| Suggestion | {specific fix recommendation}         |
| Evidence   | {code snippet or cross-reference}     |
```

## Finding ID Convention

| Agent     | Prefix | Example |
| --------- | ------ | ------- |
| Safety    | `F-S-` | F-S-1   |
| Structure | `F-T-` | F-T-1   |
| Runtime   | `F-R-` | F-R-1   |

IDs are sequential per agent, starting at 1.

## Severity Definitions

| Severity     | Meaning                               | User Action  | Maps To (validate-pr-reviews) |
| ------------ | ------------------------------------- | ------------ | ----------------------------- |
| **CRITICAL** | Security flaw, data loss, crash risk  | Must fix     | VALID BUG                     |
| **HIGH**     | Significant quality/performance issue | Should fix   | VALID IMPROVEMENT             |
| **MEDIUM**   | Improvement worth considering         | User decides | CONTROVERSIAL                 |
| **LOW**      | Minor style or convention issue       | User decides | GOOD-TO-HAVE                  |
| **INFO**     | Observation, no action needed         | Logged only  | N/A                           |

## Empty Category

When a category has zero findings, the agent MUST explicitly state:

```markdown
### {Category Name}

No issues found.
```

This signals a clean result (not a missed scan).

## Agent Summary Block

Each agent MUST end its output with a summary:

```markdown
## Agent Summary

| Metric             | Value |
| ------------------ | ----- |
| Categories scanned | {N}   |
| Total findings     | {N}   |
| CRITICAL           | {N}   |
| HIGH               | {N}   |
| MEDIUM             | {N}   |
| LOW                | {N}   |
| INFO               | {N}   |
```

## Proactive Review Document

The lead session merges all agent findings into `proactive-review.md`:

```markdown
# Proactive Review — PR #{pr_number}

**Branch:** {branch} **Date:** {date} **Files reviewed:** {count}

## Finding Registry

| ID    | Severity | Category             | File              | Title           | Decision |
| ----- | -------- | -------------------- | ----------------- | --------------- | -------- |
| F-S-1 | CRITICAL | Security Review      | auth.service.ts:5 | Missing guard   | FIX      |
| F-T-1 | HIGH     | Architectural        | blocks.service:42 | Layer violation | FIX      |
| F-R-1 | MEDIUM   | Performance Analysis | sync.service:100  | N+1 query       | SKIP     |

## Findings by Agent

### Safety Agent

{all F-S findings in full format}

### Structure Agent

{all F-T findings in full format}

### Runtime Agent

{all F-R findings in full format}

## Triage Decisions

| ID    | Decision | Reason             |
| ----- | -------- | ------------------ |
| F-S-1 | FIX      | Security risk      |
| F-R-1 | SKIP     | Acceptable for now |
| F-T-2 | DEFER    | Next sprint        |

## Fix Log

| ID    | Commit  | Files Changed     |
| ----- | ------- | ----------------- |
| F-S-1 | abc1234 | auth.service.ts   |
| F-T-1 | def5678 | blocks.service.ts |
```

## Cross-Agent Dedup Rules

When merging findings from multiple agents, duplicates are detected by:

| Match Criteria                         | Resolution                   |
| -------------------------------------- | ---------------------------- |
| Same file + overlapping lines (±5)     | Keep higher severity finding |
| Same file + similar claim (normalized) | Keep higher severity finding |
| Conflicting recommendations            | Keep both, present to user   |

Deduped findings are marked with `Dup Of: {original_id}` in the registry.
