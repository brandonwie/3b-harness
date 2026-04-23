# Page Handlers

Detailed handler logic for each edX page type. Loaded during Step 3 (Study
Loop).

## Quiz Handler (Comprehension Pages)

Graded quiz with radio buttons, checkboxes, or mixed. Each question has its own
Submit button.

### Known Limitations

- **ALL quiz elements are inside a cross-origin iframe** — Claude cannot click,
  select, type, or scroll inside them. `read_page` and `get_page_text` cannot
  see iframe content. Only screenshots can read the questions.
- **Post-Submit iframe bloat** — after Submit, the iframe height explodes (4000+
  px of whitespace between questions), making remaining questions unreachable by
  scrolling.
- **Scrolling inside the iframe wastes massive tokens** — 5-10 screenshots of
  whitespace per question with no progress. NEVER scroll to find questions.

### Workflow (Screenshot-First, User-Drives)

1. **Claude takes ONE screenshot** at page load to read visible questions.

2. **If questions are cut off** below the fold, Claude tells the user: "I can
   see Q1-Q{N}. Please scroll down and paste a screenshot of the remaining
   questions." The user takes a screenshot (e.g., with Shottr) and pastes the
   image into chat.

3. **Analyze all questions** from screenshots. Determine the correct answer for
   each with reasoning.

4. **Present all answers at once** in a table:

   ```text
   | # | Question Topic         | Answer                             |
   |---|------------------------|------------------------------------|
   | 1 | Access Modifiers       | 5th: private with only getter      |
   | 2 | Constructor Variables  | 3rd: length 50 and width 0         |
   | 3 | Constructor Chaining   | 4th: this(s, s);                   |
   ```

   For checkbox questions (select all that apply), list all correct options with
   checkmarks and explain why wrong options are wrong.

5. **User does everything**: scrolls to each question, selects the answer,
   clicks Submit, then moves to the next. Claude does NOT interact with the
   iframe at all.

6. **Log wrong answers**: If the user reports an incorrect answer, record it in
   Wrong Answer Patterns with full analysis.

### Token Budget

