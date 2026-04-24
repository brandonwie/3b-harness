---
name: research-paper
description: >-
  Intake, analyze, and process research papers (PDF or arXiv URL) into the 3B
  knowledge system. Extracts academic metadata, generates structured analysis,
  identifies 3B/Claude applicability, creates knowledge entries, and drafts blog
  + LinkedIn posts. Maintains a searchable paper library index. Use when user
  says "research paper", "analyze paper", "read this paper", "paper review",
  shares an arXiv link/PDF path, or wants to process a research paper.
allowed-tools:
  [Read, Write, Edit, Bash, Grep, Glob, WebFetch, Agent, AskUserQuestion]
metadata:
  version: "1.0.0"
---

# /research-paper

Intake, analyze, and index research papers into the 3B personal research
library. Full pipeline from paper discovery to knowledge extraction and content
publishing.

## Reference Files

Load during execution when the relevant step requires detailed reference:

| File                                                          | Use During | Contains                              |
| ------------------------------------------------------------- | ---------- | ------------------------------------- |
| [paper-blog-guide.md](./references/paper-blog-guide.md)       | Step 6     | Paper-specific blog expansion rules   |
| [linkedin-post-guide.md](./references/linkedin-post-guide.md) | Step 7     | LinkedIn post format, hooks, hashtags |

## Paths

```text
3B_PATH       = ${FORGE_3B_ROOT}
RESEARCH_PATH = {3B_PATH}/personal/research
PAPERS_PATH   = {RESEARCH_PATH}/papers
PDFS_PATH     = {RESEARCH_PATH}/pdfs       # gitignored — local PDF copies
INDEX_PATH    = {RESEARCH_PATH}/_index.md
TEMPLATE_PATH = {3B_PATH}/resources/templates/paper-analysis.md
TMP_PATH      = {3B_PATH}/tmp
INTAKE_PATH   = {TMP_PATH}/intake          # universal drop folder — all skills check here
```

## Execution Steps

### Step 0: Inventory and Classify Inputs

The user may provide ANY combination of materials. Do NOT assume a single clean
input. First, inventory everything provided, then classify and validate.

**0a. Check `tmp/intake/` for pre-staged files:**

```bash
ls {INTAKE_PATH}/
```

If files exist, add them to the inventory alongside anything in the user's
message. This is the universal drop folder — users stage files here before
invoking any skill.

**0b. Scan all inputs from the user's message + intake/:**

| Material Type    | Detection                                                                    | Role                  |
| ---------------- | ---------------------------------------------------------------------------- | --------------------- |
| arXiv URL        | `arxiv.org/abs/` or `arxiv.org/pdf/`                                         | Primary paper source  |
| Other paper URL  | `openreview.net`, `doi.org`, `ieee.org`, `dl.acm.org`, `semanticscholar.org` | Primary paper source  |
| Blog/article URL | Medium, blog, news site, personal site                                       | Supplementary context |
| Social post      | X/Twitter, LinkedIn post text or URL                                         | Discovery context     |
| Local PDF        | File path ending in `.pdf`                                                   | Primary paper source  |
| Local markdown   | File path ending in `.md`                                                    | Supplementary context |
| Pasted text      | Inline text about the paper                                                  | Supplementary context |
| No args          | Nothing provided                                                             | List mode             |

**0c. Classify each material into a role:**

- **Primary source**: The actual paper (URL or PDF). There should be exactly 1.
- **Supplementary context**: Blog posts, social posts, someone's notes, markdown
  summaries. There can be 0 or many.
- **Discovery context**: How/where the user found it. Captured in frontmatter.

**0d. Validate and clarify (CRITICAL):**

Present the inventory to the user and ask what's missing:

```text
Materials received:
  - [Primary] arXiv:2603.20639 (paper URL)
  - [Context] Tweet thread from @researcher (discovery context)
  - [Context] summary-notes.md (supplementary analysis)

Questions:
  1. Is this everything, or do you have additional materials?
  2. {Any specific gaps — e.g., "I can't access the PDF from this
     IEEE link. Do you have a local copy?"}

Ready to proceed?
```

**Clarification triggers** — ask the user when:

| Situation                              | What to Ask                                                                                          |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| URL is a blog post, not a paper        | "This looks like a blog post about a paper. Want me to find the original paper link?"                |
| URL is paywalled (IEEE, ACM, Springer) | "This is behind a paywall. Do you have a local PDF, or should I work from the abstract only?"        |
| Only context given, no paper source    | "I see context/notes but no paper link or PDF. Can you share the paper source?"                      |
| PDF has no clear metadata              | "I couldn't extract title/authors from this PDF. Can you provide them?"                              |
| Multiple paper URLs given              | "I see multiple paper links. Which one should I analyze? (Others can be added to the reading queue)" |

