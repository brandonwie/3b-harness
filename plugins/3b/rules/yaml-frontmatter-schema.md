# YAML Frontmatter — 3B Full Schema

Base YAML Frontmatter requirement (tags, created, updated, status) is in global
`~/.claude/CLAUDE.md`. Below is the full schema for 3B files with all optional
fields.

```yaml
---
# REQUIRED
tags: [topic1, topic2]
created: YYYY-MM-DD
updated: YYYY-MM-DD # Last modification date (same as created initially)
status: not-started | in-progress | completed

# OPTIONAL - Add when applicable
source: project-name | url # Origin of the knowledge
projects: [project1, project2] # Related projects
confidence: high | medium | low | unverified # Certainty level (Principle #9)

# FORWARD LINKS - Add when referencing other files
related: # Files I explicitly reference
  - path: ./relative-path.md
    context: "Why I reference this"
  - path: ../category/other-file.md
    context: "Relationship explanation"

# USAGE TRACKING - Add when knowledge is applied
when_used:
  - date: YYYY-MM-DD
    project: project-name
    context: "What triggered this"

# BLOG PUBLISHING - For knowledge entries synced to {blog_domain}
blog:
  publishable: true | false | "review" # Appropriate for public blog?
  ready: false # Editorial: polished and ready?
  published_at: null # First publication date (set by sync)
  last_synced: null # Last sync to blog (set by sync)
  needs_resync: false # Set by /wrap, cleared by /blog-publish sync
  exclude_reason: null # If not publishable, why?

# REFERENCES - Credible sources backing this knowledge
references:
  - url: "https://docs.example.com/"
    type: official # official | authoritative | verified | experience
    title: "Documentation Title"
    verified_date: YYYY-MM-DD
    notes: "Optional context"
    author: "Author Name" # Required for authoritative type
---
```

## Linking Strategy (Obsidian-style)

- **External references (`references:`)** — URLs to official docs, RFCs, GitHub.
  Used for blog publishing credibility. NOT part of Zettelkasten graph.
- **Forward links (`related:`)** — Internal links to other 3B files. Core
  Zettelkasten connections. Explicitly maintained.
- **Backlinks** — NOT stored in files; computed at query time from forward
  links. Manual backlinks drift and become unmaintainable.

**IMPORTANT:** Never add `backlinks:` to frontmatter. If you find one, remove
it.

## Rules Files (`.claude/rules/*.md`) — `paths:` by default

Rules files use a separate frontmatter schema governed by Claude Code's
auto-load gate, NOT the 3B schema above. Any `.claude/rules/*.md` without a
`paths:` block auto-loads at **every session start** as "project instructions,
checked into the codebase." That burns session-start context budget on rules
that apply only to narrow task areas.

**Default: new rules files MUST ship with `paths:`** to scope auto-load. Only
truly universal rules (apply every task, every turn) omit `paths:`.

```yaml
---
paths:
  - "**/*topic-keyword*"
  - "**/.topic-dir/**"
---
```

Benchmark: as of 2026-04-18, the four rules files that legitimately auto-load
universally are:

- `change-discipline.md`
- `pr-review-lifecycle.md`
- `yaml-frontmatter-schema.md` (this file)
- `tag-taxonomy.md`

If a new rule does not fit alongside those four in universality, add `paths:`.

**Template:** `resources/templates/rules-file.md` (scoped-by-default scaffold).

**Background:** `knowledge/devops/claude-code-scoped-project-instructions.md` —
the mechanism, measurement (~15.5K tok/session saved after 6 files scoped), and
the mental-model traps (@-import, mention-based, hook-based) that wasted ~30
minutes hunting the gate.
