---
name: doc-audit
description: >-
  Audit documentation for stale references, broken links, missing
  cross-references, and outdated content. Scans markdown files, validates
  frontmatter, checks relative links, and reports parity gaps. Use when user
  says "audit docs", "doc audit", "check stale links", "find broken references",
  "documentation health", or "validate docs".
allowed-tools: [Read, Glob, Grep, Bash, Write, AskUserQuestion]
metadata:
  version: "1.0.0"
---

# /doc-audit

Scan a project or directory for documentation health issues. Produces a
prioritized report of problems to fix.

## Purpose

Catch documentation rot before it causes confusion:

- Broken relative links (`[text](./missing.md)`)
- Stale frontmatter (`updated:` older than file's last real edit)
- Missing cross-references (files that should link to each other but don't)
- Orphaned files (no inbound links from any other file)
- Frontmatter violations (missing required fields)
- Outdated content signals (TODO markers, deprecated references)

## Trigger Phrases

- "audit docs" / "doc audit" / "/doc-audit"
- "check stale links" / "find broken references"
- "documentation health" / "validate docs"
- "scan docs for issues"

## Step 0: Determine Scope

Ask user if not specified:

1. **Current directory** - Audit cwd recursively
2. **Specific path** - Audit a given directory
3. **Full 3B** - Audit entire 3B repository
4. **Project docs only** - Audit a specific project's docs

Set `AUDIT_ROOT` to the chosen path.

## Step 1: Discover Files

```bash
# Find all markdown files in scope
find {AUDIT_ROOT} -name "*.md" -not -path "*/node_modules/*" \
  -not -path "*/.git/*" -not -path "*/tmp/*"
```

Build a file inventory with paths for link resolution.

## Step 2: Check Relative Links

For each markdown file, extract all relative links:

- `[text](./path.md)` and `[text](../path.md)` patterns
- `related:` paths in YAML frontmatter — **use `knowledge-link-checker.py`** for
  bulk automated validation:
  `python3 ~/.claude/scripts/knowledge-link-checker.py --fix-suggestions`.
  Reports broken links with source, target, and suggested corrections. Covers
  knowledge/, guides/, personal/, and projects/ directories.
- Anchor links (`[text](#heading)`)

**Validate each link:**

| Check                | Pass                         | Fail                     |
| -------------------- | ---------------------------- | ------------------------ |
| Target file exists   | File found at resolved path  | **BROKEN LINK**          |
| Anchor target exists | Heading found in target file | **BROKEN ANCHOR**        |
| Target is in scope   | Inside audit root            | **EXTERNAL** (warn only) |

## Step 3: Validate Frontmatter

For each file, check YAML frontmatter against required fields:

**Required fields (3B convention):**

- `tags` (array, non-empty)
- `created` (valid date)
- `updated` (valid date)
- `status` (one of: not-started, in-progress, completed)

**Staleness check:**

- If `updated` date is more than 90 days behind file's git last-modified date,
  flag as **STALE METADATA**
- If `status: in-progress` and no git changes in 60+ days, flag as **ABANDONED**

## Step 4: Detect Orphaned Files

Build a link graph from Step 2 results:

- **Inbound links**: How many files link TO this file
- **Outbound links**: How many files this file links TO

Flag files with **zero inbound links** as **ORPHAN** (except index files,
README.md, CLAUDE.md, and root-level files).

## Step 5: Content Signals

Scan file content for staleness indicators:

| Signal           | Pattern                                | Severity |
| ---------------- | -------------------------------------- | -------- |
| TODO markers     | `TODO`, `FIXME`, `HACK`, `XXX`         | Medium   |
| Deprecated refs  | `deprecated`, `removed`, `obsolete`    | Low      |
| Placeholder text | `TBD`, `placeholder`, `lorem ipsum`    | Medium   |
| Date references  | Hardcoded dates more than 6 months old | Low      |

## Step 6: Generate Report

Present findings grouped by severity:

```markdown
## Doc Audit Report: {AUDIT_ROOT}

**Scanned:** {N} files | **Issues:** {N} total

### Critical (fix now)

| File            | Issue       | Details                           |
| --------------- | ----------- | --------------------------------- |
| path/file.md:15 | BROKEN LINK | Links to ./missing.md (not found) |

### Warning (fix soon)

| File         | Issue          | Details                                   |
| ------------ | -------------- | ----------------------------------------- |
| path/file.md | STALE METADATA | updated: 2025-06-01, last git: 2026-01-15 |
| path/file.md | ORPHAN         | Zero inbound links                        |

### Info (review when convenient)

| File            | Issue | Details              |
| --------------- | ----- | -------------------- |
| path/file.md:42 | TODO  | "TODO: add examples" |
```

## Step 7: Offer Fixes

After presenting the report, ask user:

1. **Auto-fix what's possible** - Update stale `updated:` dates, remove broken
   links
2. **Fix specific category** - e.g., "fix all stale metadata"
3. **Export report** - Save to `tmp/doc-audit-{date}.md`
4. **Done** - Just the report, no fixes

**Auto-fixable issues:**

- STALE METADATA → Update `updated:` to git last-modified date
- Missing `status:` → Add `status: in-progress`

**Not auto-fixable (require judgment):**

- BROKEN LINK → Need to determine correct target or remove
- ORPHAN → Need to decide if file should be linked or deleted
- TODO markers → Need human to resolve

## Output

```text
Doc audit complete for {AUDIT_ROOT}

Scanned: {N} files
Critical: {N} (broken links, missing required fields)
Warning:  {N} (stale metadata, orphans)
Info:     {N} (TODOs, placeholders)

Report saved to: tmp/doc-audit-{date}.md (if exported)
```

## Quick Reference

```text
TRIGGER:  "audit docs" | "doc audit" | "/doc-audit"
SCOPE:    Directory, project, or full 3B
CHECKS:   Links, frontmatter, orphans, content signals
OUTPUT:   Prioritized report (Critical/Warning/Info)
FIXES:    Auto-fix metadata; manual fix for links/orphans
```