If the user says "that's all" or confirms, proceed. If they add more materials,
re-inventory.

**0e. List mode (no args):**

1. Read `{INDEX_PATH}`
2. Show: total papers, papers by status, recent additions, reading queue
3. Ask user what they want to do (add new paper, update existing, browse)
4. Stop here unless user provides a paper to process

### Step 1: Acquire Paper and Extract Metadata

Based on the primary source identified in Step 0:

**1a. Acquire the paper content:**

| Source Type                   | Acquisition                                                                                  |
| ----------------------------- | -------------------------------------------------------------------------------------------- |
| arXiv URL                     | WebFetch abstract page + `curl` PDF to `{PDFS_PATH}/{author}-{year}-{original_filename}`     |
| Other paper URL (open access) | WebFetch the page, find PDF link, download to `{PDFS_PATH}/`                                 |
| Other paper URL (paywalled)   | WebFetch for abstract/metadata only. Note: **abstract-only mode** — analysis will be limited |
| Local PDF                     | Copy to `{PDFS_PATH}/{author}-{year}-{original_filename}`                                    |

**1b. Extract metadata:**

For arXiv: title, authors, abstract, date, categories, venue from comments. For
other URLs: title, authors, abstract, DOI, venue from the page. For local PDFs:
Read first 3 pages — extract title, authors, abstract. Search for arXiv ID, DOI,
or conference venue in the text.

**1c. Classify paper type:**

| Type                 | Signal                                                | Template Adaptation                                                |
| -------------------- | ----------------------------------------------------- | ------------------------------------------------------------------ |
| Empirical            | Has experiments, benchmarks, metrics tables           | Full template (default)                                            |
| Position/Perspective | No experiments, argues a thesis, proposes frameworks  | Skip Results table, expand Approach as "Argument Structure"        |
| Survey/Review        | Reviews existing literature, compares many approaches | Replace Approach/Results with "Taxonomy" and "Comparison" sections |
| Technical Report     | Implementation details, system description            | Focus on architecture and practical details                        |

Inform the user of the detected type. They can override.

**1d. Generate slug and dedup check:**

1. Generate `paper_slug`: `{first-author-lastname}-{year}-{kebab-title-slug}`
   - Slug from title: 2-4 most distinctive words in kebab-case
   - Example: `rafailov-2023-direct-preference-optimization`
2. **Dedup check**: `ls {PAPERS_PATH}/` — check if a file with matching
   author+year already exists
   - If match found: inform user, offer to update the existing analysis
   - If no match: proceed to Step 2

**1e. Process supplementary materials:**

For each supplementary context from Step 0:

- Blog posts/articles: WebFetch, extract key insights and perspectives
- Markdown files: Read, note any analysis or opinions
- Social posts: Capture recommender, key quote, and angle

Store these as structured notes for use in Step 3 (applicability) and Step 4
(Critical Reading Notes). Supplementary context often contains WHY the paper
matters — perspectives the paper itself doesn't state.

### Step 2: Read and Comprehend

**Full-access mode (PDF available):**

Multi-pass reading strategy:

| Pass          | Pages                  | Purpose                                                       |
| ------------- | ---------------------- | ------------------------------------------------------------- |
| 1 — Structure | First 5 + last 3       | Abstract, intro, related work, conclusion. Build section map. |
| 2 — Core      | Methodology + Results  | Key approach, experiments, numbers.                           |
| 3 — Details   | Appendices (if needed) | Supplementary material, proofs, extra results.                |

**Abstract-only mode (no PDF — paywall, missing, etc.):**

Work from: abstract + any supplementary context from Step 0. Analysis will be
limited. Set `confidence: low` in frontmatter. Add to reading queue for full
analysis when PDF becomes available.

**After reading, internally note:**

- Core contribution (1-2 sentences)
- Problem being solved
- Methodology/approach summary
- Key results and claims (if empirical)
- Argument structure (if position/perspective)
- Limitations acknowledged by authors
- Novel techniques or concepts introduced
- How supplementary context (Step 0) adds to or challenges the paper

### Step 3: Draft Analysis — USER CONTRIBUTION (applicability)

1. Read the paper analysis template: `{TEMPLATE_PATH}`
2. Draft the analysis (TL;DR through Results sections) based on Step 2 notes
3. Present the draft analysis to the user via `AskUserQuestion`:

