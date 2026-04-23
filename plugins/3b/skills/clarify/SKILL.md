---
name: clarify
description: >-
  Resolve requirement, intent, or strategic uncertainty through structured
  hypothesis-driven questioning. Three auto-detected modes: vague (ambiguous
  requirements to concrete specs), unknown (strategic blind spots to 4-quadrant
  playbook), metamedium (content vs form reframing to leverage analysis). ALWAYS
  uses AskUserQuestion. Trigger on "clarify", "scope this", "spec this out",
  "what am I missing", "blind spots", "content vs form", "diminishing returns",
  "make this clearer", "assumption check", "요구사항 명확히", "뭘 놓치고 있지",
  "뭘 모르는지 모르겠어", "같은 방식이 안 먹혀", "관점 전환", "전략 점검", "내용
  vs 형식". Standalone or sub-workflow for other skills.
metadata:
  version: "1.0.0"
---

# /clarify — Resolve Uncertainty

Resolve ambiguity through structured, hypothesis-driven questioning. Three modes
handle different types of uncertainty. **ALWAYS use AskUserQuestion** — never
ask clarifying questions in plain text.

## When to Use

| Signal                                             | Mode           |
| -------------------------------------------------- | -------------- |
| Ambiguous feature request, incomplete spec         | **vague**      |
| "What am I missing?", strategic blind spots        | **unknown**    |
| Diminishing returns, "same approach isn't working" | **metamedium** |

For technical bugs and root cause analysis, use `/investigate` instead. /clarify
handles **intent** uncertainty; /investigate handles **technical** uncertainty.

## Reference Files

Load during execution when the relevant phase needs detailed reference:

| File                                                      | Use During | Contains                                 |
| --------------------------------------------------------- | ---------- | ---------------------------------------- |
| [question-design.md](./references/question-design.md)     | Phase 2    | AskUserQuestion patterns for all 3 modes |
| [playbook-template.md](./references/playbook-template.md) | Phase 3    | Unknown mode 4-quadrant output template  |
| [alan-kay-quotes.md](./references/alan-kay-quotes.md)     | Phase 1, 3 | Metamedium source material and examples  |

## Trigger Phrases

- "clarify" / "/clarify" / "clarify this"
- "scope this" / "spec this out" / "make this clearer"
- "what am I missing" / "blind spots" / "assumption check"
- "content vs form" / "diminishing returns" / "different approach"
- "요구사항 명확히" / "뭘 놓치고 있지" / "뭘 모르는지 모르겠어"
- "같은 방식이 안 먹혀" / "관점 전환" / "전략 점검" / "내용 vs 형식"

---

## Phase 0: Mode Detection

Auto-detect mode from context, or accept explicit override.

### Detection Signals

| Signal                                                       | Mode       | Confidence |
| ------------------------------------------------------------ | ---------- | ---------- |
| `/clarify vague` or caller specifies `mode: vague`           | vague      | Explicit   |
| `/clarify unknown` or caller specifies `mode: unknown`       | unknown    | Explicit   |
| `/clarify metamedium` or caller specifies `mode: metamedium` | metamedium | Explicit   |
| Feature request with scope/behavior/criteria undefined       | vague      | High       |
| Bug report with unclear reproduction steps                   | vague      | High       |
| "What am I missing?", strategic uncertainty                  | unknown    | High       |
| Strategy/plan document needing scrutiny                      | unknown    | High       |
| "Same approach isn't working", diminishing returns           | metamedium | High       |
| Optimizing content with unclear leverage                     | metamedium | Medium     |

**Ambiguous cases**: Default to **vague** (most common). Present detected mode
before proceeding:

> "Detected **{mode}** mode — {reason}. Override with `/clarify {other_mode}` if
> needed."

### Sub-Workflow Invocation

When called by another skill, the caller provides:

