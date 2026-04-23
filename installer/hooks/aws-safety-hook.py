#!/usr/bin/env python3
"""PreToolUse hook: gate destructive AWS CLI commands.

Detects AWS CLI commands that modify, delete, or create resources
anywhere in the command string — catches chained commands (&&, ||, ;),
pipes (|), env var prefixes (VAR=x aws ec2 ...), and subshells
(bash -c "aws ec2 ...") that bypass glob-based permission patterns.

Decision hierarchy:
  ask   → all state-modifying AWS CLI commands
  (none)→ read-only commands (describe-*, list-*, get-*) pass through silently

Modeled on terraform-safety-hook.py. Same architecture:
  regex detection → classify() → permission decision.
"""
import json
import re
import sys

# AWS CLI verbs that modify infrastructure state.
# Regex uses \S+ to match any service name, catching all AWS services.
DANGEROUS_PATTERNS = [
    # Destructive verbs across all services
    r"aws\s+\S+\s+delete-\S*",
    r"aws\s+\S+\s+remove-\S*",
    r"aws\s+\S+\s+terminate-\S*",
    r"aws\s+\S+\s+revoke-\S*",
    r"aws\s+\S+\s+deregister-\S*",
    r"aws\s+\S+\s+disassociate-\S*",
    r"aws\s+\S+\s+release-\S*",
    r"aws\s+\S+\s+deauthorize-\S*",
    # Mutating verbs across all services
    r"aws\s+\S+\s+modify-\S*",
    r"aws\s+\S+\s+update-\S*",
    r"aws\s+\S+\s+create-\S*",
    r"aws\s+\S+\s+put-\S*",
    r"aws\s+\S+\s+attach-\S*",
    r"aws\s+\S+\s+detach-\S*",
    r"aws\s+\S+\s+stop-\S*",
    # EC2 specific
    r"aws\s+ec2\s+run-instances\b",
    # IAM specific (broad — IAM changes are high-risk)
    r"aws\s+iam\s+\S+",
    # S3 destructive operations
    r"aws\s+s3\s+rm\b",
    r"aws\s+s3\s+rb\b",
    r"aws\s+s3\s+mv\b",
    r"aws\s+s3api\s+delete-\S*",
    r"aws\s+s3api\s+put-\S*",
    # Route53 (DNS changes)
    r"aws\s+route53\s+change-\S*",
]

# Read-only IAM subcommands that should NOT trigger the hook.
# Without this, the broad IAM pattern above would block harmless reads.
IAM_READONLY = re.compile(
    r"aws\s+iam\s+(get-|list-|generate-|simulate-)\S*"
)

DANGEROUS_RE = re.compile("|".join(DANGEROUS_PATTERNS))


def extract_service_and_verb(match_text: str):
    """Extract AWS service and verb from matched text."""
    parts = match_text.split()
    if len(parts) >= 3:
        return parts[1], parts[2]
    if len(parts) >= 2:
        return parts[1], "unknown"
    return "unknown", "unknown"


def classify(command: str):
    """Return (decision, reason) or None if command is safe."""
    match = DANGEROUS_RE.search(command)
    if not match:
        return None

    matched_text = match.group().strip()

    # Exempt read-only IAM operations
    if IAM_READONLY.search(command) and "iam" in matched_text:
        # Only exempt if the ENTIRE aws iam command is read-only
        # If there are multiple aws commands chained, still flag
        iam_commands = re.findall(r"aws\s+iam\s+\S+", command)
        if all(IAM_READONLY.search(c) for c in iam_commands):
            return None

    service, verb = extract_service_and_verb(matched_text)

    return (
        "ask",
        f"AWS CLI: '{service} {verb}' will modify cloud resources. "
        "This action may change production infrastructure. "
        "Confirm to proceed.",
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
