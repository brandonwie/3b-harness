# Claude Code Customizations

> **Last Updated:** 2026-03-26
>
> **Upstream:** <https://github.com/jarrodwatts/claude-hud>

This document tracks all customizations, patches, and configurations made to
Claude Code setup. All portable configuration is centralized in 3B.

---

## Source of Truth: 3B Repository

All portable Claude Code configuration is stored in 3B and symlinked to
`~/.claude`. This enables:

- Version control of configuration
- Easy machine bootstrapping (clone 3B, run setup.sh)
- Single source of truth across machines

### Symlink Structure

```text
~/.claude/
├── commands/ → 3b/.claude/global-claude-setup/commands
├── scripts/ → 3b/.claude/global-claude-setup/scripts
├── hooks/ → 3b/.claude/global-claude-setup/hooks
├── settings.json → 3b/.claude/global-claude-setup/settings.json
├── statusline-wrapper.sh → 3b/.claude/global-claude-setup/statusline-wrapper.sh
├── CLAUDE.md → 3b/.claude/global-claude-setup/templates/CLAUDE.md
├── CUSTOMIZATIONS.md → 3b/.claude/global-claude-setup/CUSTOMIZATIONS.md
├── RTK.md → 3b/.claude/global-claude-setup/RTK.md
├── claude-hud-patches/ → 3b/.claude/global-claude-setup/claude-hud-patches
├── task-tracker.json → 3b/.claude/global-claude-setup/task-tracker.json
├── friction-log.json → 3b/.claude/friction-log.json
├── friction-log-archive.json → 3b/.claude/friction-log-archive.json
├── skills/ → 3b/.claude/skills
├── ide/                                    (regular dir - VS Code extension)
├── agents/                                 (regular dir - agent definitions)
└── plugins/claude-hud/config.json → 3b/.claude/global-claude-setup/plugins/...

~/.claude-work/                             (all chain through ~/.claude → 3b)
├── settings.json → ~/.claude/settings.json
├── settings.local.json → 3b/.claude/global-claude-setup/settings.local.work.json
├── CLAUDE.md → ~/.claude/CLAUDE.md
├── CUSTOMIZATIONS.md → ~/.claude/CUSTOMIZATIONS.md
├── RTK.md → ~/.claude/RTK.md
├── commands/ → ~/.claude/commands
├── scripts/ → ~/.claude/scripts
├── hooks/ → ~/.claude/hooks
├── claude-hud-patches/ → ~/.claude/claude-hud-patches
├── statusline-wrapper.sh → ~/.claude/statusline-wrapper.sh
├── task-tracker.json → ~/.claude/task-tracker.json
├── friction-log.json → ~/.claude/friction-log.json
├── friction-log-archive.json → ~/.claude/friction-log-archive.json
├── skills/ → ~/.claude/skills
├── agents/ → ~/.claude/agents
├── ide/ → ~/.claude/ide
└── plugins/claude-hud/config.json → ~/.claude/plugins/...
```

### settings.json Architecture

Both profiles share a single `settings.json` via symlinks (3B → personal →
work). Profile-specific overrides use `settings.local.json`:

```text
settings.json (shared, symlinked)     → env, permissions, hooks, plugins, etc.
settings.local.json (per-profile)     → work: statusLine + enabledMcpjsonServers
                                        personal: none (deleted, all in base)
project/.claude/settings.local.json   → project-specific (unchanged)
```

Merge order: `settings.json` → global `settings.local.json` → project
`settings.local.json`. Claude Code deep-merges, so work's `statusLine.command`
overwrites the base value while everything else is inherited.

### Files NOT in 3B (Machine-Specific)

| File                             | Reason                 |
| -------------------------------- | ---------------------- |
| `.claude.json`                   | Account credentials    |
| `history.jsonl`                  | Session history        |
| `plugins/cache/`                 | Plugin binaries        |
| `plugins/installed_plugins.json` | Machine-specific paths |
| `security_warnings_state_*.json` | Session-specific       |

---

## Profile Structure

```text
~/.claude        → Personal profile (default)
~/.claude-work   → Work profile (team plan)
```

### How Profiles Work

| Profile  | Config Dir       | Alias   | Account           |
| -------- | ---------------- | ------- | ----------------- |
| Personal | `~/.claude`      | `cpers` | Personal Max plan |
| Work     | `~/.claude-work` | `cwork` | Team plan         |

---

## Claude HUD Configuration

### Version Pin (2026-04-21)

`claude-hud` is pinned to **v0.0.12** with `autoUpdate: false` in
`~/.claude/plugins/known_marketplaces.json`. Upstream bumped `main`'s
`plugin.json` to 0.1.0 on 2026-04-20 (commit `4d2a023`) without a Git tag,
GitHub Release, or CHANGELOG entry. The marketplace auto-updater followed `main`
and cached vanilla 0.1.0; `statusline-wrapper.sh`'s `ls -td` then swapped the
active code path silently, erasing all 9 patches.

Recovery: delete the 0.1.0 cache folder, `git checkout 6e146239` in the
marketplace repo (last pre-bump commit), revert `installed_plugins.json` to
0.0.12, and re-run the patch script. Re-enable `autoUpdate` only after upstream
publishes a real 0.1.x release. Full post-mortem + forward-port notes in
[`claude-hud-patches/UPGRADE-GUIDE.md`](./claude-hud-patches/UPGRADE-GUIDE.md) §
Untagged Version Bumps.