| Parameter     | Required | Description                            |
| ------------- | -------- | -------------------------------------- |
| `mode`        | Yes      | vague / unknown / metamedium           |
| `context`     | Yes      | The ambiguous text or document         |
| `scope_limit` | No       | Max questions (overrides mode default) |
| `return_to`   | No       | Skill to return control to             |

---

## Phase 1: Intake

### All Modes

Record: trigger source, current project context, original text verbatim.

### Vague Mode

Categorize ambiguities found in the input:

| Category        | What to Identify                      |
| --------------- | ------------------------------------- |
| **Scope**       | Who is affected? All users or subset? |
| **Behavior**    | What happens on success? On failure?  |
| **Interface**   | API? UI? CLI? Internal?               |
| **Data**        | What format? What validation?         |
| **Constraints** | Performance? Security? Compatibility? |
| **Priority**    | Must-have vs nice-to-have?            |

### Unknown Mode

1. **If file/document provided**: Read and extract goals, components, implicit
   assumptions, missing elements
2. **If topic keyword only**: Skip to Phase 2 (R1 questions establish scope)
3. **Gather context**: Glob for related files (CLAUDE.md, README, decision
   records). Identify underutilized assets — existing tools, past projects,
   unexploited expertise. These become Unknown Known candidates.
4. **Draft initial 4-quadrant classification** (intentionally rough — R1
   corrects it):
   - Known Knowns (confirmed working)
   - Known Unknowns (questions without answers)
   - Unknown Knowns (assets not leveraged)
   - Unknown Unknowns (risks not yet imagined)

### Metamedium Mode

**Read [alan-kay-quotes.md](./references/alan-kay-quotes.md) for source
material.**

Label each component of the user's current work as content or form:

```text
[CONTENT] Writing a blog post about AI consulting
[FORM]    Building a pipeline that turns consulting retros into blog posts
[CONTENT] Deploying a new API endpoint
[FORM]    Building a codegen that auto-generates endpoints from schemas
[CONTENT] Fixing a flaky test
[FORM]    Building a test infrastructure that prevents flaky tests by design
```

Present the labeling to the user as a brief diagnosis.

---

## Phase 2: Structured Questioning

**CRITICAL: Use AskUserQuestion tool for EVERY question. Never ask questions in
plain text.**

**Read [question-design.md](./references/question-design.md) for detailed
patterns, round templates, and formatting rules.**

### Core Principle: Hypotheses as Options

Present plausible interpretations as options instead of open questions. Each
option is a testable hypothesis. The hypotheses ARE the analysis — by designing
good options, 80% of the work is done before the user answers.

```text
BAD:  "What kind of login do you want?"           ← open, high cognitive load
GOOD: "OAuth / Email+Password / SSO / Magic link" ← pick one, lower load
```

### Vague Mode Questions (5-8 total)

Batch up to 4 related questions per AskUserQuestion call. Each question resolves
one ambiguity category from Phase 1.

**Stop when**: All critical ambiguities resolved, OR user signals "good enough",
OR 8 questions reached.

### Unknown Mode Questions (7-10 total, 3 rounds)

| Round | Purpose                 | Questions | Key Trait                         |
| ----- | ----------------------- | --------- | --------------------------------- |
| R1    | Validate draft quadrant | 3-4       | Broad, one per quadrant boundary  |
| R2    | Drill weak spots        | 2-3       | Targeted, derived from R1 answers |
| R3    | Execution details       | 2-3       | Specific, optional if R2 suffices |

**CRITICAL**: R2 questions are generated from R1 answers. R3 from R2. **Never
use pre-prepared questions across rounds.**

R1 question targets:

| Quadrant | Pattern                       | Example                             |
| -------- | ----------------------------- | ----------------------------------- |
| KK       | "Is this really certain?"     | "Primary revenue source?" (options) |
| KU       | "Where's the weakest link?"   | "Which connection is weakest?"      |
| UK       | "What exists but isn't used?" | Based on context findings           |
| UU       | "What's the biggest fear?"    | Risk scenarios as options           |

