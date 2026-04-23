---
paths:
  - "**/*firecrawl*"
  - "**/.firecrawl/**"
---

# Firecrawl Usage Policy

Routing, credit discipline, and exit strategy for the Firecrawl CLI and skill
bundle. Firecrawl is **on trial** — installed 2026-04-15 on the free tier with
1,175 credits total (not monthly). If it is not proving clear value by
2026-07-15, remove it via § Removal below.

Firecrawl is open source (<https://github.com/firecrawl/firecrawl>). If hosted
credits become a blocker but the tool is valuable, see § Self-Hosting Escape
Hatch before removing.

## Exit Strategy (If API Credit Limit Hits)

When `firecrawl --status` shows credits at or near zero, or the API starts
returning 429 / credit-exhausted errors, pick **one** of two paths:

| Path             | When to pick                                                                              | What you do                                                                                                                                                                                 | Effort                                                         |
| ---------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **1. Remove**    | Tool hasn't earned its place — WebFetch + playwright + chrome-devtools cover actual needs | Follow § Removal checklist below: delete rule file, revert 2 CLAUDE.md pointers, revert .gitignore lines, delete memory files, `asdf uninstall firecrawl`, revoke API keys                  | ~30 sec of edits + 1 min of uninstall commands                 |
| **2. Self-host** | Tool has proven valuable and you want to keep using it without credit caps                | Follow § Self-Hosting Escape Hatch below: clone repo, `docker compose up`, set `FIRECRAWL_API_URL` env var. Zero skill edits — the installed CLI and build skills already honor the env var | 1–2 hours initial setup, ongoing maintenance of your own infra |

**Decision heuristic**: Review `.claude/buffer.md` for `[FIRECRAWL]` entries
logged since install. If you count fewer than ~10 useful runs per week, path 1.
If you count many runs and kept reaching for `firecrawl-crawl` or
`firecrawl-agent` (the high-value features), path 2 is worth the setup cost.

**Upgrade to paid tier is NOT recommended as a default** because it defeats the
reversibility-first design — paid subscriptions create lock-in and recurring
cost review overhead. If neither path 1 nor path 2 fits, ask explicitly before
upgrading.

## Installation State

- **CLI binary**: `firecrawl` v1.14.9 via asdf shim (`~/.asdf/shims/firecrawl`)
- **Authentication**: stored credentials (not env-var). Verify with
  `firecrawl --status`.
- **Skills**: 12 folders live at `~/.agents/skills/firecrawl*`, symlinked into
  `3b/.claude/skills/firecrawl*`. Because `~/.claude/skills` →
  `3b/.claude/skills` (and work profile chains onward), both profiles see all
  skills globally.
- **Routing policy**: this file, auto-loaded via two pointers:
  - `3b/CLAUDE.md` under "## Skill Routing" (active inside the 3B repo)
  - `3b/.claude/global-claude-setup/templates/CLAUDE.md` under "## External Tool
    Routing" (symlinked to `~/.claude/CLAUDE.md` and `~/.claude-work/CLAUDE.md`
    — active across all repos, both profiles)
- **Gitignore**: `.firecrawl/` (CLI outputs) and `.claude/skills/firecrawl*`
  (installer-managed symlinks) are both ignored repo-wide.

No changes to `settings.json`, shell env, or shell profile. The only edit to
`global-claude-setup/` is the 1-line pointer mentioned above.

## Credit Discipline (Hard Rule)

1,175 credits sounds like a lot but drains fast. Defaults protect the budget:

1. **Prefer free tools first.** Default to `WebFetch` (single static page) or
   built-in `WebSearch` (snippet-level search). Only escalate to Firecrawl when
   those fail or are structurally wrong for the job.
2. **Escalation signals** (pick Firecrawl when these match):
   - `WebFetch` returned garbled content → JS-rendered SPA, needs
     `firecrawl-scrape`
   - Need structured JSON extraction from a complex page → `firecrawl-agent`
   - Need full page content for each search hit, not just snippets →
     `firecrawl-search`
   - Need to walk a multi-page section of a site → `firecrawl-crawl` (expensive)
   - Need to click/log-in/fill-forms on a live page → `firecrawl-interact`
3. **Explicit confirmation required** before running either of these (they can
   drain credits in a single run):
   - `firecrawl-crawl` — can burn 100–500+ credits
   - `firecrawl-download` — bulk offline save, also heavy
4. **Log heavy runs** to `.claude/buffer.md` with estimated credit cost, e.g.:
   `[FIRECRAWL] scraped 23 pages of next.js docs — est 23 credits`

## Decision Matrix

| Task                                       | Tool                                                        | Credit cost  |
| ------------------------------------------ | ----------------------------------------------------------- | ------------ |
| Static page, known URL, plain HTML         | `WebFetch`                                                  | 0            |
| Broad search (snippets only)               | built-in `WebSearch`                                        | 0            |
| JS-rendered SPA; `WebFetch` failed         | `firecrawl-scrape`                                          | ~1/page      |
| Search + full content extraction           | `firecrawl-search`                                          | ~1–5/query   |
| Multi-page site section (confirm first)    | `firecrawl-crawl`                                           | 10–500+      |
| URL discovery only                         | `firecrawl-map`                                             | ~1           |
| Structured JSON (pricing tables, listings) | `firecrawl-agent`                                           | varies       |
| Interactive flow (login, forms)            | `firecrawl-interact` / `chrome-devtools-mcp` / `playwright` | varies       |
| Offline save of a site (confirm first)     | `firecrawl-download`                                        | 100s         |
| Integrating Firecrawl into product code    | `firecrawl-build-*`                                         | 0 (code gen) |

