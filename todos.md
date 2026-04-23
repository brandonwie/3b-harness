---
tags: [todos, 3b-harness]
created: 2026-04-23
updated: 2026-04-23
status: in-progress
---

# 3b-harness — TODOs

Near-term action backlog for the harness. Tracked here (not in GitHub
Issues) because this is a personal workspace.

Status markers: `[ ]` open, `[~]` in-progress, `[x]` done, `[-]` skipped,
`[!]` blocker.

## Current focus — cross-variant comparison

Goal: diff the two interview plugin snapshots
(`plugins/interview-claude/` v0.0.1 and `plugins/interview-codex/`
v0.1.0) side by side, decide the path forward, then unblock the
release roadmap.

### Adjudication (2026-04-23, revised same day)

CA1 + CA3 resolved via self-review cross-analysis plus a user-driven
course correction:

- [`review-from-claude.md`](./review-from-claude.md) — Claude's review of
  `interview-claude` against `interview-codex` baseline.
- [`review-from-codex.md`](./review-from-codex.md) — Codex's review of
  `interview-codex` against `interview-claude` baseline.
- [`consolidated-plan.md`](./consolidated-plan.md) — reconciles both
  reviews; see its **⚠️ REVISION** banner at top for the corrected
  direction.

**Direction chosen: CA3 option (a) — Merge best-of-both.** One plugin,
[`plugins/3b/`](./plugins/3b/), with TWO **layers** (not two plugins):

- **Conversational layer** — SKILL.md playbook + 7 agent prompts.
  Zero runtime deps. Slash command `/3b:interview`. Works on Claude
  Code, Codex, Gemini CLI, any future AI agent that can read markdown.
- **Programmatic layer** — [`plugins/3b/engine/`](./plugins/3b/engine/)
  Python package (`interview_plugin_core`). Numeric ambiguity scoring,
  file-locked state persistence, 60+ async tests. Optional — loads
  prompts from the same `plugins/3b/agents/` as the conversational
  layer (SSoT).

Old snapshots moved to [`archive/plugins/`](./archive/) with
explanatory READMEs. The first-pass adjudication (keep both as
siblings) is recorded in consolidated-plan.md's REVISION section.

- [x] **CA1 — Cross-analyze both snapshots.** Done via `review-from-claude.md`
  + `review-from-codex.md`. All 8 design axes covered. See also
  `consolidated-plan.md` §1 structural comparison matrix.

- [ ] **CA2 — Write `docs/interview-skill/10-variant-comparison.md`**
  (EN). **Scope revised** — doc now describes the two-**layer**
  architecture of `plugins/3b/` rather than two sibling plugins.
  Contents:
  - [ ] Why the plugin has a conversational layer AND a programmatic
        layer (prompt-heavy vs engine-heavy as two surfaces of one
        plugin, not two plugins).
  - [ ] When to use which layer; how they share `agents/` via SSoT.
  - [ ] Reference to the archived original variants as design-journey
        context.
  - [ ] Mirror doc in Korean:
        `docs/interview-skill/10-variant-comparison.ko.md`
  - [ ] Update `docs/interview-skill/README.md` index to list doc 10

- [x] **CA3 — Decide direction.** Chose **(a) Merge best-of-both**
  into single `plugins/3b/` with archived originals under
  `archive/plugins/`. See Adjudication block above.
  - [ ] Document decision in
        `docs/interview-skill/11-direction-decision.md` (formal ADR
        still TODO — `consolidated-plan.md` REVISION is the current
        record but a dedicated ADR keeps the decision trail cleaner).
  - [ ] Update root README (Phase 6 — to reflect single-plugin
        workspace + archive layout).

## Post-comparison roadmap (blocked on CA3)

After CA3 picks a direction, these tasks apply to whichever plugin
wins. Versioning restarts at `v0.1.0` once the winner is chosen — the
`-claude` v0.0.1 and `-codex` v0.1.0 numbers are frozen snapshot labels
and will not continue.

- [ ] **v0.1.0** — first usable cross-agent release (Path B working on
  Claude Code / Codex / Gemini CLI). Includes proper versioned tag,
  per-agent install instructions with tested commands, release notes
  in CHANGELOG.
- [ ] **v0.2.0** — Path A (MCP) via `interview-ai` PyPI package.
  See `docs/interview-skill/09-plugin-build-decisions.md` Phase 2.
  - [ ] Port core utilities (types, errors, file_lock, security,
        initial_context, seed dataclass)
  - [ ] Port providers (LLMAdapter + litellm impl)
  - [ ] Port simplified config
  - [ ] Port agents/loader
  - [ ] Port InterviewEngine + state + scorer + events
  - [ ] Port event_store
  - [ ] Port MCP types + errors
  - [ ] Port InterviewHandler (drop plugin-mode per D13b)
  - [ ] MCP server registration + CLI entry
  - [ ] Un-tombstone SKILL.md Step 0.5
  - [ ] Fresh tests (property / integration / contract)
  - [ ] PyPI publish dry-run + docs update
- [ ] **v0.3.0** — Phase 3 (see same build-decisions doc Phase 3).
  - [ ] Port brownfield detection + codebase explorer
  - [ ] Port PM variant (pm_interview.py, pm_handler.py, pm_seed,
        pm_document, pm_completion, question_classifier)
  - [ ] Add ontologist as 6th `InterviewPerspective`
  - [ ] Register PM MCP tool
  - [ ] Fresh PM + brownfield tests
  - [ ] End-to-end smoke on all 3 agents
  - [ ] Claude marketplace submission + PyPI publish

## Harness infrastructure (run in parallel to CA1–CA3 when slack time)

### 3B integration — **priority** (do early; pays off every session after)

