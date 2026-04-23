# Question Design Guide

Detailed patterns for designing hypothesis-driven questions across all three
/clarify modes.

## AskUserQuestion Formatting

```text
question: "Clear, specific question ending with ?"
header: "Short label (max 12 chars)"
options:
  - label: "Option A"
    description: "Why this matters or what it implies"
  - label: "Option B"
    description: "Why this matters or what it implies"
multiSelect: true  # when compound causes are likely
```

**Universal Rules:**

- 3-4 options per question (never 5+)
- `description` explains implications, not just restates `label`
- `multiSelect` for cause/blocker questions; single for priority/choice
- Batch up to 4 related questions per AskUserQuestion call

---

## Vague Mode Patterns

Resolve each ambiguity category from Phase 1 intake.

| Category        | Question Pattern                   | Example Options                                          |
| --------------- | ---------------------------------- | -------------------------------------------------------- |
| **Scope**       | "Who is affected by this?"         | All users / Admins only / Specific roles / API consumers |
| **Behavior**    | "What should happen when X fails?" | Fail silently / Show error / Auto-retry / Fallback       |
| **Interface**   | "How should this be exposed?"      | REST API / GraphQL / CLI / Internal service              |
| **Data**        | "What format should output use?"   | JSON / CSV / Both / Custom                               |
| **Constraints** | "What performance requirement?"    | <100ms / <1s / No requirement / Best effort              |
| **Priority**    | "How critical is this?"            | Must-have for launch / Nice-to-have / Future             |

**Batching Strategy:**

- Group related categories (e.g., Scope + Behavior in one call)
- Lead with the most ambiguous category
- Stop when remaining ambiguities are non-critical

**Example AskUserQuestion call (vague mode):**

```text
questions:
  - question: "Which authentication method should the login use?"
    header: "Auth method"
    options:
      - label: "Email + Password"
        description: "Traditional signup with email verification"
      - label: "OAuth (Google/GitHub)"
        description: "Delegated auth, no password management needed"
      - label: "Magic link"
        description: "Passwordless email-based login"
    multiSelect: false
  - question: "What should happen after registration?"
    header: "Post-signup"
    options:
      - label: "Immediate access"
        description: "User can use the app right away"
      - label: "Email verification first"
        description: "Must confirm email before access"
    multiSelect: false
```

---

## Unknown Mode Patterns

### R1 Questions: Validate the Draft

Design one question per quadrant boundary. Goal: confirm or correct the initial
classification.

| Quadrant | Question Pattern                     | Example                                               |
| -------- | ------------------------------------ | ----------------------------------------------------- |
| **KK**   | "What's the confirmed reality?"      | "Primary revenue source?" with options per hypothesis |
| **KU**   | "Where's the weakest link?"          | "Which connection in your process is weakest?"        |
| **UK**   | "What assets exist but aren't used?" | Based on context findings                             |
| **UU**   | "What's the scariest scenario?"      | "Most feared outcome?" with risk scenarios            |

**Tip**: Surface surprising assets from context exploration as UK options.

### R2 Questions: Deepen the Weak Spots

Triggered by R1 answers. Focus on the 1-2 most uncertain areas.

| R2 Type               | Trigger                       | Example                                    |
| --------------------- | ----------------------------- | ------------------------------------------ |
| **Root cause**        | KU has unclear "why"          | "Core reason this isn't happening?"        |
| **Feasibility**       | Proposed solution seems hard  | "Is this realistic? What's blocked it?"    |
| **Priority**          | Multiple items compete        | "Pick top 3 from these Known Unknowns"     |
| **Hidden constraint** | Suspected unstated limit      | "Tried this before? What happened?"        |
| **Drop candidate**    | "Execution scattered" emerged | "Which of these can be stopped or paused?" |

### Reading R1 Answers for R2 Design

| R1 Signal                     | R2 Strategy                                            |
| ----------------------------- | ------------------------------------------------------ |
| Compound answer (multiSelect) | Area is complex — break apart with root cause question |
| Unexpected answer             | Draft was wrong — revise quadrant, probe deeper        |
| "Other" selected              | User sees outside the frame — open exploration         |
| Strong conviction             | Area is likely KK — validate with evidence, move on    |

### R3 Questions: Execution Details

Only for prioritized top items. Skip if R2 provides enough.

| R3 Type         | When                      | Example                                      |
| --------------- | ------------------------- | -------------------------------------------- |
| Tool/channel    | Multiple execution paths  | "Publish via: X / Y / Z?"                    |
| Pattern ID      | Need to design a template | "What insight type do you find most often?"  |
| Past experience | Check if tried before     | "Tried this approach? What worked?"          |
| Success signal  | Defining "done"           | "What response tells you this format works?" |

---

## Metamedium Mode Patterns

### The Fork Question

Always present as the first question in Phase 2:

```text
questions:
  - question: "This is currently [CONTENT/FORM]-level work. Where should effort go?"
    header: "Level"
    options:
      - label: "Proceed with content"
        description: "Optimize within the current form — faster, lower risk"
      - label: "Explore form change"
        description: "What if the medium/structure itself changed? Higher leverage"
      - label: "Content now, note form"
        description: "Do the content work, but flag the form opportunity for later"
    multiSelect: false
```

### Form Exploration Follow-ups

If "Explore form change" selected, ask about:

| Question Target  | Pattern                           | Example Options                                  |
| ---------------- | --------------------------------- | ------------------------------------------------ |
| **Constraints**  | "What limits a form change?"      | Time / Skill gap / Dependencies / Risk tolerance |
| **Properties**   | "What new property matters most?" | Automatic / Repeatable / Scalable / Composable   |
| **Minimum test** | "Smallest test of the new form?"  | Prototype / Proof of concept / One-off trial     |

---

## Common Mistakes (All Modes)

### Asking the same question twice in different words

R1: "What's your biggest challenge?" R2: "What's hardest right now?" **Fix**: R2
must drill INTO the R1 answer, not re-ask it.

### Options that aren't real hypotheses

"Option A: Good" "Option B: Bad" "Option C: Maybe" **Fix**: Each option should
represent a distinct, plausible situation.

### Skipping multiSelect when causes are compound

"Why can't you do video?" with single-select misses "skill gap AND high
standards" **Fix**: Default to multiSelect for "why/blocker" questions.

### Going past the cap

Fatigue kills quality. If R2 answers are clear, skip R3 entirely. If vague mode
resolves critical ambiguities early, stop before reaching 8.
