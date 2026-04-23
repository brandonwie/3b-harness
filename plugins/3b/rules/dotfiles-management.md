---
paths:
  - "dotfiles/**"
---

# Dotfiles Submodule Management

The `dotfiles/` folder is a **git submodule** containing personal configuration
files (zsh, git, vim, tmux, vscode, etc.).

## Checking for Changes

When working in 3B, check for dotfiles changes with:

```bash
git status  # Shows "modified: dotfiles (modified content)" if changed
```

To see what changed inside dotfiles:

```bash
cd dotfiles && git status && git diff
```

## Commit Workflow (IMPORTANT)

**Never commit dotfiles changes without asking the user first.**

When you detect dotfiles has uncommitted changes:

1. **Report** what changed in dotfiles
2. **Ask** the user if they want to commit and push
3. **Only proceed** with explicit approval

**Commit sequence (after user approval):**

```bash
# 1. Commit inside dotfiles submodule
cd dotfiles
git add -A
git commit -m "description of changes"
git push

# 2. Update submodule reference in 3B
cd ..
git add dotfiles
git commit -m "chore(dotfiles): update submodule reference"
```

## Symlink Health

Apps like gh and karabiner can silently overwrite stow symlinks with regular
files on update. Use `stow-doctor.sh` to detect and repair:

```bash
# From dotfiles directory
./stow-doctor.sh          # check all packages
./stow-doctor.sh fix      # repair broken symlinks

# From anywhere (shell function defined in .zshrc)
dotfiles                  # check all
dotfiles fix              # repair all
```

Run after `brew upgrade`, app updates, or when a config change from the repo
doesn't take effect.

## Why This Matters

- Dotfiles affect all machines using this config
- Changes propagate via `git pull` in dotfiles repo
- Accidental commits can break shell/editor on other machines
- Always verify changes are intentional before committing
