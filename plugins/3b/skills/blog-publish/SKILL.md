---
name: blog-publish
description: >-
  Discover, sync, and publish blog posts from 3B knowledge base. Runs dry-run
  sync to find publishable posts, lets user select which to publish, syncs
  English versions, expands them into narrative blog posts, then translates to
  Korean using /translate-ko workflow. Use when user says "publish blog", "sync
  posts", "new blog posts", or "blog publish".
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion]
metadata:
  version: "2.0.0"
---

# /blog-publish

Discover, sync, and translate blog posts from the 3B knowledge base to a Svelte
blog project (configured via `$BLOG_REPO` env var, or `{blog_domain}` template).
Orchestrates the full pipeline with user checkpoints at each stage.

**Prerequisite:** This skill assumes a Svelte-based blog project with an
`npm run sync` script that ingests knowledge from 3B. The exact integration is
maintainer-specific; see `references/blog-writing-guide.md` for the expected
project layout.

## Reference Files

Load during execution when the relevant step requires detailed reference:

| File                                                        | Use During | Contains                               |
| ----------------------------------------------------------- | ---------- | -------------------------------------- |
| [blog-writing-guide.md](./references/blog-writing-guide.md) | Step 5     | Blog expansion rules, structure, style |

## Execution Steps

### Step 0: Detect Environment

1. Verify cwd is the blog project (check for `svelte.config.js`)
2. Set `BLOG_PATH` to project root (or `$BLOG_REPO` env var if set)
3. Set `3B_PATH` to `${FORGE_3B_ROOT}`
4. Verify both paths exist

If not in the blog project directory, stop and tell the user to `cd` there
first.

### Step 1: Discover Available Posts

Run three discovery commands:

```bash
# 1. Check for expanded posts with upstream changes (hash guard)
npm run sync:check -- --verbose

# 2. Check for needs_resync flag (set by /wrap)
grep -rl "needs_resync: true" ${FORGE_3B_ROOT}/knowledge/

# 3. Run dry-run sync for new/updated posts
npm run sync -- --dry-run --verbose
```

Parse the combined output into 5 categories:

| Category          | Source                              | Description                                  |
| ----------------- | ----------------------------------- | -------------------------------------------- |
| **Hash mismatch** | `sync:check` → `⚠️  HASH MISMATCH`  | Expanded posts with upstream content changes |
| **Ready to sync** | dry-run → `✅ Would sync:` (new)    | New posts, can publish now                   |
| **Needs resync**  | grep → `needs_resync: true`         | Published entries enriched since last sync   |
| **Updated**       | dry-run → `✅ Would sync:` (exists) | Content updates to non-expanded posts        |
| **Almost ready**  | dry-run → `⏭️  Skipping (REASON):`  | Show blocker + how to fix                    |

**Note:** "Hash mismatch" posts are expanded and protected — they require manual
merge via `npm run sync:diff -- --slug=<slug>`. "Needs resync" entries may
overlap with "Updated" (both are republishable). Show "Hash mismatch" first as
it requires the most attention.

**Fixable skip reasons** (show in "almost ready"):

- `no official/authoritative reference` — needs 1 official/authoritative ref
  added to 3B source frontmatter
- `not ready (blog.ready: false)` — needs `blog.ready: true` set in 3B source
- `needs review` — publishable is set to `"review"` instead of `true`

**Non-fixable skip reasons** (ignore silently):

- `no blog metadata (legacy file)`
- `not publishable`
- `excluded category`
- `no frontmatter`
- `not completed`
- `no references`

### Step 2: Present Results to User

Use `AskUserQuestion` to show discovered posts and let user choose.

**Display format example:**