### Config File Location

```text
3b/.claude/global-claude-setup/plugins/claude-hud/config.json  (source of truth)
~/.claude/plugins/claude-hud/config.json → symlink to 3B
~/.claude-work/plugins/claude-hud/config.json → symlink to ~/.claude version
```

Both profiles share the same HUD display settings via symlinks.

### HUD Binary (Symlink Status)

Each profile has its own **independent** HUD binary. These are NOT symlinked.

```text
~/.claude/plugins/cache/claude-hud/claude-hud/{version}/      # Personal (patched)
~/.claude-work/plugins/cache/claude-hud/claude-hud/{version}/  # Work (patched)
```

| Component                         | Shared (symlinked)  | Independent (per-profile) |
| --------------------------------- | ------------------- | ------------------------- |
| `config.json`                     | Yes (both → 3B SoT) | -                         |
| `.usage-cache.json`               | -                   | Yes (separate usage data) |
| `plugins/cache/claude-hud/`       | -                   | Yes (separate binaries)   |
| `statusline-wrapper.sh`           | Yes (→ 3B SoT)      | -                         |
| `plugins/known_marketplaces.json` | -                   | Yes (per-profile)         |
| `plugins/installed_plugins.json`  | -                   | Yes (per-profile)         |

Because binaries are independent, **both must be patched** when HUD updates. The
`claude-hud-post-patches.sh` script handles this automatically.

**Marketplace gap (2026-03-25):** `known_marketplaces.json` is per-profile and
NOT symlinked. Third-party plugins (e.g., `dx@ykdojo`) must be installed in both
profiles separately, or their marketplace repos added to
`extraKnownMarketplaces` in shared `settings.json`. Without this, the work
profile sees "Plugin not found in marketplace" errors for plugins that only the
personal profile has installed. (`claude-stt` was removed 2026-03-30 — replaced
by built-in `/voice`.)

### Current HUD Settings

```json
{
  "lineLayout": "expanded",
  "showSeparators": true,
  "pathLevels": 2,
  "gitStatus": {
    "enabled": true,
    "showDirty": true,
    "showAheadBehind": true,
    "showFileStats": true
  },
  "display": {
    "showModel": true,
    "showContextBar": true,
    "showTools": true,
    "showAgents": true,
    "showTodos": true,
    "showConfigCounts": true,
    "showTokenBreakdown": true,
    "showUsage": true,
    "showDuration": true,
    "showSpeed": true,
    "contextValue": "percent",
    "usageThreshold": 0,
    "sevenDayThreshold": 0,
    "quote": "Learn to work harder on yourself than you do on your job."
  }
}
```

---

## Patches Applied

### 1. Multi-Account Keychain Support

**Problem:** HUD only reads from base keychain entry `Claude Code-credentials`.

**Solution:** Patch `usage-api.ts` to support `CLAUDE_HUD_KEYCHAIN_SERVICE` env
var.

File (both profiles):

- `~/.claude/plugins/cache/claude-hud/claude-hud/{version}/src/usage-api.ts`
- `~/.claude-work/plugins/cache/claude-hud/claude-hud/{version}/src/usage-api.ts`

```typescript
// Line ~248: readKeychainCredentials function
['find-generic-password', '-s', process.env.CLAUDE_HUD_KEYCHAIN_SERVICE || 'Claude Code-credentials', '-w'],
```

### 2. Multi-Account Cache Support

**Problem:** Usage cache hardcoded to `~/.claude/...`, causing
cross-contamination.

**Solution:** Three patches to `usage-api.ts`:

#### Patch 2a: defaultDeps.homeDir (line ~102)

```typescript
const defaultDeps: UsageApiDeps = {
  // PATCHED: Allow custom config dir via env var (for multi-account support)
  homeDir: () => process.env.CLAUDE_HUD_CONFIG_DIR || os.homedir()
  // ...
};
```

#### Patch 2b: getCachePath (line ~46)

```typescript
function getCachePath(homeDir: string): string {
  // PATCHED: If CLAUDE_HUD_CONFIG_DIR is set, it IS the config dir
  if (process.env.CLAUDE_HUD_CONFIG_DIR) {
    return path.join(homeDir, "plugins", "claude-hud", ".usage-cache.json");
  }
  return path.join(
    homeDir,
    ".claude",
    "plugins",
    "claude-hud",
    ".usage-cache.json"
  );
}
```

#### Patch 2c: getKeychainBackoffPath (line ~197)

```typescript
function getKeychainBackoffPath(homeDir: string): string {
  // PATCHED: If CLAUDE_HUD_CONFIG_DIR is set, it IS the config dir
  if (process.env.CLAUDE_HUD_CONFIG_DIR) {
    return path.join(homeDir, "plugins", "claude-hud", ".keychain-backoff");
  }
  return path.join(
    homeDir,
    ".claude",
    "plugins",
    "claude-hud",
    ".keychain-backoff"
  );
}
```

### 3. Skip Keychain Option

**Problem:** Work profile needs file-based credentials.

**Solution:** Already in HUD - check for `CLAUDE_HUD_SKIP_KEYCHAIN=1`.

### 4. Display Feature Patches

**Problem:** HUD source code lacks features that were added to the compiled
dist: quota bars, configurable sevenDayThreshold, minutes-only reset time for 5h
window, and apiError type hints. These source patches are lost when the plugin
updates (new version directory).

