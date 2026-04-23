# Claude HUD Patches

Upstream: <https://github.com/jarrodwatts/claude-hud>

This directory contains patches for running Claude HUD with multiple accounts
(personal + work) and custom display features (quota bars, configurable
thresholds, improved reset time formatting).

## The Problem

Claude Code stores OAuth credentials in macOS Keychain under
`"Claude Code-credentials"`. However:

- Each Claude Code installation creates its **own** keychain entry with a unique
  suffix
- The HUD plugin only reads from the base `"Claude Code-credentials"` entry
- This causes both personal and work sessions to show the **same** (incorrect)
  usage stats

## The Solution

We patch the HUD to:

1. **Personal**: Read from the correct keychain entry via
   `CLAUDE_HUD_KEYCHAIN_SERVICE` env var
2. **Work**: Skip keychain entirely and use file-based credentials via
   `CLAUDE_HUD_SKIP_KEYCHAIN=1`

## Directory Structure

```text
~/.claude/                          # Personal profile (default, Max plan)
├── settings.json                   # Global settings (statusLine → wrapper)
├── statusline-wrapper.sh           # Unified HUD wrapper (symlink → 3B)
├── claude-hud-patches/              # THIS DIRECTORY (symlink → 3B)
│   ├── claude-hud-post-patches.sh    # Re-apply patches after updates (both profiles)
│   ├── templates/                  # Template files for complex patches
│   │   ├── colors.ts             # Neon color palette (Group O)
│   │   ├── usage.ts               # Custom usage renderer (Group D)
│   │   ├── speed-tracker.ts       # Output speed tracking (Group I)
│   │   ├── session-line.ts        # Enhanced compact layout (Group J)
│   │   ├── identity.ts            # Enhanced expanded context (Group K)
│   │   ├── project.ts             # Merged project line (Group R)
│   │   ├── quote.ts              # Quote renderer (Group P)
│   │   └── render-index.ts       # Layout with quote (Group Q)
│   └── README.md                   # This file
├── plugins/
│   ├── claude-hud/
│   │   ├── config.json             # HUD display config (symlink → 3B, SoT)
│   │   └── .usage-cache.json       # Personal usage cache
│   └── cache/claude-hud/           # Personal HUD binary (patched independently)
└── ide/                            # VS Code extension registration

~/.claude-work/                     # Work profile (Team plan)
├── ide → ~/.claude/ide             # Shares IDE registration with personal
├── plugins/
│   ├── claude-hud/
│   │   ├── config.json → ~/.claude version  # Shares display config
│   │   └── .usage-cache.json       # Work usage cache (separate)
│   └── cache/claude-hud/           # Work HUD binary (patched independently)
└── ...
```

**Key point:** Each profile has its own independent HUD binary under
`plugins/cache/claude-hud/`. These are NOT symlinked — both must be patched
separately. The `claude-hud-post-patches.sh` script handles this automatically.

## Keychain Entries

Found via: `security dump-keychain | grep "Claude Code"`

| Entry                              | Account  | Plan   | Managed By           |
| ---------------------------------- | -------- | ------ | -------------------- |
| `Claude Code-credentials`          | Base     | varies | Claude Code binary   |
| `Claude Code-credentials-7195fd18` | Personal | max    | Claude Code (native) |
| `Claude Code-credentials-0e3ff1b1` | Work     | team   | Claude Code (native) |

**Note:** Claude Code creates and refreshes these entries automatically. No
manual sync is needed. The HUD reads from the correct entry via the
`CLAUDE_HUD_KEYCHAIN_SERVICE` env var set by the wrapper.

## Wrapper Configuration

A unified `statusline-wrapper.sh` (in 3B, symlinked to `~/.claude/`) detects the
active profile from `CLAUDE_CONFIG_DIR` and sets:

- `CLAUDE_HUD_CONFIG_DIR` → profile-specific cache directory
- `CLAUDE_HUD_KEYCHAIN_SERVICE` → profile-specific keychain entry

