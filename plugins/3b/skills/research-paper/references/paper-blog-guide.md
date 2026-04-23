---
tags: [reference, blog, research]
created: 2026-04-01
updated: 2026-04-01
status: completed
---

# Paper Blog Writing Guide

Blog posts derived from research papers follow a different structure than
knowledge-derived posts. The reader hasn't read the paper — your job is to make
them understand why they should care and what they can use.

## How Paper Blogs Differ from Knowledge Blogs

| Dimension | Knowledge Blog (existing)      | Paper Blog (new)                            |
| --------- | ------------------------------ | ------------------------------------------- |
| Source    | `knowledge/{category}/`        | `personal/research/papers/`                 |
| Arc       | Problem → Solution → Result    | Discovery → Insight → Application           |
| Voice     | "I solved this problem"        | "I read this paper and here's what matters" |
| Audience  | Reader has the same problem    | Reader is curious about research            |
| Code      | Required (from implementation) | Optional (from application attempt)         |
| Reference | 1+ official/authoritative      | The paper itself is the primary reference   |

## Structure

### 1. Hook — Why This Paper Matters (2-3 sentences)

NOT "I read a paper." Instead, the practical implication.

Good hooks:

- "If you're building RAG pipelines, you might be overcomplicating retrieval."
- "There's a faster way to align LLMs that doesn't need a reward model."
- "Everyone is doing X. This paper shows why Y works better."

Frame in terms of the reader's daily work, not academic significance.

### 2. The Context — What Problem This Addresses (1-2 paragraphs)

Set up the problem the paper solves. Use practitioner language.

- What's the current state of the art?
- What's broken or inefficient about it?
- Why should someone building production systems care?

### 3. The Paper's Approach (2-3 paragraphs)

Explain the methodology at an engineer's level.

- Lead with the core idea in one sentence
- Walk through the approach step by step
- Use Mermaid diagrams for complex architectures
- Compare to the approach the reader probably knows

### 4. Key Results (1-2 paragraphs + table if available)

Numbers and comparisons. Be specific.

- Performance improvements with concrete metrics
- Comparison table if the paper has benchmarks
- Honest about limitations

### 5. My Take — Practical Applications (2-3 paragraphs, USER-INFLUENCED)

This is where Brandon's perspective adds unique value.

- How does this relate to systems I've built?
- What would I change in my current architecture based on this?
- What concepts did I extract into my knowledge base?

This section must reflect the user's actual input from Step 6 of the skill. Do
NOT fabricate personal experiences or project references.

### 6. Try This (1-2 paragraphs)

Actionable closing for the reader.

- Specific sections worth reading for deeper understanding
- Implementation starting points
- Links to code/tools if applicable
- When to use this approach vs alternatives

### 7. References

- The paper (primary — full citation with arXiv link)
- Related papers mentioned in the post
- Official docs for tools/frameworks discussed

## Anti-patterns

- Do NOT dump the abstract as the intro
- Do NOT use academic language ("we propose a novel framework")
- Do NOT skip the "My Take" section — it's what differentiates from a paper
  summary service
- Do NOT include every result — pick the 2-3 most impactful
- Do NOT forget limitations — honest assessment builds trust

## Blog Frontmatter

Paper-derived blog posts use the same blog frontmatter as knowledge-derived
posts. The sync script at
`$BLOG_REPO/scripts/sync-from-3b.ts` (maintainer-specific) handles the rest. The
source paper analysis file (in `personal/research/papers/`) is what gets
`blog.ready: true` and synced.
