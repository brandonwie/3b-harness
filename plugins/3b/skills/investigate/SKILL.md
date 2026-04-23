---
name: investigate
description: >-
  Investigate a bug, issue, or question by running parallel searches across
  codebase, git history, docs, and external sources. Produces a consolidated
  analysis with root cause hypothesis and recommended fix. Use when user says
  "investigate", "dig into", "root cause", "why is this happening", "trace this
  bug", or "figure out why".
allowed-tools:
  [Read, Glob, Grep, Bash, Task, WebSearch, WebFetch, AskUserQuestion]
metadata:
  version: "1.0.0"
---

# /investigate

Deep investigation skill for bugs, unexpected behavior, and technical questions.
Runs parallel searches and produces a consolidated analysis.

## Purpose

Replace ad-hoc debugging with a structured investigation that:

- Searches code, git history, docs, and external sources in parallel
- Builds a timeline of when the issue was introduced
- Identifies root cause with evidence
- Proposes fixes ranked by confidence

## Trigger Phrases

- "investigate {issue}" / "/investigate"
- "dig into this" / "trace this bug"
- "root cause analysis" / "why is this happening"
- "figure out why {symptom}"

## Step 0: Capture the Problem Statement

If not provided, ask user for:

1. **What** is happening (symptom)
2. **When** it started (if known)
3. **Where** it occurs (file, endpoint, environment)
4. **Expected** behavior vs actual behavior

Format as investigation brief:

```text
SYMPTOM:  {what is happening}
EXPECTED: {what should happen}
LOCATION: {file/endpoint/area}
SINCE:    {when it started, or "unknown"}
```

## Step 1: Parallel Search Phase

Launch these searches simultaneously using Task tool agents:

### 1a: Code Search

- Grep for error messages, function names, variable names
- Find all callers/callees of suspect functions
- Check for recent changes in suspect files

### 1b: Git History Search

```bash
# Find when suspect files were last changed
git log --oneline -10 -- {suspect_files}

# Search commit messages for related keywords
git log --oneline --grep="{keyword}" -20

# Find who changed the suspect code
git log --format="%h %an %s" -- {suspect_files}
```

### 1c: Documentation Search

- Check project CLAUDE.md for relevant rules or patterns
- Search 3B knowledge base for prior incidents
- Check ADRs for intentional design decisions

### 1d: External Search (if needed)

- Search for error messages or library issues
- Check GitHub issues on relevant dependencies
- Look for known bugs in framework versions

## Step 2: Correlate Findings

Merge results from all parallel searches. Build a timeline:

```text
TIMELINE:
  {date} - {commit/event} - {what changed}
  {date} - {commit/event} - {what changed}
  ...
  {date} - SYMPTOM FIRST REPORTED
```

Identify the **most likely introduction point** (the commit or change that
correlates with when the symptom started).

## Step 3: Form Hypothesis

> Implements Principle #9: Scientific Thinking (`~/.claude/CLAUDE.md`).

State the root cause hypothesis using this format:

```text
ROOT CAUSE HYPOTHESIS:
  What:  {the specific code/config that is wrong}
  Why:   {why it causes the symptom}
  When:  {when it was introduced}
  Proof: {evidence supporting this hypothesis}

CONFIDENCE: High / Medium / Low
```

If multiple hypotheses exist, rank them by evidence strength.

### Requirement Ambiguity Branch

If the root cause hypothesis is "requirement ambiguity" — the code is working as
implemented but the specification is ambiguous or wrong (confidence: High) —
present this as the finding. Recommend the user run `/clarify vague` to resolve
the requirement uncertainty before implementing a fix. Do NOT propose code
changes for requirements problems.

## Step 4: Propose Fix

For each hypothesis, propose a fix:

| Hypothesis    | Fix              | Risk         | Effort          |
| ------------- | ---------------- | ------------ | --------------- |
| {description} | {what to change} | Low/Med/High | Small/Med/Large |

## Step 5: Present to User

Show the full investigation report:

1. Problem statement (from Step 0)
2. Timeline (from Step 2)
3. Root cause hypothesis (from Step 3)
4. Proposed fixes (from Step 4)
5. Ask: Implement fix / Investigate further / Save report

## Output

```text
Investigation complete: {brief title}

Hypothesis: {one-line root cause}
Confidence: {High/Medium/Low}
Evidence:   {N} code refs, {N} commits, {N} docs
Fix:        {recommended action}
```

## Known Failure Modes

| Symptom                                       | Cause                             | Fix                                                            |
| --------------------------------------------- | --------------------------------- | -------------------------------------------------------------- |
| Hypothesis formed before evidence gathered    | Anchoring bias on first clue      | Complete all 4 parallel searches before forming hypothesis     |
| Root cause is a symptom, not the actual cause | Stopped investigation too shallow | Ask "but why?" until reaching the actual root cause            |
| Fix proposal breaks other functionality       | Didn't check callers/dependents   | Always search for callers of the function being modified       |
| Missed intentional design decision            | Didn't check ADRs or git history  | Always search `projects/moba/decisions/` and git log           |
| Investigation report too long to act on       | Included every detail found       | Focus report on top hypothesis + evidence; details in appendix |
| Wrong confidence rating                       | Didn't apply Scientific Thinking  | Use pre-claim checklist: hypothesis, assumptions, bias check   |

## Quick Reference

```text
TRIGGER:   "investigate" | "dig into" | "root cause"
INPUT:     Symptom + location (ask if not given)
PARALLEL:  Code search + git history + docs + external
OUTPUT:    Timeline + hypothesis + fix proposal
AGENTS:    Uses Task tool for parallel search
```
