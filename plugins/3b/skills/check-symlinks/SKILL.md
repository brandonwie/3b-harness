---
name: check-symlinks
description: >-
  Audit and repair all symlinks from 3B to global config profiles (~/.claude,
  ~/.claude-work) and project repositories. Use this skill whenever the user
  says "check symlinks", "symlink audit", "verify symlinks", "fix symlinks",
  "symlink health", or "check links". Also trigger when the user reports
  settings not propagating, config drift between profiles, or after Claude Code
  UI updates or plugin reinstalls — these commonly overwrite symlinks with
  regular files via atomic rename.
allowed-tools: [Read, Bash, Grep, Glob, AskUserQuestion]
metadata:
  version: "1.0.0"
---

# /check-symlinks

Audit all symlinks in the 3B knowledge management system. 3B uses ~55 symlinks
across three categories to maintain a single source of truth for configs,
CLAUDE.md files, .mcp.json files, and docs/ across two profiles and 10+ project
repos.

## Why symlinks break

The most common failure: Claude Code UI (or plugins) write files atomically —
create a temp file, then `rename()` over the target. The rename replaces the
symlink inode with a regular file, silently breaking the SoT chain. Other causes
include plugin updates, git operations, and manual edits to the wrong file.

## Workflow

### Step 1: Run the audit

Execute the bundled check script:

```bash
bash ${FORGE_3B_ROOT}/.claude/skills/check-symlinks/scripts/check-symlinks.sh
```

The script checks every expected symlink and classifies each as:

| Status       | Meaning                             | Fix strategy              |
| ------------ | ----------------------------------- | ------------------------- |
| OK           | Symlink valid, target exists        | None needed               |
| REPLACED     | Regular file where symlink expected | Diff → merge → re-symlink |
| BROKEN       | Symlink exists but target missing   | Investigate → re-create   |
| MISSING      | Expected symlink doesn't exist      | Create symlink            |
| WRONG_TARGET | Symlink points to wrong file        | Confirm → re-point        |

If everything is OK, report the clean bill of health and stop.

### Step 2: Report

Present a summary table to the user:

```text
| Category | Total | OK | Issues |
|----------|-------|----|--------|
| Personal |    14 | .. |     .. |
| Work     |   ~17 | .. |     .. |
| Projects |   ~24 | .. |     .. |
| Total    |   ~55 | .. |     .. |
```

Then list each issue with its status, path, and expected target.

### Step 3: Fix issues (interactive)

Handle each issue type differently:

**REPLACED** (most common — UI overwrote symlink with a file copy):

1. Diff the regular file against the SoT:

   ```bash
   diff <regular-file-path> <expected-sot-target>
   ```

2. If identical → safe to restore directly
3. If different → show the diff to the user. The local copy may have changes
   that should be merged back into the SoT before restoring
4. After user confirms:

   ```bash
   rm <path> && ln -sf <expected-target> <path>
   ```

5. Verify the new symlink resolves correctly:

   ```bash
   ls -la <path>
   realpath <path>
   ```

**BROKEN** (symlink target missing):

- Show what the symlink currently points to
- Likely cause: SoT file was moved/renamed, or 3B repo is out of date
- Ask user whether to re-create or investigate

**MISSING** (no symlink at all):

- Offer to create: `ln -sf <expected-target> <path>`
- For project repos: check if the repo directory exists first, skip if not

**WRONG_TARGET** (points to wrong file):

- Show current target vs expected target
- Ask before fixing — might be an intentional temporary override

### Step 4: Verify

After all fixes, re-run the audit:

```bash
bash ${FORGE_3B_ROOT}/.claude/skills/check-symlinks/scripts/check-symlinks.sh
```

Report the final score (e.g., "55/55 symlinks healthy").

## Maintaining the repo map

When a new project repo is added to 3B, update `scripts/check-symlinks.sh`:

1. Add a `check_project` call in the Category C section with:
   - SoT name (matches the filename in `project-claude/`)
   - Repo path
   - docs/ target path in 3B
2. Run `/check-symlinks` to verify

The script is organized into clearly labeled sections (Categories A, B, C) so
new entries go in the obvious place.
