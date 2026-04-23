---
name: edx-study
description: >-
  Automate edX course study sessions using Chrome MCP browser tools. Claude
  reads page content via screenshots, analyzes quiz questions and presents
  answers in batch tables, navigates between pages, and creates study notes
  progressively. User handles all iframe interactions (selecting answers,
  clicking Submit, scrolling quiz pages). Two modes: study (notes +
  explanations) and exam (fast answers only). Use when user says "edx study",
  "let's study", "continue studying", "start exam", "exam mode", "practice
  exam", "course exam", or "edx [course-name]".
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
  - mcp__claude-in-chrome__tabs_context_mcp
  - mcp__claude-in-chrome__tabs_create_mcp
  - mcp__claude-in-chrome__get_page_text
  - mcp__claude-in-chrome__read_page
  - mcp__claude-in-chrome__find
  - mcp__claude-in-chrome__form_input
  - mcp__claude-in-chrome__computer
  - mcp__claude-in-chrome__navigate
metadata:
  version: "1.2.0"
---

# /edx-study

Automate edX course study sessions with Chrome MCP browser tools. Claude reads
page content via screenshots, analyzes questions, presents answers in batch
tables, navigates between pages, and builds study notes. The user handles all
iframe interactions (selecting answers, clicking Submit, scrolling quiz pages),
video watching, and coding file testing.

**Scope:** This skill handles the interactive study loop and artifact creation.
It does NOT handle session journaling (use `/wrap` after the study session).

## Reference Files

| File                                                      | Use During | Contains                                          |
| --------------------------------------------------------- | ---------- | ------------------------------------------------- |
| [page-handlers.md](./references/page-handlers.md)         | Step 3     | Per-page-type handler logic (quiz, lab, video...) |
| [platform-patterns.md](./references/platform-patterns.md) | Step 3     | edX DOM patterns, Submit retry, error recovery    |

## Autonomy Rules (CRITICAL)

These rules encode explicit user corrections from real study sessions. They are
non-negotiable.

### 1. Claude Reads, User Interacts (CRITICAL)

Claude NEVER attempts to click, select, or type inside cross-origin iframes. ALL
form interactions (radio buttons, checkboxes, dropdowns, text inputs, Submit
buttons) are performed by the user. Claude's only role on quiz/lab pages:

1. Read the page (screenshot + get_page_text)
2. Analyze questions and determine answers
3. Present all answers in a batch table
4. User does everything else

**Why:** edX quiz content lives in cross-origin iframes. Clicks don't reach
them. Scrolling through iframe whitespace wastes 10+ tool calls per question.
This rule was learned after a session that burned 50+ tool calls on a single
Comprehension page with zero successful iframe interactions.

### 2. Submit Before Next (Hard Gate)

Before ANY navigation away from a page with form inputs, confirm the user has
clicked Submit. NEVER click Next without this confirmation. Unsaved form data is
lost on navigation with NO recovery.

### 3. Screenshot-First, User Provides (CRITICAL)

On Comprehension pages with multiple questions:

1. Claude takes ONE screenshot at page load to read visible questions
2. If questions are cut off below the fold, Claude tells the user: "I can see
   Q1-Q3. Please scroll down and paste a screenshot of any remaining questions."
3. User pastes screenshot images directly into chat
4. Claude analyzes ALL questions from the screenshots and presents answers
5. User selects, submits, and scrolls — Claude does NOT scroll the iframe

**NEVER** do the old scroll-screenshot-scroll loop inside the iframe. It burns
tokens on whitespace and fails after Submit bloats the iframe.

### 4. Per-Question Submit (Comprehension)

Each graded question has its own Submit button. Submit each individually — there
is no "submit all" button. User clicks each Submit after selecting the answer
Claude provided.

### 5. Video = User Manual (policy-driven)

Videos are inside a cross-origin iframe and cannot be automated. The user's
**session-wide video policy** (set in Step 2.5) determines behavior:

- `ask-each-time` — prompt before every video page
- `watch-and-wait` — pause on every video, wait for user's "done" confirmation
- `auto-skip` — capture the visible intro prose and transcript snippets, then
  click Next without waiting