R2 triggers from R1: compound answers (messy area), unexpected answers (draft
wrong), "Other" selected (outside frame).

### Metamedium Mode Questions (3-5 total)

Present the content/form fork question:

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

If "Explore form change" selected: ask 2-4 follow-up questions about
constraints, resources, and minimum viable form.

---

## Phase 3: Synthesis

### Vague Mode — Before/After Summary

```markdown
## Requirement Clarification Summary

### Before (Original)

"{original request verbatim}"

### After (Clarified)

**Goal**: [precise description] **Scope**: [included and excluded]
**Constraints**: [limitations, preferences] **Success Criteria**: [how to know
when done]

**Decisions Made**: | Question | Decision | |----------|----------| | [ambiguity
1] | [chosen option] |
```

### Unknown Mode — 4-Quadrant Playbook

**Read [playbook-template.md](./references/playbook-template.md) for the
complete output template.**

Generate structured playbook with:

- Current State Diagnosis (confirmed findings only)
- Quadrant Matrix (KK 60% / KU 25% / UK 10% / UU 5% — adjust per context)
- KK: Systematize
- KU: Design Experiments (each with diagnosis, experiment, success criteria,
  deadline, promotion condition, kill condition)
- UK: Leverage (fastest wins)
- UU: Set Up Antennas (detection + response)
- Strategic Decision: What to Stop (non-negotiable section)
- Execution Roadmap
- Core Principles (derived from conversation, not generic advice)

**Resource percentages (60/25/10/5) are defaults.** Adjust based on context —
e.g., a startup exploring product-market fit may allocate 40% KU and 30% KK.

### Metamedium Mode — Content/Form Analysis

```markdown
## Content/Form Analysis

**Current work**: [description] **Classification**: [CONTENT / FORM]

### Form Opportunity

|                      | Detail                                         |
| -------------------- | ---------------------------------------------- |
| **Alternative form** | [what it would look like]                      |
| **New properties**   | [what it enables that current form doesn't]    |
| **Minimum test**     | [smallest version to validate]                 |
| **Status**           | [exploring / noted for later / not applicable] |
```

If "Explore form change" was selected: include 2-3 concrete form alternatives
with new properties and minimum viable version for each.

> **The Metamedium Question** — When stuck or optimizing with diminishing
> returns: "What new form/medium could make this problem disappear?"

---

## Phase 4: Persist & Return

### Standalone Invocation

Ask whether to save the output to a file:

- Vague → suggest project-appropriate location
- Unknown → suggest `{topic}-known-unknown.md`
- Metamedium → append to deliverable or save standalone

### Sub-Workflow Return

Return structured output to the calling skill. **No side effects** — no file
saves, no skill invocations, no git operations. The caller decides what to do
with the output.

| Mode       | Return Structure                                              |
| ---------- | ------------------------------------------------------------- |
| vague      | `{ goal, scope, constraints, success_criteria, decisions[] }` |
| unknown    | `{ diagnosis, quadrants, roadmap, principles[] }`             |
| metamedium | `{ classification, form_opportunity, alternatives[] }`        |

---

## Composability Protocol

### How Other Skills Invoke /clarify

```text
Invoke /clarify:
  mode: vague
  context: "{ambiguous text from the user's request}"
  scope_limit: 5
  return_to: task-starter
```

### Contract

- **Input**: mode + context (required), scope_limit + return_to (optional)
- **Output**: Structured synthesis matching the mode
- **Boundaries**: /clarify resolves uncertainty and returns control. It does NOT
  save files, invoke other skills, create issues, or modify code.
- **Scope limit**: Overrides the mode's default question cap. Caller can
  constrain the depth to prevent question fatigue in a sub-workflow.

---

## Integration with External Skills

Routing recommendations for superpowers and other third-party skills.
Documentation only — these are suggestions, not enforced dependencies.