**CRITICAL:** Claude Code does **not** pass `CLAUDE_CONFIG_DIR` to statusline
subprocesses. Each profile's `settings.json` must embed the env var in the
statusline command:

```json
// Personal (~/.claude/settings.json) — defaults to ~/.claude, no override needed
"command": "~/.claude/statusline-wrapper.sh"

// Work (~/.claude-work/settings.json) — must explicitly set CLAUDE_CONFIG_DIR
"command": "CLAUDE_CONFIG_DIR=~/.claude-work ~/.claude/statusline-wrapper.sh"
```

The wrapper then derives all HUD settings from `CLAUDE_CONFIG_DIR`:

```bash
# Personal profile → detected from default:
CLAUDE_HUD_CONFIG_DIR=~/.claude CLAUDE_HUD_KEYCHAIN_SERVICE="Claude Code-credentials-7195fd18"

# Work profile → detected from explicit env var:
CLAUDE_HUD_CONFIG_DIR=~/.claude-work CLAUDE_HUD_KEYCHAIN_SERVICE="Claude Code-credentials-0e3ff1b1"
```

## Patches Applied

27 patches organized into 18 groups. All idempotent (grep-before-apply).

### Group A (1-4): Multi-Account — `usage-api.ts`

| Patch | What                                             | Anchor                            |
| ----- | ------------------------------------------------ | --------------------------------- |
| 1     | `CLAUDE_HUD_KEYCHAIN_SERVICE` env var            | `find-generic-password`           |
| 2     | `CLAUDE_HUD_CONFIG_DIR` (homeDir)                | `homeDir: () =>`                  |
| 3     | `CLAUDE_HUD_CONFIG_DIR` (getCachePath)           | `function getCachePath`           |
| 4     | `CLAUDE_HUD_CONFIG_DIR` (getKeychainBackoffPath) | `function getKeychainBackoffPath` |

### Group B (5-6): Display Config — `config.ts`

| Patch | What                                       | Locations Modified           |
| ----- | ------------------------------------------ | ---------------------------- |
| 5     | `usageBarEnabled` (boolean, default: true) | interface + defaults + merge |
| 6     | `sevenDayThreshold` (number, default: 80)  | interface + defaults + merge |

Each field requires 3 sed insertions: interface definition, default value, and
merge validation logic. Anchored to `showUsage` and `usageThreshold`
respectively.

### Group C (7-8): Quota Bar — `colors.ts`

| Patch | What                                      | Method                         |
| ----- | ----------------------------------------- | ------------------------------ |
| 7     | `BRIGHT_BLUE`, `BRIGHT_MAGENTA` constants | sed `r` after `const CYAN`     |
| 8     | `getQuotaColor()`, `quotaBar()` functions | awk insert-before `coloredBar` |

### Group D (9): Usage Renderer — `render/lines/usage.ts`

| Patch | What                                  | Method             |
| ----- | ------------------------------------- | ------------------ |
| 9     | Custom usage renderer with quota bars | Template file copy |

The usage renderer is too heavily customized for sed patches. A full template
file (`templates/usage.ts`) is copied instead. Features:

- `formatResetHours()` — always hours for 5h window
- `formatResetTime()` — days format (`5.2d`) for 7d window
- `formatUsageError()` — error hint display
- Configurable `sevenDayThreshold` from config
- `usageBarEnabled` toggle for quota bar display

### Group E (10): Error Type — `types.ts`

| Patch | What                                     | Method                         |
| ----- | ---------------------------------------- | ------------------------------ |
| 10    | `apiError?: string` field in `UsageData` | sed `r` after `apiUnavailable` |

### Group F (11-12): Context/Speed Config — `config.ts`

| Patch | What                                              | Locations Modified                              |
| ----- | ------------------------------------------------- | ----------------------------------------------- |
| 11    | `contextValue` (`ContextValueMode`, default: `%`) | type + interface + defaults + validator + merge |
| 12    | `showSpeed` (boolean, default: false)             | interface + defaults + merge                    |

