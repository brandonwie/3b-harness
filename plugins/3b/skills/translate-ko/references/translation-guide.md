# Korean Translation Guide — Toss.tech Style

Comprehensive spec for translating English blog posts to Korean for the
maintainer's blog ({blog_domain}). Adapted from Toss.tech writing principles
with authoritative references from technical writing guides.

## Goal

Transform English tech blog posts into **natural Korean tech writing** — not
literal translation, but content that reads as if originally written in Korean
by a Korean developer for Korean developers.

## Register Decision

| Register             | When to Use                         | Sentence Endings        |
| -------------------- | ----------------------------------- | ----------------------- |
| **해요체 (default)** | Blog posts, tutorials, team culture | …해요, …했어요, …있어요 |
| **하십시오체**       | Policies, manuals, formal docs      | …합니다, …하십시오      |

**Default for {blog_domain}: 해요체.** All blog translations use this register
unless explicitly overridden.

### Ending Patterns

- **Declarative:** …해요 / …했어요 / …있어요
- **Soft agreement:** …죠 (shares context with reader: "…이죠")
- **Question hook:** …없을까? / …어떨까요? (narrative pivot, draws reader in)

**CRITICAL:** Maintain consistent endings throughout the entire post. Mixing
해요체 and 하십시오체 within one post is the most common quality issue.

---

## 4-Step Translation Workflow

### Step A — Input Analysis

1. Determine purpose/audience/medium → confirms 해요체 for blog
2. Extract proper nouns and technical terms → build glossary draft
3. Note the post's structure (sections, code blocks, tables)

### Step B — First Pass (Meaning Transfer)

Translate paragraph by paragraph, focusing on meaning:

- **MUST NOT** copy English sentence structure 1:1
- Restructure for Korean word order (SOV, modifiers before nouns)
- Break long English sentences into shorter Korean ones
- Omit pronouns where context makes the subject clear

### Step C — Second Pass (Korean Optimization)

Rewrite for natural Korean:

- Remove nominalizations ("설정 변경을 수행" → "설정을 바꾸면")
- Convert passive to active ("사용되어집니다" → "사용해요")
- Apply weed-cutting — remove filler words that add no meaning
- Check that each paragraph is 2-4 sentences (scan-optimized)

### Step D — QA Pass (Consistency Check)

- Same term = same Korean expression throughout the post
- Punctuation rules followed (see Section 4)
- No "당신" or direct "you" translations remaining
- Read aloud — does it sound like a Korean developer wrote this?

---

## Sentence-Level Rules

### 1. Active Voice + Clear Subject

Technical writing should clarify who does what. Avoid making tools the subject
when the reader (developer) is the actor.

```markdown
<!-- BAD (passive/tool-as-subject) -->

설정이 변경되어야 합니다.

<!-- GOOD (active/reader-as-subject) -->

설정을 바꾸면 돼요.
```

### 2. Remove Nominalizations (번역체 제거)

English `-tion/-ment` nouns become awkward in Korean. Use verbs instead.

```markdown
<!-- BAD (nominalized) -->

설정 변경을 수행한 후 적용을 진행합니다.

<!-- GOOD (verbal) -->

설정을 바꾼 뒤 적용하면 돼요.
```

### 3. Minimize Pronouns

Korean omits subjects when context is clear. Never translate "you" as "당신".

```markdown
<!-- BAD -->

당신은 이 패턴을 사용할 수 있습니다.

<!-- GOOD -->

이 패턴을 사용하면 돼요.
```

### 4. Terminology Consistency (Glossary-First)

Before translating, extract all technical terms and decide how to render each.
Use the same rendering throughout the entire post.

**Terms to keep in English (never transliterate):**

- Framework/tool names: Redis, Docker, AWS, Kubernetes, React, Node.js
- Patterns: cache-aside, write-through, pub/sub, middleware
- Concepts: API, REST, GraphQL, WebSocket, JWT, OAuth
- Data: JSON, YAML, SQL, NoSQL, schema
- Ops: CI/CD, deploy, rollback, scaling

