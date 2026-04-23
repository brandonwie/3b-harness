# Blog Writing Guide — Knowledge Expansion

How to expand atomic 3B knowledge entries into narrative blog posts for
a Svelte blog project ({blog_domain}). This guide is used during Step 4.5 of
`/blog-publish`.

## Core Philosophy

**Share what you learned, honestly.** The reader is a developer who has the same
problem. The post should present the problem, the options, and what you found —
not lecture from authority.

A knowledge entry is **reference material** (terse, scannable, atomic). A blog
post is **narrative sharing** (engaging, explained, contextualized). The
expansion step bridges this gap.

**Intellectual humility is non-negotiable.** Frame posts as "here is what I
found" not "here is what I'll teach you." Admit what you did not know. Present
trade-offs honestly. Let the reader draw their own conclusions.

## Blog Post Structure

Follow the **Problem → Solution → Result** arc:

### 1. Hook (2-3 sentences)

Open with the problem. State it directly from the 3B source material.

- Use first person only for things that actually happened ("I needed to..." /
  "The feature required...")
- State the problem or need — do NOT dramatize ("cost me a day of debugging")
- **NEVER fabricate experiences.** If the 3B source says "Needed to create Meet
  links," write that. Do not invent debugging sessions, wasted hours, or
  production incidents that are not in the source material.

### 2. Context (1-2 paragraphs)

Why does this problem matter? What happens if you ignore it?

- Brief background (just enough to follow along)
- Who faces this problem (what kind of project/scale)
- What you'll cover in this post

### 3. Options Explored (if source has Options Considered)

Walk through what you considered. This creates depth and shows the thought
process readers can learn from.

- Present each option fairly (not just the winner)
- Use a comparison table from the knowledge entry
- Briefly note why each was or wasn't suitable

### 4. The Solution (main body)

The approach you chose, with code examples and explanations.

- Lead with a clear statement of the approach
- Show code in digestible chunks (not one giant block)
- Explain each code block — what it does and why
- Call out gotchas or non-obvious details

### 5. Why This Works (1-2 paragraphs)

Connect back to the problem. Explain the mechanism, not just the result.

- "This works because..." (causal explanation)
- Performance/reliability/DX improvements observed
- Link to official docs for deeper reading

### 6. Practical Takeaway (closing)

Help the reader apply this to their own work.

- When to use this approach (from knowledge entry)
- When NOT to use it (from knowledge entry)
- Key gotchas or common mistakes
- One-sentence summary they can remember

## Style Rules

### Voice and Tone

- **Active voice, direct sentences** — "Redis caches the result" not "The result
  is cached by Redis"
- **Conversational but precise** — share like you are talking to a peer
- **First person is fine** — "I found that..." / "We decided to..."
- **Sharing, not lecturing** — "here is what I found" not "you should always"
- **No hedge words** — avoid "basically", "simply", "just", "actually"
- **No fabricated experiences** — if the 3B source does not describe a specific
  struggle, do not invent one. State the problem directly.

### Structure and Scannability

- **One topic per post** — narrow scope, depth over breadth
- **Short paragraphs** — 2-4 sentences maximum
- **Clear subheadings** — reader should understand the post from headings alone
- **Visual every 500-800 words** — Mermaid diagrams, comparison tables, or code
  blocks break up prose
- **Code examples always present** — no purely theoretical posts

### Technical Accuracy

- **Every claim backed by a reference** — link to official docs
- **Code must be runnable** — no pseudocode without flagging it
- **Explain jargon on first use** — don't assume the reader knows every term
- **Version-specific details noted** — "as of Redis 7.x" / "Node.js 20+"

## What the Expansion Step Does

The expansion is NOT a copy. It transforms the knowledge entry:

| Knowledge Entry (Source)     | Blog Post (Expanded)                  |
| ---------------------------- | ------------------------------------- |
| Terse bullet points          | Explained paragraphs with transitions |
| No introduction              | Hook stating the problem directly     |
| Reference-style tone         | Sharing-with-peers tone               |
| No conclusion                | Practical takeaway section            |
| Sections as standalone units | Narrative flow with transitions       |
| Implied context              | Explicit context for cold readers     |

### Specific Transformations

1. **Add narrative transitions** — "Now that we understand the problem, let's
   look at what options exist..." between sections
2. **Write an engaging intro** — rewrite the Problem section as a hook
3. **Expand Key Points** — each bullet becomes 1-2 explained sentences
4. **Add a conclusion** — summarize the takeaway (knowledge entries don't have
   this)
5. **Adjust tone** — from "reference notes" to "I'm sharing what I found"
6. **Preserve all code examples** — keep them intact, add surrounding
   explanation if terse
7. **Keep all references** — move to a References section at the bottom

## Expansion Checklist

Before finishing the expanded post:

- [ ] Hook states the problem directly (no fabricated experiences)
- [ ] All first-person claims are factually accurate to the 3B source
- [ ] Every section flows into the next (no abrupt jumps)
- [ ] Code examples have surrounding explanation
- [ ] Jargon is explained on first use
- [ ] Post has a clear takeaway the reader can act on
- [ ] All references from the knowledge entry are preserved
- [ ] Visual element exists (table, diagram, or code block) every 500-800 words
- [ ] Post reads naturally when read aloud
