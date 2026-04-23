# edX Platform Patterns

Extracted from real study sessions (GT DSA Course 1, 16+ patterns). Reference
for Step 3 (Study Loop) when interactions fail or page structure is ambiguous.

## Content Architecture

All course content lives inside a cross-origin `unit-iframe`. This is the root
cause of most automation limitations — Chrome MCP tools can see the parent page
but have inconsistent access to iframe internals.

### Module Structure (consistent across courses)

```text
Module N
├── Introduction and Overview (intro video + transcript)
├── Topic Section 1
│   ├── Lecture (video + text + images)
│   ├── Exploratory Lab (visualization tool + ungraded questions)
│   └── Comprehension (graded quiz, per-question Submit)
├── Topic Section 2
│   └── (same structure)
├── ...
└── Assignment and Review
    ├── Coding Assignment (download + implement + upload)
    └── Review Summary (recap page)
```

### Exam Structure

```text
Course Exam (N Questions)
├── Section 1 (e.g., Queue Diagramming — text inputs)
├── Section 2 (e.g., ArrayList Coding — coding solution)
├── Section 3 (e.g., Big-O — radio buttons)
├── ...
└── Section N (e.g., Data Structure Properties — mixed)
```

Exams have a timer banner, "End My Exam" button, and sidebar showing completion
status per section.

## Navigation Patterns

### Next Button

Always use `read_page(filter="interactive")` to find the Next link ref. Click
via ref, NOT coordinates — the Next button position varies with scroll state.

```text
Lookup: read_page(tabId, filter="interactive")
Find:   link with text "Next" or ref matching navigation area
Click:  computer(action: left_click, ref: "{next_ref}", tabId)
Wait:   computer(action: wait, duration: 2, tabId)
```

### Previous Button

Same pattern, look for "Previous" link ref.

### Sidebar Navigation

**WARNING:** Clicking a sidebar link to jump to a page does NOT mark the
previous page as complete. Must click Next on each page sequentially to register
progress with edX.

Sidebar links are useful for: detecting current position, counting total
sections, checking completion status (green checkmark vs empty circle).

### Page Load Timing

After clicking Next, wait 2 seconds before reading the new page. The iframe
content loads asynchronously — reading too early returns stale content.

## Interactive Element Patterns

### Radio Buttons / Checkboxes

Radio buttons and checkboxes inside the iframe respond to clicks on their **text
labels**, not the input elements themselves.

```text
DO:    Click the middle of the option text (e.g., "O(n)")
DON'T: Click the radio circle or checkbox square
```

Method:

1. `read_page(tabId)` or screenshot to identify option positions
2. Click the text label coordinates or ref

### Text Input Fields

Some iframe text fields don't respond to direct click+type. Fallback strategy:

```text
Primary:   computer(action: left_click, coordinate: [x, y]) → computer(action: type, text: "answer")
Fallback:  Click a neighboring field that works → key(Tab) to target field → type
Last:      form_input(ref, value) if ref is available from read_page
```

### Dropdown Selects

Use `read_page` to find the select element ref, then either:

- Click to open dropdown → click option text
- Use `form_input(ref, value)` if available

## Submit Button Strategy

**CRITICAL: Submit buttons are inside the cross-origin iframe and CANNOT be
reliably clicked by Claude.** Do NOT waste attempts trying — go straight to
asking the user.

### User Submits (Default)

Claude selects the answer (clicks radio/checkbox text labels). Then:

```text
Ask user: "I've selected the answer. Please click Submit, then tell me 'done'."
```

Do NOT attempt to click Submit via `find()` or coordinate clicking. This was
tested extensively and fails consistently on edX's cross-origin iframe.

### Per-Question Submit (Comprehension Pages)

Each graded question has its own Submit button. The user submits each
individually — there is no "submit all" button.

**WARNING — Post-Submit Iframe Bloat:** After the user clicks Submit on any
question, the iframe height explodes (4000+ px of whitespace appears between
questions). This makes remaining questions unreachable by scrolling. This is why
the Screenshot-First rule (Autonomy Rule #3) exists — capture ALL questions
before ANY Submit happens.

### Ungraded Labs

Lab pages often use "Check" instead of "Submit". Search for both. Lab
submissions are more lenient — incorrect answers can usually be resubmitted.

## Page Type Detection Signals

| Signal in page text                                         | Classified as  |
| ----------------------------------------------------------- | -------------- |
| No interactive elements, prose/images only                  | `lecture-text` |
| Video player or large media area with transcript, no inputs | `video`        |
| Radio buttons or checkboxes + "Submit" button(s)            | `quiz`         |
| Text input fields + "Submit" or "Check" button              | `lab`          |
| Code block prompt + "Download" or file reference            | `assignment`   |
| Summary content, recap, "Review" in heading                 | `review`       |
| Module introduction, course overview, no questions          | `intro`        |
| Timer banner + "End My Exam" button visible                 | `exam`         |

**Composite pages:** Some pages have both video AND quiz, or text AND inputs.
Handle sequentially — process video first (ask user to watch), then handle the
quiz/inputs.

## Scroll Strategy

Long pages may not show all questions in the initial viewport:

1. After reading initial content, scroll down to check for more
2. `computer(action: scroll, coordinate: [center_x, center_y], scroll_direction: "down", scroll_amount: 5)`
3. Take another screenshot or `get_page_text` to capture additional content
4. Repeat until reaching Submit button or page footer

## Error Recovery

| Failure                       | Detection                                          | Recovery                                                                             |
| ----------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Submit click fails            | Submit button inside iframe, click has no effect   | Do NOT retry — ask user to click Submit (this always fails on cross-origin iframe)   |
| Post-Submit iframe bloat      | Thousands of px whitespace after Submit            | Use Screenshot-First rule: capture ALL questions before any Submit. Cannot be fixed. |
| `get_page_text` returns no Qs | Only parent page text, no question content         | Questions are in cross-origin iframe. Use screenshots instead.                       |
| Page doesn't load after Next  | `get_page_text` returns same content               | Wait 3 more seconds, retry Next click                                                |
| Wrong answer selected         | Score shows incorrect                              | Log to Wrong Answer Patterns, do NOT retry (may penalize)                            |
| Text input wrong field        | Typed text in unexpected location                  | Ctrl+A → Delete, use Tab navigation to correct field                                 |
| Session timeout               | Page text contains "session expired" or login form | Tell user: "edX session expired. Please log back in and navigate to where we were."  |
| Tab closed or lost            | `tabs_context_mcp` returns no matching tab         | Ask user to reopen edX; re-initialize                                                |
| Iframe elements inaccessible  | `read_page` returns no interactive elements        | Fall back to screenshot + coordinate-based interaction                               |

## Video Page Protocol

Videos are inside the cross-origin iframe and CANNOT be automated. The protocol:

1. Detect video page (transcript text present, no quiz inputs)
2. Ask user via AskUserQuestion: "This page has a video. Please watch it (or
   seek to near the end if reviewing). Tell me 'done' when finished."
3. Wait for user confirmation
4. Click Next

For video pages that also have questions below the video, handle the questions
AFTER the user confirms video watching is done.