This workflow uses 1-2 screenshots (Claude's) + user-pasted images instead of
the old scroll-screenshot-scroll loop that consumed 10-20+ tool calls per
Comprehension page. The savings are significant — a typical Comprehension page
went from ~50 tool calls to ~5.

### Study Mode Additions

- Present each answer with brief reasoning
- Add key concepts from questions to notes buffer
- Wrong answers get full "Why Wrong Choices Fail" analysis

### Exam Mode Differences

- Present all answers in a batch table (faster)
- Skip reasoning unless asked
- No notes buffer updates

## Lab Handler (Exploratory Labs)

Ungraded or lightly-graded interactive exercises with text input fields.

### Workflow

1. **Read the prompt**: `get_page_text(tabId)` for all instructions and
   questions.

2. **Determine answers**: Analyze each question, compute the answer.

3. **Fill inputs sequentially**:

   a. For each text field:
   - Try: `computer(action: left_click, coordinate: [x, y])` on the field, then
     `computer(action: type, text: "{answer}")`
   - If the click misses (text appears in wrong field):
     `computer(action: key, text: "cmd+a")` →
     `computer(action: key, text: "Backspace")` → use Tab navigation from a
     known field
   - Tab between fields: `computer(action: key, text: "Tab")` then type

   b. Verify each field has the correct content (screenshot after filling all)

4. **Submit**: Labs may use "Check" or "Submit". Search for both. Labs are
   lenient — you can resubmit if incorrect.

5. **Verify results**: Read feedback. If incorrect, analyze why and retry with
   corrected answers.

### Key Differences from Quiz

- Text fields instead of radio/checkbox
- Often allows multiple submission attempts
- May have "Check" button instead of "Submit"
- Answers are often computed (trace an algorithm, draw state) rather than
  selected from options

## Video Handler

Pages with video content that cannot be automated.

### Detection

- Page has video player or large media area
- Transcript text present but no quiz input elements
- Text may include video title, duration, or "Watch the following video"

### Workflow

1. **Detect video** from page content signals.

2. **Ask user** via AskUserQuestion:

   ```text
   This page has a video: "{title if detectable}".
   Please watch it (or seek to near the end if reviewing).
   Tell me 'done' when finished.
   ```

3. **Wait** for user confirmation ("done", "finished", "next", etc.).

4. **Check for post-video questions**: After user confirms, re-read the page. If
   there are quiz or lab elements below the video, handle them using the
   appropriate handler before navigating.

5. **Navigate**: Click Next.

### Exam Mode

Exams rarely have videos. If detected in exam context, still follow the same
protocol but note it as unusual.

## Assignment Handler

Coding assignments requiring file download, implementation, and submission.

### Workflow

1. **Read the assignment prompt** fully from `get_page_text`. Scroll to capture
   all requirements, constraints, and assumptions.

2. **Check `tmp/intake/`** for pre-staged starter code files. If the user has
   already dropped files there, read them.

3. **Generate solution**:
   - Write solution code with 5W1H header comments (see
     `personal/study/CLAUDE.md` § Assignment Documentation)
   - Add per-method comments explaining WHY key decisions were made
   - Follow existing exemplar format (see `course-exam.java`,
     `m3-assignment.java`)

4. **Save to study workspace**: Write to `{COURSE_DIR}/m{N}-assignment.{ext}` or
   appropriate exam file.

5. **Inform user**:

   ```text
   Solution saved to {file_path}.

   To submit on edX:
   1. Download the starter code from edX (if not already done)
   2. Paste the solution into the appropriate method(s)
   3. Test locally (compile + run tests if provided)
   4. Upload/paste on edX and submit

   Tell me 'done' when you've submitted, or if you need help debugging.
   ```

6. **Wait** for user confirmation before navigating.

### Multiple Coding Questions (Exam)

For exams with multiple coding sections across different pages:

- Accumulate solutions in a single exam file (e.g., `course-exam.java`)
- Each solution separated by a comment header indicating the question
- Follow the existing `course-exam.java` format from DSA I

## Lecture-Text Handler

Pages with educational content (text, images, tables, code examples) but no
interactive elements.

### Workflow

1. **Read all content**: `get_page_text(tabId)` for text. Take screenshot if
   visual content (diagrams, tables, images) is present.

2. **Extract for notes** (study mode only):
   - Definitions and key concepts
   - Comparisons and trade-offs
   - Code examples with explanations
   - Diagrams described in text

3. **Add to notes buffer**: Organize by topic hierarchy detected in the content.
   Use headings from the page as section markers.

4. **Navigate**: Click Next directly (no Submit gate needed — no forms).

### Exam Mode

In exam mode, read the content for context but don't build notes. Some exam
pages have explanatory text before questions — read it to inform answers.

## Review Handler

Summary/recap pages at the end of a module or section.

### Workflow

1. **Read summary content**: `get_page_text(tabId)` for the full review.

2. **Capture key points** (study mode): Add to notes buffer as a "Review
   Summary" section. This often contains the most important takeaways that
   should appear in Key Takeaways.

3. **Check for intake files**: The review page is a natural boundary. If there
   are PDFs in `tmp/intake/` that correspond to this module, note them for
   processing at session end.

4. **Navigate**: Click Next.

## Intro Handler

Module introduction or course overview pages.

### Workflow

1. **Read overview content**: Extract module title, learning objectives, and any
   structural information about what's coming.

2. **Initialize notes buffer** (study mode): Set up the module metadata — module
   number, topic name, and a Core Idea placeholder to be filled as content is
   consumed.

3. **Navigate**: Click Next.

## Data Structure Matching Handler (Special)

A common exam question type in DSA courses. Given add/remove operations,
determine which data structure(s) could produce the result.

### Answering Strategy

For each question: trace operations through all candidate structures:

- **Stack** (LIFO): push = add to top, pop = remove from top. Display: left =
  bottom, right = top.
- **Queue** (FIFO): enqueue = add to back, dequeue = remove from front. Display:
  left = front, right = back.
- **PriorityQueue** (min-heap): add maintains priority order, remove takes
  smallest. Display: sorted ascending.

Compare final state to expected output. Select all matching structures. If none
match, select "None" (if available) or leave unchecked.

**Common traps:**

- PQ reorders elements by priority, not insertion order
- When all removes empty the structure before re-adding, all three produce
  identical results
- Stack/Queue produce same result when removes only happen on single-element
  structures

## Diagramming Handler (Special)

Questions where you trace operations and write the state after each step.
Elements are dash-separated (e.g., "NYM-NYY-BOS-FQR").

### Answering Strategy

1. Read initial state and all operations
2. Trace each operation step-by-step:
   - For queues: enqueue at back, dequeue from front
   - For stacks: push/pop from top
   - For ArrayLists: track indices, handle invalid operations → "NA"
3. Fill each text field with the resulting state
4. Submit all at once (these typically have a single Submit for all fields)