Claude NEVER attempts to play, seek, or interact with the video player itself.

### 6. Coding Assignments = User Tests

Claude provides the solution code, writes it to a file. The user downloads
starter code, pastes the solution, tests locally, and submits on edX.

### 7. Session Policies Asked Once (NOT Per-Page)

edX courses share a consistent layout across modules and courses. Recurring page
types (videos, "What did you learn?" surveys) should be governed by
**session-wide policies** set at Step 2.5, not re-prompted per page. Re-asking
every time burns user attention and tool calls on decisions the user already
made.

Policies apply for the entire session unless the user explicitly changes them
mid-session ("let me watch this one"). The only exception is when the policy
itself is `ask-each-time` — then per-page prompts are correct.

## Step 0: Detect Context and Mode

1. **Parse mode** from user message:
   - Contains "exam", "timed", "test", "course exam", "practice exam" →
     `MODE=exam`
   - Otherwise → `MODE=study`

2. **Parse target** from user message:
   - "module 4", "m4" → extract module number
   - "dsa-ii", "course 2" → extract course identifier
   - No target specified → detect from browser context in Step 1

3. **Set paths:**
   - `3B_PATH = ${FORGE_3B_ROOT}`
   - `STUDY_PATH = {3B_PATH}/personal/study`
   - Detect course slug from user message or most recently updated study
     workspace
   - Set `COURSE_DIR` (e.g., `gt-dsa/dsa-i/`)

4. **Check `tmp/intake/`** for pre-staged materials (PDFs, code files). Note
   them for processing at session end.

## Step 1: Initialize Browser

1. Load Chrome MCP tools via ToolSearch if not already loaded:
   `ToolSearch("select:mcp__claude-in-chrome__tabs_context_mcp")`

2. Call `tabs_context_mcp` to get available tabs.

3. Find existing edX tab (URL contains `learning.edx.org`):
   - If found: use that tabId
   - If not found: ask user to open edX to the starting page

4. Take screenshot + `get_page_text(tabId)` to establish current position.

5. Detect from page content:
   - Course name (from page title or breadcrumb)
   - Current module/section (from sidebar)
   - Whether this is an exam (timer banner present)

6. Report to user:

```text
Study Session Initialized
==========================
Course:  {course name}
Module:  {N} — {topic}
Page:    {current page title}
Mode:    {study|exam}

Ready to begin.
```

## Step 2: Initialize Notes (study mode only)

**If MODE=study:**

1. Determine note file path: `{STUDY_PATH}/{COURSE_DIR}/m{N}-{topic}.md`
2. Check if file already exists:
   - Exists: read it, plan to append new content
   - New: create with frontmatter + Abbreviations table + Core Idea placeholder

   Follow study note conventions from `personal/study/CLAUDE.md`:
   - Reader level: "Explain Like I Know Nothing"
   - Module prefix naming: `m{N}-{topic}.md`
   - Abbreviations table near the top
   - 5W1H for assignments

**If MODE=exam:**

1. Prepare assignment file path only (e.g., `course-exam.java`,
   `practice-exam.java`)
2. Skip note initialization — focus on speed

## Step 2.5: Establish Session Policies

edX courses share a consistent layout across modules: video intros, prose, "What
did you learn?" surveys, and comprehension quizzes recur on every module. Asking
the user how to handle each one per-page burns attention and tool calls on
decisions they already made. Instead, set **session-wide policies** once at the
start and apply them for the rest of the session.

Use `AskUserQuestion` to ask both policy questions in a **single batched call**
so the user answers them together:

1. **Video policy** — how to handle video pages:

   | Option                     | Behavior                                                                                                                                                                      |
   | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | `ask-each-time`            | Prompt before every video page. User decides per-video.                                                                                                                       |
   | `watch-and-wait`           | Pause on each video, wait for user's "done" confirmation, then Next.                                                                                                          |
   | `auto-skip`                | Capture visible prose + transcript snippets, then click Next.                                                                                                                 |
   | `user-provides-transcript` | User copies full transcript from edX transcript panel and pastes into chat. Claude incorporates the full transcript into study notes (richest learning mode, best for exams). |