**Never transliterate technical jargon into Korean (CRITICAL):**

Technical English words that have become standard developer vocabulary must stay
in English. Korean transliteration (한글 음차) makes text harder to read and
sounds unnatural to Korean developers.

| BAD (transliterated) | GOOD (English) | Why                          |
| -------------------- | -------------- | ---------------------------- |
| 쿼리                 | query          | Standard DB/API term         |
| 런타임               | runtime        | Standard CS term             |
| 코드베이스           | codebase       | Standard dev term            |
| 리뷰                 | review         | Standard workflow term       |
| 컨텍스트             | context        | Standard CS term             |
| 파일                 | file           | Universal computing term     |
| 크로스               | cross          | As in cross-referencing      |
| 리팩토링             | refactoring    | Standard dev practice        |
| 디버깅               | debugging      | Standard dev practice        |
| 테스트               | test           | Standard dev term            |
| 캐시                 | cache          | Standard infrastructure term |
| 빌드                 | build          | Standard dev/CI term         |
| 프레임워크           | framework      | Standard dev term            |
| 템플릿               | template       | Standard dev term            |
| 커밋                 | commit         | Standard git term            |
| 브랜치               | branch         | Standard git term            |
| 머지                 | merge          | Standard git term            |
| 배포                 | deploy         | Standard ops term            |
| 클러스터             | cluster        | Standard infrastructure term |

**Rule of thumb:** If a Korean developer would say the English word in
conversation (not the Korean transliteration), keep it in English.

**Sensitive term substitutions (CRITICAL):**

Some English technical terms have Korean literal translations that carry
unintended emotional weight. Always use the technical alternative:

| English Term | BAD (literal) | GOOD (technical) | Why                                                       |
| ------------ | ------------- | ---------------- | --------------------------------------------------------- |
| orphaned     | 고아 / 고아된 | 참조가 끊긴      | '고아' means parentless child — deeply negative in Korean |

Example: "orphaned records" → "참조가 끊긴 레코드" (not "고아 레코드")

**First-mention convention:** Korean(English) or English alone — be consistent
within one post.

---

## Punctuation and Formatting Rules

### Colons and Semicolons

Korean rarely uses semicolons. Replace with sentence splits or connectors.

```markdown
<!-- English -->

There are two options: Redis and Memcached.

<!-- BAD -->

두 가지 옵션이 있습니다: Redis와 Memcached.

<!-- GOOD -->

두 가지 옵션이 있어요. Redis와 Memcached예요.
```

### Periods

- Sentences ending with a verb/adjective → add period
- Labels or phrases (not full sentences) → omit period

### Hyphens

English compound-word hyphens → remove or use natural Korean spacing.

### Parentheses

No space before opening parenthesis in Korean.

```markdown
<!-- BAD -->

Redis (인메모리 저장소)

<!-- GOOD -->

Redis(인메모리 저장소)
```

### Placeholders and Variables

Never translate `%s`, `${VAR}`, HTML entities, or code variables. Preserve their
position relative to surrounding text.

---

## Document Structure Rules

### Scan-Optimized Layout

Readers scan, not read. Structure for scanning:

- Short paragraphs (2-4 sentences max)
- Key conclusion → evidence → example (inverted pyramid per section)
- Clear subheadings that summarize each section

### Weed-Cutting (잡초 제거)

Remove words that add no meaning:

```markdown
<!-- BAD (filler) -->

기본적으로 이 패턴을 사용하면 실제로 성능이 향상됩니다.

<!-- GOOD (clean) -->

이 패턴을 쓰면 성능이 좋아져요.
```

### No Redundancy

Don't repeat the same point in different words within the same section. Say it
once, clearly.

---

## Translation Examples

### Natural Flow

```markdown
<!-- English -->

If you're using Redis, you should know this pattern.

<!-- BAD (word-for-word) -->

만약 당신이 Redis를 사용한다면, 당신은 이 패턴을 알아야 합니다.

<!-- GOOD (natural Korean) -->

Redis 쓴다면 이 패턴은 꼭 알아야 해요.
```