| External Skill       | When to Route to /clarify                                     | Mode    |
| -------------------- | ------------------------------------------------------------- | ------- |
| brainstorming        | Questions reveal strategic uncertainty, not feature decisions | unknown |
| executing-plans      | Mid-step uncertainty is about intent, not technical blocker   | vague   |
| systematic-debugging | "Bug" is correct code with wrong requirements                 | vague   |
| writing-plans        | Plan steps have ambiguous requirements forcing assumptions    | vague   |

---

## Rules

1. **Hypotheses, not open questions**: Every AskUserQuestion option is a
   testable hypothesis about the user's situation
2. **AskUserQuestion only**: NEVER ask clarifying questions in plain text
3. **Preserve intent**: Refine and sharpen, don't redirect or reinterpret
4. **Respect caps**: vague 5-8, unknown 7-10, metamedium 3-5
5. **Batch related questions**: Up to 4 per AskUserQuestion call
6. **Answers drive depth**: R2 from R1 answers, R3 from R2 (unknown mode)
7. **Draft is disposable**: Initial classifications are meant to be corrected
8. **Stop > Start**: Unknown mode must include "what to stop doing"
9. **No side effects in sub-workflow**: Return structured output only

## Anti-Patterns

| Anti-Pattern                         | Why It's Wrong                     | Fix                         |
| ------------------------------------ | ---------------------------------- | --------------------------- |
| Open questions ("What do you want?") | High cognitive load, vague answers | Use hypothesis options      |
| 5+ options per question              | Choice fatigue                     | Cap at 3-4 options          |
| Pre-prepared R2 questions            | Performative, not responsive       | Generate R2 from R1 answers |
| Equal depth on all quadrants         | Wastes time, loses focus           | Focus on weakest area       |
| Skipping "What to Stop"              | Adding without subtracting         | Always include stop section |
| Plain text questions                 | Bypasses structured tooling        | ALWAYS use AskUserQuestion  |
| Saving files in sub-workflow         | Side effects violate contract      | Return output to caller     |

## Known Failure Modes

| Symptom                           | Cause                               | Fix                                             |
| --------------------------------- | ----------------------------------- | ----------------------------------------------- |
| Wrong mode auto-detected          | Ambiguous context signals           | Accept explicit override; ask if unsure         |
| User fatigued by questions        | Exceeded cap or asked redundant Qs  | Enforce caps; stop when "good enough"           |
| Vague output after clarification  | Didn't resolve critical ambiguities | Check all categories from Phase 1 intake        |
| R2 repeats R1 questions           | Ignored R1 answers                  | R2 must drill INTO R1 answer, not re-ask        |
| Metamedium applied to simple task | Not everything needs form analysis  | Default to vague; metamedium needs clear signal |
| Sub-workflow modified files       | Forgot no-side-effects rule         | /clarify returns output only; caller acts       |
| Caller didn't specify mode        | Sub-workflow invoked without mode   | Always require mode in sub-workflow calls       |

## Quick Reference

```text
TRIGGER:   "/clarify" | "scope this" | "what am I missing" | "content vs form"
MODES:     vague (5-8 Qs) | unknown (7-10 Qs, 3 rounds) | metamedium (3-5 Qs)
TOOL:      AskUserQuestion ONLY — never plain text questions

DETECTION: Auto from context signals; explicit override with /clarify {mode}

PHASES:
  0. Detect    — mode selection (auto or explicit)
  1. Intake    — record trigger, categorize uncertainty
  2. Question  — hypothesis-as-options via AskUserQuestion
  3. Synthesize — mode-specific output
  4. Persist   — standalone: ask to save; sub-workflow: return to caller

SUB-WORKFLOW:
  Input:  mode (req), context (req), scope_limit, return_to
  Output: structured synthesis (no side effects)
  Contract: no file saves, no skill invocations, no code changes

BOUNDARY:
  /clarify = intent uncertainty (what to build, what's missing, what form)
  /investigate = technical uncertainty (why is it broken, root cause)
```
