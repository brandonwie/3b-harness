# API Reference for PR Review Validation

Commands for fetching PR comments from GitHub. Use these during Phase 1 (Fetch &
Persist Reviews) when gathering review data.

## Issue Comments (General PR Comments)

**Fetch all issue comments:**

```bash
gh api repos/{owner}/{repo}/issues/{PR}/comments
```

**Fetch issue comments since a date (Round 2+):**

```bash
gh api "repos/{owner}/{repo}/issues/{PR}/comments?since={YYYY-MM-DDTHH:MM:SSZ}"
```

_Use the previous round's date from the round file header. The `since` parameter
filters by `updated_at`, so edited comments resurface correctly._

**Fetch AI bot comments only:**

```bash
gh api repos/{owner}/{repo}/issues/{PR}/comments \
  --jq '[.[] | select(.user.login | test("claude\\[bot\\]|copilot|codex|github-actions\\[bot\\]"))]'
```

**Fetch latest comment from specific bot:**

```bash
gh api repos/{owner}/{repo}/issues/{PR}/comments \
  --jq '[.[] | select(.user.login == "claude[bot]")] | last'
```

## Review Thread Comments (Inline Code Comments)

**Fetch unresolved review threads (GraphQL - recommended):**

```bash
gh api graphql -f query='
{
  repository(owner: "{owner}", name: "{repo}") {
    pullRequest(number: {PR}) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          comments(first: 10) {
            nodes {
              id
              body
              path
              line
              author { login }
            }
          }
        }
      }
    }
  }
}'
```

**Important:** The `id` fields on both `reviewThreads.nodes` and
`comments.nodes` are needed for replying to and resolving threads in Phase 3.

**Fetch review comments (REST - fallback):**

```bash
gh api repos/{owner}/{repo}/pulls/{PR}/comments
```

## Responding to Comments

**Reply to a review thread comment:**

```bash
gh api repos/{owner}/{repo}/pulls/{PR}/comments/{comment_id}/replies \
  -f body="Fixed in commit abc123"
```

**Reply to an issue comment (add new comment):**

```bash
gh api repos/{owner}/{repo}/issues/{PR}/comments \
  -f body="Addressed in commit abc123"
```

## Resolving Review Threads (Copilot)

After dismissing an INVALID Copilot review, **resolve the thread** so it doesn't
reappear in the next fetch. This requires the GraphQL thread ID.

**Step 1: Get the thread ID from the fetch query above.** The `reviewThreads`
query returns thread nodes — capture the `id` field.

**Step 2: Resolve the thread:**

```bash
gh api graphql -f query='
mutation {
  resolveReviewThread(input: {threadId: "{thread_id}"}) {
    thread {
      isResolved
    }
  }
}'
```

**Step 3: Reply before resolving (recommended):**

```bash
# First reply to the thread with the dismissal reason
gh api repos/{owner}/{repo}/pulls/{PR}/comments/{comment_id}/replies \
  -f body="Dismissed: {Pattern Name} — {reason}. Reinforcing comment added at {file:line}."

# Then resolve the thread
gh api graphql -f query='
mutation {
  resolveReviewThread(input: {threadId: "{thread_id}"}) {
    thread {
      isResolved
    }
  }
}'
```

**Note:** The `thread_id` and `comment_id` come from the Phase 1 fetch query
above, which already includes `id` fields on both `reviewThreads.nodes` and
`comments.nodes`.

## Minimizing Issue Comments (Phase 7.5)

After processing is complete, minimize addressed AI review comments and trigger
commands to keep the PR conversation clean.

**Identify trigger commands (user-typed review invocations):**

```bash
gh api repos/{owner}/{repo}/issues/{PR}/comments \
  --jq '[.[] | select(.body | test("^\\s*/(?:review|claude-review)"; "i")) | {id: .id, node_id: .node_id, body: .body, user: .user.login}]'
```

**Identify bot review comments:**

```bash
gh api repos/{owner}/{repo}/issues/{PR}/comments \
  --jq '[.[] | select(.user.login | test("claude\\[bot\\]|github-actions\\[bot\\]")) | select(.is_minimized == false) | {id: .id, node_id: .node_id, user: .user.login}]'
```

**Minimize a comment (GraphQL):**

```bash
gh api graphql -f query='
mutation {
  minimizeComment(input: {subjectId: "{node_id}", classifier: RESOLVED}) {
    minimizedComment {
      isMinimized
      minimizedReason
    }
  }
}'
```

`classifier` options: `RESOLVED` (default for addressed reviews), `OUTDATED`,
`DUPLICATE`, `OFF_TOPIC`, `ABUSE`, `SPAM`. Always use `RESOLVED`.

**Check if already minimized:**

The REST API returns `is_minimized` field on issue comments. Filter with
`select(.is_minimized == false)` to skip already-hidden comments.

**Note:** `node_id` (NOT `id`) is required for the GraphQL mutation. The REST
API returns both fields.

## Filtering Unresolved Threads

GitHub's GraphQL API does not support `isResolved` as a query argument on
`reviewThreads`. Filter client-side after fetch:

```bash
# Using jq to filter unresolved threads only
gh api graphql -f query='...' \
  | jq '.data.repository.pullRequest.reviewThreads.nodes
        | map(select(.isResolved == false))'
```

This prevents already-resolved threads from appearing in the classification list
and wasting processing time.

## Round 2+ Fetch Optimization

Avoid re-fetching already-processed comments in subsequent rounds:

| Comment Type   | Optimization                                      | Savings                             |
| -------------- | ------------------------------------------------- | ----------------------------------- |
| Issue comments | `since` parameter with previous round's date      | Skips large Claude review bodies    |
| Review threads | `isResolved=false` filter (already in base query) | Excludes resolved from prior rounds |

**Issue comments** are the primary optimization target — Claude's structured
reviews can be 2000+ tokens, and re-fetching them every round wastes context
window.

**Review threads** are already efficient: threads resolved in previous rounds
(INVALID → resolved, VALID → fixed+resolved) are excluded by the `isResolved`
filter. DEFERRED threads intentionally stay unresolved and ARE re-fetched —
Phase 1.5 dedup handles these.