**Solution:** Patches 5-10 in `claude-hud-post-patches.sh` add these features to
source files. Uses a hybrid strategy:

| File                    | Patches | Method                      | What                                          |
| ----------------------- | ------- | --------------------------- | --------------------------------------------- |
| `config.ts`             | 5-6     | sed insert-after            | `usageBarEnabled`, `sevenDayThreshold` fields |
| `colors.ts`             | 7-8     | sed `r` + awk insert-before | `BRIGHT_BLUE`/`BRIGHT_MAGENTA`, `quotaBar()`  |
| `render/lines/usage.ts` | 9       | Template file copy          | Custom renderer with all display features     |
| `types.ts`              | 10      | sed `r` after anchor        | `apiError?: string` in `UsageData`            |

All patches are idempotent — `grep -q` checks prevent re-application.

### 5. Speed and Context Display Features

**Problem:** The newer marketplaces HUD version has `showSpeed` (output token
speed display) and `contextValue` (percent vs tokens context display) features
that are missing from the cache/0.0.6 source. These features require changes
across 6 files.

**Solution:** Patches 11-19 in `claude-hud-post-patches.sh` add these features
using a mix of sed patches and template copies:

| File                       | Patches | Method                | What                                                  |
| -------------------------- | ------- | --------------------- | ----------------------------------------------------- |
| `config.ts`                | 11-12   | sed insert-after      | `contextValue`, `showSpeed` fields + validators       |
| `types.ts`                 | 13-14   | sed `r` after anchor  | `output_tokens` in StdinData, `extraLabel` in Context |
| `stdin.ts`                 | 15-16   | sed `s/` + cat append | Export `getTotalTokens`, add `getProviderLabel`       |
| `speed-tracker.ts`         | 17      | Template file copy    | New module: output token speed tracking               |
| `render/session-line.ts`   | 18      | Template file copy    | Enhanced compact layout with all features             |
| `render/lines/identity.ts` | 19      | Template file copy    | Enhanced expanded context with `contextValue`         |

**Config options:**

```json
{
  "display": {
    "showSpeed": true,
    "contextValue": "percent"
  }
}
```

- `showSpeed` (default: `false`) — displays `out: 42.5 tok/s` in compact layout
- `contextValue` (default: `"percent"`) — set to `"tokens"` to show `45.2k/200k`
  instead of `45%`

### 6. Neon Color Palette and Quote Display

**Problem:** Basic 16-color ANSI codes adapt to terminal theme, making colors
inconsistent. The wrapper rendered its own info line separately from HUD output.

**Solution:** Patches 23-27 in `claude-hud-post-patches.sh`:

| File                      | Patches | Method             | What                                             |
| ------------------------- | ------- | ------------------ | ------------------------------------------------ |
| `render/colors.ts`        | 23      | Template file copy | 256-color neon palette with 4-level thresholds   |
| `config.ts`               | 24      | sed insert-after   | `quote` field (`string \| null`)                 |
| `render/lines/quote.ts`   | 25      | Template file copy | Quote renderer (neon violet, line 0 of expanded) |
| `render/index.ts`         | 26      | Template file copy | Layout with quote at top of expanded mode        |
| `render/lines/project.ts` | 27      | Template file copy | Merged project line with email + env version     |

### 7. apiError Propagation

**Problem:** When the usage API failed, `fetchUsageApi` returned bare `null` —
the error reason (429, timeout, network) was lost. The HUD showed `Usage ⚠` with
no indication of WHY, making root cause invisible.

**Solution:** Patch 28 in `claude-hud-post-patches.sh` converts `usage-api.ts`
to a template that uses a discriminated union `FetchResult` instead of
`UsageApiResponse | null`.

| Change          | Before                           | After                                      |
| --------------- | -------------------------------- | ------------------------------------------ |
| `fetchUsageApi` | Returns `null` on any error      | Returns `{ ok: false, error: 'http-429' }` |
| `getUsage`      | Sets `apiUnavailable: true` only | Also sets `apiError: fetchResult.error`    |
| `UsageApiDeps`  | `fetchApi` returns `... \| null` | Returns `Promise<FetchResult>`             |
| HUD display     | `Usage ⚠`                        | `Usage ⚠ (429)` or `⚠ (timeout)` etc.      |

Error types: `http-{statusCode}`, `timeout`, `network`, `parse`.

**Note:** This patch converts `usage-api.ts` to a full template (includes
patches 1-4). On re-run, patches 1-4 detect existing markers and no-op; patch 28
copies the template which includes all prior changes.

### 8. 429 Rate-Limit Backoff

**Problem:** When the usage API returned 429 (rate-limited), the failure cache
TTL was only 15 seconds — causing 4 retries/minute that perpetuated the 429. The
`Retry-After` header from 429 responses was never read.

**Solution:** Patch 29 in `claude-hud-post-patches.sh` adds 429-specific
backoff:

| Change             | Before               | After                                       |
| ------------------ | -------------------- | ------------------------------------------- |
| Failure TTL        | 15s for ALL failures | 15s generic, **5 min for 429** specifically |
| `Retry-After`      | Header ignored       | Parsed and used as TTL override if present  |
| `FetchResult`      | `error: string` only | Added `retryAfterMs?: number`               |
| `CacheFile`        | `data` + `timestamp` | Added `ttlOverrideMs?` for per-entry TTL    |
| `readCacheState()` | Single TTL check     | 3-tier: `ttlOverrideMs` > 429 TTL > generic |

