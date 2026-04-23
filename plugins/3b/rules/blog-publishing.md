---
paths:
  - "knowledge/**"
  - "scripts/**"
---

# Blog Publishing Integration

Knowledge entries can be synced to a maintainer-owned blog. This section
documents the workflow and decision criteria. Examples below use
`{blog_domain}` as a placeholder — substitute your own blog's domain (and
matching repo folder) when configuring the sync script.

## Three Types of Links (IMPORTANT)

| Type          | Purpose                           | Storage      | Example                     |
| ------------- | --------------------------------- | ------------ | --------------------------- |
| `references:` | External URLs for credibility     | Stored       | Official docs, RFCs, GitHub |
| `related:`    | Internal Zettelkasten connections | Stored       | Links to other 3B files     |
| `backlinks:`  | Reverse connections               | **Computed** | NOT stored in files         |

**Why backlinks are computed:**

- Manual backlinks drift and become unmaintainable
- Forward links (`related:`) are the source of truth
- Graph tools compute backlinks from forward links (Obsidian-style)
- **NEVER add `backlinks:` to frontmatter** - remove if found

## Publishability Criteria

```text
Decision Tree:
├── Category is moba/? → publishable: false (company-specific)
├── Contains proprietary info? → publishable: false
├── Contains company examples? → publishable: "review" (generalize examples)
├── No external references? → publishable: "review" (needs-references)
├── Only experience refs? → publishable: "review" (needs external ref)
└── Has official/authoritative ref? → publishable: true
```

## Generalizing Company Examples

When knowledge contains company-specific examples but the **concept is
transferable**, generalize the examples to make them blog-publishable:

| Type          | Company-Specific         | Generalized            |
| ------------- | ------------------------ | ---------------------- |
| Project IDs   | `714756`                 | `{PROJECT_ID}`         |
| S3 buckets    | `arch-amplitude-storage` | `amplitude-raw-bucket` |
| Internal URLs | `api.company.com`        | `api.example.com`      |
| Emails        | `john@company.com`       | `user@example.com`     |
| DB names      | `moba_production`        | `app_production`       |

**Use `{PLACEHOLDER}` syntax** for values readers should replace.

After generalizing, update:

```yaml
blog:
  publishable: true # was "review"
  exclude_reason: null # was "contains-company-examples"
```

## Publishing Workflow

1. **During /wrap**: Blog metadata is auto-added to new knowledge files
2. **Review**: Check files with `publishable: "review"` and fix issues
3. **Mark ready**: Set `blog.ready: true` when content is polished
4. **Sync**: Run sync script to copy to blog repo

**Sync Script Location** (replace `{blog_domain}` with your blog's folder):
`~/dev/personal/{blog_domain}/scripts/sync-from-3b.ts`

```bash
# Dry run (preview what would sync)
cd ~/dev/personal/{blog_domain}
deno run --allow-read --allow-write --allow-env scripts/sync-from-3b.ts --dry-run

# Apply sync
deno run --allow-read --allow-write --allow-env scripts/sync-from-3b.ts
```

**Sync filters for:**

- `blog.publishable === true`
- `blog.ready === true`
- Has at least one `official` or `authoritative` reference
- `status === "completed"`

**After sync:** Source file's `blog.published_at` and `blog.last_synced` are
updated.

## Resync Lifecycle

When `/wrap` enriches a published knowledge entry (adds content, not just
`when_used:` metadata), it sets `blog.needs_resync: true`. This flag is:

- **Set by**: `/wrap` Step 5 (when content or references change on a published
  entry)
- **Cleared by**: `/blog-publish` sync (after the entry is re-synced to the
  blog) and by `sync-from-3b.ts` script
- **Not set for**: metadata-only updates (`when_used:` additions without content
  changes)

Detection:

```bash
grep -r "needs_resync: true" knowledge/
```

## Audit Script

For bulk analysis of existing knowledge files:

```bash
# Dry run
npx ts-node scripts/audit-knowledge-blog.ts

# Apply auto-fixes
npx ts-node scripts/audit-knowledge-blog.ts --apply

# Include review files
npx ts-node scripts/audit-knowledge-blog.ts --apply --include-review
```
