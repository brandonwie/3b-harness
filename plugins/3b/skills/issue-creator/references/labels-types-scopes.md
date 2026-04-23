# Labels, Types & Scopes Reference

Lookup tables for title types, scopes, issue types, labels, and GraphQL
commands. Use during Steps 1-6 when composing issue metadata.

## Title Types

| Type       | When to Use                           | GitHub Issue Type |
| ---------- | ------------------------------------- | ----------------- |
| `feat`     | New feature or capability             | Feature           |
| `fix`      | Bug fix                               | Bug               |
| `perf`     | Performance improvement               | Feature           |
| `security` | Security vulnerability or fix         | Bug               |
| `docs`     | Documentation changes                 | Task              |
| `refactor` | Code refactoring (no behavior change) | Task              |
| `test`     | Testing changes                       | Task              |
| `chore`    | Maintenance tasks                     | Task              |
| `build`    | Build/dependency changes              | Task              |

## Scope Table

| Scope          | Area                                   |
| -------------- | -------------------------------------- |
| `sync`         | Calendar sync (Google, Outlook, Apple) |
| `queue`        | BullMQ queues, background jobs         |
| `auth`         | Authentication, OAuth                  |
| `subscription` | LemonSqueezy, payments                 |
| `websocket`    | WebSocket, real-time                   |
| `block`        | Block entity operations                |
| `calendar`     | Calendar entity operations             |
| `recurrence`   | Recurring events                       |
| `notification` | Push notifications, webhooks           |
| `migration`    | Database migrations                    |
| `api`          | REST API endpoints                     |
| `infra`        | AWS, Docker, deployment                |

## GitHub Issue Types

**This is NOT a label** - it's GitHub's native Issue Type field.

| Issue Type  | When to Use                       | Title Types                                  |
| ----------- | --------------------------------- | -------------------------------------------- |
| **Bug**     | Something is broken, needs fixing | `fix`, `security`                            |
| **Feature** | New capability or enhancement     | `feat`, `perf`                               |
| **Task**    | Maintenance, refactoring, chores  | `chore`, `refactor`, `docs`, `test`, `build` |

### Fetching Type IDs (GraphQL)

Type IDs are repository-specific. Fetch them dynamically:

```bash
gh api graphql -f query='
{
  repository(owner: "{OWNER}", name: "{REPO}") {
    issueTypes(first: 10) {
      nodes { id name }
    }
  }
}'
```

### Setting Issue Type

After creating the issue, set the type via GraphQL:

```bash
# Get issue node ID
ISSUE_ID=$(gh api graphql -f query='
{
  repository(owner: "{OWNER}", name: "{REPO}") {
    issue(number: {NUMBER}) { id }
  }
}' --jq '.data.repository.issue.id')

# Set type
gh api graphql -f query="
mutation {
  updateIssue(input: {id: \"$ISSUE_ID\", issueTypeId: \"{TYPE_ID}\"}) {
    issue { number issueType { name } }
  }
}"
```

## Label Strategy

### Domain Labels (if applicable)

| Label         | When                         |
| ------------- | ---------------------------- |
| `sync`        | Calendar sync related        |
| `queue`       | Queue/background job changes |
| `migration`   | Database migrations          |
| `testing`     | Test coverage                |
| `ci_cd`       | CI/CD workflows              |
| `build`       | Dependencies, packages       |
| `security`    | Security issues              |
| `performance` | Performance improvements     |

### Priority Labels (REQUIRED)

| Label             | Criteria                                              |
| ----------------- | ----------------------------------------------------- |
| `priority:high`   | Production bugs, security issues, blocking other work |
| `priority:medium` | Important features, non-critical bugs, upcoming needs |
| `priority:low`    | Nice-to-have, future improvements, minor enhancements |

### Status Labels (optional)

| Label    | When                                          |
| -------- | --------------------------------------------- |
| `watch`  | On hold, waiting for decision                 |
| `hotfix` | Urgent production fix (implies priority:high) |