**Note:** Template-based patch (re-copies `usage-api.ts`). Includes all patches
1-4, 28, and 29.

### 9. Upstream Parity (API Timeout, User-Agent, Endpoint Guard)

**Problem:** Comparing installed HUD v0.0.6 (patched) against upstream v0.0.9
revealed three differences that caused excessive API calls and 429 storms:

1. **API timeout 5s vs 15s** — Upstream gives the usage API 15 seconds to
   respond (configurable via `CLAUDE_HUD_USAGE_TIMEOUT_MS`). The patched version
   hardcoded 5s. When the API was slow (6-14s), the patched version timed out
   every time, creating failure→retry storms that seeded 429 rate limits.
2. **User-Agent `claude-hud/1.0` vs `claude-code/2.1`** — Anthropic's API may
   apply different rate limits to unrecognized User-Agent strings.
3. **Missing `isUsingCustomApiEndpoint()` guard** — Upstream skips the usage API
   entirely when `ANTHROPIC_BASE_URL` points to a non-Anthropic host (custom
   providers). The patched version made the call regardless.

**Solution:** Patch 30 in `claude-hud-post-patches.sh` ports these three fixes
from upstream 0.0.9:

| Change                | Before (patched 0.0.6) | After (Patch 30)                   |
| --------------------- | ---------------------- | ---------------------------------- |
| API timeout           | 5s hardcoded           | **15s** (matches upstream)         |
| `User-Agent` header   | `claude-hud/1.0`       | `claude-code/2.1`                  |
| Keychain timeout      | 5s                     | **3s** (matches upstream)          |
| Custom endpoint guard | Missing                | `isUsingCustomApiEndpoint()` added |

**Note:** Template-based patch (re-copies `usage-api.ts`). Includes all patches
1-4, 28, 29, and 30.

**Neon color palette (256-color ANSI):**

| Role         | Name         | 256 Code | ANSI Escape      |
| ------------ | ------------ | -------- | ---------------- |
| Quote        | Neon Violet  | 135      | `\x1b[38;5;135m` |
| UI chrome    | Neon Cyan    | 51       | `\x1b[38;5;51m`  |
| Healthy bar  | Neon Green   | 46       | `\x1b[38;5;46m`  |
| Warning bar  | Neon Yellow  | 226      | `\x1b[38;5;226m` |
| Critical bar | Neon Red     | 196      | `\x1b[38;5;196m` |
| Inactive bar | Gray         | 245      | `\x1b[38;5;245m` |
| Git parens   | Neon Magenta | 207      | `\x1b[38;5;207m` |

**4-level color thresholds (both context and usage bars):**

| Range   | Color  | Meaning       |
| ------- | ------ | ------------- |
| 0%      | Gray   | Idle/inactive |
| 1-50%   | Green  | Healthy       |
| 51-90%  | Yellow | Warning       |
| 91-100% | Red    | Critical      |

**Config option:**

```json
{
  "display": {
    "quote": "Learn to work harder on yourself than you do on your job."
  }
}
```

**Wrapper changes:** The wrapper now detects email and env version BEFORE
launching HUD, passes them as `CLAUDE_HUD_EMAIL`, `CLAUDE_HUD_ENV_LABEL`,
`CLAUDE_HUD_ENV_VERSION` env vars, and no longer outputs its own line.

---

## Keychain Services

Claude Code stores OAuth credentials in macOS Keychain. Each installation gets a
unique suffix (hash of install path).

| Service Name                       | Account Type   | Managed By                         |
| ---------------------------------- | -------------- | ---------------------------------- |
| `Claude Code-credentials`          | Base entry     | Claude Code binary                 |
| `Claude Code-credentials-7195fd18` | Personal (Max) | Claude Code (native, auto-created) |
| `Claude Code-credentials-0e3ff1b1` | Work (Team)    | Claude Code (native, auto-created) |

### How Keychain Token Management Works

Claude Code natively manages profile-specific keychain entries. Each profile
gets its own entry with a unique suffix (hash of install/config path).

```text
1. User runs `cwork` or `cpers`
2. Shell sets CLAUDE_CONFIG_DIR → Claude Code uses that profile
3. Claude Code reads token from profile-specific keychain entry
4. If token expired: Claude auto-refreshes and writes back to same entry
5. Claude Code runs statusline command from profile's settings.json
6. Work settings.json embeds CLAUDE_CONFIG_DIR in the command itself
   (Claude Code may NOT pass env vars to statusline subprocess)
7. Wrapper detects profile → sets CLAUDE_HUD_KEYCHAIN_SERVICE → HUD
   reads correct token → shows correct usage
```

No manual token sync is needed. Claude Code handles refresh automatically. The
user only needs `/login` if the refresh token itself is revoked (rare).

### Statusline Command Per Profile (CRITICAL)

Claude Code does not pass `CLAUDE_CONFIG_DIR` to statusline subprocesses. Each
profile's `settings.json` must **embed** the config dir in the command (verified
working 2026-02-04):

