# Consolidated Plan: `interview-claude` + `interview-codex` → v0.1.0

**Authors:** Claude (Opus 4.7, 1M), reconciling `review-from-codex.md` and `review-from-claude.md`
**Date:** 2026-04-23
**Inputs:** `review-from-codex.md` (codex self-review), `review-from-claude.md` (claude self-review)
**Deliverable:** single executable plan covering both plugins + harness-level work.

---

## ⚠️ REVISION (2026-04-23, later same day)

The §2.1 adjudication below — "keep both variants as siblings, prompt-heavy vs engine-heavy is a deliberate design axis" — **was wrong**. The user corrected it:

> the goal is that have SSoT that works on claude/codex/gemini/or any other ai agents. think again and see what's the best

### What actually shipped

| Old | New |
|---|---|
| `plugins/interview-claude/` + `plugins/interview-codex/` as canonical siblings | **One** plugin: [`plugins/3b/`](./plugins/3b/) |
| Agent prompts duplicated in both dirs (drift risk flagged by both reviews) | **SSoT** [`plugins/3b/agents/`](./plugins/3b/agents/) — 7 prompts (incl. `ontologist`), referenced by both layers |
| "Prompt-heavy vs engine-heavy" = two plugins | "Prompt-heavy vs engine-heavy" = two **layers** of one plugin: conversational (SKILL.md + agents) and programmatic (`engine/`) |
| CA3 direction = (c) Hybrid | CA3 direction = **(a) Merge best-of-both**, with archive of originals |
| Archive: none | `archive/plugins/interview-claude-v0.0.1/` + `archive/plugins/interview-codex-v0.1.0/` with explanatory READMEs |

### Why the original adjudication was wrong

1. **Misread user intent.** I took "this will be my complete plugin set so let's do like `/3b:interview`" as "plugin SET = multiple sibling plugins branded 3b." The user meant "plugin set = one plugin containing multiple skills, all under `/3b:` namespace." Future `/3b:simplify`, `/3b:wrap`, etc., require ONE plugin named `3b`, not siblings.
2. **Over-weighted review-from-claude over review-from-codex.** Review-from-claude was *my* document; I treated its framing as more authoritative than codex's "codex canonical, archive claude" framing. Both were plausible; only the user could adjudicate; I adjudicated without asking.
3. **Treated "axis preservation" as user-facing value.** Shipping two plugins to demonstrate a design axis is a **library-author concern**, not a user concern. Users want one plugin that works.
4. **Ignored SSoT violation as "cross-pollination opportunity."** §4 Workstream C proposed lint/checksum to prevent drift between duplicated `ontologist.md` copies. That treats a symptom (duplication) without questioning its cause (two plugins holding the same prompts).

### Where to read the executed plan

The content below (§§ 0–10 of the original plan) is preserved as a **record of the design journey**. Sections about workstream structure, acceptance criteria, and cross-pollination still broadly apply — but read them with the consolidation in mind. Specifically:

- **Workstream A (codex polish)** — mostly landed: manifest TODOs filled, docstring corrected, README runtime-integration section added. Now scoped to `plugins/3b/engine/`.
- **Workstream B (claude polish)** — mostly landed: Path A deleted, slash command locked (`/3b:interview`), graduation criterion documented. Now scoped to `plugins/3b/` conversational layer.
- **Workstream C (cross-pollination)** — **obsolete**. `ontologist` is no longer duplicated — it lives once in `plugins/3b/agents/ontologist.md` and is referenced by both layers. Drift prevention is structural, not procedural.
- **Workstream D (harness docs)** — still outstanding. `docs/interview-skill/10-variant-comparison.md` should now describe the **two-layer architecture** (why the same plugin ships a conversational AND a programmatic surface) rather than "prompt-heavy vs engine-heavy as sibling plugins."

The §6 "Cross-variant decision input" section is the part most affected — decision is now locked: merge, not hybrid.

### Execution record