2. **Survey policy** — how to handle "What did you learn?" ungraded widgets:

   | Option                  | Behavior                                              |
   | ----------------------- | ----------------------------------------------------- |
   | `skip`                  | Ignore the widget and navigate past it. (Recommended) |
   | `user-click-and-submit` | Claude suggests relevant tags; user clicks + submits. |
   | `ask-each-time`         | Prompt before every survey.                           |

**Recommended defaults** (put first in the option list with "(Recommended)"):

- Video: `watch-and-wait` for first-time viewing; `auto-skip` for review passes
  or exam mode. `ask-each-time` is fine if the user is unsure — it's the
  conservative default.
- Survey: `skip` — these widgets are ungraded and don't affect progress.

**Record the policies in session state** (mental model, not a file). When you
encounter a video or survey page in Step 3, check the policy first and apply it
without re-asking — unless the policy is `ask-each-time` or the user explicitly
overrides mid-session ("let me watch this one in full").

**Exam mode note:** In `MODE=exam`, default to `auto-skip` for videos and `skip`
for surveys without asking — exams prioritize speed and the user almost
certainly doesn't want interruptions.

## Step 3: Study Loop (Core)

**Read [page-handlers.md](./references/page-handlers.md) for detailed handler
logic. Read [platform-patterns.md](./references/platform-patterns.md) for DOM
patterns and error recovery.**

Repeat for each page:

### 3a. Read Current Page

1. `computer(action: screenshot, tabId)` — always screenshot first (most
   reliable for iframe content)
2. `get_page_text(tabId)` — get parent page text (sidebar, nav — useful for
   detecting page type and section progress)
3. For lecture-text pages only: try JS scroll to bottom once (`javascript_tool`
   → `document.querySelector('.unit-container').scrollTop = scrollHeight`), then
   screenshot again if new content appears
4. For quiz/lab pages: do NOT scroll — ask user to screenshot hidden questions

### 3b. Classify Page Type

Determine page type from content signals:

| Signal                                     | Type           | Handler                                |
| ------------------------------------------ | -------------- | -------------------------------------- |
| No interactive elements, prose/images only | `lecture-text` | Read content + notes                   |
| Video/transcript present, no quiz inputs   | `video`        | Apply session video policy (Step 2.5)  |
| Radio/checkbox options + Submit button(s)  | `quiz`         | Select answers + Submit per Q          |
| Text input fields + Submit/Check button    | `lab`          | Fill inputs + Submit                   |
| Coding prompt, file download reference     | `assignment`   | Provide solution, user tests           |
| Summary/review content, recap              | `review`       | Read content + notes                   |
| Timer banner + "End My Exam"               | `exam-page`    | Fast answer mode                       |
| "What did you learn?" + topic tags         | `survey`       | Apply session survey policy (Step 2.5) |

**Composite pages** (e.g., video + quiz + survey on the same page): handle each
component sequentially — video per policy, then quiz/lab, then survey per
policy. The Submit-first gate applies to the quiz/lab component only.

**Survey pages:** "What did you learn?" widgets appear at module intro/end
pages. These are optional feedback forms (not graded). Apply the session survey
policy from Step 2.5 — do NOT block on these or re-prompt per page.

### 3c. Execute Handler

Route to the appropriate handler from `references/page-handlers.md`:

**lecture-text / intro / review:**

- Read all content, extract key concepts
- In study mode: add to notes (definitions, comparisons, code examples)
- Click Next directly (no Submit gate — no forms)

**video:**

Check the session video policy from Step 2.5 and apply it:

- **`watch-and-wait`:** Capture any visible intro prose / transcript snippet to
  notes. Tell the user: "Watching this video — let me know when you're done."
  Wait for confirmation, then proceed.
- **`auto-skip`:** Capture visible prose + transcript snippet to notes. Do NOT
  wait — continue to post-video check and navigation.
- **`ask-each-time`:** Use AskUserQuestion per-video with four options (watch
  fully / skim to end / skip / paste transcript). Apply the selected behavior
  for this page only.
- **`user-provides-transcript`:** The user will paste the full video transcript
  directly into chat. Wait for them to paste it, then incorporate the entire
  transcript into the study notes as a **properly structured section** (not a
  raw dump). Process the transcript per the "Transcript Ingestion" rules below.

