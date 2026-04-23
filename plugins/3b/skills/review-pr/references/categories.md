# Review Categories — Proactive PR Review

7 review categories organized by agent group. Each category includes generic
checklist items and NestJS/TypeORM-specific items for this project.

---

## Safety Agent Categories

### 1. Security Review

**Generic checklist:**

- [ ] Injection risks (SQL, command, template injection)
- [ ] Authentication/authorization flaws (missing guards, role checks)
- [ ] Data exposure (sensitive fields in responses, logging PII)
- [ ] Hardcoded secrets (env vars, API keys, connection strings)
- [ ] CORS/CSRF/rate limiting gaps
- [ ] Input validation missing or insufficient
- [ ] Unsafe deserialization or eval usage
- [ ] Path traversal or file access vulnerabilities

**NestJS/TypeORM-specific:**

- [ ] Missing `@UseGuards()` on controller endpoints
- [ ] Missing `ValidationPipe` or class-validator decorators on DTOs
- [ ] Raw SQL queries without parameterization (prefer QueryBuilder)
- [ ] Helmet/CORS misconfiguration in `main.ts`
- [ ] Sensitive entity fields exposed without `@Exclude()` or response DTOs
- [ ] TypeORM `.query()` with string interpolation (SQL injection risk)

### 7. Dependency & Deployment Safety

**Generic checklist:**

- [ ] Breaking changes to API contracts (request/response shape changes)
- [ ] Breaking changes to DB schema (column drops, type changes)
- [ ] New environment variables required but not documented
- [ ] Migration safety (reversibility, data preservation, idempotency)
- [ ] New dependency impact (bundle size, license compatibility, known CVEs)
- [ ] Observability gaps (missing logging, error tracking, health checks)
- [ ] Configuration changes that affect other environments

**NestJS/TypeORM-specific:**

- [ ] TypeORM migration ordering (timestamps must be sequential)
- [ ] `synchronize: true` in production config (NEVER)
- [ ] Docker/ECS config changes (port mappings, env vars, health checks)
- [ ] Entity column changes without corresponding migration
- [ ] Cascade options that could cause unintended deletes
- [ ] Missing `@Index()` on frequently queried columns in new entities

---

## Structure Agent Categories

### 4. Architectural Assessment

**Generic checklist:**

- [ ] Separation of concerns (controller → service → repository layers)
- [ ] SOLID principles adherence (especially SRP and DIP)
- [ ] Module boundary violations (cross-module direct imports)
- [ ] Appropriate design pattern usage
- [ ] Consistent abstraction levels within functions/methods
- [ ] Circular dependency risks

**NestJS/TypeORM-specific:**

- [ ] Business logic leaking into controllers (should be in services)
- [ ] Repository access from controllers (must go through service layer)
- [ ] Direct cross-module service injection (use module exports properly)
- [ ] Entity logic that belongs in a service (fat entities)
- [ ] Missing module registration for new providers/controllers
- [ ] Proper use of NestJS DI (avoid `new` for injectable services)

**Cross-reference:** Load `clean-code-principles.md` — SOLID section, Ch.6
(Objects and Data Structures), Ch.17 (Design Smells)

### 2. Code Quality & Style

**Generic checklist:**

- [ ] Naming conventions (intention-revealing, consistent, searchable)
- [ ] Function structure (single responsibility, appropriate length)
- [ ] Dead code or commented-out code
- [ ] Magic numbers/strings without named constants
- [ ] Consistent error handling patterns
- [ ] Appropriate use of types (no `any` without justification)

**Project-specific conventions** — load from the caller's `CLAUDE.md` /
`AGENTS.md` / equivalent project-rules file. Typical items to check for
here (customize per project):

- Date / time handling rules (native `Date` vs a project-supplied util)
- Type-safety escape hatches (`!`, `as Type`, `any` without justification)
- Test file naming + location convention
- Comment / docstring style

**Cross-reference:** if `clean-review` plugin is installed, load
`/clean-review:clean-code-principles` (Ch.2 Meaningful Names, Ch.3
Functions, Ch.4 Comments).

### 6. Maintainability & Simplicity

**Generic checklist:**

- [ ] Cyclomatic complexity (deeply nested conditionals, long switch chains)
- [ ] Code smell detection (bloaters, couplers, dispensables)
- [ ] Atomic changes (one concern per PR, not mixed refactor + feature)
- [ ] Readability and self-documenting code
- [ ] Over-engineering (premature abstraction, YAGNI violations)
- [ ] Copy-paste duplication (Rule of Three)

**NestJS/TypeORM-specific:**

- [ ] Overly complex QueryBuilder chains (consider breaking into methods)
- [ ] God services (single service doing too many things)
- [ ] Unused module imports or provider registrations
- [ ] Overly generic utility functions (prefer specific, discoverable code)

**Cross-reference:** Load `refactoring-catalog.md` — Code Smells by Category,
Refactoring Workflow

---

## Runtime Agent Categories

### 3. Performance Analysis

**Generic checklist:**

- [ ] N+1 query detection (loops with DB calls inside)
- [ ] Inefficient DB queries (JS filtering instead of DB-level WHERE)
- [ ] Memory: holding full objects when only IDs/fields needed
- [ ] Batching for large operations (bulk insert/update/delete)
- [ ] Unnecessary sequential operations (could be parallelized)
- [ ] Missing pagination for unbounded result sets

**NestJS/TypeORM-specific:**

- [ ] Eager loading traps (`eager: true` in entity relations)
- [ ] Missing `select` in find options (fetching all columns)
- [ ] QueryBuilder vs `find()` — use QueryBuilder for complex queries
- [ ] Missing `.take()` / `.skip()` on queries without limits
- [ ] Inefficient `leftJoinAndSelect` (loading full relation trees)
- [ ] `save()` vs `update()` — `save()` loads entity first, `update()` doesn't

**Complexity targets (default template — override in project `CLAUDE.md` if
the project declares its own scale profile):**

| Data Size  | Acceptable Time | Notes                       |
| ---------- | --------------- | --------------------------- |
| < 1k items | O(n²) okay      | Small data, simplicity wins |
| 1k - 10k   | O(n log n) max  | Typical app scale           |
| 10k - 100k | O(n) required   | Power-user scale            |
| 100k+      | O(n) + batching | Extreme scale               |

**Always ask:** "What happens at the project's upper-bound scale?"

### 5. Test Quality

**Generic checklist:**

- [ ] Coverage gaps (changed source code without corresponding test updates)
- [ ] Flakiness indicators (timing deps, ordering deps, shared mutable state)
- [ ] Behavioral vs implementation testing ratio (test outcomes, not internals)
- [ ] Test isolation (each test independent, no cross-test state leakage)
- [ ] Meaningful assertions (not just "doesn't throw")
- [ ] Edge case coverage (nulls, empty arrays, boundary values)

**Project-specific conventions** — load from the caller's `CLAUDE.md` /
`TESTING.md` / equivalent. Typical items to check for here (customize per
project):

- Test file naming + co-location convention
- Mock quality (realistic data, not testing mocks themselves)
- Project-supplied test-factory helpers
- Timezone / time-sensitive test hygiene
- Mock location convention
- One-concern-per-test-file rule

**Cross-reference:** load the project's `TESTING.md` (or equivalent) for
full testing guidelines.