### Conversational Tone

```markdown
<!-- BAD (formal/stiff) -->

이 패턴을 사용하면 성능이 향상될 것입니다.

<!-- GOOD (conversational) -->

이 패턴 쓰면 성능이 확 좋아져요.
```

### Concise Expression

```markdown
<!-- BAD (robotic) -->

Redis는 인메모리 데이터 저장소입니다. 이것은 매우 빠릅니다.

<!-- GOOD (natural) -->

Redis는 메모리 기반 저장소라서 엄청 빠릅니다.
```

### Blog-Appropriate Opening

```markdown
<!-- BAD (too formal) -->

본 문서에서는 Redis 캐싱 패턴에 대하여 설명하고자 합니다.

<!-- GOOD (blog-appropriate) -->

이번 글에서는 Redis 캐싱 패턴을 알아볼게요.
```

---

## Anti-Patterns and Corrections

| Anti-Pattern                             | Correction                        | Why                            |
| ---------------------------------------- | --------------------------------- | ------------------------------ |
| "~의 수행/진행을 실시합니다"             | "~합니다" or "~해서 ~해요"        | Nominalization removal         |
| "~되어집니다/~해집니다"                  | "~됩니다" or "~해요"              | Unnecessary passive layering   |
| "당신은 ~할 수 있습니다"                 | "~할 수 있어요" or "~하면 돼요"   | Pronoun minimization           |
| "A; B; C"                                | "A. 그리고 B. 또한 C."            | Semicolon avoidance            |
| "만약 ~한다면"                           | "~하면" or "~한다면"              | Drop redundant "만약"          |
| Passive voice overuse ("사용되어집니다") | "사용해요"                        | Active voice preference        |
| Awkward particles ("Redis을")            | "Redis를"                         | Correct particle after English |
| Inconsistent formality (합니다/해요 mix) | Pick one register for entire post | Tone consistency               |
| Transliterated jargon (쿼리, 런타임)     | Use English (query, runtime)      | No 한글 음차 for tech terms    |

---

## Voice Calibration (Writing Examples)

Before translating, read Brandon's Korean writing samples from
`~/dev/personal/3b/personal/writing-examples/` (most recent first). These
capture his natural professional Korean voice.

### Register Difference

| Source            | Register | Sentence Endings        | Used For                   |
| ----------------- | -------- | ----------------------- | -------------------------- |
| Writing examples  | 한다체   | …한다, …이다, …판단한다 | PR reviews, internal notes |
| Blog translations | 해요체   | …해요, …있어요, …돼요   | Public blog posts          |

### What to Extract