**Transcript Ingestion (when policy is `user-provides-transcript`):**

When the user pastes a transcript, you must transform it into study notes — NOT
just append the raw text. Apply these rules:

1. **Structure the content** into logical subsections with clear headings (e.g.,
   "Concept", "Pseudocode", "Example Walkthrough", "Edge Cases").
2. **Preserve the lecturer's voice** for key definitions but **restate in your
   own words** where the transcript is verbose or repetitive. Never copy long
   stretches verbatim — rewrite for density.
3. **Pull out algorithms and pseudocode** into fenced code blocks. Use real
   language (Java for this course) when the transcript shows code.
4. **Extract named concepts into the Abbreviations table** at the top of the
   note file if they're new.
5. **Flag gotchas and edge cases** with a bold label (e.g., "**Edge case:**").
6. **Do NOT invent content** the transcript doesn't cover. If the transcript
   leaves something unexplained, either note the gap or consult prior notes
   (don't hallucinate missing steps).
7. **Multiple transcripts per page:** Some pages have 2+ videos back-to-back.
   Label each section (e.g., `#### Video 1: Concept` / `#### Video 2: Code`) and
   keep them distinct in the note.
8. **Apply the Explain Like I Know Nothing rule** from
   `personal/study/CLAUDE.md` — define terms on first use, don't stack jargon.

**Always** check for post-video content below the video (quiz, lab, survey) and
handle each component per its own handler before navigating. The user can
override the policy at any time by telling you so ("let me watch this one" or
"skip the rest of the videos").

**quiz:**

- Take ONE screenshot to read visible questions
- If questions are cut off: tell user to screenshot remaining and paste into
  chat
- Analyze all questions, present ALL answers in a batch table:

  ```text
  | # | Question | Answer |
  |---|----------|--------|
  | 1 | Topic    | Option text or ordinal position |
  ```

- User selects and submits each question
- User reports wrong answers → log to Wrong Answer Patterns
- Claude NEVER clicks inside the iframe (see Autonomy Rule #1)

**lab:**

- Read questions from screenshot, compute answers
- Present all answers to user in a clear format
- User fills text fields and clicks Submit/Check
- If labs have simple text inputs outside iframes, Claude may try to fill them
  (one attempt only — if it fails, present answers for user to fill)

**assignment:**

- Read full prompt and requirements
- Generate solution with 5W1H header comments
- Write to study workspace or `tmp/intake/`
- Tell user: "Solution saved. Download starter code, paste, test, and submit on
  edX. Tell me 'done' when finished."
- Wait for confirmation

**survey:**

Check the session survey policy from Step 2.5 and apply it:

- **`skip`:** Do not mention the survey, do not block. Just proceed to the next
  component or navigate.
- **`user-click-and-submit`:** Briefly list the topic tags that seem relevant to
  the page's actual content (e.g., "For this page I'd pick: Binary Search Trees,
  Time Complexity"). User clicks + submits. No Submit-first gate — surveys are
  ungraded, so unsaved survey state is not a data loss.
- **`ask-each-time`:** Use AskUserQuestion to choose between skip / suggest tags
  / skip all future surveys. Apply accordingly.

Surveys are NEVER part of the Submit-first gate in Step 3d — they're ungraded
and losing unsaved survey state has no consequence.

### 3d. Submit-First Gate

**Before ANY navigation** to the next page:

1. Check if the current page had form inputs (quiz, lab, or text fields)
2. If yes: execute the Submit retry strategy (see Autonomy Rule #2)
3. Only proceed to navigation after Submit is confirmed

### 3e. Navigate to Next Page

1. `read_page(tabId, filter="interactive")` — find "Next" link ref
2. `computer(action: left_click, ref: "{next_ref}", tabId)` — click Next
3. `computer(action: wait, duration: 2, tabId)` — wait for page load
4. Return to Step 3a

### 3f. Session Boundary Detection

**Module end (MANDATORY STOP):** When a module's last page is reached (no more
Next within the module section, or sidebar shows all pages checked), Claude MUST
stop and ask the user before continuing:

> "Module {N} complete. Would you like to /wrap this session or continue to the
> next module?"

Do NOT auto-advance into the next module. Study sessions are managed per-module
— the user decides when to continue.

**Exam end:** All sections show completed in sidebar, or user says "end exam".

**User interrupt:** User says "stop", "pause", "done", "wrap" → proceed to
Step 4.

**Unresolvable issue:** If Claude encounters something it cannot resolve after
the error recovery attempts (Submit failures, page load issues, iframe blocks),
STOP and ask the user for help rather than guessing or skipping.

## Step 4: Session End

### 4a. Finalize Study Notes (study mode)

1. Write/update the study note file with all accumulated content
2. Add **Key Takeaways** section — synthesize the most important concepts from
   the module
3. Add **Wrong Answer Patterns** table if any quiz questions were missed:

   | Question Topic | Correct Answer | Why Wrong Choices Fail     |
   | -------------- | -------------- | -------------------------- |
   | {topic}        | {answer}       | {reasoning per distractor} |

4. Quality check: scan for unexplained jargon (Explain Like I Know Nothing rule)
5. Ensure all abbreviations are in the Abbreviations table

### 4b. Finalize Assignments

1. If coding solutions were generated: ensure they are saved with 5W1H headers
2. For exams: consolidate all coding solutions into a single exam file (e.g.,
   `course-exam.java` with comment headers per question)

### 4c. Process Staged Materials

1. Check `tmp/intake/` for files staged during the session
2. PDFs → move to `{COURSE_DIR}/refs/m{N}-{topic}.pdf`, create companion summary
3. Code files → move to `{COURSE_DIR}/` with proper naming
4. After organizing, `tmp/intake/` should be empty

### 4d. Update Course Index

1. Read `{COURSE_DIR}/_index.md`
2. Add study notes to the Learning Sequence section under the correct module
3. Add new refs to the Course Materials section
4. Add exam files to the Exams section (if applicable)

### 4e. Update Goal Progress

1. Read the relevant goal file (e.g., `personal/goals/gt-dsa.md`)
2. Check off completed items:
   - Module completion checkboxes
   - Course completion (if all modules + exam done)
   - Certificate earned (if applicable)

### 4f. Write to Buffer

Append a structured session summary to `{3B_PATH}/.claude/buffer.md`:

```markdown
## YYYY-MM-DD HH:MM - edx-study

**What:** edX study session — {course}, Module {N}: {topic} **Why it matters:**
Progress toward {certificate/goal} **Details:**

- Mode: {study|exam}
- Pages covered: {count}
- Quiz scores: {score list}
- Notes created: {file paths}
- Assignment: {file path if applicable}
```

### 4g. Report

```text
Study Session Complete
=======================
Course:  {course name}
Module:  {N} — {topic}
Pages:   {count} pages processed
Mode:    {study|exam}

Created/Updated:
  - Study notes: {path}
  - Assignment: {path}
  - Refs: {count} files organized
  - Course index: _index.md updated
  - Goal progress: {goal file} updated

Quiz Scores:
  - {section}: {score}

Buffer updated. Run /wrap when ready to journal.
```

## Troubleshooting

| Problem                       | Cause                                | Fix                                                   |
| ----------------------------- | ------------------------------------ | ----------------------------------------------------- |
| Submit click doesn't register | Inside cross-origin iframe           | Retry with coordinate click; ask user on 3rd attempt  |
| Page content not loading      | Async iframe load                    | Wait 3 more seconds, retry `get_page_text`            |
| Text typed in wrong field     | Scroll offset changed coordinates    | Ctrl+A → Delete, use Tab navigation                   |
| edX session expired           | Inactivity timeout                   | User re-logs in, navigates back, tells Claude "ready" |
| Tab lost                      | User closed or navigated away        | `tabs_context_mcp` to find tab; ask user to reopen    |
| Wrong answer on quiz          | Incorrect analysis                   | Log to Wrong Answers, do NOT retry (may penalize)     |
| No interactive elements found | `read_page` can't see iframe content | Fall back to screenshot + coordinate clicking         |
| Video detected in exam        | Unusual but possible                 | Follow standard video protocol (ask user to watch)    |
