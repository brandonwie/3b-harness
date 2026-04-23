---
paths:
  - "**/.tool-versions"
  - "**/Brewfile"
  - "**/Brewfile.lock.json"
  - "**/*.rb" # Homebrew formulae
  - "**/package.json"
  - "**/requirements*.txt"
  - "**/pyproject.toml"
  - "**/Cargo.toml"
  - "**/go.mod"
  - "**/build.gradle*"
  - "**/pom.xml"
  - "**/deno.json"
  - "**/bun.lock"
  - "**/bunfig.toml"
---

# Runtime Environment

**Strategy:** asdf for dev language runtimes (version pinning per-project),
Homebrew for apps and tools. Never use `nvm`, `pyenv`, `rustup`, or other
single-language managers.

## asdf Runtimes (`~/.tool-versions`)

| Runtime | Global Version | Notes                                   |
| ------- | -------------- | --------------------------------------- |
| Node.js | 24.14.0        | Also has npm/npx                        |
| Python  | 3.14.3         | 3.11.7, 3.12.13, 3.13.12 also installed |
| Java    | Temurin 25.0.2 | OpenJDK 21.0.2 also installed           |
| Rust    | 1.94.0         | Includes cargo                          |
| Bun     | 1.3.10         |                                         |
| Deno    | 2.7.5          |                                         |
| Go      | 1.26.1         | Plugin name: `golang`                   |
| Kotlin  | 2.3.10         | Runs on asdf Java (JRE 25)              |

**Key commands:** `asdf list`, `asdf install <plugin> <ver>`,
`asdf set <plugin> <ver>`, `asdf reshim <plugin>`.

Per-project `.tool-versions` overrides global. After installing new binaries
(pip, npm global), run `asdf reshim <plugin>`.

## Brew-Managed Languages

These stay on Homebrew — either as direct tools or as transitive deps of brew
apps. They don't conflict with asdf (shims take PATH priority).

| Formula     | Why on Brew                          |
| ----------- | ------------------------------------ |
| php         | Tool/CLI; asdf build fails on macOS  |
| python@3.13 | Transitive dep of awscli, gcloud-cli |
| python@3.14 | Transitive dep of commitizen         |
| luajit      | Transitive dep of neovim             |

## Why It Exists

Migrated from global `~/.claude/CLAUDE.md` on 2026-04-18 as part of token usage
reduction (issue #13). Only relevant when working with language runtime config
files — no reason to auto-load every session.

## Related

- `knowledge/devops/claude-code-scoped-project-instructions.md` — rules-file
  scoping mechanism + rationale
