---
paths:
  - "knowledge/**"
---

# Knowledge Creation Rules

When creating or updating knowledge entries in `knowledge/`, enforce the 5W1H
structure to produce rich, blog-expandable content.

## Required Sections (All Entries)

Every knowledge entry MUST include:

| Section                      | 5W1H | Purpose                                |
| ---------------------------- | ---- | -------------------------------------- |
| **The Problem**              | WHY  | What problem prompted this knowledge   |
| **Difficulties Encountered** | HOW  | What made solving this hard            |
| **The Solution**             | HOW  | Implementation with code/examples      |
| **When to Use**              | WHEN | Scenarios where this applies           |
| **When NOT to Use**          | WHEN | Anti-patterns, inappropriate scenarios |

### Difficulties Encountered (Required)

Capture the struggle before the resolution. This section answers: "What made
this problem hard to solve?" Include any of:

- **Dead ends tried** — approaches that seemed right but failed, and why
- **Misleading signals** — error messages, docs, or assumptions that led you
  astray
- **Non-obvious gotchas** — things you only discovered through trial and error
- **Time sinks** — parts that took disproportionately long and why

This section is required because it captures the most transferable knowledge —
the traps that others will fall into. It also provides the narrative arc that
makes blog posts engaging (struggle → resolution).

## Decision-Oriented Knowledge (Options Rule)

> The global Decision Documentation Protocol (`~/.claude/CLAUDE.md`) defines the
> universal rule. Below is the 3B-specific application for knowledge entries.

If the knowledge describes a **decision** (chose X over Y), it MUST also
include:

| Section                | Purpose                                                  |
| ---------------------- | -------------------------------------------------------- |
| **Options Considered** | At least 2 alternatives (aim for 3) with pros/cons table |
| **Why This Approach**  | Rationale for the chosen option                          |

### How to Detect Decision Knowledge

A knowledge entry is decision-oriented if ANY of these are true:

- The author chose one tool/library/pattern over alternatives
- The entry compares approaches (e.g., "Redis vs Memcached")
- The solution involves a trade-off (performance vs simplicity)
- The entry mentions "instead of", "rather than", or "over"

### Options Table Format

```markdown
## Options Considered

| Option   | Pros         | Cons         |
| -------- | ------------ | ------------ |
| Option A | Pro 1, Pro 2 | Con 1        |
| Option B | Pro 1        | Con 1, Con 2 |
| Option C | Pro 1, Pro 2 | Con 1, Con 2 |

## Why This Approach

Chose Option A because [specific Pro] outweighs [specific Con] given {constraint
connecting to the problem}.
```

## Concept-Only Knowledge

Not all knowledge involves decisions. Pure concept entries (e.g., "What is event
sourcing?") may use the simpler **Overview + Key Points** structure from the
template. However, they still MUST include:

- The Problem (why learn this)
- Difficulties Encountered (what made it hard)
- Example (practical demonstration)
- When to Use / When NOT to Use

## Quality Gate for Blog Publishing

Knowledge entries with `blog.publishable: true` are expanded into narrative blog
posts by the `/blog-publish` skill. Richer source entries produce better blog
posts. Before marking `blog.ready: true`, verify:

- [ ] Problem section clearly states the pain point
- [ ] Difficulties section captures dead ends or gotchas
- [ ] Solution includes working code examples
- [ ] At least one official or authoritative reference exists
- [ ] If decision-oriented: Options table has 2+ alternatives
- [ ] When to Use / When NOT to Use are specific (not generic)

## Confidence Rating

Assess the `confidence:` frontmatter field for every knowledge entry:

| Level        | Criteria                                                  |
| ------------ | --------------------------------------------------------- |
| `high`       | Verified by official docs, tested in production, proven   |
| `medium`     | Supported by authoritative sources or limited testing     |
| `low`        | Based on inference, single data point, or untested theory |
| `unverified` | Hypothesis or hearsay, not yet validated                  |

Knowledge entries with `confidence: low` or `unverified` MUST NOT have
`blog.publishable: true`. They need validation before publishing.
