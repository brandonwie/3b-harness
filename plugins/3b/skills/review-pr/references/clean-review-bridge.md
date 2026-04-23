# Clean Review Bridge — Pointer Document

This document tells the Structure Agent which external reference files to load
for each category it covers. **No content is duplicated here** — agents load the
source files directly.

## Reference File Locations

| File                       | Absolute Path                                                                  |
| -------------------------- | ------------------------------------------------------------------------------ |
| `clean-code-principles.md` | `~/.claude/global-claude-setup/commands/clean-review/clean-code-principles.md` |
| `refactoring-catalog.md`   | `~/.claude/global-claude-setup/commands/clean-review/refactoring-catalog.md`   |
| `TESTING.md`               | `{project_repo}/.claude/prompts/TESTING.md`                                    |
| `BLOCKS.md`                | `{project_repo}/.claude/prompts/BLOCKS.md`                                     |

## Category → Reference Mapping

### 4. Architectural Assessment

Load from `clean-code-principles.md`:

- **SOLID Principles** section (all 5 principles)
- **Chapter 6: Objects and Data Structures** (Law of Demeter, data/object
  anti-symmetry)
- **Chapter 17: Smells & Heuristics** (Rigidity, Fragility, Immobility)
- **Design Rules Summary** (6 rules)

### 2. Code Quality & Style

Load from `clean-code-principles.md`:

- **Chapter 2: Meaningful Names** (intention-revealing, avoid disinformation,
  pronounceable, searchable)
- **Chapter 3: Functions** (small, do one thing, one level of abstraction,
  descriptive names)
- **Chapter 4: Comments** (good comments vs bad comments)

### 6. Maintainability & Simplicity

Load from `refactoring-catalog.md`:

- **Code Smells by Category** (bloaters, OO abusers, change preventers,
  dispensables, couplers)
- **Refactoring Catalog by Category** (composing methods, moving features,
  organizing data, simplifying conditionals, dealing with generalization)
- **Refactoring Workflow** (5-step process)
- **When to Refactor** (6 triggers)

### 5. Test Quality (Runtime Agent)

Load from project `TESTING.md`:

- Test file naming conventions
- Test factory patterns
- Timezone testing rules
- Mock conventions

### Domain Context (All Agents)

When reviewing files under `src/blocks/`, load from project `BLOCKS.md`:

- 10 critical rules (soft delete, manual updatedAt, event architecture)
- Sync protection documentation map
- Event ordering constraints