Patch 11 adds the `ContextValueMode` type, the `validateContextValue` function,
and inserts the field at 5 locations (type export, interface, defaults, merge,
validator). Patch 12 follows the same 3-location pattern as patches 5-6.

### Group G (13-14): Types — `types.ts`

| Patch | What                                          | Method                            |
| ----- | --------------------------------------------- | --------------------------------- |
| 13    | `output_tokens?: number` in StdinData         | sed `r` after `input_tokens`      |
| 14    | `extraLabel: string \| null` in RenderContext | sed `r` after `config: HudConfig` |

### Group H (15-16): Stdin Helpers — `stdin.ts`

| Patch | What                                           | Method              |
| ----- | ---------------------------------------------- | ------------------- |
| 15    | Export `getTotalTokens` (was private)          | sed `s/` visibility |
| 16    | `isBedrockModelId()`, `getProviderLabel()` fns | cat append          |

### Group I (17): Speed Tracker — `speed-tracker.ts`

| Patch | What                            | Method             |
| ----- | ------------------------------- | ------------------ |
| 17    | `getOutputSpeed()` module (new) | Template file copy |

New module that tracks output token speed across HUD invocations using a
file-based cache. Patched with `CLAUDE_HUD_CONFIG_DIR` support for
multi-account.

### Group J (18): Session Line — `render/session-line.ts`

| Patch | What                                    | Method             |
| ----- | --------------------------------------- | ------------------ |
| 18    | Enhanced session line with all features | Template file copy |

Features: `formatContextValue`, `getOutputSpeed`, `getProviderLabel`,
`quotaBar`, `formatUsageError`, `extraLabel`, `sevenDayThreshold`,
`usageBarEnabled`.

### Group K (19): Identity Line — `render/lines/identity.ts`

| Patch | What                                     | Method             |
| ----- | ---------------------------------------- | ------------------ |
| 19    | Enhanced identity line with contextValue | Template file copy |

Features: `formatContextValue`, `getTotalTokens` import for tokens display mode.

### Group L (20): Project Line — `render/lines/project.ts`

| Patch | What                                         | Method             |
| ----- | -------------------------------------------- | ------------------ |
| 20    | Model badge + provider label on project line | Template file copy |

Features: `[Model | Plan]` display (e.g., `[Opus | Max]`), `getProviderLabel`
for Bedrock billing label, `red('API')` indicator for API key users.

### Group M (21): Render Layout — `render/index.ts`

| Patch | What                                          | Method             |
| ----- | --------------------------------------------- | ------------------ |
| 21    | Reordered expanded layout with combined lines | Template file copy |

Reorders expanded mode: project first, then context+usage combined on one line,
then activity (tools/agents/todos), then environment (config counts) at bottom.

### Group N (22): Usage Speed — `render/lines/usage.ts`

| Patch | What                                  | Method           |
| ----- | ------------------------------------- | ---------------- |
| 22    | Usage line with speed display (tok/s) | Template re-copy |

Adds `getOutputSpeed` import from `speed-tracker.ts` and appends `tok/s` to
usage line when `showSpeed` is enabled and speed data is available.

### Group O (23): Neon Palette — `colors.ts`

| Patch | What                                | Method             |
| ----- | ----------------------------------- | ------------------ |
| 23    | Full neon color palette (256-color) | Template file copy |

Replaces entire `colors.ts` with 256-color ANSI neon palette. Adds `violet()`
export and unifies `getContextColor`/`getQuotaColor` to 4-level thresholds:

| Range   | Color        | ANSI Code  | Meaning       |
| ------- | ------------ | ---------- | ------------- |
| 0%      | Gray (245)   | `38;5;245` | Idle/inactive |
| 1-50%   | Green (46)   | `38;5;46`  | Healthy       |
| 51-90%  | Yellow (226) | `38;5;226` | Warning       |
| 91-100% | Red (196)    | `38;5;196` | Critical      |

