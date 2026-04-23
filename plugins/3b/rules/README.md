# `plugins/3b/rules/`

Methodology rules loaded by 3b-plugin skills. These are prose references —
not code, not skills. Skills read them via `${CLAUDE_PLUGIN_ROOT}/rules/…`.

## Frontmatter schema

Plugin rule files use **Claude Code's path-gating schema**, not the 3B
universal YAML schema. When a rule begins with

```yaml
---
paths:
  - "knowledge/**"
---
```

Claude Code auto-loads that rule only when editing a matching path.

This schema is a distinct mechanism from 3B's universal frontmatter
(`tags: / created: / updated: / status:`), which targets knowledge-file
discoverability. **Do not bulk-add the 3B universal fields to rule
files** — it can conflict with path-gated loading and adds no benefit.
Rules that need a `paths:` trigger declare it; rules that are always
loaded by a skill need no frontmatter at all.

## Current rules

| File | Loading | Purpose |
|---|---|---|
| `blog-publishing.md` | on-demand | Blog sync pipeline + voice calibration notes |
| `change-discipline.md` | universal | Commit scope, root-cause verification, friction lifecycle |
| `claude-settings-lookup.md` | on-demand | Resolving `settings.json` inheritance + permission sources |
| `dotfiles-management.md` | on-demand | Home-dir config conventions |
| `firecrawl-usage.md` | on-demand | Firecrawl credit discipline + routing matrix |
| `knowledge-creation.md` | path-gated (`knowledge/**`) | 5W1H template + required sections |
| `pr-review-lifecycle.md` | universal | PR review end-to-end flow |
| `reference-credibility.md` | on-demand | Source evaluation tiers |
| `runtime-environment.md` | on-demand | asdf + Homebrew runtime policy |
| `tag-taxonomy.md` | on-demand | Canonical `tags:` values |
| `task-starter-post-plan.md` | on-demand | Plan → implementation transition |
| `tmp-files.md` | path-gated (`tmp/**`) | `tmp/` as personal scratch / internal-only |
| `yaml-frontmatter-schema.md` | path-gated (`*.md`) | Full 3B frontmatter schema for knowledge files |

"Universal" rules are loaded by multiple skills or by the plugin's
global entry. "On-demand" rules are loaded by specific skills when a
relevant flow triggers. "Path-gated" rules auto-load when editing a
matching path.
