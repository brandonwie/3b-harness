#!/usr/bin/env python3
"""PreToolUse hook: gate terraform/tofu/terragrunt state-modifying commands.

Detects terraform apply, destroy, import, state rm/mv, taint, etc.
anywhere in the command string — catches chained commands (&&, ||, ;),
pipes (|), env var prefixes (VAR=x terraform apply), and subshells
(bash -c "terraform apply") that bypass glob-based permission patterns.

Also catches:
  - Global flags between binary and subcommand (-chdir=DIR, -no-color)
  - OpenTofu (tofu) — drop-in terraform replacement
  - Terragrunt — terraform wrapper with its own CLI
  - The -destroy flag on terraform apply (equivalent to terraform destroy)

Decision hierarchy:
  deny  → destroy with -auto-approve (nuclear option)
  ask   → all other state-modifying commands
  (none)→ read-only commands pass through silently
"""
import json
import re
import sys

# Optional flags (like -chdir=DIR) between the binary and subcommand.
# terraform -chdir=infra -no-color apply → must still catch "apply"
_F = r"(?:-\S+\s+)*"

# Subcommands that modify state or infrastructure.
# _F allows any number of dash-prefixed flags between binary and subcommand.
DANGEROUS_SUBCOMMANDS = [
    # Terraform
    rf"terraform\s+{_F}apply",
    rf"terraform\s+{_F}destroy",
    rf"terraform\s+{_F}import",
    rf"terraform\s+{_F}state\s+rm",
    rf"terraform\s+{_F}state\s+mv",
    rf"terraform\s+{_F}state\s+push",
    rf"terraform\s+{_F}state\s+replace-provider",
    rf"terraform\s+{_F}taint",
    rf"terraform\s+{_F}untaint",
    rf"terraform\s+{_F}force-unlock",
    rf"terraform\s+{_F}workspace\s+delete",
    rf"terraform\s+{_F}workspace\s+new",
    rf"terraform\s+{_F}refresh",
    rf"terraform\s+{_F}console",
    # OpenTofu (drop-in terraform replacement, same CLI)
    rf"tofu\s+{_F}apply",
    rf"tofu\s+{_F}destroy",
    rf"tofu\s+{_F}import",
    rf"tofu\s+{_F}state\s+rm",
    rf"tofu\s+{_F}state\s+mv",
    rf"tofu\s+{_F}state\s+push",
    rf"tofu\s+{_F}taint",
    rf"tofu\s+{_F}untaint",
    rf"tofu\s+{_F}force-unlock",
    rf"tofu\s+{_F}refresh",
    rf"tofu\s+{_F}console",
    # Terragrunt (terraform wrapper)
    r"terragrunt\s+apply",
    r"terragrunt\s+destroy",
    r"terragrunt\s+apply-all",
    r"terragrunt\s+destroy-all",
    r"terragrunt\s+run-all\s+apply",
    r"terragrunt\s+run-all\s+destroy",
]

DANGEROUS_RE = re.compile("|".join(DANGEROUS_SUBCOMMANDS))
AUTO_APPROVE_RE = re.compile(r"-auto-approve")
# Detect destroy: explicit subcommand OR -destroy flag on apply
DESTROY_RE = re.compile(rf"(?:terraform|tofu)\s+{_F}destroy")
DESTROY_FLAG_RE = re.compile(r"(?:^|\s)-destroy\b")


def classify(command: str):
    """Return (decision, reason) or None if command is safe."""
    match = DANGEROUS_RE.search(command)
    if not match:
        return None

    matched_cmd = match.group().strip()
    is_destroy = bool(DESTROY_RE.search(command)) or bool(
        DESTROY_FLAG_RE.search(command)
    )
    is_auto = bool(AUTO_APPROVE_RE.search(command))

    if is_destroy and is_auto:
        return (
            "deny",
            f"BLOCKED: '{matched_cmd} -auto-approve' — "
            "destroys infrastructure without confirmation. "
            "Remove -auto-approve or run manually in your terminal.",
        )

    if is_destroy:
        return (
            "ask",
            f"DANGER: '{matched_cmd}' will DESTROY infrastructure. "
            "This can cause production downtime. Confirm to proceed.",
        )

    if is_auto:
        return (
            "ask",
            f"WARNING: '{matched_cmd}' with -auto-approve skips "
            "Terraform's own confirmation prompt. Confirm to proceed.",
        )

    return (
        "ask",
        f"TERRAFORM APPLY: '{matched_cmd}' will modify live infrastructure. "
        "BEFORE confirming: Verify you have completed the Plan Review Protocol — "
        "a structured change table with risk classifications for every resource. "
        "Security group changes must list exact rules added/removed. "
        "Confirm ONLY after the user has acknowledged all DANGER items.",
    )


try:
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name", "")

    # Only inspect Bash commands
    if tool_name != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    result = classify(command)
    if result:
        decision, reason = result
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            },
            sys.stdout,
        )

except Exception:
    # Never block on hook errors — fail open
    sys.exit(0)