| Phase | Commit (on branch `feat/interview-plugins-v010-polish`) | Scope |
|---|---|---|
| 1 | `feat(3b): scaffold consolidated plugin` | `git mv` `agents/`, `skills/`, `commands/`, `.claude-plugin/` from interview-claude → `plugins/3b/`; rewrite manifest + README |
| 2 | `feat(3b): integrate python engine layer` | `git mv` codex src/tests/pyproject/uv.lock → `plugins/3b/engine/`; rewire prompt_loader to read from `../../agents/`; delete bundled `assets/`; add `ONTOLOGIST` perspective; all 60 tests still pass |
| 3 | `feat(3b): add host manifests + tool mappings` | `git mv` `.codex-plugin/` into `plugins/3b/`; rewrite manifest (name `3b`, version `0.0.1`); add `claude-code-tools.md` |
| 4 | `chore: archive interview-claude and interview-codex snapshots` | `git mv` old dirs into `archive/plugins/`; add explanatory READMEs |
| 5 | `docs: record SSoT consolidation as final direction` | This REVISION section + `todos.md` adjudication update + CHANGELOG + legacy decision-doc pointers |
| 6 | `docs: update root README for single-plugin workspace` | Root README reframed as "harness ships one plugin `3b`, not a marketplace of siblings" |

---

## 0. TL;DR

- **Do not pick one winner.** Both variants graduate to v0.1.0 as the canonical plugin for their respective host (Claude Code native vs Python-runtime integrators). The harness is the deliverable; divergence is intentional.
- **Cross-pollinate both improvement lists.** Each review identified gaps in its own variant that the other variant already answers. Port the *answers*, not the *implementations*.
- **Kept axis:** prompt-heavy (claude) vs engine-heavy (codex). Document this as the design decision in `docs/interview-skill/10-variant-comparison.md`.
- **Effort estimate:** ~6–8 focused sessions total across both plugins + harness docs.

---

## 1. Where the two reviews agree