| Profile  | `statusLine.command`                                                           |
| -------- | ------------------------------------------------------------------------------ |
| Personal | `~/.claude/statusline-wrapper.sh` (defaults to `~/.claude`)                    |
| Work     | `CLAUDE_CONFIG_DIR=~/.claude-work ~/.claude/statusline-wrapper.sh`             |

**Why:** The wrapper reads `CLAUDE_CONFIG_DIR` to determine which keychain entry
and cache to use. Without the explicit env var in the command, the wrapper
always defaults to the personal profile.

### Token Expiration Check (statusline-wrapper.sh)

The wrapper checks if the profile-specific token is expired before using it.

**Logic:**

| Profile        | Token Valid          | Token Expired/Missing               |
| -------------- | -------------------- | ----------------------------------- |
| Personal (Max) | Use profile keychain | Fall back to default (same account) |
| Work (Team)    | Use profile keychain | Use profile anyway (no fallback)    |

**Why no fallback for work?**

Work and Personal are **different accounts** (Team vs Max). Falling back to
default keychain would show the wrong account's usage data.

### Why `_claude_sync_token` Was Removed (2026-02-04)

Previously, a shell hook `_claude_sync_token()` ran after each session to copy
the base keychain entry to the profile-specific entry. This was **actively
harmful** because:

1. Claude Code writes refreshed tokens to profile-specific entries natively
2. The sync always copied from the BASE entry (which held whichever account
   logged in last)
3. After a personal session, the base entry had the personal (Max) token
4. The sync then **overwrote** the work entry with the personal token
5. This also created duplicate keychain entries (different `acct` names for the
   same service), causing unpredictable `security find-generic-password`
   behavior

**IMPORTANT:** After removing `_claude_sync_token` from `.zshrc`, you must
reload the shell (`source ~/.zshrc` or open a new terminal) before running
`cwork`/`cpers`. The old function stays in memory in existing shells and will
continue contaminating keychain entries until the shell is reloaded.

### Keychain Commands Reference

```bash
# FIND/READ a keychain entry
/usr/bin/security find-generic-password -s "SERVICE_NAME" -w
#   -s  = Service name to search for (the "svce" attribute)
#   -w  = Output only the password data (not metadata)
# Output: The password/data stored in that entry (our OAuth JSON)

# DELETE a keychain entry
/usr/bin/security delete-generic-password -s "SERVICE_NAME"
#   -s  = Service name to delete
# Output: Prints the deleted entry details to STDOUT (not stderr!)
# Note: Returns error if entry doesn't exist (suppress with 2>/dev/null)

# ADD/CREATE a keychain entry
/usr/bin/security add-generic-password -s "SERVICE_NAME" -a "ACCOUNT" -w "DATA"
#   -s  = Service name (how we look it up later)
#   -a  = Account name (just for identification, shown in Keychain Access app)
#   -w  = The password/data to store
# Note: Fails if entry already exists (delete first, or use -U to update)

# DUMP all keychain entries (for debugging)
/usr/bin/security dump-keychain 2>/dev/null | grep -A5 "Claude Code"
#   dump-keychain = List all entries in default keychain
#   2>/dev/null   = Suppress stderr (permission warnings)
#   grep -A5      = Show 5 lines After each match
```

### Redirect Syntax Reference

```bash
# Common redirect patterns used in these scripts:

2>/dev/null       # Redirect stderr (fd 2) to /dev/null (discard errors)
>/dev/null        # Redirect stdout (fd 1) to /dev/null (discard output)
>/dev/null 2>&1   # Redirect stdout to /dev/null, then stderr to same place
                  # 2>&1 means "redirect fd 2 to wherever fd 1 currently goes"
                  # Order matters: must redirect stdout first, then stderr

# Why we use >/dev/null 2>&1 for delete-generic-password:
# - On success: prints entry details to STDOUT (we don't want to see this)
# - On failure: prints error to STDERR (we also don't want to see this)
# - Using just 2>/dev/null would still show the success output
```

---

## Environment Variables

| Variable                      | Purpose                        | Used By                 |
| ----------------------------- | ------------------------------ | ----------------------- |
| `CLAUDE_CONFIG_DIR`           | Sets active profile directory  | Claude Code binary      |
| `CLAUDE_HUD_CONFIG_DIR`       | Override HUD cache location    | usage-api.ts (patched)  |
| `CLAUDE_HUD_KEYCHAIN_SERVICE` | Override keychain service name | usage-api.ts (patched)  |
| `CLAUDE_HUD_SKIP_KEYCHAIN`    | Skip keychain entirely         | usage-api.ts (built-in) |
| `CLAUDE_HUD_EMAIL`            | Account email for project line | project.ts (template)   |
| `CLAUDE_HUD_ENV_LABEL`        | Runtime label (node/py/go)     | project.ts (template)   |
| `CLAUDE_HUD_ENV_VERSION`      | Runtime version (v24.14.0)     | project.ts (template)   |

### How Environment Variables Work in Shell Functions

```bash
# Set for SINGLE COMMAND only (not exported to current shell):
CLAUDE_CONFIG_DIR=~/.claude-work command claude "$@"
#   ↑ This variable ONLY exists for the `claude` command
#   After command finishes, variable is gone

# vs. EXPORT (persists in current shell and child processes):
export CLAUDE_CONFIG_DIR=~/.claude-work
claude "$@"
#   ↑ Variable persists after command, affects all subsequent commands

# The `command` keyword:
command claude "$@"
#   Bypasses shell functions/aliases, runs the actual binary
#   Without it: `claude` would call our function recursively
#   With it: runs /usr/local/bin/claude (or wherever installed)

# $@ vs $*
"$@"  # All arguments as SEPARATE words: "arg1" "arg2" "arg3"
"$*"  # All arguments as SINGLE word: "arg1 arg2 arg3"
# Always use "$@" to preserve argument boundaries
```