Supersedes Group C patches 7-8 (their guards pass since template includes all
previous content).

### Group P (24-25): Quote Display — `config.ts` + `quote.ts`

| Patch | What                                    | Method                         |
| ----- | --------------------------------------- | ------------------------------ |
| 24    | `quote` config field (`string \| null`) | sed (interface+defaults+merge) |
| 25    | `renderQuoteLine()` renderer (new file) | Template file copy             |

Adds configurable quote string to `display` section. Rendered in neon violet
(256-color code 135) as the first line of expanded mode.

### Group Q (26): Quote Layout — `render/index.ts`

| Patch | What                               | Method             |
| ----- | ---------------------------------- | ------------------ |
| 26    | Render layout with quote as Line 0 | Template file copy |

Re-copies `render/index.ts` with `renderQuoteLine` import and call at top of
`renderExpanded()`.

### Group R (27): Merged Project — `render/lines/project.ts`

| Patch | What                                  | Method             |
| ----- | ------------------------------------- | ------------------ |
| 27    | Project line with email + env version | Template file copy |

Re-copies `project.ts` with:

- `CLAUDE_HUD_EMAIL` env var → email on project line
- `CLAUDE_HUD_ENV_LABEL`/`CLAUDE_HUD_ENV_VERSION` → runtime version display
- `getModelDisplayWithVersion()` → parses `claude-opus-4-7` into `Opus 4.7`

## Template Files

The `templates/` directory contains full file replacements for modules that
diverge too far from upstream for sed patches.

| Template           | Target                         | Update When                                              |
| ------------------ | ------------------------------ | -------------------------------------------------------- |
| `colors.ts`        | `src/render/colors.ts`         | Upstream changes color exports or bar functions          |
| `usage.ts`         | `src/render/lines/usage.ts`    | Upstream changes `renderUsageLine` or `UsageData`        |
| `speed-tracker.ts` | `src/speed-tracker.ts`         | Upstream adds speed tracking or changes `StdinData`      |
| `session-line.ts`  | `src/render/session-line.ts`   | Upstream changes `renderSessionLine` or imports          |
| `identity.ts`      | `src/render/lines/identity.ts` | Upstream changes `renderIdentityLine` or imports         |
| `project.ts`       | `src/render/lines/project.ts`  | Upstream changes `renderProjectLine` or imports          |
| `quote.ts`         | `src/render/lines/quote.ts`    | Upstream adds quote rendering or changes `RenderContext` |
| `render-index.ts`  | `src/render/index.ts`          | Upstream changes line order, render function, or imports |

**Updating templates after HUD version bump:**

1. Check if upstream changed the target file: `diff` template vs new upstream
2. If upstream has new features, merge them into the template
3. Run `claude-hud-post-patches.sh` — patches 9, 17-27 copy the updated
   templates

## After Plugin Update

Run the patch script (patches both profiles automatically):

```bash
~/.claude/claude-hud-patches/claude-hud-post-patches.sh
```

Then clear caches:

```bash
rm -f ~/.claude/plugins/claude-hud/.usage-cache.json
rm -f ~/.claude-work/plugins/claude-hud/.usage-cache.json
```

## Verify Patches

