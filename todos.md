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

- [ ] **CA1 — Cross-analyze both snapshots.** Diff across 8 design axes:
  - [ ] Folder layout + manifest shape
        (`.claude-plugin/plugin.json` vs `.codex-plugin/*.json`)
  - [ ] Cross-agent portability strategy (SKILL.md dual-path vs
        Codex-specific vs portable-Python)
  - [ ] Scoring approach (agent-only qualitative vs Python numerical
        core in `plugins/interview-codex/src/interview_plugin_core/ambiguity.py`)
  - [ ] Agent / perspective prompt set (7 in `interview-claude`
        including `ontologist` vs whatever `interview-codex` ships in
        its `assets/`)
  - [ ] State / persistence model (none in `-claude` vs whatever
        `-codex` does in `src/interview_plugin_core/`)
  - [ ] Test strategy (none yet in `-claude` vs `tests/` in `-codex`)
  - [ ] Dependency footprint (zero Python deps vs uv-managed project
        with pyproject + uv.lock)
  - [ ] Distribution approach (Claude marketplace vs Codex native)

- [ ] **CA2 — Write `docs/interview-skill/10-variant-comparison.md`**
  (EN). Contents:
  - [ ] Summary matrix (axes × variants × verdict)
  - [ ] Per-axis verdict (who wins / what's the tradeoff)
  - [ ] Merge recommendations (can we take best of both? specific
        pieces?)
  - [ ] Risks of each direction (pick / merge / keep both)
  - [ ] Mirror doc in Korean:
        `docs/interview-skill/10-variant-comparison.ko.md`
  - [ ] Update `docs/interview-skill/README.md` index to list doc 10

- [ ] **CA3 — Decide direction.** Options:
  - [ ] (a) Merge best-of-both into a single new plugin (new name TBD)
  - [ ] (b) Promote one as primary; archive the other as reference
  - [ ] (c) Hybrid — keep two specialized variants for different use
        cases
  - [ ] Document decision in
        `docs/interview-skill/11-direction-decision.md`
  - [ ] Update root README Roadmap + this todos.md post-comparison
        section accordingly

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