---

## Maintenance Notes

### When HUD Plugin Updates

If claude-hud updates, re-run the patch script. It patches **both** personal and
work profiles automatically (each has its own independent HUD binary):

```bash
~/.claude/claude-hud-patches/claude-hud-post-patches.sh
```

The script detects which profiles have HUD installed and patches each one. If a
profile's HUD is missing, it skips with a warning.

Relevant files patched per profile:

- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/usage-api.ts`
  **(template)**
- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/config.ts`
- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/render/colors.ts`
- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/render/lines/usage.ts`
- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/types.ts`
- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/stdin.ts`
- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/speed-tracker.ts`
- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/render/session-line.ts`
- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/render/lines/identity.ts`
- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/render/lines/project.ts`
- `{profile}/plugins/cache/claude-hud/claude-hud/{version}/src/render/lines/quote.ts`

**Note:** Template files in `claude-hud-patches/templates/` (`colors.ts`,
`usage.ts`, `usage-api.ts`, `speed-tracker.ts`, `session-line.ts`,
`identity.ts`, `project.ts`, `quote.ts`, `render-index.ts`) may need updating if
upstream changes function signatures, import paths, or the `RenderContext` type.
Check `diff` between templates and new upstream after version bumps.

### When OAuth Token Expires

Claude Code auto-refreshes access tokens using the refresh token. Manual
`/login` is only needed if:

- Refresh token is revoked (password change, org admin action)
- Authentication errors appear in session
- Initial setup of a new profile

```bash
# Run /login inside the correct profile session
cwork   # then /login for work
cpers   # then /login for personal
```

### When Adding New Accounts

1. Find the keychain service name:
   `/usr/bin/security dump-keychain 2>/dev/null | grep "Claude Code"`
2. Add new case to `statusline-wrapper.sh`
3. Create directory: `mkdir -p ~/.claude-{profile}/plugins/claude-hud`
4. Symlink config:
   `ln -s ~/.claude/plugins/claude-hud/config.json ~/.claude-{profile}/plugins/claude-hud/config.json`
5. **Set statusline command** in `~/.claude-{profile}/settings.json`:
   `"command": "CLAUDE_CONFIG_DIR=~/.claude-{profile} ~/.claude/statusline-wrapper.sh"`
6. Run `~/.claude/claude-hud-patches/claude-hud-post-patches.sh` to patch the
   new HUD binary

---

## Troubleshooting

### HUD Shows Wrong Plan (e.g., "Max" instead of "Team")

**Symptom:** Running `cwork` but HUD displays personal account usage.

**Cause:** Profile-specific keychain entry has wrong token, or duplicate
keychain entries exist (e.g., from the now-removed `_claude_sync_token`).

**Diagnosis:**

```bash
# Check what token is in the work keychain entry:
/usr/bin/security find-generic-password -s "Claude Code-credentials-0e3ff1b1" -w 2>/dev/null | \
  python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print('subscriptionType:', d.get('claudeAiOauth',{}).get('subscriptionType','N/A'))"

# Should show "team" for work profile, "max" for personal
```

**Fix:**

```bash
# 1. Ensure shell is reloaded (critical after any .zshrc changes)
source ~/.zshrc
# Or open a new terminal — old functions stay in memory otherwise

# 2. Check for duplicate entries (same service, different accounts)
/usr/bin/security dump-keychain 2>/dev/null | grep -B5 "Claude Code-credentials-0e3ff1b1"
# If duplicates exist, delete all and let Claude recreate:
/usr/bin/security delete-generic-password -s "Claude Code-credentials-0e3ff1b1" >/dev/null 2>&1
# Run again if duplicates existed (delete removes one at a time)
/usr/bin/security delete-generic-password -s "Claude Code-credentials-0e3ff1b1" >/dev/null 2>&1

# 3. Clear stale cache
rm -f ~/.claude-work/plugins/claude-hud/.usage-cache.json  # for work
rm -f ~/.claude/plugins/claude-hud/.usage-cache.json       # for personal

# 4. Start the correct profile and login (from reloaded shell)
cwork  # then /login
```

### HUD Shows No Usage Data

**Symptom:** Plan name shows but usage percentages are missing.

**Possible Causes:**

1. **OAuth token expired** → Run `/login` in the affected profile's session
2. **Patches not applied** → Run
   `~/.claude/claude-hud-patches/claude-hud-post-patches.sh`
3. **Wrong keychain service** → Check `CLAUDE_HUD_KEYCHAIN_SERVICE` in wrapper
4. **Cache stale** → Delete `.usage-cache.json` for that profile

**Diagnosing expired token:**

```bash
# Check if work token is expired
WORK_TOKEN=$(/usr/bin/security find-generic-password \
  -s "Claude Code-credentials-0e3ff1b1" -w 2>/dev/null)
EXPIRES_AT=$(echo "$WORK_TOKEN" | jq -r '.claudeAiOauth.expiresAt')
NOW_MS=$(($(date +%s) * 1000))

echo "Expires: $EXPIRES_AT"
echo "Now:     $NOW_MS"
if [[ "$EXPIRES_AT" -lt "$NOW_MS" ]]; then
  echo "Status: EXPIRED - run /login in cwork session"
else
  echo "Status: Valid"
fi
```