- **Vocabulary choices** — which English terms Brandon keeps vs translates
- **Sentence patterns** — how he structures compound sentences
- **English-Korean mixing** — where he code-switches naturally (e.g., "sync를
  받을 필요가 없다", "tolerable 한 gap")
- **Connectives** — transitional words and phrases (따라서, 다만, 즉)

### What NOT to Extract

- **Sentence endings** — 한다체 endings must be converted to 해요체
- **Formality level** — writing examples are more formal (work context)

### Calibration Example

**From writing example (한다체):**

> 즉각적인 업데이트에는 약간 영향이 있을 수 있겠지만, 충분히 tolerable 한 gap
> 이라고 판단한다.

**Blog adaptation (해요체, same voice):**

> 즉각적인 업데이트에 약간 영향이 있을 수 있지만, 충분히 tolerable한 gap이에요.

Notice: vocabulary ("즉각적인", "tolerable한 gap"), sentence structure, and
English mixing are preserved. Only the ending changed (판단한다 → 이에요).

---

## AI Agent Spec (Machine-Readable)

Embed in system context for automated translation:

```yaml
name: en_to_ko_blog_translation_guide
version: 1.0
default_style:
  register: haeyo-che # 해요체
  tone: concise, friendly, technical
  target: Korean developers
hard_rules:
  - avoid_literal_structure: true
  - prefer_active_voice: true
  - minimize_pronouns: true
  - remove_nominalizations: true
  - enforce_terminology_consistency: true
  - voice_calibration_from_writing_examples: true
punctuation_rules:
  - replace_semicolon: "split_or_connector"
  - colon_at_sentence_end: "period"
  - no_space_before_parenthesis: true
  - period_when_sentence_final: true
glossary_policy:
  - first_mention: >-
      Korean(English) or English(Korean) but be consistent within one post
  - follow_official_names: true
qa_checklist:
  - scanability: "short paragraphs, clear headings"
  - weed_cutting: "remove filler"
  - placeholders_intact: true
  - register_consistent: true
  - no_pronoun_you: true
voice_calibration:
  source: "~/dev/personal/3b/personal/writing-examples/"
  register_note: "Examples use 한다체; convert endings to 해요체"
  extract: ["vocabulary", "sentence_patterns", "english_mixing", "connectives"]
  ignore: ["sentence_endings", "formality_level"]
```

---

## Korean Frontmatter Template

```yaml
---
title: "한국어 제목"
description: "한국어 설명"
date: "YYYY-MM-DD" # Same as English original
updated: "YYYY-MM-DD"
tags: [tag1, tag2] # Can be Korean or English
category: backend
draft: false
lang: ko
source_lang: en
source_slug: original-english-slug
source_updated: "YYYY-MM-DD"
translation_date: "YYYY-MM-DD" # Today's date
---
```

---

## Quality Checklist

Before publishing a translation:

- [ ] Register is consistent (해요체 throughout, no 합니다 mix)
- [ ] Read aloud — does it sound like a Korean developer wrote it?
- [ ] Technical accuracy preserved (code, numbers, concepts)
- [ ] Code comments translated (if any)
- [ ] Links still work
- [ ] Frontmatter complete with translation metadata
- [ ] No English phrases that should be translated
- [ ] No Korean phrases that sound machine-translated
- [ ] No "당신" or direct "you" translations remaining
- [ ] Nominalizations removed (no "수행/진행/실시" patterns)
- [ ] Passive voice minimized (no "되어집니다" patterns)
- [ ] Terminology consistent (same term = same Korean throughout)
- [ ] Paragraphs are 2-4 sentences (scan-optimized)
- [ ] Filler words removed (잡초 제거 applied)
- [ ] `[번역 필요]` removed from title
- [ ] `draft: false` set

---

## References

1. [토스의 8가지 라이팅 원칙들](https://toss.tech/article/8-writing-principles-of-toss)
   — Weed-cutting, scan optimization, writing principles
2. [가이드라인을 시스템으로 만드는 법](https://toss.tech/article/introducing-toss-error-message-system)
   — Error message system, 해요체 application, question hooks
3. [KDE Localization/ko/styleguide](https://community.kde.org/KDE_Localization/ko/styleguide)
   — Korean localization rules, passive voice avoidance
4. [토스페이먼츠 테크니컬 라이터가 하는 일](https://toss.tech/article/tech-writer-1)
   — 해요체 sentence ending patterns in practice
5. [문장의 주체를 분명하게 하기](https://technical-writing.dev/sentence/subject.html)
   — Active voice, clear subject in Korean tech writing
6. [자연스러운 한국어 표현 쓰기](https://technical-writing.dev/sentence/natural-kor-expression.html)
   — Nominalization removal, natural Korean expressions
7. [일관되게 쓰기](https://technical-writing.dev/sentence/consistency.html) —
   Terminology consistency enforcement
8. [Gengo 스타일 가이드](https://gengo.com/ko/translators/resources/style-guide/)
   — Punctuation rules (colons, semicolons, hyphens, parentheses)
9. [WordPress.com 한국어 스타일가이드](https://translate.wordpress.com/glossaries-and-style-guides/korean-style-guide/)
   — Period rules, placeholder handling, semicolon avoidance
