# Public / private split inside `plugins/3b/`

> **Policy doc for maintainers.** Public users never see this unless they
> browse the plugin directly on GitHub — it's not a skill, not a rule, and
> is not loaded into any session.

## Why this exists

`plugins/3b/` is a **shared workspace**. The 3B maintainer develops skills,
rules, and agents against a private knowledge system (3B — Brandon's Binary
Brain, at `~/dev/personal/3b/`). Some of those skills are generically useful
(clarify, investigate, review-pr, …) and ship publicly. Others are tightly
coupled to the 3B file layout (`wrap`, `clean-actives`, `code-historian`, …)
and would be useless noise for anyone who doesn't mirror the 3B conventions.

Rather than maintain two parallel plugin trees (`3b-public/` + `3b-private/`),
we keep one tree and split by **gitignore**. Public content is committed;
private content is staged locally but blocked from Git.

## Architectural constraint: one plugin directory

`plugins/3b/` holds **all** Forge plugin content — not only 3B-coupled
items. This is a hard requirement of Claude Code's plugin spec, not a
stylistic choice:

- The slash-command namespace (`/3b:*`) is driven by the `"name"` field
  in `.claude-plugin/plugin.json`.
- Plugin names are globally unique, and there is no cross-directory
  manifest merging.
- Therefore all `/3b:*` commands must physically live inside **one**
  plugin directory.

Consequence: portable skills (e.g. `interview`, `clarify`, `investigate`)
and 3B-coupled skills (e.g. `wrap`, `clean-actives`) both live under
`plugins/3b/`. The Tier-A / Tier-B / Tier-C classification below is the
mechanism that separates **ship-worthy** from **locally-staged** content,
not the directory layout.

## The rule

Inside `plugins/3b/`:

- **Committed (ships publicly):** anything that is genuinely portable —
  accepts no assumptions about `~/dev/personal/3b/` paths, `buffer.md`,
  `ACTIVE-STATUS.md`, `project-claude/`, `prompts/*/PROJECT-CONFIG.md`, or
  any other 3B-specific filesystem convention.
- **Gitignored (local-only, 3B-bounded):** anything that assumes 3B layout
  or writes into 3B-owned paths.

The gitignore patterns live in [`../../.gitignore`](../../.gitignore) under
the comment banner "3B-bounded plugin content staged locally but NOT for
public distribution."

## The decision rubric

When adding a new item to `plugins/3b/`:

1. **Does it hardcode any 3B path?** (e.g., `~/dev/personal/3b/`,
   `3b/knowledge/**`, `3b/journals/**`, `3b/projects/**`,
   `.claude/buffer.md`, `ACTIVE-STATUS.md`)
   → Gitignore it.
2. **Does it read/write 3B-owned config?** (e.g.,
   `prompts/{name}/PROJECT-CONFIG.md`, `project-claude/{name}.md`)
   → Gitignore it.
3. **Does it only use 3B-sounding NAMES but work fine elsewhere?**
   (e.g., a skill that mentions "knowledge base" but takes the path as a
   parameter)
   → Ship it publicly.
4. **Does it only reference 3B in comments / examples / descriptions but
   the logic is generic?**
   → Ship it publicly; sanitize comments to neutral language when convenient.

## Tier classification (post-Wave-3)

After the Wave 3 SSoT flip, tier classification is **manifest-driven** for
any file that has crossed into forge ownership. The grep-based heuristic
below remains useful for scoring **new candidates** (files in 3B that have
not yet been evaluated for the manifest), but for already-shipped content
the source of truth is [`SOURCE-MANIFEST.yaml`](./SOURCE-MANIFEST.yaml).

| Tier | Definition | Storage |
|------|------------|---------|
| **A** | Listed in `SOURCE-MANIFEST.yaml`. Forge owns the file; 3B consumes via symlink. | Committed in `plugins/3b/` (or `installer/hooks/`) |
| **B** | Candidate — content looks portable but not yet migrated. Surfaced by `scripts/check-3b-drift.sh` Check C. | Real file in 3B `.claude/`; awaits manifest entry |
| **C** | 3B-private. Hardcodes 3B layout or writes to 3B-owned paths. | Real file in 3B `.claude/`; gitignored in forge if present |

A file's tier is therefore a property of where it lives in the system, not
a score computed against its content.

## Candidate scoring (new files only)

Before adding a new 3B source to the manifest, use the existing grep
rubric to confirm it is Tier-A-eligible:

```bash
grep -cE '~/dev/personal/3b/|3b/knowledge|3b/journals|3b/projects/|buffer\.md|ACTIVE-STATUS|project-claude|prompts/.*PROJECT-CONFIG' "$FILE"
```

- `0–2` hits → Tier A candidate. Migrate, scrub if needed, add to manifest.
- `3–10` hits → Tier B candidate. Parameterize (env vars + placeholders),
  then migrate.
- `≥ 11` hits → Tier C. Leave in 3B; do not migrate.

Check C in `scripts/check-3b-drift.sh` automates this scan against the
four canonical 3B directories (`skills/`, `rules/`, `agents/`,
`global-claude-setup/scripts/`) and lists unmigrated Tier-A-looking files
as advisory findings.

## Drift tracking (Wave 2 through Wave 3)

[`SOURCE-MANIFEST.yaml`](./SOURCE-MANIFEST.yaml) records, for each
migrated entry, the 3B `source_path` + `source_sha` at the time of sync,
plus the `scrub` rules applied (env vars, placeholders, strip categories).
No 3B content is stored — only path references and commit SHAs, so the
manifest is public-safe.

**Wave 2 semantics (pre-flip):** forge held parameterized copies derived
from 3B. The drift script counted commits in 3B since the recorded SHA and
surfaced drift between forge and upstream.

**Wave 3 semantics (post-flip):** forge is SoT. 3B consumes via relative
symlink. The drift script no longer counts commits — that comparison is
trivially equal. Instead, it runs five integrity checks:

| Check | Trigger | Severity |
|-------|---------|----------|
| **A** | Manifest entry in 3B is not a symlink, or target missing | Critical |
| **B** | Symlink resolves to the wrong forge path | Critical |
| **C** | Tier-A-looking file in 3B not in the manifest | Advisory |
| **D** | Forge Tier-A file reintroduced a `~/dev/personal/3b/` path | Advisory |
| **E** | Recorded symlink got replaced by a regular file (plugin reinstall) | Critical |

Checks A/B/E activate when `scripts/.flip-state.json` is present
(post-flip mode). C/D run always.

The [`claude-forge-crosschecker`](./agents/claude-forge-crosschecker.md)
agent produces this audit in structured-report form via its **Mode 2 —
Source Drift Check**.

## Future: un-gitignoring

When the 3B repo itself generalizes its conventions — when `buffer.md`,
`ACTIVE-STATUS.md`, and the `projects/*/actives/` pattern become
configurable rather than hardcoded — we revisit this split and promote
Tier-C items to committed. Until then, anything gitignored stays gitignored.

## Lineage note

The `claude-forge` project was a short-lived sibling initiative focused on
general Claude Code settings + plugin management. Its scope folded into
3b-forge in April 2026. The `claude-forge-crosschecker.md` agent is the
one artifact that carries the name forward.

## Related

- [`../../installer/README.md`](../../installer/README.md) — parallel Wave 1
  status banner for the installer payload.
- [`../../tmp/migration-analysis.md`](../../tmp/migration-analysis.md) —
  full tier classification and migration waves.
- [Repo root `.gitignore`](../../.gitignore) — the actual enforcement.