```text
🔒 Expanded posts with upstream changes (hash mismatch):
  1. backend/redis-queue-patterns → run sync:diff to view changes
  2. devops/claude-code-shared-config → run sync:diff to view changes

📝 New posts ready to sync:
  3. backend/new-post-slug
  4. aws/another-post

🔁 Needs resync (enriched since last publish):
  5. aws/security-groups-fundamentals

🔄 Updated posts (non-expanded, content changed):
  6. backend/existing-post

⚠️ Almost ready (fixable blockers):
  7. data/some-post → needs official reference
  8. backend/other-post → blog.ready: false
```

**Options:**

- "All new" — sync all new posts (skip updated and almost-ready)
- "Select by number" — let user pick specific posts (hash-mismatch posts require
  manual merge via `sync:diff`)
- "Skip" — exit without syncing

If no posts found in any category, report that and exit.

### Step 3: Fix Blockers (if user selected "almost ready" posts)

For each selected "almost ready" post:

1. Read the 3B source file at `{3B_PATH}/knowledge/{category}/{slug}.md`
2. Show current state (references, blog metadata)
3. Help user fix the blocker:
   - **Missing reference** → search for official docs URL, suggest adding to
     frontmatter references list
   - **`ready: false`** → confirm with user, update to `true`
   - **`needs review`** → show current content summary, confirm with user,
     update `publishable: true`
4. Write updated frontmatter back to 3B source file

### Step 4: Sync English Posts

Run actual sync:

```bash
npm run sync
```

Verify new files appeared in `src/content/posts/en/` by checking the output for
`✅ Synced:` lines.

After each successful sync of a "needs resync" entry:

1. Run `npm run sync` as normal
2. The sync script clears `needs_resync: false` in the 3B source file
3. Verify the flag was cleared

If sync reports errors, show them and stop.

After sync, run `npm run validate:dates` to catch any date inconsistencies
before proceeding to expansion. Fix any errors before continuing.

### Step 5: Expand to Blog Post

**Read [references/blog-writing-guide.md](./references/blog-writing-guide.md)
for expansion rules before starting.**

For each newly synced post:

1. Read the synced English post from `src/content/posts/en/{category}/{slug}.md`
2. Read the 3B source knowledge from `{3B_PATH}/knowledge/{category}/{slug}.md`
3. Expand the knowledge into a narrative blog post following the guide:
   - Add a narrative hook/intro (past-self perspective)
   - Expand terse bullet points into explained paragraphs
   - Add transitions between sections
   - If source has Options Considered, walk through the decision process
   - Add a conclusion/practical takeaway section
   - Preserve all code examples and references
4. **Set hash guard fields in frontmatter:**
   - Set `expanded: true` — marks this post as protected from sync overwrite
   - Keep `source_content_hash` as-is (already set by sync in Step 4)
5. **Bump `updated` date in frontmatter** to today's date (`YYYY-MM-DD`). The
   expansion is a content change — `updated` must reflect it so post sorting
   shows the correct recency.
6. Write the expanded post back to `src/content/posts/en/{category}/{slug}.md`
7. Show diff to user for confirmation before proceeding

**For "hash mismatch" posts (expanded, upstream content changed):**

1. Run `npm run sync:diff -- --slug={slug}` to see the content diff
2. Read the EXISTING expanded blog post from
   `src/content/posts/en/{category}/{slug}.md`
3. Read the UPDATED 3B source from `{3B_PATH}/knowledge/{category}/{slug}.md`
4. Identify what changed (new sections, new references, new examples)
5. Integrate new content into the existing narrative — preserve the existing
   hook, structure, and flow