```text
Paper: {title}
Authors: {authors}
Core Contribution: {1-2 sentences}

Key Findings:
  1. {finding}
  2. {finding}
  3. {finding}

Initial 3B Applicability Assessment:
  - {suggested applicability 1}
  - {suggested applicability 2}

Please provide:
1. How does this apply to your projects/goals? (5-10 lines)
   - Which projects could use these ideas?
   - What would you try first?
   - Connections to papers/concepts you've seen before?
2. Relevance rating: high | medium | low
3. Priority: implement-soon | reference-only | foundational | read-later
4. Any corrections to the analysis above?
```

1. Wait for user response before proceeding

### Step 4: Create Paper Analysis File

1. Read `{TEMPLATE_PATH}` for the full template structure
2. Populate all sections:
   - Frontmatter: paper metadata, discovery context, user's applicability
     assessment, references, blog metadata
   - Body: TL;DR, Problem, Approach, Results, 3B Applicability (from user),
     Critical Reading Notes
3. Write to `{PAPERS_PATH}/{paper_slug}.md`
4. Set `status: analyzed` in frontmatter

**Frontmatter checklist:**

- [ ] `tags:` includes `paper` + topic tags
- [ ] `paper:` block has all metadata fields
- [ ] `discovery:` block has date, source, context
- [ ] `applicability:` block has user's rating and priority
- [ ] `references:` includes the paper URL as `authoritative`
- [ ] `blog.publishable: true` (default for paper analyses)
- [ ] `created:` and `updated:` set to today

### Step 5: Knowledge Extraction — USER DECIDES (Claude analyzes)

**Claude does the analysis. User makes the decision.**

1. Identify ALL candidate concepts from the paper. For each, apply the
   extraction threshold (from `/wrap` criteria):

   | #   | Criterion           | Checks                                           |
   | --- | ------------------- | ------------------------------------------------ |
   | 1   | **Surprise**        | Did this challenge an assumption?                |
   | 2   | **Recurrence**      | Will this come up again in future work?          |
   | 3   | **Gotcha**          | Could someone waste time without this knowledge? |
   | 4   | **Transferability** | Applies beyond this paper?                       |
   | 5   | **Decision**        | Non-trivial choice made between alternatives?    |

2. **Analyze and present with verdicts** — Claude evaluates each candidate and
   provides a clear recommendation with reasoning:

```text
Knowledge Extraction Analysis for "{title}":

  # | Concept | Category | Threshold | Verdict | Reasoning
  1 | {name}  | {cat}    | 3/5       | EXTRACT | {why it stands alone}
  2 | {name}  | {cat}    | 2/5       | SKIP    | {why not worth it}
  3 | {name}  | {cat}    | 3/5       | SKIP    | {despite score, too coupled to paper}

  Recommendation: {Extract #1 only / Skip all / etc.}
  Reasoning: {1-2 sentences explaining the overall verdict}

  Options: [Accept recommendation] [Override: e.g., also extract #2] [Skip all]
```

**Key rules:**

- Claude MUST provide a clear verdict per candidate, not just list them
- "SKIP — too coupled to this paper" is a valid reason even if threshold is met
- "Reference for {project}" is a valid alternative to extraction
- User picks from Claude's analysis — they don't fill in blanks

1. For each approved concept:
   - Create `knowledge/{category}/{topic}.md` using the knowledge-entry template
   - Set `source: personal-research` in frontmatter
   - Add `related:` link back to the paper analysis file
   - Add `references:` with the paper URL as `authoritative`
   - Set `blog.publishable: true` if the concept is transferable
2. Update the paper analysis `related:` frontmatter to link to created entries
3. Update paper status to `extracted` if any entries were created

### Step 6: Blog Post Draft (optional) — USER CONTRIBUTION (angle)

**Read `references/paper-blog-guide.md` before this step.**

Ask the user:

```text
Blog Post for "{title}":

Want to create a blog post from this paper?

If yes, I need:
1. Hook: Why should your readers care? (2-3 sentences)
2. Your angle: What's unique about YOUR take on this?
   (e.g., "I tried this in my RAG pipeline" or "This changes how I think about X")
3. Target audience: AI engineers | backend devs | general tech
4. Tone: practical-guide | analysis | opinion-piece

Options: [Write blog] [Skip — maybe later]
```

If user wants a blog post:

1. Generate draft following the paper blog structure from the reference guide
2. Write to `{TMP_PATH}/blog-draft-{paper_slug}.md`
3. Tell user: "Draft saved to tmp/. When ready, use /blog-publish to go live."
4. Update paper status to `published` (or keep `extracted` if skipped)