**Interactive flows — which tool?** For single-shot actions (one click, one
form), prefer `firecrawl-interact`. For complex debugging where you need to
inspect DOM, console, or network, use `chrome-devtools-mcp`. For headless test
automation or scripted multi-step flows, use `playwright`.

## Output Location

CLI writes to `./.firecrawl/` in the repo root. This path is gitignored in 3B
and should be gitignored in any other repo that uses Firecrawl. **Never commit
scraped content** — cite the source URL and re-scrape if you need it again.

## API Key Handling

- **CLI usage**: no env var needed. The CLI stores credentials internally after
  the browser auth flow (check `firecrawl --status`).
- **Build skills** (`firecrawl-build-*`): these integrate Firecrawl into product
  code and require `FIRECRAWL_API_KEY` in the project's `.env`. Mint fresh keys
  at <https://www.firecrawl.dev/app/api-keys> — do **not** reuse the onboarding
  session key.
- **No global env var**: `FIRECRAWL_API_KEY` is deliberately not added to
  `~/.zshrc` or `settings.json`. Per-project injection keeps blast radius small.

## Candidate Integration Points (Notes Only — Not Yet Rewired)

These existing 3B skills could reach for Firecrawl in specific cases. No changes
have been made to them yet; note them here so future integration work has a
concrete starting point:

- `/research-paper` — `firecrawl-scrape` for arXiv abstract pages when PDF
  extraction is brittle (especially paywalled or JS-heavy preprint servers)
- `/blog-publish` — `firecrawl-scrape` for a post-sync sanity check that
  the maintainer's blog ({blog_domain}) rendered the post correctly
- `/investigate` — `firecrawl-search` for external reference lookups during
  root-cause analysis when built-in `WebSearch` returns thin results

Revisit these after 2026-06-01 if Firecrawl usage has proven steady.

## § Self-Hosting Escape Hatch

Firecrawl is open source. If hosted credits become a blocker but the tool is
earning its place, self-host and point the existing install at your own endpoint
— no skill rewrites needed.

**Migration path:**

1. Clone `https://github.com/firecrawl/firecrawl` and follow its `SELF_HOST.md`
   (Docker Compose + Playwright worker + Redis).
2. Set `FIRECRAWL_API_URL` in the shell env or per-project `.env`:

   ```bash
   export FIRECRAWL_API_URL=http://localhost:3002   # or your deployed host
   ```

3. CLI honors this env var automatically. Build skills (`firecrawl-build-*`)
   already declare `FIRECRAWL_API_URL` as an optional input in their SKILL.md
   frontmatter — no edits required.
4. Verify: `firecrawl --status` should hit the self-hosted URL.
   `firecrawl scrape https://example.com` should succeed without consuming
   hosted credits (credit counter stays flat).

**Trade-off:** Hosted-credit caps disappear; you own the infra instead (compute,
Playwright browser upkeep, Redis, incident response). Roughly worth considering
when monthly hosted usage would exceed ~10k credits consistently.

## § Removal (Self-Documenting Uninstall)

If Firecrawl is not proving value, remove all touchpoints in order. Each step is
a single command or trivial edit — full removal takes under a minute.

```bash
# 1. Upstream skill source (installer drop)
rm -rf ~/.agents/skills/firecrawl*

# 2. Dangling symlinks in 3B
rm ~/dev/personal/3b/.claude/skills/firecrawl*

# 3. This rule file
rm ~/dev/personal/3b/.claude/rules/firecrawl-usage.md

# 4. Pointer line in 3B CLAUDE.md — edit 3b/CLAUDE.md and remove the two-line
#    pointer that references firecrawl-usage.md (under "## Skill Routing")

# 4b. Global CLAUDE.md pointer — edit
#     3b/.claude/global-claude-setup/templates/CLAUDE.md and remove the
#     entire "## External Tool Routing" section (the Firecrawl pointer).
#     Also remove its row from the "## Update Log" table at the bottom.
#     The change propagates to both ~/.claude and ~/.claude-work via
#     existing symlinks — no further action needed.

# 5. Gitignore — edit 3b/.gitignore and remove the `.firecrawl/` line and
#    the two `.claude/skills/firecrawl*` lines

# 6. Auto-memory files — Claude Code encodes the project's absolute path
#    into its per-project memory dir (e.g. an absolute path `/Users/me/dev/foo`
#    becomes `-Users-me-dev-foo`). Adjust the slug for your home:
rm ~/.claude/projects/{project-slug}/memory/project_firecrawl.md
# Edit MEMORY.md and remove the firecrawl index line

# 7. Uninstall the CLI binary
asdf list firecrawl           # confirm installed version
asdf uninstall firecrawl 1.14.9
asdf plugin remove firecrawl  # optional — removes the asdf plugin too

# 8. Revoke API keys at https://www.firecrawl.dev/app/api-keys

# 9. CLI credential cache (if present)
rm -rf ~/.config/firecrawl ~/.firecrawl

# 10. (Optional) Sign out of the account at
#     https://www.firecrawl.dev/signin
```

After step 6, commit the four in-repo removals together:

```bash
git add 3b/.claude/rules/firecrawl-usage.md 3b/CLAUDE.md 3b/.gitignore \
        3b/.claude/global-claude-setup/templates/CLAUDE.md
```

(staged as deletions/modifications), then commit with a message like
`chore(3b): remove firecrawl integration — tool did not prove value`.

## Update Log

| Date       | Change                         |
| ---------- | ------------------------------ |
| 2026-04-15 | Initial policy — tool on trial |
