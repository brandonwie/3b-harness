---
tags: [mcp, configuration, integrations, plugins]
created: 2026-04-24
updated: 2026-04-24
status: completed
paths:
  - "**/.mcp.json"
  - ".claude/project-claude/*.mcp.json"
  - ".claude/rules/mcp-*.md"
  - ".claude/global-claude-setup/settings.json"
---

# MCP Strategy

How MCP servers, plugins, and Anthropic-hosted integrations are configured,
shared, and used across profiles and projects.

## Server Inventory

### Anthropic-Hosted Integrations (Platform-Managed)

These require no local configuration — managed via OAuth through the Claude
platform. **All disconnected by default (2026-03-25)** to save ~50K+ context
tokens per session. Re-enable on demand via `/mcp`.

| Integration     | Tool Prefix                         | Purpose                             | Default  |
| --------------- | ----------------------------------- | ----------------------------------- | -------- |
| Gmail           | `mcp__claude_ai_Gmail__*`           | Draft, search, read emails          | Disabled |
| Google Calendar | `mcp__claude_ai_Google_Calendar__*` | Events, free time, scheduling       | Disabled |
| Notion          | `mcp__claude_ai_Notion__*`          | Pages, databases, comments, search  | Disabled |
| Sentry          | `mcp__claude_ai_Sentry__*`          | Issues, events, traces, projects    | Disabled |
| Slack           | `mcp__claude_ai_Slack__*`           | Channels, threads, messages, search | Disabled |

**Enable when needed:** `/mcp` → select integration → OAuth reconnects. No local
config changes required. Disable after use to reclaim context budget.

### Plugins (via `enabledPlugins` in settings.json)

Installed per-profile but configured identically in both profiles' settings.

| Plugin                                    | Both Profiles | Provides MCP Tools               | Purpose                     |
| ----------------------------------------- | ------------- | -------------------------------- | --------------------------- |
| context7@claude-plugins-official          | Yes           | Yes (`mcp__context7__*`)         | Library doc lookup          |
| playwright@claude-plugins-official        | Yes           | Yes (`mcp__plugin_playwright_*`) | Browser automation          |
| frontend-design@claude-plugins-official   | Yes           | No (skill only)                  | UI design skill             |
| security-guidance@claude-plugins-official | Yes           | No (guidance only)               | Security best practices     |
| claude-hud@claude-hud                     | Yes           | No (statusline)                  | HUD display                 |

**Disabled/removed plugins:**

- `claude-stt@jarrodwatts-claude-stt` — removed 2026-03-30. Archived upstream
  project. Replaced by built-in `/voice` command.
- `github@claude-plugins-official` — disabled 2026-03-25. MCP server requires
  `GITHUB_PERSONAL_ACCESS_TOKEN` for `api.githubcopilot.com`. Redundant with
  `gh` CLI which handles all GitHub operations.
- `dx@ykdojo` — disabled 2026-03-25. Only used once (`dx:handoff`, 2026-02-24).
  Overlaps with existing skills (`claude-md-management`, `/wrap`).
- `claude-mem@thedotmack` — **uninstalled 2026-04-17** (disabled 2026-03-21,
  briefly re-enabled, then removal attempted twice). 32-day measurement showed
  3,315 observations ingested vs. 1 retrieval (0.03% rate). First removal
  attempt flipped `enabledPlugins` to `false` and `rm -rf`'d the data/cache —
  but claude-mem's `Setup` hook (`scripts/smart-install.js`) auto-reinstalled
  the plugin on next session start because `installed_plugins.json` still
  tracked it. Second attempt used `/plugin uninstall claude-mem@thedotmack` to
  clear the registry, then deleted the `enabledPlugins` entry entirely,
  `rm -rf`'d all install paths (cache + marketplaces in both profiles), removed
  10 accumulated uv chroma-mcp archives, and cleared the work-profile registry
  entry. Total reclaim ~2.0 GB. Grep/Glob + auto-memory cover the actual
  workflow. Lesson: `enabledPlugins: false` is cosmetic —
  `installed_plugins.json` is the true registry, and `marketplaces/` is a
  separate install location that survives cache deletion.

