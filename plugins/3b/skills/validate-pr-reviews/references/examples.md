# Example Session & Classification Flows

Worked examples for reference during validation. Use these to calibrate
classification decisions and understand expected workflow.

## Full Example Session

**User says:** "validate pr reviews"

**Flow:**

1. Load config + resolve folder: `{actives_path}/consolidate-analytics-api/`
2. Count existing validation files → Round 3
3. Get PR number and repo info
4. Fetch claude[bot] issue comments (comprehensive reviews)
5. Parse Claude's review — extract items from "Issues & Recommendations"
6. Fetch unresolved review threads (Copilot inline comments)
7. Create `3_validate_pr_review.md` with all extracted items
8. Present each item for classification
9. User classifies: 3 VALID BUG, 1 GOOD-TO-HAVE, 1 CONTROVERSIAL, 3 INVALID
10. CONTROVERSIAL: Present For/Against analysis → user re-classifies as SKIP
11. Ask user for GOOD-TO-HAVE: Fix 1
12. Fix 4 issues (3 bugs + 1 good-to-have)
13. Update corresponding test files
14. For 3 INVALID: Document patterns, add code comments, reply+resolve on GitHub
15. For 1 SKIPPED CONTROVERSIAL: Add reinforcing comment with discussion
    reasoning, reply+resolve on GitHub
16. Phase 5.5: Verify — 4 comments added, 7 GitHub replies, 7 threads resolved →
    PASS
17. Commit each fix separately (one fix = one commit, source + test), push
18. Reply "Fixed in {hash}" on 4 VALID threads, resolve them
19. Update tracking file, present report
20. Ask if ready for next round

## INVALID Flow Examples

### Example 1: Variable Reassignment Pattern

```text
Agent flags: "resyncOccurred can be undefined after retry"
Pattern:     Variable Reassignment
Analysis:    Agent saw destructuring, assumed all values come from retryResult
Reality:     Line 327 explicitly sets resyncOccurred = true
Action:      Add reinforcing comment:

// NOTE: Explicitly set to true (not from retryResult) because 410 recovery IS a resync event.
resyncOccurred = true;
```

### Example 2: Stale Diff / Feature Exists Pattern

```text
Agent flags: "CRITICAL: resyncRequired not handled in sync-blocks.helper.ts"
Pattern:     Stale Diff / Feature Exists
Analysis:    Agent reviewing outdated diff, not current code
Reality:     Line 232-247 destructures AND handles resyncRequired with full recovery flow
Action:      Add reinforcing comment:

// NOTE: resyncRequired IS handled below (line ~247) - triggers full 410 recovery flow
const { resyncRequired } = findEventsResult;
```

### Example 3: Feature Exists Pattern

```text
Agent flags: "CRITICAL: accessRole parameter missing from findEvents"
Pattern:     Feature Exists
Analysis:    Agent didn't read full function signature
Reality:     Line 461 has accessRole?: CalendarAccessRole parameter
Action:      Add reinforcing comment in JSDoc:

/**
 * NOTE: accessRole parameter EXISTS and is used for ACL-aware 410 recovery.
 */
accessRole?: CalendarAccessRole,
```

### Example 4: Webhook Flow Misunderstanding Pattern

```text
Agent flags: "softDeleteAllByUserId not wrapped in transaction with subscription creation"
Pattern:     Webhook Flow Misunderstanding
Analysis:    Agent suggests atomicity for webhook handler operations
Reality:     In webhook flows:
             1. External service (LemonSqueezy) already committed the subscription
             2. Our local operation is just syncing state
             3. If sync fails, webhook redelivery handles it
             4. Rolling back old subscriptions would be wrong - they should stay deleted
Action:      Add reinforcing comment:

/**
 * NOTE: This is intentionally NOT wrapped in a transaction with subscription creation.
 * If subscription creation fails after this soft-delete, the user's old expired
 * subscriptions remain soft-deleted. This is acceptable because:
 * 1. The new subscription already exists on LemonSqueezy's side
 * 2. Webhook redelivery or manual sync will eventually create the local record
 * 3. Old expired subscriptions should be cleaned up regardless
 */
await this.subscriptionRepo.softDeleteAllByUserId(userId);
```

## CONTROVERSIAL Flow Examples

### Example 5: Retry Logic Suggestion → SKIP (YAGNI-adjacent)

```text
Agent flags: "Add retry logic for external API call in syncEvents"
Classification: CONTROVERSIAL (debatable — could be correct in some contexts)

Discussion:
  For:      External APIs can fail transiently; retry improves reliability
  Against:  This is a webhook handler — webhook redelivery IS the retry mechanism.
            Adding retry inside the handler adds complexity with no benefit.
  Context:  Retry logic makes sense for user-facing API calls, but webhook
            handlers already have built-in retry via the external service.
  Confidence: High (clear architectural reason against)

User decision: → Skip
Action:   Add reinforcing comment:
  // NOTE: No retry logic needed — webhook redelivery handles transient failures.
  // Adding retry here would duplicate the built-in retry mechanism of LemonSqueezy webhooks.
Round file: CONTROVERSIAL → SKIP (webhook redelivery is the retry mechanism)
```

### Example 6: Pattern Change Suggestion → VALID IMPROVEMENT

```text
Agent flags: "Replace manual array filter+map with flatMap for cleaner code"
Classification: CONTROVERSIAL (uncertain — could be stylistic or a real improvement)

Discussion:
  For:      flatMap is more idiomatic, eliminates intermediate array allocation,
            and reduces cognitive load (one operation instead of two)
  Against:  Current code is readable and works; change is cosmetic
  Context:  The method processes 500+ items in production. flatMap avoids
            creating the intermediate filtered array, reducing GC pressure.
  Confidence: Medium (performance benefit is real but minor)

User decision: → VALID IMPROVEMENT
Action:   Fix immediately, update tests
Round file: CONTROVERSIAL → VALID IMPROVEMENT
```

### Example 7: Error Handling Gap → INVALID (Feature Exists)

```text
Agent flags: "Missing error handling for null calendarId in syncBlocks"
Classification: CONTROVERSIAL (might be a real gap or might be handled elsewhere)

Discussion:
  For:      If calendarId is null, downstream calls will fail with cryptic errors
  Against:  CalendarId is validated at the DTO layer (line 42: @IsNotEmpty())
            and the service method has a guard clause (line 156: if (!calendarId))
  Context:  The null check exists at two prior layers. By the time we reach
            syncBlocks, calendarId is guaranteed non-null by the type system
            AND runtime validation.
  Confidence: High (feature exists at multiple layers)

User decision: → INVALID
Action:   Full 5-step INVALID workflow (Pattern: Feature Exists)
  // NOTE: calendarId is validated at DTO layer (@IsNotEmpty) and service
  // guard clause (line 156). Null is impossible here.
Round file: CONTROVERSIAL → INVALID (Feature Exists — validated at DTO + service layers)
```
