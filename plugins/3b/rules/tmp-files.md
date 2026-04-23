---
paths:
  - "tmp/**"
---

# Temporary Files (tmp/)

The `tmp/` folder is for **Claude session scratch space** - temporary files that
help during a conversation but don't need to persist.

## Use tmp/ for

- Session context that's too large for conversation memory
- Intermediate analysis or planning documents
- Draft content before finalizing to proper location
- Debugging notes and temporary logs
- Work-in-progress that may be discarded

## Structure

```text
tmp/
├── intake/                 # UNIVERSAL DROP FOLDER — all skills check here
│   ├── {any-pdf}.pdf      # Papers, slides, docs
│   ├── {any-notes}.md     # Context files, summaries
│   └── {any-file}.*       # Screenshots, code, etc.
├── {session-id}/           # Use date or descriptive name
│   ├── context.md         # Session context dump
│   ├── analysis.md        # Intermediate analysis
│   └── draft-*.md         # Draft documents
└── .gitkeep               # Keep folder in git (contents ignored)
```

## intake/ — Universal File Drop

`tmp/intake/` is the **single entry point** for staging files before any skill
session. Drop files here when you don't know (or don't care) which skill will
process them.

**How it works:**

1. You download/save files → drop in `tmp/intake/`
2. You invoke a skill (`/research-paper`, study session, etc.)
3. The skill auto-scans `intake/` and classifies what it finds
4. After processing, files move to their proper permanent locations

**Skills that check intake/:**

| Skill             | What It Looks For                         | Moves Files To                  |
| ----------------- | ----------------------------------------- | ------------------------------- |
| `/research-paper` | PDFs, markdown context, URLs in .md files | `personal/research/pdfs/`       |
| Study sessions    | Course PDFs, slides, assignments          | `personal/study/{course}/refs/` |

**Rules:**

- Drop anything here — the skill figures out what to do with it
- Files stay in `intake/` until a skill processes them (no auto-cleanup)
- After processing, check that `intake/` is empty
- Direct input (URLs in prompts, explicit file paths) still works alongside

**Legacy:** `personal/study/per-session-temp-references/` was the previous study
staging folder. It still works but `tmp/intake/` is preferred — one habit for
all workflows.

## Rules

- Everything in `tmp/` is gitignored except `.gitkeep`
- Claude should clean up old session folders when starting new work
- If content becomes valuable, move it to the appropriate permanent location
- Use descriptive folder names: `tmp/2026-01-23-airflow-debug/`
