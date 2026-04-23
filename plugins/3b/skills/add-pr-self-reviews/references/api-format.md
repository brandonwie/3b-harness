# API Format & Error Handling

Use during Phase 5 (Create PR Review with Inline Comments) for the correct JSON
submission approach and troubleshooting API errors.

## CRITICAL: JSON Format (Learned from Error)

**WRONG approach (causes HTTP 422 error):**

```bash
# ❌ This DOES NOT work - gh api -f doesn't create proper JSON arrays
gh api repos/{owner}/{repo}/pulls/{PR}/reviews -X POST \
  -f event="COMMENT" \
  -f body="Review body" \
  -f "comments[0][path]=file.ts" \
  -f "comments[0][line]=123" \
  -f "comments[0][body]=Comment"

# Error: "For 'properties/comments', {...} is not an array. (HTTP 422)"
```

**CORRECT approach (write JSON file, then use --input):**

```bash
# ✅ Step 1: Write JSON to a temp file using the Write tool
# (Use the Write tool to create /tmp/pr-review-{PR}.json with proper JSON)

# ✅ Step 2: Submit via --input flag with file path
gh api repos/{owner}/{repo}/pulls/{PR}/reviews \
  -X POST --input /tmp/pr-review-{PR}.json

# ✅ Step 3: Clean up temp file
rm /tmp/pr-review-{PR}.json
```

**Why file-based approach (NOT heredoc):**

- `gh api -f` with bracket notation creates malformed JSON
- GitHub API expects `comments` to be a proper JSON array
- **CRITICAL:** Heredoc causes `HTTP 400` when body contains Korean/Unicode
- Writing to a file with the Write tool preserves UTF-8 encoding correctly
- `--input /path/to/file` reads the file directly without shell encoding issues

**CRITICAL: Always use the Write tool + --input file approach.** **NEVER use
heredoc piping for review JSON with non-ASCII content.**

## JSON Escaping Rules

| Character    | Escape As | Example                          |
| ------------ | --------- | -------------------------------- |
| Double quote | `\"`      | `"body": "Use \"this\" pattern"` |
| Newline      | `\n`      | `"body": "Line 1\nLine 2"`       |
| Backslash    | `\\`      | `"body": "path\\to\\file"`       |
| Tab          | `\t`      | (avoid, use spaces)              |

## Error Handling

### Line Number Issues

If a line number doesn't match the diff:

1. Re-read the file to get current line numbers
2. Verify the line is in the PR diff (not just context)
3. Adjust to nearest relevant line in the diff

### API Errors

| Error         | Cause                   | Solution                       |
| ------------- | ----------------------- | ------------------------------ |
| 422 Invalid   | Bad JSON format         | Check escaping, use `--input`  |
| 404 Not Found | Wrong PR number or path | Verify PR exists and file path |
| 403 Forbidden | No write access         | Check GitHub permissions       |

### Fallback

If inline comments fail, create a single review comment with all explanations
formatted as a list with file:line references.

## Lessons Learned (PR #644)

### Error: HTTP 422 with `-f comments[0][path]` syntax

**Problem:** Using `gh api -f "comments[0][path]=..."` does NOT create a JSON
array.

**Solution:** Use Write tool + `--input` to submit proper JSON.

### Target Line Verification

**Problem:** Comments placed on wrong lines appear in unexpected locations.

**Solution:** Always read the actual file to get current line numbers, then
verify the line is in the PR diff (added/changed lines only).