### Project-Level MCP Servers (`.mcp.json`)

| Server                   | Project       | Type | Purpose                                 |
| ------------------------ | ------------- | ---- | --------------------------------------- |
| postgres-local           | myapp-api    | npx  | Local dev DB (localhost:5432)           |
| postgres-aws-aurora-prod | myapp-api    | uvx  | Prod DB (readonly, via Secrets Manager) |
| postgres-aws-aurora-prod | myapp-infra | uvx  | Prod DB (readonly, same cluster)        |
| postgres-local           | another-project        | npx  | Local dev DB (localhost:5432)           |

**SoT:** 3B is the canonical source for `.mcp.json` files (same pattern as
CLAUDE.md). SoT files live in `3b/.claude/project-claude/` and symlink to each
project repo:

| SoT File                  | Target Repo   | Symlink Path | Servers                           |
| ------------------------- | ------------- | ------------ | --------------------------------- |
| `myapp-api.mcp.json`    | myapp-api    | `.mcp.json`  | postgres-local, postgres-aws-prod |
| `myapp-infra.mcp.json` | myapp-infra | `.mcp.json`  | postgres-aws-prod                 |
| `another-project.mcp.json`         | another-project        | `.mcp.json`  | postgres-local                    |

Sentry and Notion were removed from the myapp-api config — use Anthropic-hosted
integrations instead (see Preference Order below).

### Global MCP Servers (`mcpServers` in settings.json)

No global MCP servers currently configured. QMD was removed 2026-03-29 after
structured validation showed zero value over Grep/Glob. See
`knowledge/devops/qmd-semantic-search.md` for the full decision record.

### Settings.json MCP Keys

| Key                          | Source                                     | Value                          |
| ---------------------------- | ------------------------------------------ | ------------------------------ |
| `enableAllProjectMcpServers` | `settings.json` (shared)                   | `true`                         |
| `enabledMcpjsonServers`      | `settings.local.work.json` (work override) | `["postgres-aws-aurora-prod"]` |

`enableAllProjectMcpServers: true` (in the shared base) auto-enables all servers
in the current project's `.mcp.json`. The `enabledMcpjsonServers` in the work
override is a global whitelist — it ensures `postgres-aws-aurora-prod` is
available even outside the project directory. This is the only intentional MCP
difference between the two profiles.

## Shared Config Guard Pattern

CLAUDE.md files and rules are shared across profiles via symlinks. MCP tool
references must be written defensively so they don't break for devs who lack
specific servers.

**Pattern: "If configured" guard**

```text
RULE: Postgres MCP (ALWAYS USE)
  -> If configured, use mcp__postgres__query
  -> Prefer MCP over direct psql commands
```

The "if configured" phrasing allows the rule to degrade gracefully. Claude Code
will surface an error if the tool doesn't exist, but the instruction itself
won't cause confusion.

**Pattern: Permission wildcard**

```json
"allow": ["mcp__*"]
```

The `mcp__*` wildcard in permissions auto-approves all MCP tools regardless of
source (plugins, .mcp.json, Anthropic-hosted). No per-server permission entries
needed.

**Pattern: Anthropic-hosted over .mcp.json**

For services available as both Anthropic-hosted and `.mcp.json` (Sentry,
Notion), prefer the Anthropic-hosted version (`mcp__claude_ai_*`) in shared
docs. It requires zero local setup and works across all profiles.

## Decision Framework

When choosing how to access an external service:

