# Commit Command

Analyze staged and unstaged changes, then create commits following Conventional
Commits for semantic-release.

## Arguments

`$ARGUMENTS`

## Commit Strategy

**Parse the arguments to determine mode:**

| Command      | Mode             | Behavior                                             |
| ------------ | ---------------- | ---------------------------------------------------- |
| `/commit`    | Atomic (default) | Multiple commits, each for logically related changes |
| `/commit -a` | All-in-one       | Single commit with all changes                       |

## Commit Message Format (Conventional Commits)

All commits MUST follow
[Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### Types (required)

| Type       | Description                          | Semantic Release         |
| ---------- | ------------------------------------ | ------------------------ |
| `feat`     | New feature                          | **Minor** (0.X.0)        |
| `fix`      | Bug fix                              | **Patch** (0.0.X)        |
| `docs`     | Documentation only                   | No release               |
| `style`    | Formatting, no code change           | No release               |
| `refactor` | Code restructure, no behavior change | No release               |
| `perf`     | Performance improvement              | **Patch**                |
| `test`     | Adding/updating tests                | No release               |
| `build`    | Build system or dependencies         | No release               |
| `ci`       | CI configuration                     | No release               |
| `chore`    | Maintenance tasks                    | No release               |
| `revert`   | Revert previous commit               | Depends on reverted type |

### Scope (optional but recommended)

Use the primary affected area:

- **Apps:** `api`, `worker`, `web`, `connector`, `guardrails`
- **Infra:** `k3s`, `docker`, `terraform`, `ansible`
- **Observability:** `grafana`, `prometheus`, `loki`, `tempo`
- **Docs:** `docs`, `readme`, `architecture`
- **Other:** `deps`, `config`, `scripts`

### Subject Rules

- Imperative mood: "add" not "added" or "adds"
- No period at the end
- Max 50 characters
- Lowercase first letter

### Breaking Changes

For breaking changes, append an exclamation mark after type/scope:

```text
feat(api)!: replace JWT auth with Keycloak OIDC

BREAKING CHANGE: All existing JWT tokens are invalidated.
Clients must re-authenticate via Keycloak.
```

### Footer (Issue & Breaking Change References)

Issue references go in the **footer**, not the subject line. The footer is
separated from the body by a blank line.

**Keywords:**

| Keyword               | Effect                     |
| --------------------- | -------------------------- |
| `Closes #N` / `Close` | Auto-closes issue on merge |
| `Fixes #N` / `Fix`    | Auto-closes issue on merge |
| `Refs #N` / `Ref`     | References without closing |

**Examples:**

```text
feat(api): add health check endpoint

Implement /health and /ready endpoints for k8s liveness
and readiness probes.

Closes #123
```

```text
fix(auth): handle expired refresh tokens

Refs #456
```

Multiple issues:

```text
feat(calendar): add multi-provider sync

Closes #487
Closes #492
BREAKING CHANGE: CalendarService.sync() signature changed
```

## Pre-flight Checks (before any commits)

Before staging or committing, perform these scope checks:

### Scope Check

1. Run `git rev-parse --show-toplevel` to get the CWD repo root
2. Run `git diff --cached --name-only` to list any already-staged files
3. Run `git status --porcelain` to see unstaged/untracked changes
4. For each file that will be committed, check if it belongs to the CWD repo:
   - Resolve symlinks: use `readlink -f <file>` or equivalent
   - Get the git repo root of the resolved path
   - Compare against the CWD repo root

**If files span multiple repos**, STOP and warn the user:

> Scope warning: staged files span multiple repos ({repo1}, {repo2}). This may
> cause cross-repo commits. Unstage files from other repos?

### Symlink Check

For each staged file, check if it is a symlink (`test -L <file>`):

1. Resolve the symlink to its real target
2. Verify the target file exists (warn if broken symlink)
3. Check if the target is in a different repo than CWD

**If symlink targets are outside the repo**, WARN the user:

> Symlink alert: {file} points to {target} (repo: {target_repo}). The symlink
> itself will be committed, but changes to the target belong to another repo.

**Skip these checks** when no symlinks are detected among staged files
(optimization for most repos).

---

## Process

### For Atomic Mode (default `/commit`)

1. Run `git status` and `git diff` to analyze all changes
2. Group changes by **context/feature/purpose**:
   - Same feature across files → one commit
   - Different features → separate commits
   - Docs separate from code changes
3. For each logical group:
   - `git add <relevant-files>`
   - `git commit` with semantic message
4. Run `git status` to verify clean state

### For All-in-One Mode (`/commit -a`)

1. Run `git status` and `git diff` to analyze all changes
2. Determine the **primary** change type (feat > fix > refactor > chore)
3. Stage all changes: `git add -A`
4. Create single commit with semantic message covering all changes
5. Run `git status` to verify

## Examples

### Atomic Mode (default)

```bash
# Changes: new API endpoint + updated tests + fixed typo in README

# Commit 1: Feature (with issue reference in footer)
git commit -m "$(cat <<'EOF'
feat(api): add health check endpoint

Closes #42
EOF
)"

# Commit 2: Tests (no issue — type alone is sufficient)
git commit -m "test(api): add health check endpoint tests"

# Commit 3: Docs (no issue needed)
git commit -m "docs(readme): fix typo in installation section"
```

### All-in-One Mode (`-a`)

```bash
# Same changes, single commit
git add -A
git commit -m "feat(api): add health check endpoint with tests"
```

## Important Rules

- NEVER skip the semantic type prefix
- NEVER use generic messages like "update files" or "fix stuff"
- NEVER commit secrets (.env, credentials, API keys) - warn user if detected
- Each message should explain WHY, not just WHAT
- Use HEREDOC for multi-line commit messages:

  ```bash
  git commit -m "$(cat <<'EOF'
  feat(api): add PII masking middleware

  Integrate Presidio for automatic PII detection and masking
  before content reaches LLM processing pipeline.

  Closes #234
  EOF
  )"
  ```

- If grouping is ambiguous in atomic mode, ask the user for clarification
