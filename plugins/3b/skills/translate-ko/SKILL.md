---
name: translate-ko
description: >-
  Translate English content to natural Korean. Supports blog posts, PR
  descriptions, documentation, READMEs, and general text. Uses voice calibration
  from writing examples and a 4-step workflow (Analyze, Translate, Rewrite, QA).
  Use when user says "translate to Korean", "Korean translation", "translate
  this", "ko version", or "한국어로".
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion]
metadata:
  version: "1.0.0"
---

# /translate-ko

Translate English content to natural Korean that reads as if originally written
by a Korean developer.

## Reference Files

Load during execution:

| File                                                      | Use During | Contains                                      |
| --------------------------------------------------------- | ---------- | --------------------------------------------- |
| [translation-guide.md](./references/translation-guide.md) | All steps  | Korean translation rules, tone, anti-patterns |
| `~/dev/personal/3b/personal/writing-examples/*.md`        | Step 2     | Brandon's Korean voice samples (calibration)  |

## Execution Steps

### Step 1: Determine Context

Ask the user (or infer from the file) what context this translation is for:

| Context | Register         | Typical Output                       |
| ------- | ---------------- | ------------------------------------ |
| blog    | 해요체 (default) | Blog post for the maintainer's blog ({blog_domain}) |
| docs    | 하십시오체       | README, documentation, formal guides |
| pr      | 한다체           | PR description, commit message       |
| general | 해요체           | Any other content                    |

If the source is a blog post file (in `src/content/posts/en/`), default to
`blog`. Otherwise ask.

### Step 2: Voice Calibration

**Read [references/translation-guide.md](./references/translation-guide.md)
before starting.**

1. Read all files in `~/dev/personal/3b/personal/writing-examples/` (most recent
   first)
2. Absorb Brandon's natural Korean writing patterns:
   - Vocabulary choices and English-Korean mixing style
   - Sentence structure and connective patterns
   - Level of directness and technical terminology usage
3. Note: Writing examples use 한다체. Convert endings to match the target
   register from Step 1.

### Step 3: Identify Source

Determine what to translate:

- **File path provided** → read the file
- **No path** → ask the user for the source file or text

Identify the output path:

- **Blog context** → `src/content/posts/ko/{category}/{slug}.md`
- **Other contexts** → ask user, or default to `{source-dir}/{slug}.ko.md`

### Step 4: Translate (4-Step Workflow)

Follow the workflow from
[translation-guide.md](./references/translation-guide.md):

#### Step A — Input Analysis

1. Confirm register from Step 1
2. Extract proper nouns and technical terms → build glossary
   - Never transliterate technical jargon into Korean (e.g., query not 쿼리,
     runtime not 런타임, codebase not 코드베이스) — see translation guide for
     full list
3. Note the source structure (sections, code blocks, tables)

#### Step B — First Pass (Meaning Transfer)

Translate paragraph by paragraph, focusing on meaning:

- Do NOT copy English sentence structure 1:1
- Restructure for Korean word order (SOV, modifiers before nouns)
- Break long English sentences into shorter Korean ones
- Omit pronouns where context makes the subject clear

#### Step C — Second Pass (Korean Optimization)

Rewrite for natural Korean:

- Remove nominalizations ("설정 변경을 수행" → "설정을 바꾸면")
- Convert passive to active ("사용되어집니다" → "사용해요")
- Apply weed-cutting — remove filler words
- Check paragraph length (2-4 sentences)

#### Step D — QA Pass

- Same term = same Korean expression throughout
- Punctuation rules followed
- No "당신" or direct "you" translations
- Read aloud — does it sound like a Korean developer wrote this?
- Register consistency (no mixing 합니다/해요/한다 endings)

### Step 5: Write Output

1. Write the translated file to the output path
2. Show a summary of what was translated and where

**Blog context extras:**

- Update frontmatter: remove `[번역 필요]` from title, set `draft: false`, set
  `translation_date` to today
- Use the Korean frontmatter template from translation-guide.md

### Step 6: Report

Show summary:

```text
✅ Translated:
  - {source} → {output} ({register})
  - Terms kept in English: {list}
  - Word count: {en_count} → {ko_count}
```

## Context-Specific Rules

### Blog Posts

- Register: 해요체
- Frontmatter: use Korean frontmatter template from translation-guide.md
- Remove `[번역 필요]` from title
- Set `draft: false` and `translation_date`

### PR Descriptions

- Register: 한다체
- Keep section headers in English (## Summary, ## Test Plan)
- Translate body content only
- Preserve markdown formatting and links

### Documentation

- Register: 하십시오체
- Keep code examples untranslated
- Translate comments within code blocks
- Preserve all links and references

### General

- Register: 해요체
- Follow translation guide defaults
