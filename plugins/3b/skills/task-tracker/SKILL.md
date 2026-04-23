---
name: task-tracker
description: >-
  Track repeating task patterns after completing non-trivial work. Normalizes
  tasks to kebab-case labels in `~/.claude/task-tracker.json`, bumps counts, and
  suggests skill/hook/command automation when thresholds are met. Trigger after
  finishing any multi-step task that could be templated, or when the user says
  "track this pattern", "tracker check", or "suggest automation". Also invoked
  automatically by `/wrap` Step 4.7.
---

# Task Tracker Skill

## Purpose

After completing any non-trivial task, check if it should be tracked as a
repeating pattern. This helps identify workflows worth automating into skills,
hooks, or commands.

## When to Track

Track a task when ALL of these are true:

- Task required multiple steps or meaningful effort
- Task is NOT already a skill, hook, or command
- Task could reasonably be automated or templated

Do NOT track: one-off questions, trivial fixes, unique debugging.

## How to Track

1. Read `~/.claude/task-tracker.json`
2. Normalize the task to a short kebab-case label (e.g., `fix-linting-errors`,
   `address-pr-reviews`)
3. If label exists: increment `count`, update `lastSeen`, append to `examples`
   (keep max 3, drop oldest)
4. If new: create entry with `count: 1`, set `suggestedType`
5. Write updated JSON back

Label normalization: group similar tasks under one label. "Fix lint" and "run
linter and fix" = `fix-linting-errors`.

## Automation Type Heuristic

| Pattern                      | Type      | Why               |
| ---------------------------- | --------- | ----------------- |
| Multi-step with user input   | `skill`   | Needs interaction |
| Should trigger automatically | `hook`    | Event-driven      |
| Simple manual invocation     | `command` | One-shot          |
| File generation/templating   | `skill`   | Complex output    |
| Validation/checking          | `hook`    | Pre/post tool     |

## When to Suggest (threshold: 2)

When `count >= 2` AND `min_sessions >= 2` (unique dates) AND
`dismissed === false`, ask the user:

> Pattern detected: "{label}" done {count} times. Examples: {examples}
> Suggested: create a {suggestedType}. Options: Create now / Change type /
> Dismiss / Later

If user picks "Dismiss", set `dismissed: true`. If user picks "Later", do
nothing (ask again next time). If user picks "Create now", help create the
automation.

## Severity Override

If a task matches a friction-log pattern with severity `blocker` or `critical`,
trigger the suggestion at `count >= 1` (bypasses both threshold and
min_sessions). Critical friction indicates the task caused real damage — even a
single occurrence warrants automation consideration.

## /wrap Integration

Task pattern detection runs during `/wrap` Step 4.7 (after friction analysis).
This provides a consistent execution point rather than relying on Claude
remembering to check after every task. Manual tracking between /wrap sessions is
still encouraged for capture accuracy.

## History

Migrated from global `~/.claude/CLAUDE.md` to skill on 2026-04-18 as part of
token usage reduction (issue #13). Skill loads only when invoked — no session
baseline cost.