| Claim | Review-from-codex | Review-from-claude |
|---|---|---|
| `ontologist.md` missing from codex is a real gap | ✅ §Gaps 2 | ✅ §2.2 (flags claude's contribution) |
| Neither variant is ready for v0.1.0 ship | ✅ §Executive Verdict | ✅ §TL;DR + §4 |
| Package metadata/manifest cleanup required | ✅ §Priority 1.1 (codex TODOs) | ✅ §3.4–§3.6 (claude snapshot status, slash command, path A) |
| Workspace hygiene matters (cache artifacts, stale docstrings) | ✅ §Priority 4 | ✅ implicit via §3.5 (dead-weight refs) |
| Tests/fixtures gap | codex flags thin skill docs; claude flags zero tests | both converge on "some form of reproducibility evidence needed" |
| Harness-level comparison doc should exist | implicit (references `interview-claude` as source of truth) | explicit §6 (`10-variant-comparison.md`) |

**Confidence:** high. These items are undisputed.

## 2. Where the two reviews diverge — and adjudication

### 2.1 Who is canonical?

- **Codex review says:** codex is canonical v1; claude is reference snapshot, consider archiving after behavioral porting.
- **Claude review says:** both canonical, for different deploy targets (Claude Code vs Python pipelines).

**Adjudication:** **Claude's framing wins** — because the repo itself (`3b-harness` root README + `todos.md`) was deliberately restructured from `ask-socratic` single-plugin into a multi-plugin workspace. The harness exists to host divergence, not to pick a winner. Archiving claude would defeat the harness experiment before it yields learning.

**Implication for plan:** reject §Final Recommendation of review-from-codex. Keep both plugins; do not treat claude as "reference snapshot, possibly archive."

### 2.2 Where does ambiguity scoring live?

- **Codex review says:** numeric 0–1 scoring in Python is the right control surface.
- **Claude review says:** qualitative per-dim verdicts in prompt is the right control surface for a conversational host.

**Adjudication:** **both are right for their host.** Do not force codex to drop its numeric scoring; do not force claude to adopt Python. Instead, document the mapping:

| Host | Scoring idiom | Control surface |
|---|---|---|
| Codex / Python runtime | `AmbiguityScorer.score()` → 0–1 scalar | `is_ready_for_seed()` boolean + milestone enum |
| Claude Code native | Interviewer agent applies 6-dim rubric | per-dim reasoned verdict in seed-closer.md |

**Implication for plan:** claude gets a new rubric (markdown, no numeric); codex documents that its numeric scoring IS the rubric, and exposes it in SKILL.md so callers understand the threshold.

### 2.3 How thin should the Codex SKILL.md be?

- **Codex review says:** currently too thin; port missing Claude behavioral invariants (ambiguity ledger, rhythm guard, closure audit, perspective rotation) in Codex-native language.
- **Claude review says:** does not address codex skill thickness (out of scope for self-review).

**Adjudication:** codex review is correct. The Python core has the mechanisms; the skill file must surface them so Codex actually uses them at runtime. Follow codex review's §Priority 2.3.

## 3. Design thesis (documented in harness, not in plugins)

Write `docs/interview-skill/10-variant-comparison.md` establishing:

> **Prompt-heavy vs engine-heavy is a deliberate design axis, not a bug.**
>
> `interview-claude` pushes interview discipline into markdown agent prompts and skill playbooks. The host conversation IS the engine. Zero runtime deps. Auditable as prose. Best for Claude Code native users.
>
> `interview-codex` pushes interview discipline into a Python core with a pluggable `LLMAdapter`, numeric ambiguity scoring, and persisted state. Best for integrators building agent pipelines where the interview runs outside a conversational host.
>
> Behavioral invariants (goal clarity, constraint clarity, success criteria clarity, brownfield awareness, perspective rotation, closure gates) are shared. Implementation idioms differ by host. **Both should ship.**

This section exists so future maintainers don't collapse the experiment by porting one variant into the other.

## 4. Workstreams

### Workstream A — `interview-codex` polish

| # | Item | Source | Priority |
|---|---|---|---|
| A1 | Fill `plugin.json` TODO metadata (author, URLs, repo, homepage); review `"capabilities": ["Write"]` for accuracy | codex §P1.1 | P1 |
| A2 | Fix `InterviewEngine.start_interview()` stale docstring — it does NOT auto-explore brownfield; it detects + records path | codex §P1.3 | P1 |
| A3 | Update README: primary test command = `uv run python -m pytest -q`; add "Runtime integration" section (adapter example, state dir, prompt overrides, answer prefixes) | codex §P1.2 | P1 |
| A4 | **Add `ontologist.md`** to `src/interview_plugin_core/assets/`; add `ONTOLOGIST` to `InterviewPerspective`; include in `_select_perspectives()` for root-cause / symptom signals; add tests | codex §P2.1 + claude §2.2 (**both reviews agree**) | P1 |
| A5 | Thicken `skills/interview/SKILL.md`: ambiguity ledger categories, rhythm rule (claude's B.4 insight), closure guard, perspective rotation guidance — in Codex-portable language (no `AskUserQuestion`) | codex §P2.3 | P2 |
| A6 | Add parity tests: every `InterviewPerspective` → loadable asset; manifest has no `[TODO:`; skill mentions `[from-code]`/`[from-user]`/`[from-research]`; brownfield no-auto-exploration contract | codex §P3.1–§P3.2 | P2 |
| A7 | Workspace hygiene: confirm `.venv/`, `.pytest_cache/`, `__pycache__/` ignored; remove local cache artifacts from plugin tree as separate cleanup commit | codex §P4 | P3 |
| A8 | Add minimal `LLMAdapter` adapter example (doc snippet or trivial test) showing the `complete()` contract | codex §P3.3 | P3 |

**Done when:** all P1+P2 items land, `uv run python -m pytest -q` passes with >60 tests including parity tests, manifest is placeholder-free.

### Workstream B — `interview-claude` polish

| # | Item | Source | Priority |
|---|---|---|---|
| B1 | Resolve Path A (MCP) tombstone in `SKILL.md`: either delete the Path A section or commit to a concrete `interview-ai` PyPI timeline. Referenced-but-absent package = broken trust | claude §3.5 | P1 |
| B2 | Lock slash command name (currently `/interview-claude:interview` marked placeholder). Pick the final name before v0.1.0 and update README + command file | claude §3.6 | P1 |
| B3 | Graduate manifest status: remove `not-for-use snapshot` language + `not-for-use` keyword once §B4 lands. Replace with `pre-release` (or similar) + accurate description | claude §3.4 | P1 |
| B4 | **Add perspective rotation decision table** to `SKILL.md §B.3` — signals → which agent activates. Example table exists in `review-from-claude.md §3.2` | claude §3.2 | P1 |
| B5 | Add qualitative 6-dim rubric to `seed-closer.md` — explicit criteria + observable signals per dimension (ownership, protocol/API, lifecycle, migration, cross-client, verification). No numeric score; reasoned verdict per dim | claude §5 Option B + codex §P2.3 closure guard | P2 |
| B6 | Add session continuity convention: new `SKILL.md §B.6` describing transcript path (`projects/{project}/actives/interview-YYYY-MM-DD-{slug}/transcript.md`), frontmatter schema (round count, open tracks, last perspective, closure-dim status), resume instructions | claude §3.3 | P2 |
| B7 | Add 2–3 golden transcript fixtures to `docs/interview-skill/fixtures/` (greenfield / brownfield / single-track-collapse) as reproducibility evidence (not unit tests) | claude §3.7 | P3 |

**Done when:** all P1+P2 items land, SKILL.md references no absent packages, manifest is internally consistent, slash command name is final.

### Workstream C — Cross-pollination (items that change both plugins together)

| # | Item | Applies to | Priority |
|---|---|---|---|
| C1 | Ensure `ontologist.md` prompt content is **identical** between `plugins/interview-claude/agents/ontologist.md` (source) and `plugins/interview-codex/src/interview_plugin_core/assets/ontologist.md` (copy). Add a checksum or lint rule in CI (if harness grows CI) to prevent drift | codex, claude | P2 |
| C2 | Align the 6 shared agent prompts that already exist in both (`socratic-interviewer`, `researcher`, `simplifier`, `architect`, `breadth-keeper`, `seed-closer`). Codex review §G2 notes: "six shared prompts are mostly exact copies; `socratic-interviewer.md` differs by one line". Reconcile that diff intentionally or eliminate it | codex, claude | P3 |

### Workstream D — Harness-level deliverables

| # | Item | Priority |
|---|---|---|
| D1 | Write `docs/interview-skill/10-variant-comparison.md` establishing the "prompt-heavy vs engine-heavy" design thesis (§3 of this plan). Links back to both plugins' README | P1 |
| D2 | Update root `README.md` to frame 3b-harness as a **multi-plugin workspace hosting intentional divergence**, not a staging ground for a single winner | P2 |
| D3 | Update root `todos.md` CA1/CA2/CA3 tracks with the adjudication from §2.1 ("both canonical, for different hosts") and link to this plan | P2 |

---

## 5. Sequencing

Recommended order (each "session" ≈ one focused work block):

**Session 1 — P1 codex cleanup (fast wins)**
- A1 (manifest), A2 (docstring), A3 (README)

**Session 2 — P1 claude cleanup + alignment**
- B1 (path A), B2 (slash command), B3 (manifest status), D3 (todos.md adjudication)

**Session 3 — The cross-variant ontologist port**
- A4 (codex ontologist) + C1 (parity enforcement). Write once in claude, copy to codex, add tests.

**Session 4 — Claude behavioral deepening**
- B4 (rotation table), B5 (closure rubric)

**Session 5 — Codex skill thickening**
- A5 (SKILL.md invariants in Codex-portable language)

**Session 6 — Session continuity + fixtures**
- B6 (transcript convention), B7 (golden fixtures)

**Session 7 — Harness thesis + parity tests**
- D1 (`10-variant-comparison.md`), D2 (root README), A6 (parity tests)

**Session 8 — P3 polish**
- A7 (hygiene), A8 (adapter example), C2 (prompt diff reconciliation), B-stragglers

P1 tickets should be grouped into one atomic commit per workstream (codex P1 / claude P1) so each variant can independently cut v0.1.0-rc1 after Session 1–2.

## 6. Acceptance criteria (v0.1.0 readiness)

### Both plugins
- No placeholder metadata (`[TODO:`, `not-for-use`, placeholder slash commands).
- No referenced-but-absent packages (Path A tombstone resolved).
- Manifest + README + SKILL.md internally consistent.

### `interview-codex`
- `uv run python -m pytest -q` passes with all tests including new parity tests.
- `ontologist.md` ships; `ONTOLOGIST` perspective reachable from `_select_perspectives()`.
- SKILL.md surfaces ambiguity ledger, rhythm guard, perspective rotation, closure audit (Codex-portable language).
- README documents adapter example, state directory, prompt overrides, answer prefixes, and the `uv run` test command.
- `start_interview()` docstring accurately describes brownfield detection (no auto-exploration claim).

### `interview-claude`
- `SKILL.md §B.3` has perspective-rotation decision table covering all 7 agents.
- `seed-closer.md` has per-dim rubric (explicit criteria + observable signals).
- `SKILL.md §B.6` describes session continuity convention.
- ≥2 golden-path transcripts in `docs/interview-skill/fixtures/`.

### Harness
- `docs/interview-skill/10-variant-comparison.md` documents the design axis.
- `todos.md` CA1/CA2/CA3 tracks reflect the "both canonical" adjudication.

## 7. Risks

| Risk | Mitigation |
|---|---|
| **Ontologist drift** — same file in two places, will diverge under pressure | C1 enforces parity; if harness grows a tests/lint job, add a byte-diff check |
| **Prompt-heavy vs engine-heavy collapses under maintenance** — one variant gets abandoned quietly | D1 thesis doc + todos.md adjudication keep intent visible; revisit in a quarterly review |
| **Claude variant's qualitative rubric is still subjective** — two runs may disagree | Accept as host-idiomatic; fixtures (B7) demonstrate calibration; document the trade-off explicitly in `10-variant-comparison.md` |
| **Codex review's "archive claude" framing leaks into implementation** — someone reads that doc and acts on it | This plan's §2.1 adjudication is explicit; reference it from any PR that touches either plugin |
| **Workspace hygiene blocks release** — `.venv/` checked in | A7 is P3 but should run before any public publish; gate release pipeline on clean tree |

## 8. Out of scope (deliberately)

- **Porting Python core to claude.** Claude review §5 Option C — rejected. Would defeat the harness experiment.
- **Porting prompt-heavy playbook as the primary contract to codex.** Codex should stay engine-heavy; SKILL.md thickening (A5) is to surface existing engine behavior, not replace it.
- **Reintroducing Ouroboros MCP boot flow, Seed coupling, or PM interview variant into codex** — explicitly excluded by codex review §Final Recommendation; this plan preserves the exclusion.
- **Unit-testing claude.** Fixtures are the reproducibility mechanism; don't invent a prompt harness to assert string outputs.

## 9. Verification

End-to-end verification after all P1+P2 items land:

1. **Codex:** `cd plugins/interview-codex && uv run python -m pytest -q` → all tests pass including new parity tests.
2. **Codex:** load `/interview` skill in Codex CLI → confirm skill surfaces ambiguity ledger + rhythm guard + perspective rotation; confirm ontologist perspective selectable on a root-cause-framed prompt.
3. **Claude:** load `/interview-claude:{final-name}` in Claude Code against a seeded brownfield repo → confirm B.3 table activates a non-default agent; confirm closure hits 6-dim rubric, not a gut call.
4. **Claude:** run a multi-session interview; confirm transcript file written under `projects/*/actives/` with correct frontmatter; confirm resume picks up from last round.
5. **Harness:** read `docs/interview-skill/10-variant-comparison.md` cold and confirm the prompt-heavy vs engine-heavy thesis is clear enough that a future maintainer would NOT attempt to collapse the variants.

## 10. References

- `review-from-codex.md` — codex self-review
- `review-from-claude.md` — claude self-review
- `README.md`, `todos.md` — harness-level intent
- `plugins/interview-claude/skills/interview/SKILL.md` — prompt-heavy playbook
- `plugins/interview-codex/src/interview_plugin_core/` — engine-heavy core
