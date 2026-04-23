# RTK - Rust Token Killer

**Usage**: Token-optimized CLI proxy (60-90% savings on dev operations)

## Meta Commands (always use rtk directly)

```bash
rtk gain              # Show token savings analytics
rtk gain --history    # Show command usage history with savings
rtk discover          # Analyze Claude Code history for missed opportunities
rtk proxy <cmd>       # Execute raw command without filtering (for debugging)
```

## Installation Verification

```bash
rtk --version         # Should show: rtk X.Y.Z
rtk gain              # Should work (not "command not found")
which rtk             # Verify correct binary
```

⚠️ **Name collision**: If `rtk gain` fails, you may have reachingforthejack/rtk
(Rust Type Kit) installed instead.

## Hook Status: DISABLED (2026-03-21)

The PreToolUse hook (`rtk-rewrite.sh`) has been **removed from settings.json**.

**Why:** The hook returned `permissionDecision: "allow"` unconditionally for all
rewritten commands, bypassing `deny` and `ask` patterns in settings.json. This
created a systemic security vulnerability — any command RTK could rewrite
(including `aws` CLI) would skip permission checks. Upstream issues #260 and
issue 243 are unresolved.

**RTK binary still works standalone:** prefix any command with `rtk` manually
(e.g., `rtk git status`). Only the automatic hook integration is disabled.

**Re-enable when:** upstream issue #260 is fixed with proper permission
passthrough (hook should NOT override `ask`/`deny` decisions).