```bash
# Group A: Multi-account (both should return > 0)
grep -c "CLAUDE_HUD_CONFIG_DIR" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/usage-api.ts
grep -c "CLAUDE_HUD_CONFIG_DIR" \
  ~/.claude-work/plugins/cache/claude-hud/claude-hud/*/src/usage-api.ts

# Group B: Display config
grep -c "usageBarEnabled" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/config.ts

# Group C: Quota bar
grep -c "quotaBar" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/render/colors.ts

# Group D: Usage renderer
grep -c "formatResetMins" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/render/lines/usage.ts

# Group E: Error type
grep -c "apiError" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/types.ts

# Group F: contextValue + showSpeed config
grep -c "ContextValueMode" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/config.ts
grep -c "showSpeed" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/config.ts

# Group G: types
grep -c "output_tokens" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/types.ts
grep -c "extraLabel" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/types.ts

# Group H: stdin helpers
grep -c "getProviderLabel" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/stdin.ts

# Group I: speed tracker
grep -c "getOutputSpeed" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/speed-tracker.ts

# Group J: session line
grep -c "formatContextValue" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/render/session-line.ts

# Group K: identity
grep -c "formatContextValue" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/render/lines/identity.ts

# Group L: project line
grep -c "getModelName" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/render/lines/project.ts

# Group O: neon palette
grep -c "NEON_VIOLET" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/render/colors.ts

# Group P: quote config + renderer
grep -c "quote:" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/config.ts
grep -c "renderQuoteLine" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/render/lines/quote.ts

# Group Q: quote in render layout
grep -c "renderQuoteLine" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/render/index.ts

# Group R: merged project line
grep -c "CLAUDE_HUD_EMAIL" \
  ~/.claude/plugins/cache/claude-hud/claude-hud/*/src/render/lines/project.ts
```

## Testing

```bash
# Test personal
echo '{"cwd": "'$(pwd)'"}' | ~/.claude/statusline-wrapper.sh

# Test work
CLAUDE_CONFIG_DIR=~/.claude-work echo '{"cwd": "'$(pwd)'"}' | ~/.claude/statusline-wrapper.sh
```

## History: The Keychain Discovery

### Initial Problem (2026-01-14)

- Personal Claude Code session was showing **work account** usage stats (Team
  plan, 73%/94%)
- Expected to see personal account stats (Max plan)

### First Attempt: Separate Config Directories

- Created `~/.claude-personal/` and `~/.claude-work/` directories
- Set up separate `statusline-wrapper.sh` for each account
- **Result**: Still showed work stats because HUD reads from keychain

### Second Attempt: Fake HOME Directory

- Created `~/.claude-work-home/` with symlink `.claude` → `~/.claude-work`
- Set `HOME` env var when running work HUD
- **Result**: Config/cache separated, but keychain is system-wide - still showed
  work stats

### Third Attempt: File-Based Credentials for Work

- Patched work HUD to skip keychain (`CLAUDE_HUD_SKIP_KEYCHAIN=1`)
- Saved work credentials to `~/.claude-work/.credentials.json`
- Ran `/login` in personal session to update keychain
- **Result**: Keychain still showed "team" - login didn't change it!

### The Discovery: Multiple Keychain Entries

Running `security dump-keychain | grep "Claude Code"` revealed:

```text
"Claude Code-credentials"           ← HUD reads this (work)
"Claude Code-credentials-0e3ff1b1"  ← Work duplicate
"Claude Code-credentials-7195fd18"  ← Personal! (hidden)
```

**Key insight**: Claude Code creates **separate keychain entries per
installation** with unique suffixes! The HUD was hardcoded to read from the base
entry (no suffix), missing the personal credentials entirely.

### Final Solution

1. Patched HUD to use `CLAUDE_HUD_KEYCHAIN_SERVICE` env var
2. Patched HUD to use `CLAUDE_HUD_CONFIG_DIR` for cache/backoff paths
3. Unified wrapper detects profile and sets both env vars
4. Both accounts now show correct usage stats!

### How to Find Your Keychain Entry Suffix

```bash
# List all Claude Code keychain entries
security dump-keychain | grep "svce.*Claude Code-credentials"

# Check which entry has your account
security find-generic-password -s "Claude Code-credentials-SUFFIX" -w | jq '.claudeAiOauth.subscriptionType'
```

### Lessons Learned

1. Claude Code supports multiple accounts — each gets its own keychain entry
2. The keychain entry suffix is a hash of the install/config path
3. Claude Code manages profile-specific entries natively (auto-refresh)
4. Manual token sync (`_claude_sync_token`) was harmful — it overwrote correct
   profile entries with the base entry (wrong account). Removed 2026-02-04.