| Need                     | Use                                   | Why                                |
| ------------------------ | ------------------------------------- | ---------------------------------- |
| AWS service docs/pricing | CLI (`aws`) or WebFetch               | No AWS MCP plugin available yet    |
| Database queries         | `.mcp.json` postgres server           | Direct SQL, schema introspection   |
| Sentry issues/events     | Anthropic-hosted (`claude_ai_Sentry`) | Zero config, OAuth managed         |
| Notion pages/databases   | Anthropic-hosted (`claude_ai_Notion`) | Zero config, OAuth managed         |
| Slack messaging          | Anthropic-hosted (`claude_ai_Slack`)  | Zero config, OAuth managed         |
| Library documentation    | Context7 plugin                       | Resolves library IDs automatically |
| Browser testing          | Playwright plugin                     | Full browser automation            |
| GitHub operations        | `gh` CLI or GitHub plugin             | Both work; CLI for scripting       |
| 3B knowledge search      | Grep/Glob + `knowledge-librarian`     | Always current, zero overhead      |
| One-off API queries      | WebFetch + curl                       | No server setup needed             |

**Preference order:** Anthropic-hosted > Plugin > `.mcp.json` > CLI > WebFetch

Rationale: Anthropic-hosted integrations are maintained by Anthropic, require no
local setup, and work identically across all machines and profiles.

## Gaps and Recommendations

### ~~Redundant Sentry/Notion Configuration~~ (Resolved 2026-03-09)

Removed `sentry` and `notion` from `myapp-api.mcp.json`. Use Anthropic-hosted
integrations (`mcp__claude_ai_Sentry__*`, `mcp__claude_ai_Notion__*`) instead.
Saves 2 npx process spawns per session.

### ~~Duplicate postgres-aws-aurora-prod~~ (Resolved 2026-03-09)

Both configs now managed as SoT files in `3b/.claude/project-claude/` and
symlinked to each project repo. Drift prevented by single-source editing.

### ~~claude-mem Plugin~~ (Uninstalled 2026-04-17)

Disabled 2026-03-21, re-enabled at some point, **uninstalled 2026-04-17** after
a 32-day retention measurement: 3,315 observations ingested, 1 retrieval (0.03%
rate).

**Removal took two attempts:**

1. First attempt (commit `092f4fb`): flipped `enabledPlugins` to `false`,
   `rm -rf`'d data + plugin cache + uv archive (~1.85 GB). On next session
   start, claude-mem's `Setup` hook (`scripts/smart-install.js`)
   auto-reinstalled the plugin because `installed_plugins.json` still tracked
   it. A new empty corpus started accumulating and new uv chroma-mcp archives
   proliferated.
2. Second attempt (commit after `ba69f34`): ran
   `/plugin uninstall claude-mem@thedotmack` to clear the registry, then deleted
   the `enabledPlugins` entry **entirely** (not flipped to false), `rm -rf`'d
   cache + marketplaces dirs in both profiles, removed 10 accumulated uv
   chroma-mcp archives, and manually cleared the work-profile
   `installed_plugins.json` entry. Total reclaim ~2.0 GB.

**Lessons:**

- `enabledPlugins: false` in settings.json is cosmetic —
  `~/.claude/plugins/installed_plugins.json` is the true registry that gates the
  Setup-hook auto-install.
- Claude Code plugins have **two** install locations per profile:
  `plugins/cache/{author}/` (versioned downloads) and
  `plugins/marketplaces/{author}/` (persistent registered install). Both must be
  deleted for a clean removal.
- Grep/Glob + `knowledge-librarian` + auto-memory cover the actual
  knowledge-search workflow. No `.claude-mem` data or plugin cache remains.

### No AWS MCP Servers

The `AWS_MCP_SERVICES.md` doc in `myapp-infra` prompts references 5 AWS MCP
services (docs, pricing, cost-explorer, cloudwatch, support). These appear to be
aspirational — no corresponding `.mcp.json` entries or plugins exist.

**Recommendation:** If AWS MCP servers become available as Anthropic-hosted
integrations, adopt them. Until then, continue using `aws` CLI and WebFetch.
Remove or annotate `AWS_MCP_SERVICES.md` to indicate these are not yet
configured.

### ~~Missing Personal-Profile Plugins in Work~~ (Resolved 2026-03-14)

`claude-stt` and `dx` are now in both profiles via shared `settings.json`
symlink. No asymmetry remains.