**Fix for expired token:**

```bash
# Start the correct profile and login
cwork   # or cpers for personal
/login  # refreshes token for current profile
```

**Verify patches are applied (both profiles):**

```bash
# Personal - should return a number > 0
grep -c "CLAUDE_HUD_CONFIG_DIR" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/usage-api.ts

# Work - should return a number > 0
grep -c "CLAUDE_HUD_CONFIG_DIR" \
  ~/.claude-work/plugins/cache/claude-hud/claude-hud/*/src/usage-api.ts
```

### /ide Command Errors (Dual Account Setup)

#### Error: "onInstall is not defined"

**Symptom:** Running `/ide` throws JavaScript error:

```text
ERROR  onInstall is not defined
file:///.../claude-code/cli.js:4078:2901
```

**Cause:** VS Code extension writes lock files to `~/.claude/ide/`, but when
running from work directory with `CLAUDE_CONFIG_DIR=~/.claude-work`, CLI looks
in `~/.claude-work/ide/` (empty). The mismatch triggers a buggy installation
code path.

**Fix:** Symlink the IDE folder so both profiles share IDE registration:

```bash
rm -rf ~/.claude-work/ide
ln -s ~/.claude/ide ~/.claude-work/ide
```

#### Error: "No available IDEs detected"

**Symptom:** `/ide` shows no IDEs even though VS Code extension is installed.

**Possible Causes:**

1. **Lock files not created** - VS Code extension needs window reload
2. **IDE folder mismatch** - Work profile looking in wrong directory
3. **Extension not active** - Extension needs to be enabled/started

**Diagnosis:**

```bash
# Check if lock files exist
ls -la ~/.claude/ide/

# Should show .lock files like:
# 12345.lock  (PID of VS Code process)
```

**Fix:**

1. **Reload VS Code window:** `Cmd+Shift+P` → "Developer: Reload Window"
2. **Verify symlink exists:** `ls -la ~/.claude-work/ide` should show
   `→ ~/.claude/ide`
3. **Check extension output:** `Cmd+Shift+P` → "Output: Show Output Channels" →
   "Claude Code"

**Note:** If running from VS Code's integrated terminal, `/ide` is not needed -
connection is automatic. The `/ide` command is only for connecting from an
external terminal (iTerm, Terminal.app) to a running VS Code instance.

### Shift+Enter Not Working in iTerm2 (Newline in Claude Code)

**Symptom:** Pressing Shift+Enter submits the prompt instead of inserting a
newline. Works fine in Ghostty.

**Cause:** iTerm2's global key map was sending a raw `\n` (Action 12: Send Text
with vim Special Chars), which is identical to a regular Enter keypress. Claude
Code's TUI requires the **CSI u** escape sequence (`ESC[13;2u`) to distinguish
Shift+Enter from Enter. Ghostty implements the Kitty keyboard protocol natively
and sends this automatically; iTerm2 does not.

**Fix (applied 2026-03-26):**

```bash
# Set Shift+Enter to send CSI u escape sequence
defaults write com.googlecode.iterm2 "GlobalKeyMap" \
  -dict-add "0xd-0x20000-0x24" '{ Action = 10; Text = "[13;2u"; }'
```

- **Action 10** = "Send Escape Sequence" (iTerm2 auto-prepends `ESC`)
- **Text** = `[13;2u` → full sequence: `\x1b[13;2u` (Kitty protocol: key 13 =
  Return, modifier 2 = Shift)

Requires full iTerm2 quit + relaunch to take effect.

**Or via iTerm2 UI:** Preferences → Keys → Key Mappings → edit Shift+Return →
Action: "Send Escape Sequence" → value: `[13;2u`

---

## Output Styles

Output styles affect token usage, readability, and educational value.

### Current Configuration

"Explanatory" is configured globally in `settings.json` (`outputStyle` key).
This adds `★ Insight` boxes before/after code changes for educational context.
Applies to all projects.

### How to Change Styles

Output style is set in global `settings.json`:

```json
{
  "outputStyle": "Explanatory"
}
```

Available styles: `default`, `concise`, `explanatory`, `formal`. To override
per-project, add `outputStyle` to that project's `.claude/settings.local.json`
(project-level overrides global).

---

## Legacy Cleanup

These directories are no longer needed and can be removed:

| Directory                   | Status                                     |
| --------------------------- | ------------------------------------------ |
| `~/.claude-personal`        | Safe to remove - `.claude` is now personal |
| `~/.claude-backup`          | Keep or remove - contains old configs      |
| `dotfiles/claude/commands/` | Safe to remove - now in 3B                 |

---

## Update Log

