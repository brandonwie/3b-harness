---
paths:
  - "projects/*/actives/*/plan.md"
  - "projects/*/actives/*/todos.md"
---

# Task-Starter Post-Plan Enforcement

Safety net for `/task-starter` Phase 4-6 execution in plan mode sessions.
Updated in v1.4.0 to support `task_type` classification + Phase 0.5
type-conditional gates.

## Rule

When `ExitPlanMode` was called in a `/task-starter` session — or when you see a
`plan.md` in an actives/ folder with an unchecked "Pre-Implementation Setup"
checklist:

1. **Re-read** `plan.md` from the actives/ folder to recover task context
2. **Parse frontmatter** for `task_type`, `create_issue`, `create_branch`, and
   task-type-specific gate fields
   - If `task_type` is missing, **default to `feat`** (backwards compatibility
     with pre-1.4.0 plans)
   - If `create_issue` / `create_branch` fields are absent, **default both to
     `true`** (backwards compatibility — byte-identical to pre-1.2.0 behavior)
3. **Phase 0.5 gate verification** — before any coding, confirm the
   type-specific field is set:

   | `task_type`   | Gate field REQUIRED in frontmatter                                                      | Meaning of a null/missing value                                     |
   | ------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
   | `feat`        | none                                                                                    | —                                                                   |
   | `fix`         | `reproducible` (true / false) + `repro_method`                                          | Phase 0.5.fix was skipped — re-run reproduce step before coding     |
   | `refactor`    | `plan.md` contains "Regression gate" H2 with integration/e2e commands that passed green | Phase 0.5.refactor was skipped — run regression suite before coding |
   | `perf`        | `baseline_ref` (git SHA or artifact path)                                               | Phase 0.5.perf was skipped — capture baseline before coding         |
   | `chore`       | `chore_subtype` (chore / docs / test / ci)                                              | Phase 0.5.chore was skipped — pick subtype before coding            |
   | `investigate` | `time_box_hours` + `started_at`                                                         | Phase 0.5.investigate was skipped — set time-box before coding      |

4. **Execute** only the checklist items that match the Phase 0 selections:

   | `create_issue` | `create_branch` | Required actions before coding            |
   | :------------: | :-------------: | ----------------------------------------- |
   |      true      |      true       | Issue + Branch (with issue #) + todos.md  |
   |      true      |      false      | Issue + todos.md (stay on current branch) |
   |     false      |      true       | Branch (no issue #) + todos.md            |
   |     false      |      false      | Nothing — proceed directly to coding      |

5. Do NOT interpret user's "go ahead", "proceed", or "start" as "skip to coding"
   **unless both booleans are false AND the Phase 0.5 gate is satisfied**
6. Only after the Phase 0.5 gate AND all **selected** Phase 4-6 steps are done,
   announce readiness and ask to proceed
7. Do NOT skip a selected step just because another step was unselected — each
   boolean is independent
8. **Investigate time-box auto-stop** — if `task_type == investigate` and
   current time exceeds `started_at + time_box_hours`, HALT before the next tool
   call and fire `AskUserQuestion` with options `Extend (+1h)` | `Extend (+4h)`
   | `Abandon` | `Convert to full task`. See SKILL.md Phase 0.5.investigate step
   4 for the exact prompt.

## Anti-Skip Guarantee

The guarantee from v1.1.0 still holds, scoped to the chosen subset:

- If `create_issue == true`, Claude **must** create the issue before coding
- If `create_branch == true`, Claude **must** create the branch before coding
- If either is true, `todos.md` **must** be generated before coding

The only case where no setup is required is when **both** are `false`.

## Branch Base and Naming (Phase 5 reference)

**Base branch (priority order):**

1. `base_branch` from PROJECT-CONFIG.md if set
2. First local branch matching `dev*` (prefer `develop` > `dev` > `development`)
3. Fall back to `main`

**Naming:**

- Both `create_issue` and `create_branch`: `{type}/{issue-number}-{short-desc}`
- Only `create_branch` (no issue): `{type}/{short-desc}`

## Why This Rule Exists

Plan mode creates a turn boundary at `ExitPlanMode` — Claude's turn ends and the
user's next message starts a fresh turn. The skill's Phase 4-6 instructions may
not survive context compaction across this boundary. This rules file loads into
every conversation turn, and the `plan.md` on disk (with frontmatter booleans)
ensures the task context and setup decisions are always recoverable.
