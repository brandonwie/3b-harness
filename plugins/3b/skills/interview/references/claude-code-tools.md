# Tool-name mapping: Claude Code (default)

SKILL.md is written in Claude Code's native tool vocabulary, so when
running inside Claude Code **no translation is needed** — use the tool
names as written.

| SKILL.md says | Claude Code tool |
|---|---|
| `Read` | `Read` |
| `Write` | `Write` |
| `Edit` | `Edit` |
| `Grep` | `Grep` |
| `Glob` | `Glob` |
| `Bash` | `Bash` |
| `AskUserQuestion` | `AskUserQuestion` |
| `WebFetch` | `WebFetch` |
| `WebSearch` | `WebSearch` |
| `${CLAUDE_PLUGIN_ROOT}` | resolved automatically to the plugin's install path |

## Notes

- Claude Code's `AskUserQuestion` uses structured `{label, description}`
  option objects. The SKILL.md examples are authored in that format.
- If you are NOT running in Claude Code, see the sibling mapping files:
  - [`codex-tools.md`](./codex-tools.md)
  - [`gemini-tools.md`](./gemini-tools.md)
