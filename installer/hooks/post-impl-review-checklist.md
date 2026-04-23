# Post-Implementation Review Checklist

Checklist for the automatic post-implementation review agent. This file is read
by `post-implementation-review-hook.py` and embedded in the review advisory.

The review agent receives this checklist and reports findings with severity
levels. It does NOT auto-fix — the user decides what to act on.

## Checklist Items

### 1. Error Handling

- No swallowed exceptions (empty catch blocks without re-throw or logging)
- Async errors are awaited or have `.catch()` handlers
- Error messages are actionable (include what failed and why)
- No `console.log` used for error reporting in production code

### 2. Edge Cases

- Null/undefined inputs handled at function boundaries
- Empty collections handled (empty arrays, empty strings, empty objects)
- Off-by-one errors in loops, slicing, or index access
- Boundary values considered (0, -1, MAX_INT, empty string)

### 3. Type Safety

- No `any` type without explicit justification comment
- No unsafe type assertions without a runtime guard (language-specific —
  e.g., TS: `as Type`, `!` non-null; Rust: `unwrap()`; Python: silent
  `cast()`). If an assertion is unavoidable, pair it with a guard.
- Generic constraints are tight enough to prevent misuse
- Function return types match all code paths

### 4. Naming

- Variables describe what they hold, not how they're used
- Functions describe what they do (verb + noun)
- No single-letter variables outside loop counters
- Boolean names start with is/has/should/can

### 5. Function Size

- Single responsibility per function
- Functions under 30 lines (flag exceptions for review)
- One level of abstraction per function
- No deeply nested conditionals (>3 levels)

### 6. Side Effects

- No hidden state changes (function modifies external state without its name
  indicating it)
- Pure functions where possible (same input = same output)
- Side effects documented in function name or JSDoc

### 7. Test Coverage

- Every new public method has at least one test
- Edge cases from item 2 are covered in tests
- Test names describe the behavior being tested
- No test code that tests implementation details instead of behavior

### 8. Security

- No hardcoded secrets, API keys, or credentials
- Input validation on system boundaries (user input, API responses)
- No SQL/command injection vectors (string interpolation in queries)
- Sensitive data not logged or exposed in error messages

### 9. Algorithmic Efficiency

- Unnecessary repeated iterations over the same collection?
- O(n²) or worse where O(n) is achievable (nested loops, indexOf in loop)?
- Using Array where Set/Map would give O(1) lookups?
- Filtering/transforming in application code when the DB query could do it?
- Large data sets processed without batching?

### 10. Simplicity & Consistency

- Is the solution the simplest that works? No premature abstraction?
- Does the code follow existing patterns in the same module/directory?
- Could someone unfamiliar with the codebase understand this in one read?
- Is the code easy to test in isolation? (No hidden dependencies)
- Is the code easy to refactor? (No tight coupling to unrelated modules)

### 11. Observability

- Are logs placed at meaningful boundaries (service entry, error paths, external
  calls), not sprinkled everywhere?
- Log level appropriate? (error for failures, warn for recoverable issues, debug
  for dev-only — never info-spam for happy paths)
- Do logs include enough context to debug (IDs, operation name) without
  including sensitive data (passwords, tokens, PII)?
- No `console.log` left from debugging?

### 12. Documentation Quality

- Do new/modified public functions have JSDoc with `@param` and `@returns`?
- Do inline comments explain WHY, not WHAT? (No code-repeating comments)
- If complex logic was added, is there a reference to where the full explanation
  lives (README, ADR, issue link)?
- Are `TODO`/`FIXME` comments tied to an issue number?

## Severity Levels

| Level    | Definition                                  | Action                |
| -------- | ------------------------------------------- | --------------------- |
| CRITICAL | Security vulnerability or data loss risk    | Must fix before merge |
| HIGH     | Bug or logic error that will cause failures | Should fix            |
| MEDIUM   | Code quality issue that hinders maintenance | Consider fixing       |
| LOW      | Style or naming suggestion                  | Optional              |