| Date       | Change                                                             | Reason                                                                                                                                                    |
| ---------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-03-26 | Fix Shift+Enter in iTerm2: CSI u escape sequence for key mapping   | iTerm2 sent raw `\n` (Action 12) — identical to Enter. Changed to Action 10 (Send Escape Sequence) with `[13;2u` (Kitty protocol). Ghostty works natively |
| 2026-03-14 | Fix Patch 9 retry storm: add writeCache to stale-cache fallback    | Missing writeCache caused ~30 API calls/min when stale good data existed; work profile stuck in 429 loop. Guard updated to detect buggy version           |
| 2026-03-17 | Add `terraform-safety-hook.py` PreToolUse hook (global)            | Regex-based gate for 12 dangerous terraform subcommands; catches command chaining bypasses; denies `destroy -auto-approve`; overrides RTK allow           |
| 2026-03-17 | Add `.claude/settings.local.json` in backend-infra (project)       | Project-level deny + ask rules for terraform import, state rm/mv, taint, force-unlock; defense-in-depth layer 2                                           |
| 2026-03-17 | Add `.claude/rules/terraform-safety.md` in backend-infra (project) | Auto-loads on `.tf` glob; documents safe vs dangerous commands, required apply workflow, production awareness; defense-in-depth layer 3                   |
| 2026-03-14 | Config: failureCacheTtlSeconds 15→120, showTools: false            | 15s failure TTL too aggressive (sustains 429); tools activity line not useful enough for statusline space                                                 |
| 2026-03-14 | Usage display: remove spaces around `/` in reset time format       | `(4.9h / 5h)` → `(4.9h/5h)` — saves 4 chars per line; applied to both profiles + template SoT                                                             |
| 2026-03-14 | Symlink unification: settings.json now symlinked to both profiles  | Eliminates 3-copy drift; work overrides via settings.local.work.json; RTK.md moved to 3B SoT; friction-log + HUD config symlinks added to work            |
| 2026-03-10 | Add Group U (patch 30): upstream parity fixes                      | API timeout 5s→15s, User-Agent fix, keychain 5s→3s, isUsingCustomApiEndpoint guard — all ported from upstream 0.0.9 to stop 429 storms                    |
| 2026-03-10 | Add Group T (patch 29): 429 backoff with Retry-After               | 429 failures now cached for 5 min (was 15s); parses Retry-After header; adds ttlOverrideMs to CacheFile for per-entry TTL                                 |
| 2026-03-05 | Add Group S (patch 28): apiError propagation via FetchResult       | Usage warning showed bare `⚠` with no error type; now shows `⚠ (429)` etc. via discriminated union in fetchUsageApi                                       |
| 2026-03-04 | Add Groups O-R (patches 23-27): neon palette + quote + merged      | Neon HUD redesign: 256-color palette, quote on top, merged project line with email+env, 4-level color thresholds                                          |
| 2026-03-04 | Wrapper passes CLAUDE_HUD_EMAIL/ENV_LABEL/ENV_VERSION to HUD       | Consolidate rendering into HUD; wrapper no longer outputs its own info line                                                                               |
| 2026-03-03 | Add Group L (patch 20): model badge on project line                | `[Opus \| Max]` display missing from cache project.ts; ported getModelName + getProviderLabel from marketplaces                                           |
| 2026-03-03 | Add Groups F-K (patches 11-19): showSpeed, contextValue            | Port features from marketplaces version; speed-tracker, session-line, identity templates; config/types/stdin sed patches                                  |
| 2026-03-03 | Add display feature patches (5-10) to `claude-hud-post-patches.sh` | Quota bars, sevenDayThreshold, formatResetMins, apiError patches lost on plugin update; now durable via hybrid sed + template                             |
| 2026-03-03 | Add `sevenDayThreshold: 0` to HUD config, patch source usage.ts    | 7d window hidden (source hardcoded `>= 80`); 5h reset showed `1h7m` instead of minutes                                                                    |
| 2026-03-03 | Add `.claude/rules/claude-settings-lookup.md`                      | Quick-reference rule for locating Claude settings across profiles                                                                                         |
| 2026-03-02 | Output style documentation and per-project guidance                | v1.1 Phase 5: document available styles, add project-specific recommendations                                                                             |
| 2026-02-04 | Embed `CLAUDE_CONFIG_DIR` in work statusline command (verified)    | Claude Code does not pass env vars to statusline subprocess; wrapper always defaulted to personal profile                                                 |
| 2026-02-04 | Remove `_claude_sync_token` from `.zshrc`                          | Sync copied base keychain (personal) to work entry, overwriting correct work token. Claude Code manages profile entries natively.                         |
| 2026-02-04 | Clean up duplicate keychain entries                                | `_claude_sync_token` created entries with `acct: "Claude Code"` alongside native `acct: "$USER"` entries, causing unpredictable reads                     |
| 2026-02-04 | Patch script now patches both profiles                             | Work HUD was unpatched — script only targeted `~/.claude`                                                                                                 |
| 2026-02-04 | Fix patch detection false-positives                                | Patches 3/4 checked file-wide for `CLAUDE_HUD_CONFIG_DIR`, matched patch 2's homeDir change instead of function-specific usage                            |
| 2026-02-04 | Remove stale `.claude.json.backup`                                 | Backup had `installMethod: "global"`, causing native install mismatch warning                                                                             |
| 2026-02-02 | IDE folder symlink for dual accounts                               | Fix `/ide` errors when using work profile                                                                                                                 |
| 2026-01-27 | Token expiration check in wrapper                                  | Fix HUD showing no usage when token expired                                                                                                               |
| 2026-01-27 | No fallback for work profile                                       | Work (Team) and Personal (Max) are different accounts                                                                                                     |
| 2026-01-26 | Initial documentation                                              | Consolidated all HUD patches and setup info                                                                                                               |
