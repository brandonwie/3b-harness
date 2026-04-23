---
name: interview
description: >
  Portable Socratic interview to clarify vague requirements before implementation.
  Use when the user says "interview me", "clarify requirements", "scope this",
  "help me think through this feature", or asks for a requirements interview.
---

# /interview

Run a direct, portable interview flow. Do not rely on Ouroboros MCP tools, deferred-tool loading, update checks, or Seed generation commands.

## Goals

- Reduce ambiguity across the core requirement dimensions:
  - goal
  - constraints
  - success criteria
  - brownfield context when relevant
- Expose hidden assumptions before implementation starts.
- Keep the conversation in interview mode until the request is clear enough to hand off as a spec or implementation brief.

## Behavior

1. Ask exactly one concrete question at a time.
2. Stay in questions-only mode while interviewing. Do not design or implement unless the user explicitly ends the interview.
3. Start broad, then narrow:
   - first resolve the main goal and intended outcome
   - then constraints and boundaries
   - then success criteria and verification
   - then edge cases or non-goals
4. If the context is brownfield, focus on intent and change decisions rather than rediscovering what exists.
5. Keep multiple ambiguity tracks visible. Do not fixate on one subtopic for too many rounds.

## Enriched answers

The caller may provide answers prefixed with:

- `[from-code]` for factual codebase state
- `[from-user]` for human decisions
- `[from-research]` for external facts

Use those as context. Ask follow-up questions about decisions, tradeoffs, and expected outcomes.

## Stop conditions

Prefer ending the interview when these are explicit enough to hand off:

- what is being built or changed
- what is out of scope
- what constraints matter
- how success will be judged

If the user signals "that’s enough" or "let’s proceed", ask a final closure question if any major ambiguity remains; otherwise summarize the clarified requirement and transition.
