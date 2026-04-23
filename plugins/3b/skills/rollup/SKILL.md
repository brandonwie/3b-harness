---
name: rollup
description: >-
  Aggregate journal entries into higher-level summaries using clean-slate rollup
  strategy. Combines daily entries into weekly, weekly into monthly, monthly
  into quarterly, quarterly into yearly. Cleans ephemeral levels after
  aggregation. Use when user says "rollup", "aggregate journals", "weekly
  summary", "monthly rollup", or "summarize this week/month".
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion]
metadata:
  version: "1.0.0"
---

# /rollup

Aggregate journal entries into higher-level summaries using a clean-slate
strategy.

**Scope:** This skill handles journal aggregation only:

- Creates weekly, monthly, quarterly, or yearly summaries
- Cleans ephemeral files after aggregation
- Preserves daily entries (permanent)

Does NOT: update project docs, extract knowledge, or commit changes.

---

## Integration with /wrap

This skill is **automatically invoked by /wrap** when rollup conditions are met:

**Primary triggers (day-based):**

| Date Condition                      | /wrap Behavior                               |
| ----------------------------------- | -------------------------------------------- |
| Sunday/Monday                       | Prompts for weekly rollup of previous week   |
| 1st-3rd of month                    | Prompts for monthly rollup of previous month |
| Quarter start (Apr/Jul/Oct/Jan 1-3) | Prompts for quarterly rollup                 |
| Jan 1-7                             | Prompts for yearly rollup                    |

**Secondary triggers (missing-rollup detection):**

If the primary day-based trigger does NOT fire, check for missing rollups:

| Check                             | Condition                                                       | /wrap Behavior                               |
| --------------------------------- | --------------------------------------------------------------- | -------------------------------------------- |
| Previous week's rollup missing    | No `YYYY-wWW.md` for last week AND daily files exist for it     | Prompts for weekly rollup of previous week   |
| Previous month's rollup missing   | No `YYYY-MM.md` for last month AND source files exist for it    | Prompts for monthly rollup of previous month |
| Previous quarter's rollup missing | No `YYYY-QN.md` for last quarter AND monthly files exist for it | Prompts for quarterly rollup                 |
| Previous year's rollup missing    | No `YYYY.md` for last year AND quarterly files exist for it     | Prompts for yearly rollup                    |

This ensures rollups are offered even if the user wraps mid-week or mid-month,
as long as a previous period's rollup is missing and source material exists.

When `/wrap` detects a rollup is due (via either trigger), it will ask:

```text
A {level} rollup is due for {period}. Create now?
- Yes, include in this session
- Skip for now (run /rollup later)
```

**Standalone usage:** You can also invoke `/rollup` directly at any time.

---

## Usage

```text
/rollup [level]

Levels:
  weekly    - Aggregate current week's daily entries
  monthly   - Aggregate weekly entries, CLEAN weekly files
  quarterly - Aggregate monthly entries, CLEAN monthly files
  yearly    - Aggregate quarterly entries, CLEAN quarterly files

Auto-detection:
  /rollup (no args) - Detects what's due based on current date
```

---

## Execution Steps

### Step 0: Detect Context

1. Get current **local** date by running `date '+%Y-%m-%d'` in Bash (NOT from
   the system context's `currentDate`, which uses UTC and may show yesterday's
   date for KST users between midnight and 8:59 AM)
2. Determine rollup level from argument or auto-detect
3. Set `3B_PATH` to `${FORGE_3B_ROOT}`
4. Determine target period based on level
5. **Compute target file path** and check if it already exists:
   - weekly: `{3B_PATH}/journals/YYYY/weekly/YYYY-wWW.md`
   - monthly: `{3B_PATH}/journals/YYYY/monthly/YYYY-MM.md`
   - quarterly: `{3B_PATH}/journals/quarterly/YYYY-QN.md`
   - yearly: `{3B_PATH}/journals/yearly/YYYY.md`
