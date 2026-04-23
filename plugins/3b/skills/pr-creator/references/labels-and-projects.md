# Label Discovery & Project Selection

Use during Step 4 (Select Labels) and Step 5 (Ask About Project) for detailed
discovery, mapping, and error recovery procedures.

## Label Discovery

### Step 4a: Check Available Labels First

```bash
# List available labels in the repository
gh label list --limit 100
```

### Step 4b: Universal Labels (Work Anywhere)

| Label           | When to Use                |
| --------------- | -------------------------- |
| `bug`           | Fixing something broken    |
| `enhancement`   | New feature or improvement |
| `documentation` | Docs changes only          |

### Step 4c: Priority Labels (If Available)

| Label                     | Criteria                                        |
| ------------------------- | ----------------------------------------------- |
| `priority:high` or `P0`   | Production bugs, security issues, blocking work |
| `priority:medium` or `P1` | Important features, non-critical bugs           |
| `priority:low` or `P2`    | Nice-to-have, minor enhancements                |

If priority labels don't exist: skip with warning, don't create them.

### Step 4d: Domain Labels (From PROJECT-CONFIG.md)

Only use domain-specific labels if defined in PROJECT-CONFIG.md. If no domain
labels defined, use only universal labels.

### Step 4e: Commit Type to Label Mapping

| Title Type | Primary Label   | Fallback      |
| ---------- | --------------- | ------------- |
| `feat`     | `enhancement`   | -             |
| `fix`      | `bug`           | -             |
| `docs`     | `documentation` | -             |
| `perf`     | `performance`   | `enhancement` |
| `security` | `security`      | `bug`         |
| `refactor` | `enhancement`   | -             |
| `test`     | `testing`       | `enhancement` |
| `chore`    | `build`         | `enhancement` |
| `ci`       | `ci_cd`         | `enhancement` |

### Step 4f: Graceful Degradation

```text
Label application order:
1. Try exact label → Success
2. Try fallback label → Success
3. Use 'enhancement' → Success
4. No labels available → Continue with WARNING
```

**Never fail PR creation due to missing labels.**

## Project Selection

### Step 5a: Discover Available Projects

```bash
gh project list --owner {OWNER} --limit 10
```

### Step 5b: Check PROJECT-CONFIG.md for Default

Use `github.project_name` and `github.project_number` from config as the
suggested default option.

### Step 5c: Present Options to User (ALWAYS)

**CRITICAL:** Even if there's an obvious default, ASK the user. Never
auto-assign.

### Step 5d: Handle Edge Cases

| Scenario                         | Action                                              |
| -------------------------------- | --------------------------------------------------- |
| No projects found                | Ask: "No projects found. Continue without project?" |
| User selects "None"              | Skip project assignment, continue with PR           |
| API error                        | Warn user, continue without project                 |
| Config has project but API fails | Use config value, warn about potential mismatch     |

## Error Recovery

### Label Failures

Try fallback label → skip with warning → continue PR creation.

### Project Failures

Warn user about error → ask to continue without project → complete PR.

### Korean Translation Failures

Create PR with English-only body → add TODO comment → warn user.

### Partial Success Output

Report clearly what succeeded and what had warnings.
