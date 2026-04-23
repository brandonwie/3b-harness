# Change Discipline Rules

Rules that prevent common friction points observed across 360+ sessions.

## Scope Discipline (before starting changes)

Before modifying any files, state:

1. Files that WILL be modified
2. Files that are OFF-LIMITS
3. The specific goal of this change

## Commit Scope (atomic commits)

Only commit files directly related to the current task. Never include unrelated
changes in a commit. Follow the atomic commit and Conventional Commits rules
defined in global `~/.claude/CLAUDE.md` (Git Commit Discipline). Use the
`/commit` command for guided atomic commits with pre-flight checks.

## Root Cause Verification (before implementing fixes)

Before implementing a fix, restate:

1. The problem (what is wrong)
2. The root cause (why it is wrong)
3. The fix (what will change)
4. Affected files (what will be touched)

## Hypothesis-Driven Claims

Before asserting a root cause, diagnosis, or recommendation, apply the
Scientific Thinking pre-claim checklist from global `~/.claude/CLAUDE.md`
(Principle #9). State your hypothesis, list assumptions, and rate confidence.

## Restart-if-Lost

If context is lost or approach is unclear, restart the task from scratch rather
than continuing blindly.

## Prototype-First

For non-trivial tasks, explore multiple approaches with quick prototypes before
committing to one.

## Tool Substitution Ban (infrastructure)

When Terraform manages a resource, NEVER use AWS CLI, GCP CLI, or any direct
cloud provider CLI to modify that resource as a workaround. If `terraform plan`
shows unexpected results (e.g., "No changes" when changes are expected),
investigate WHY rather than bypassing Terraform. The only exception: the user
explicitly instructs you to use the CLI.

This rule exists because on 2026-03-20, Claude used
`aws ec2 revoke-security-group-egress` directly when `terraform plan` showed "No
changes" (inline block authoritativeness trap). The effect was bypassing
Terraform's `ask` permission gate — a destructive infrastructure change ran
without user confirmation.

## Dead-End Abandonment

If an approach is not working after reasonable effort, abandon it and try a
different approach rather than forcing it.

## Friction Lifecycle

Friction-log observations in `.claude/friction-log.json` move through a
three-stage lifecycle. Each stage has explicit criteria for promotion.

### Stage transitions

```text
observation (single incident)
    ↓ after 3+ occurrences across ≥2 sessions
accumulating (pattern detected, watching)
    ↓ after a clear fix is proposed and validated
ready (proposal drafted, awaiting application)
    ↓ after the fix is applied and verified
resolved (archived to friction-log-archive.json)
```

### Promotion rules

- **observation → accumulating:** An observation becomes an accumulating pattern
  when the same friction surfaces in at least **3 sessions across at least 2
  distinct days**. Count is tracked by the `correction-detector-hook` and
  friction-log entries with matching `category` + similar `target`.
- **accumulating → ready:** Moves to `ready` when:
  1. A clear proposal exists (concrete config change, rule file, hook script)
  2. The proposal has been tested in at least one new session (fix works)
  3. The blast radius is understood (which files change, what breaks)
  4. Rollback plan exists
- **ready → resolved:** Moves to `resolved` after the proposal is merged and:
  1. No new observations matching the same pattern for ≥14 days
  2. Or the fix is a structural change that mechanically prevents the friction
     (e.g., a hook that blocks the trap)
  3. Entry is moved from `friction-log.json` to `friction-log-archive.json`
- **severity override:** Observations with severity `blocker` or `critical` skip
  the accumulating stage and go directly to `ready` — a single critical incident
  is enough to warrant a fix.

### Deprecation

A resolved pattern can be **deprecated** (removed from archive) when:

- 90 days have passed with no reoccurrence
- The underlying system has changed such that the pattern is structurally
  impossible (e.g., the file being protected was deleted)
- A newer, broader rule supersedes the specific pattern

Deprecate by annotating the archive entry with `deprecated: true` and a one-line
reason. Don't delete — archive entries are historical records.

### Who applies fixes

- **Claude applies fixes during `/wrap`** when a `ready` pattern is detected and
  the user confirms
- **Manual application** for structural changes that need user approval (new
  hooks, permission model changes, skill rename)
- **Never auto-apply** without user confirmation — friction fixes touch
  settings.json and rules files, both of which are user-visible configuration

### Integration with this rules file

Patterns that reach `ready` and apply broadly enough may graduate to a rule in
this file (Change Discipline Rules). When that happens:

1. Write the rule here with a clear trigger and action
2. Note the rule in the friction-log entry's resolution
3. Move the friction entry to resolved/archived
4. The rule becomes the enforcement mechanism; the friction entry stays as
   historical context
