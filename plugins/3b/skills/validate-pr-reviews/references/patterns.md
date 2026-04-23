# Confusion Patterns & Why Analysis

Reference for classifying INVALID reviews during Phase 3 (Handle
Classifications). Use this to identify which pattern caused the AI reviewer's
confusion and to select the appropriate reinforcing comment template.

## 8 Known Confusion Patterns

| Pattern                           | Description                                      | How to Recognize                                                      |
| --------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------- |
| **Stale Diff**                    | Agent reviews outdated code version              | Claims feature is "missing" but it exists in current code             |
| **Variable Reassignment**         | Agent misreads assignment flow                   | Sees destructuring, assumes all values from same source               |
| **Cross-File Blindness**          | Agent doesn't check related files                | Asks about behavior defined in another file                           |
| **Cascade Ignorance**             | Agent doesn't understand ORM cascades            | Flags "missing" error handling that ORM handles                       |
| **Intentional Design**            | Agent flags intentional trade-off                | Suggests "fix" that would break documented design                     |
| **Feature Exists**                | Agent claims missing implementation              | Implementation exists, agent didn't read full file                    |
| **Webhook Flow Misunderstanding** | Agent suggests transactions for webhook handlers | Asks for transaction wrapping when external service already committed |
| **YAGNI Suggestion**              | Agent recommends premature optimization          | Suggests performance monitoring/caching for low-traffic paths         |

## Comment Templates by Pattern

| Pattern                       | Comment Template                                                                                                                                     |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stale Diff / Feature Exists   | `// NOTE: [Feature] IS [implemented/handled] [here/below] - [brief description]`                                                                     |
| Variable Reassignment         | `// NOTE: Explicitly set to X (not from Y) because [reason]`                                                                                         |
| Cross-File Blindness          | `// NOTE: Related logic in [file:line] handles [concern]`                                                                                            |
| Cascade Ignorance             | `// NOTE: cascade:true handles [operation] - no manual handling needed`                                                                              |
| Intentional Design            | `// NOTE: [Pattern] intentionally [omitted/designed this way] - [reason]`                                                                            |
| Webhook Flow Misunderstanding | `// NOTE: This is intentionally NOT wrapped in a transaction because [external service] already committed. [Retry mechanism] handles sync failures.` |
| YAGNI Suggestion              | `// NOTE: [Optimization] intentionally deferred — current scale does not justify complexity.`                                                        |

### Generic Fallback Template

When no specific pattern template fits, use:

`// NOTE: [What reviewer flagged] is [not applicable/handled/intentional] because [reason]. See [file:line] for details.`

This ensures every INVALID review gets a reinforcing comment, even for novel
confusion patterns not yet catalogued.

## Root Cause Categories

| Category          | Description                              | Example                                         |
| ----------------- | ---------------------------------------- | ----------------------------------------------- |
| Missing Context   | Cross-file, cascade, or flow not visible | Agent didn't see related file                   |
| Stale Information | Outdated diff, feature added later       | Code exists but agent saw old version           |
| Misread Code      | Variable reassignment, wrong line        | Agent misunderstood assignment flow             |
| Philosophical     | YAGNI, intentional design trade-off      | Agent suggests "improvement" we chose not to do |

**Note:** Philosophical patterns (YAGNI, Intentional Design) still require
reinforcing comments. "User decision" does not exempt the item — the comment
prevents the same AI reviewer from flagging it again in the next round.

## 5W1H Why Analysis Template

Complete this for EACH INVALID or SKIPPED review:

```markdown
### Why Analysis: Comment #{N}

| 5W1H      | Field             | Content                                     |
| --------- | ----------------- | ------------------------------------------- |
| **What**  | Review Comment    | "{exact comment from reviewer}"             |
| **What**  | Claimed Issue     | What reviewer thought was wrong             |
| **What**  | Actual Reality    | What the code actually does                 |
| **Why**   | Confusion Pattern | {one of 8 patterns} OR "NEW: {description}" |
| **Why**   | Root Cause        | Why reviewer couldn't see the truth         |
| **How**   | Prevention        | What code comment will prevent this         |
| **Who**   | Agent             | Which AI reviewer (Claude/Copilot/Codex)    |
| **Where** | Location          | `file:line` where the comment was flagged   |
| **When**  | Round             | Validation round number and date            |

**Root Cause Category:** {category from above}
```