### Step 7: LinkedIn Post Draft (optional) — USER CONTRIBUTION (context line)

**Read `references/linkedin-post-guide.md` before this step.**

**Purpose:** LinkedIn posts are professional signals for recruiters and hiring
managers — compact, objective, informative. NOT content marketing or personal
blog. The post should show "this person reads research and thinks clearly."

Ask the user:

```text
LinkedIn Post for "{title}":

Want to share this on LinkedIn? (compact professional post, not a blog)

If yes, I need:
1. One line of professional context connecting this to your work area
   (e.g., "Relevant to multi-agent orchestration systems I work with")
2. Which single finding is most interesting to highlight?

Options: [Write LinkedIn post] [Skip]
```

If user wants a LinkedIn post:

1. Generate post following the structure from the reference guide:
   - Line 1: What the paper found (factual, specific)
   - Core: Why it matters practically (3-5 lines, no editorializing)
   - Close: Paper link + optional context line
   - 2-3 hashtags max (domain-relevant only)
2. English only, objective/informative tone
3. Target 100-200 words (under 200 is critical)
4. No emojis, no engagement bait, no "I just read..."
5. Write to `{TMP_PATH}/linkedin-draft-{paper_slug}.md`
6. Tell user: "Draft saved to tmp/. Copy to LinkedIn when ready."

**After posting:** When user confirms the post is live:

- Update paper analysis frontmatter: `linkedin.posted: YYYY-MM-DD`,
  `linkedin.hook: "{one-line angle}"`
- Delete draft from `{TMP_PATH}/` (served its purpose, post lives on LinkedIn)
- Draft is NOT a permanent artifact — the paper analysis records the fact

### Step 8: Update Library Index

1. Read `{INDEX_PATH}`
2. Determine the paper's topic area (from arXiv categories or content)
3. Add the paper to the appropriate "By Topic" section:
   - If topic section exists: add row to the table
   - If new topic: create a new H3 section
4. Add to "Recent Additions" table
5. Update "Quick Stats" counts
6. Write the updated index

### Step 9: Report

```text
Research Paper Processed
========================

Paper: {title}
Authors: {authors}
Source: {arxiv_url or pdf_path}

Created:
  ✓ Paper analysis: personal/research/papers/{slug}.md
  {✓ or ·} Knowledge entries: {list or "skipped"}
  {✓ or ·} Blog draft: tmp/blog-draft-{slug}.md {or "skipped"}
  {✓ or ·} LinkedIn draft: tmp/linkedin-draft-{slug}.md {or "skipped"}

Updated:
  ✓ Paper library index: personal/research/_index.md

Library: {N} papers across {M} topic areas.

Next steps:
  {- Review blog draft, then /blog-publish when ready}
  {- Copy LinkedIn draft to LinkedIn}
  {- Related papers to read: {suggestions based on citations}}
```

## Failure Modes

| Symptom                              | Cause                                     | Fix                                                                                                           |
| ------------------------------------ | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| PDF read fails                       | Paper > 20 pages per chunk                | Use multi-pass: pages 1-20, then 21-40                                                                        |
| arXiv fetch fails                    | Rate limiting or URL format               | Try arxiv.org/abs/ format, wait and retry                                                                     |
| Duplicate detected                   | Paper already in library                  | Offer to update existing analysis                                                                             |
| No extraction candidates             | Paper is too specialized                  | Skip Step 5 — not every paper yields knowledge                                                                |
| Blog draft feels generic             | Missing user's angle                      | Step 6 requires user hook — don't auto-generate                                                               |
| URL is a blog, not a paper           | User shared commentary not the source     | Ask: "This is a blog post about a paper. Want me to find the original?"                                       |
| Paper is paywalled                   | IEEE, ACM, Springer without open access   | Ask for local PDF. If unavailable, proceed in abstract-only mode (`access: abstract-only`, `confidence: low`) |
| No primary source found              | User gave only context files or notes     | Ask: "I see context but no paper source. Can you share the paper link or PDF?"                                |
| Can't extract metadata from PDF      | Scanned PDF or unusual formatting         | Ask user for title, authors, year manually                                                                    |
| Mixed inputs unclear                 | Multiple URLs, unclear which is the paper | Present inventory from Step 0d, ask user to confirm roles                                                     |
| Position paper with Results template | Wrong paper type detected                 | User can override type in Step 1c. Template adapts sections accordingly                                       |