5. Duplicate keychain entries (same service, different `acct`) cause
   unpredictable `security find-generic-password` behavior. Always clean up.
6. After editing `.zshrc`, always reload the shell (`source ~/.zshrc` or new
   terminal). Old functions stay in memory in existing shells.

---

## Troubleshooting

### Check keychain entries

```bash
# List all entries
security dump-keychain 2>/dev/null | grep -E "(svce.*Claude|acct)" | head -20

# Check for DUPLICATES (same service, different acct — should not happen)
security dump-keychain 2>/dev/null | grep "svce.*Claude Code-credentials" | sort | uniq -c
# If any count > 1, delete all and let Claude recreate:
# security delete-generic-password -s "SERVICE_NAME" >/dev/null 2>&1
# (run multiple times — delete only removes the first match)
```

### Check specific keychain content

```bash
# Should show "team" for work, "max" for personal
security find-generic-password -s "Claude Code-credentials-0e3ff1b1" -w 2>/dev/null | \
  python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('claudeAiOauth',{}).get('subscriptionType','N/A'))"
```

### View usage cache

```bash
cat ~/.claude/plugins/claude-hud/.usage-cache.json 2>/dev/null | python3 -m json.tool
cat ~/.claude-work/plugins/claude-hud/.usage-cache.json 2>/dev/null | python3 -m json.tool
```

---

## Update Log

| Date       | Change                                                          | Root Cause                                                                                                     |
| ---------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 2026-03-03 | Add Groups O-R (patches 23-27): neon palette + quote + merged   | Neon HUD redesign: 256-color palette, quote on top, merged project line, 4-level color thresholds              |
| 2026-03-03 | Wrapper passes CLAUDE_HUD_EMAIL/ENV_LABEL/ENV_VERSION to HUD    | Consolidate rendering into HUD; wrapper no longer outputs its own line                                         |
| 2026-03-03 | Add Group L (patch 20) for model badge on project line          | `[Opus \| Max]` display missing from cache project.ts; marketplaces has getModelName + getProviderLabel        |
| 2026-03-03 | Add Groups F-K (patches 11-19) for showSpeed + contextValue     | Features exist in marketplaces version but missing from cache/0.0.6 source                                     |
| 2026-03-03 | Add templates: speed-tracker.ts, session-line.ts, identity.ts   | Files too different from upstream for sed patches; template copy approach                                      |
| 2026-03-03 | Add Groups B-E (patches 5-10) for display features              | Source patches lost on plugin update; quota bars, thresholds, formatResetMins, apiError needed durability      |
| 2026-03-03 | Add `templates/usage.ts` for template-based patching            | usage.ts too heavily customized for sed; hybrid sed + template approach                                        |
| 2026-03-03 | Remove broken Patch 5 (`session-line.ts` 7d threshold)          | Replaced by Group D template with configurable `sevenDayThreshold` from config                                 |
| 2026-02-04 | Embed `CLAUDE_CONFIG_DIR` in work statusline command (verified) | Claude Code does not pass env vars to statusline subprocesses; wrapper defaulted to personal                   |
| 2026-02-04 | Remove `_claude_sync_token` from `.zshrc`                       | Sync overwrote work keychain with personal token; Claude manages entries natively                              |
| 2026-02-04 | Clean up duplicate keychain entries                             | Sync created `acct: "Claude Code"` duplicates alongside native `acct: "$USER"` entries                         |
| 2026-02-04 | Patch script now targets both `~/.claude` and `~/.claude-work`  | Script only patched personal profile; work HUD ran unpatched                                                   |
| 2026-02-04 | Fix patch 3/4 detection (function-scoped grep)                  | File-wide grep for `CLAUDE_HUD_CONFIG_DIR` matched patch 2's homeDir, causing false-positive "Already patched" |
| 2026-01-27 | Token expiration check in wrapper                               | HUD showed no data when token expired                                                                          |
| 2026-01-14 | Initial multi-account discovery and patches                     | HUD hardcoded to base keychain entry                                                                           |