6. **Update `source_content_hash`** to the new hash (recompute from the current
   cleaned 3B body so future syncs know we're up to date). The hash value can be
   obtained by running: `npm run sync:check -- --verbose` (shows hashes)
7. **Bump `updated` date in frontmatter** to today's date (`YYYY-MM-DD`).
8. Show diff to user for confirmation

**For "needs resync" posts (flagged by /wrap, may or may not be expanded):**

1. If the post has `expanded: true` → follow "hash mismatch" flow above
   (includes `updated` bump)
2. If the post is NOT expanded → sync overwrites it normally, then expand as new
   (includes `updated` bump in the expansion step)

**Important:** The expansion transforms reference-style content into
teaching-a-peer narrative. It is NOT a copy — it adds depth, context, and flow
that atomic knowledge entries don't have.

**Note:** Reading time is auto-computed by `remark-reading-time` plugin at build
time — no manual `readingTime` frontmatter needed. The share link ("Copy link")
is rendered client-side and requires no content changes.

### Step 6: Create Korean Translation Templates

For each newly synced post, run:

```bash
npm run translation:create -- --slug={slug}
```

Where `{slug}` is the filename without `.md` extension.

If templates already exist (for updated posts), skip this step for those posts
and note they may need translation updates.

### Step 7: Translate to Korean

Follow the `/translate-ko` skill workflow with `context=blog` (해요체 register).

For each post, the translation source and output are:

- **Source:** `src/content/posts/en/{category}/{slug}.md`
- **Output:** `src/content/posts/ko/{category}/{slug}.md`

The `/translate-ko` skill handles voice calibration, the 4-step translation
workflow (Analyze → Translate → Rewrite → QA), and blog-specific frontmatter
updates. See [translate-ko/SKILL.md](../translate-ko/SKILL.md) for full details.

**Date sync (applies to all translations, new and updated):**

- Set `source_updated` to the EN post's current `updated` value
- This ensures `npm run validate:dates` passes and KO/EN dates stay consistent

**For "needs resync" posts that already have Korean translations:**

1. Skip `npm run translation:create` (template already exists)
2. Identify the delta between old and new English content
3. Translate ONLY the new/changed sections
4. Integrate into the existing Korean post, preserving existing translations
5. Update `translation_date` in Korean frontmatter

### Step 8: Build and Verify

```bash
npm run build
```

Check for build errors. If errors occur:

1. Read the error output
2. Fix the issue (usually frontmatter or markdown formatting)
3. Rebuild

### Step 9: Report

Show summary:

```text
✅ Published:
  - backend/new-post (EN + KO)
  - aws/another-post (EN + KO)

🔄 Updated:
  - backend/existing-post (EN only, KO translation may need update)

📊 Blog now has X posts (Y with Korean translations)
```

Count posts by listing files in `en/` and `ko/` directories.

## Execution Checklist

```text
- [ ] Environment detected (BLOG_PATH, 3B_PATH)
- [ ] Dry-run output parsed correctly
- [ ] User confirmed which posts to publish
- [ ] Blockers fixed (if any selected)
- [ ] English posts synced successfully
- [ ] Posts expanded from knowledge to blog narrative
- [ ] Korean templates created
- [ ] Translations completed (natural Korean, not robotic)
- [ ] Frontmatter updated (draft: false, [번역 필요] removed)
- [ ] EN posts have `updated` bumped to today after expansion
- [ ] KO posts have `source_updated` matching EN `updated`
- [ ] `npm run validate:dates` passes clean
- [ ] Build passes with no errors
- [ ] Summary reported to user
```

## Troubleshooting

| Problem                             | Cause                                  | Fix                                                |
| ----------------------------------- | -------------------------------------- | -------------------------------------------------- |
| `npm run sync` permission error     | Missing `--allow-env` in Deno flags    | Check package.json sync script has `--allow-env`   |
| No posts found                      | All posts already synced or none ready | Check 3B source files for `blog.ready: true`       |
| Translation template already exists | Post was previously synced             | Skip template creation; check if KO needs updating |
| Build fails after sync              | Frontmatter issues or markdown errors  | Read build error, fix the specific file            |
| Korean template has `[번역 필요]`   | Template not fully translated          | Complete translation and update frontmatter        |
| Expansion produces shallow content  | Source knowledge entry lacks depth     | Enrich 3B source first (add Problem, Options)      |
