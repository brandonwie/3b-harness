---
paths:
  - "**/.local/**"
---

# .local Migration Workflow

> **Note:** This workflow is now integrated into `/wrap` (Step 1.5). The /wrap
> skill automatically checks for unprocessed `.local/` files each session,
> replacing the need for standalone migration passes. This rules file remains
> the reference for classification rules, diff-check workflow, and stub
> patterns.

Project `.local/` folders act as **staging areas** for knowledge capture during
active development. Periodically, transferable knowledge migrates to 3B.

---

## Standard `.local` Structure

Every project `.local/` should follow this layout:

```text
.local/
├── CLAUDE.md          # Required: governance, migration references
├── README.md          # Optional: human guide for complex setups
├── .env / .env.example # Environment config (if needed)
├── docker-compose.yml  # Local services (if needed)
├── data/              # SQL dumps, JSON samples, test fixtures
├── scripts/           # Shell/Python/JS utilities
├── docs/              # Reference docs (architecture, troubleshooting)
├── study/             # Study notes (migrate to 3B periodically)
├── analysis/          # Technical analysis artifacts
├── archives/          # Completed work, past results
└── temp/              # Scratch files (clean regularly)
```

---

## Classification Rules

| Folder      | Stays in `.local`? | Migrates to 3B?                         |
| ----------- | ------------------ | --------------------------------------- |
| `data/`     | YES                | No (large, project-specific)            |
| `scripts/`  | YES                | No (project-specific)                   |
| `docs/`     | Stubs only         | YES -> `guides/` or `knowledge/`        |
| `study/`    | Stubs only         | YES -> `knowledge/{category}/`          |
| `analysis/` | Stubs only         | YES -> `knowledge/{project}/`                |
| `archives/` | Review, then del   | Decisions -> `projects/{project}/decisions/` |
| `temp/`     | Delete regularly   | No                                      |

---

## Migration Map

| Source                           | Target                    | Notes                         |
| -------------------------------- | ------------------------- | ----------------------------- |
| `project/.local/study/`          | `knowledge/{category}/`   | Concepts learned              |
| `project/.local/guides/`         | `guides/procedures/`      | Operational procedures        |
| `project/.local/docs/`           | `guides/` or `knowledge/` | Architecture, troubleshooting |
| `project/.local/analysis/`       | `knowledge/{project}/`         | Technical analysis            |
| `project/.local/postmortem-*.md` | `knowledge/{project}/`         | Incident learnings            |
| `project/.local/journals/`       | `journals/YYYY/monthly/`  | Merge into existing rollups   |

---

## What Stays in `.local/` (project-specific, not migrated)

- Database dumps (`*.sql`, `*.dump`)
- Local scripts (`reset-db.sh`, `test-*.sh`)
- Test environments (`docker-compose.yml`, `.env`)
- Test data fixtures
- Project-specific config files

## What Migrates to 3B (transferable)

- Concepts learned (Redis, WebSocket, AWS patterns)
- Procedures (ECS migration, GitHub workflow)
- Post-mortems (incident learnings)
- Architecture docs (design decisions)
- Operational plans (as ADRs)
- Monthly journals (merge into existing rollups)

---

## Diff-Check Workflow

Before migrating, compare source content against existing 3B entries:

1. **Identify target** — find the matching 3B file (or confirm NEW)
2. **Read both files** — source `.local` file and 3B target
3. **Classify overlap**:
   - **Full overlap** — 3B already covers everything -> DELETE source
   - **Partial overlap** — 3B missing some content -> ENRICH 3B entry
   - **No overlap** — content is novel -> CREATE new 3B entry
4. **Enrich, don't duplicate** — add unique content to existing entries rather
   than creating parallel files
5. **Preserve 3B structure** — follow the knowledge-entry template format

---

## Post-Migration Stub Pattern

After migrating content, replace the source file with a stub pointer:

```markdown
---
tags: [stub, migrated]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: completed
---

# {Original Title}

> Migrated to 3B. See the canonical location below.

**3B Location:** `knowledge/{category}/{filename}.md` **Migrated:** YYYY-MM-DD
```

Stubs maintain discoverability in the source repo while preventing knowledge
duplication. Delete stubs during quarterly cleanup once the team is comfortable
with the 3B location.

---

## Migration Checklist

1. Scan for credentials before migration (replace with `${ENV_VAR}`
   placeholders)
2. Run diff-check workflow against existing 3B entries
3. Add proper YAML frontmatter (use knowledge-entry template)
4. Follow 5W1H documentation principles
5. Update category `_index.md` files in 3B
6. Replace migrated files with stubs in source `.local/`
7. Update source repo's `.local/CLAUDE.md` to reference 3B locations
8. Verify no transferable knowledge remains

---

## `.local/CLAUDE.md` Template

Each `.local/CLAUDE.md` should document governance and migration state:

```markdown
# .local Governance

## Structure

[Standard structure from this rule file]

## Migrated Content

| Original File  | 3B Location                 | Migrated Date |
| -------------- | --------------------------- | ------------- |
| study/topic.md | knowledge/category/topic.md | YYYY-MM-DD    |

## Remaining (project-specific, stays here)

- data/ — test fixtures, SQL dumps
- scripts/ — local automation
```

---

## Review Cadence

| Frequency   | Action                                        |
| ----------- | --------------------------------------------- |
| Per session | Write study notes, analysis in `.local/`      |
| Monthly     | Scan for migrateable content, run diff-checks |
| Quarterly   | Full audit: delete stale stubs, clean `temp/` |