Without this, every `/wrap` that touches 3b-harness has to manually
scope which changes go where and can't auto-populate the ACTIVE-STATUS
"Work" table with 3b-harness tasks. With proper 3B wiring, all of that
becomes automatic.

- [ ] **Run `/init-3b` inside 3b-harness** to wire it into the 3B
  knowledge system. This creates:
  - `3b/.claude/project-claude/3b-harness.md` (project CLAUDE.md
    source; the repo's `CLAUDE.md` becomes a symlink to this)
  - `3b/.claude/prompts/3b-harness/PROJECT-CONFIG.md` (tells skills
    where to find todos, PROGRESS, actives, docs paths)
  - `3b/projects/3b-harness/` (personal docs + task tracking —
    `todos.md`, `actives/`, `PROGRESS.md` live here)
  - Optional: `docs/` inside the repo as a symlink to
    `3b/projects/3b-harness/` (gitignored, personal-only). Decide up
    front: the existing `docs/interview-skill/` is shared/public
    analysis — it should stay committed in-repo, NOT symlinked to 3B.
    The `/init-3b` wiring needs a variant: docs stay in-repo, but the
    3B project folder still holds task tracking (`todos.md` + `actives/`).
- [ ] **Reconcile `todos.md` locations.** Two options:
  - (a) Move this `todos.md` into `3b/projects/3b-harness/todos.md`
    (the 3B-canonical location, symlinked back OR gitignored). Keeps
    `/wrap`'s PROJECT_MODE path-reading working out of the box.
  - (b) Keep `todos.md` at 3b-harness root (public, committed — good
    for contributors to see backlog) AND also wire
    `3b/projects/3b-harness/todos.md` for personal planning that
    shouldn't be public. Dual-tracker.
  - Pick one before committing to layout.
- [ ] **Confirm `PROJECT-CONFIG.md` fields** — minimally needs
  `project: 3b-harness`, `domain: personal` (or `tools`?),
  `actives_path`, `todos_path`, `type: personal` (or the new
  `plugins-workspace` type if we introduce one).
- [ ] **Verify `/wrap` auto-detection.** After `/init-3b`, run `/wrap`
  from `3b-harness/` and confirm it:
  - detects PROJECT_MODE=true,
  - reads this `todos.md` (if option a above) or the 3b-personal one
    (option b),
  - includes 3b-harness tasks in the ACTIVE-STATUS Work table,
  - commits to both repos separately with correct scopes.
- [ ] **Add routing entry to global CLAUDE.md** if not auto-detected —
  `/wrap` should know `3b-harness` is a recognized project so it
  doesn't fall back to 3B-only mode.
- [ ] **Decide `docs/` symlink question.** Current docs include the
  full interview-skill analysis (10 public files, ~170K); keeping
  them in-repo makes them visible to anyone browsing
  `github.com/brandonwie/3b-harness`. Do NOT symlink `docs/` to
  `3b/projects/3b-harness/` — that would gitignore them. Instead,
  keep `docs/` in-repo and put ONLY personal planning
  (`todos.md`, `actives/`) under the 3B project folder.
- [ ] **Update harness README's file-layout diagram** after 3B wiring
  to document which files are in-repo vs in 3B.

### General harness infrastructure

- [ ] Add `.claude-plugin-marketplace.json` (or Claude's current
  marketplace manifest format) so
  `claude plugin marketplace add brandonwie/3b-harness` discovers
  individual plugins under `plugins/` correctly.
- [ ] Document per-agent install flow for non-Claude platforms in root
  README with concrete, tested commands (current instructions are best-
  guess; both Codex and Gemini install paths need verification).
- [ ] Decide: stay under `brandonwie/` user on GitHub, or migrate the
  harness to a GitHub org once a second "real" plugin arrives.
- [ ] Add CI (GitHub Actions) running: plugin.json schema validation,
  markdown lint on docs/, eventually Python tests for PyPI package
  side.

## Future plugin ideas (not yet committed)

Backlog — raw ideas, no roadmap slot yet. Candidates only:

- [ ] `/edit` workflow skill — refactor-focused guided edit
- [ ] `/simplify` post-PR review — removes accidental complexity
- [ ] `/codebase-summary` — summary for newcomer onboarding
- [ ] `/ralph` variant — persistent verify-until-green loop
- [ ] `/wrap` lite — end-of-session checklist without full 3B
  integration (for repos not 3B-connected)
- [ ] Custom MCP servers (TBD based on which plugins ship first)

## Closed / recent

- [x] 2026-04-23 — `ask-socratic` repo scaffolded, v0.1.0-alpha
      committed.
- [x] 2026-04-23 — Rename repo `ask-socratic` → `3b-harness`. Restructure
      from single-plugin layout to harness layout with
      `plugins/<name>/`.
- [x] 2026-04-23 — Move `plugins/interview-codex/` in from
      `ouroboros/plugins/`.
- [x] 2026-04-23 — Copy `docs/interview-skill/` (10 analysis files,
      EN + KO for #09) into harness.
- [x] 2026-04-23 — Rename `plugins/interview/` →
      `plugins/interview-claude/`; demote `v0.1.0-alpha` → `v0.0.1`
      (not-for-use snapshot).

## References

- Root [README.md](./README.md) — harness overview.
- [CHANGELOG.md](./CHANGELOG.md) — history of changes.
- Key design doc:
  [docs/interview-skill/09-plugin-build-decisions.md](./docs/interview-skill/09-plugin-build-decisions.md)
  (EN) /
  [docs/interview-skill/09-plugin-build-decisions.ko.md](./docs/interview-skill/09-plugin-build-decisions.ko.md)
  (KO).
- Analysis index:
  [docs/interview-skill/README.md](./docs/interview-skill/README.md).
- Upstream: [Q00/ouroboros](https://github.com/Q00/ouroboros).