6. If target file exists → **inform user and exit** ("Rollup for {period}
   already exists at {path}. No action needed.")
7. If target file does NOT exist → proceed to Step 1

**Auto-detection logic (two-pass):**

**Pass 1 — Primary (day-based):**

| Date Condition             | Suggested Level              |
| -------------------------- | ---------------------------- |
| Sunday or Monday           | weekly (previous week)       |
| 1st of month               | monthly (previous month)     |
| Apr 1, Jul 1, Oct 1, Jan 1 | quarterly (previous quarter) |
| Jan 1-7                    | yearly (previous year)       |

**Pass 2 — Secondary (missing-rollup, runs only if Pass 1 yields nothing):**

| Check                                    | Suggested Level              |
| ---------------------------------------- | ---------------------------- |
| No weekly rollup for previous week       | weekly (previous week)       |
| + daily files exist for that week        |                              |
| No monthly rollup for previous month     | monthly (previous month)     |
| + weekly (or daily) files exist for it   |                              |
| No quarterly rollup for previous quarter | quarterly (previous quarter) |
| + monthly files exist for it             |                              |
| No yearly rollup for previous year       | yearly (previous year)       |
| + quarterly files exist for it           |                              |

Pass 2 checks each level in order (weekly first). It collects ALL missing
rollups and suggests them to the user. This catches rollups missed due to
wrapping on a non-trigger day (e.g., Tuesday after a week with no Sunday/Monday
wrap).

### Step 1: Gather Source Files

Based on level, read source files:

**Weekly:**

- Read daily journals for the target week
- Path: `{3B_PATH}/journals/YYYY/MM/YYYY-MM-DD.md`
- Find all entries where date falls within the target week

**Monthly:**

- Read weekly rollups for the target month
- Path: `{3B_PATH}/journals/YYYY/weekly/YYYY-wWW.md`
- If no weekly files exist, read daily journals directly

**Quarterly:**

- Read monthly rollups for the target quarter
- Path: `{3B_PATH}/journals/YYYY/monthly/YYYY-MM.md`

**Yearly:**

- Read quarterly rollups for the target year
- Path: `{3B_PATH}/journals/quarterly/YYYY-QN.md`

### Step 2: Extract Key Information

For each source file, extract:

| Field           | Description                       |
| --------------- | --------------------------------- |
| Focus areas     | Main topics/projects worked on    |
| Accomplishments | Tasks completed, features shipped |
| Learnings       | Knowledge entries created/updated |
| Challenges      | Problems solved with solutions    |
| Metrics         | Session counts, entries created   |

### Step 3: Generate Summary

Use the appropriate template from `resources/templates/`:

| Level     | Template               |
| --------- | ---------------------- |
| weekly    | `journal-weekly.md`    |
| monthly   | `journal-monthly.md`   |
| quarterly | `journal-quarterly.md` |
| yearly    | `journal-yearly.md`    |

**Content strategy by level:**

| Level     | Include                                                                 | Exclude                              |
| --------- | ----------------------------------------------------------------------- | ------------------------------------ |
| Weekly    | Session summaries (1-2 lines), key learnings, projects, metrics         | Full code blocks, detailed debugging |
| Monthly   | Weekly highlights, major accomplishments, knowledge created, statistics | Daily granular details               |
| Quarterly | Month themes (1 paragraph), major projects, skills developed, goals     | Weekly details                       |
| Yearly    | Quarter themes, flagship projects, growth summary, goals assessment     | Monthly details                      |

### Step 4: Present to User

Show proposed changes using `AskUserQuestion`:

```text
/rollup Analysis

LEVEL: {weekly|monthly|quarterly|yearly}
PERIOD: {description of period}

SOURCE FILES:
- {file1.md}
- {file2.md}

WILL CREATE:
- {target-file.md}

WILL CLEAN (after aggregation):
- {file1.md}
- {file2.md}

Proceed?
```

Options:

- "Create only" - create summary, keep source files
- "Create + Clean" - create summary and delete source files
- "Preview" - show generated content without saving
- "Cancel" - exit without changes

### Step 5: Write Summary

Create the rollup file at the appropriate location:

| Level     | Output Path                                  |
| --------- | -------------------------------------------- |
| weekly    | `{3B_PATH}/journals/YYYY/weekly/YYYY-wWW.md` |
| monthly   | `{3B_PATH}/journals/YYYY/monthly/YYYY-MM.md` |
| quarterly | `{3B_PATH}/journals/quarterly/YYYY-QN.md`    |
| yearly    | `{3B_PATH}/journals/yearly/YYYY.md`          |

### Step 6: Clean Source Files (if selected)

**Clean-slate rules:**

| After Creating | Delete                                               |
| -------------- | ---------------------------------------------------- |
| Monthly        | All `YYYY/weekly/YYYY-wWW.md` files for that month   |
| Quarterly      | All `YYYY/monthly/YYYY-MM.md` files for that quarter |
| Yearly         | All `quarterly/YYYY-QN.md` files for that year       |

**NEVER delete:**

- Daily journal entries (`YYYY/MM/YYYY-MM-DD.md`)
- Yearly summaries (`yearly/YYYY.md`)

### Step 7: Report

Show summary:

```text
/rollup Complete

CREATED:
✓ {output-file-path}

CLEANED:
✓ {deleted-file-1}
✓ {deleted-file-2}

PRESERVED:
• {N} daily entries in YYYY/MM/

Next rollup due:
• {level} on {date}
```

---

## File Naming Conventions

| Level     | Format        | Example       |
| --------- | ------------- | ------------- |
| Weekly    | `YYYY-wWW.md` | `2026-w04.md` |
| Monthly   | `YYYY-MM.md`  | `2026-01.md`  |
| Quarterly | `YYYY-QN.md`  | `2026-Q1.md`  |
| Yearly    | `YYYY.md`     | `2026.md`     |

---

## Week Number Calculation

Use ISO week numbers:

- Week 1 is the first week with at least 4 days in the year
- Weeks start on Monday
- A week belongs to the year in which its Thursday falls

```bash
# Get ISO week number for a date
date -d "2026-01-26" +%G-w%V
# Output: 2026-w05
```

---

## Quarter Mapping

| Quarter | Months                      |
| ------- | --------------------------- |
| Q1      | January, February, March    |
| Q2      | April, May, June            |
| Q3      | July, August, September     |
| Q4      | October, November, December |

---

## Path Reference

| Path                               | Description                   |
| ---------------------------------- | ----------------------------- |
| `${FORGE_3B_ROOT}`                | 3B root                       |
| `{3B}/journals/YYYY/MM/`           | Daily journals (PERMANENT)    |
| `{3B}/journals/YYYY/weekly/`       | Weekly rollups (EPHEMERAL)    |
| `{3B}/journals/YYYY/monthly/`      | Monthly rollups (EPHEMERAL)   |
| `{3B}/journals/quarterly/`         | Quarterly rollups (EPHEMERAL) |
| `{3B}/journals/yearly/`            | Yearly rollups (PERMANENT)    |
| `{3B}/journals/ROLLUP-STRATEGY.md` | Strategy documentation        |

---

## Known Failure Modes

| Symptom                            | Cause                          | Fix                                                  |
| ---------------------------------- | ------------------------------ | ---------------------------------------------------- |
| Wrong week number calculated       | Used non-ISO week calculation  | Use ISO weeks: `date +%G-w%V` (week starts Monday)   |
| Source files not found for rollup  | Wrong path or date range       | Verify paths match `journals/YYYY/MM/` structure     |
| Monthly rollup missing weeks       | No weekly rollups existed      | Fall back to reading daily journals directly         |
| Accidentally deleted daily entries | Included dailies in clean step | Dailies are PERMANENT — never in clean-slate list    |
| Quarter boundary off-by-one        | Wrong month-to-quarter mapping | Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec       |
| Duplicate rollup created           | Rollup file already existed    | Step 0 now checks target path; exits early if exists |
| Rollup prompt on every /wrap       | /wrap Step 8 was date-only     | /wrap Step 8 now checks target file before prompting |
| Wrong date used (off by one day)   | System `currentDate` uses UTC  | Step 0 now uses `date` bash cmd (local time)         |

## Related

- [journals/ROLLUP-STRATEGY.md](../../../journals/ROLLUP-STRATEGY.md)
- [resources/templates/journal-weekly.md](../../../resources/templates/journal-weekly.md)
- [resources/templates/journal-monthly.md](../../../resources/templates/journal-monthly.md)
- [resources/templates/journal-quarterly.md](../../../resources/templates/journal-quarterly.md)
- [resources/templates/journal-yearly.md](../../../resources/templates/journal-yearly.md)
