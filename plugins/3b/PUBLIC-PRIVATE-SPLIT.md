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

## Coupling signal check

Run this grep anywhere in `plugins/3b/` (or when considering a new copy
from 3B) to score coupling:

```bash
grep -cE '~/dev/personal/3b/|3b/knowledge|3b/journals|3b/projects/|buffer\.md|ACTIVE-STATUS|project-claude|prompts/.*PROJECT-CONFIG' "$FILE"
```

- `0–2` hits → Tier A, commit publicly.
- `3–10` hits → Tier B, commit publicly **only after** parameterizing the
  hardcoded paths.
- `≥ 12` hits → Tier C, gitignore it (or leave it in the 3B source repo).

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
