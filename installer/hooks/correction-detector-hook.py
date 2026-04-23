#!/usr/bin/env python3
"""UserPromptSubmit hook: detects user corrections and reminds Claude to save
feedback memory.

When a user corrects Claude's approach ("no, use X", "that's wrong", "stop
doing X"), this hook prints a [CORRECTION-DETECTED] advisory. Claude reads
this and saves a feedback-type memory entry for future sessions.

v1.1 (forge v1.4, B1): Also writes corrections to a pending JSON file
(~/.claude/.corrections-pending.json) for /wrap to consume during friction
analysis. Controlled by CLAUDE_CORRECTION_BRIDGE env var (default: enabled).
Set CLAUDE_CORRECTION_BRIDGE=0 to disable file persistence.

Design principles:
  - Regex-based detection (no LLM calls, <10ms)
  - Cooldown: max once per 5 user prompts (prevent noise)
  - Anti-triggers: short prompts, questions, greetings
  - Fail-open: any exception → sys.exit(0)
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Counter file to implement cooldown
COUNTER_PATH = os.path.expanduser("~/.claude/.correction-detector-count")

# Pending corrections file for /wrap consumption (B1 bridge)
PENDING_PATH = os.path.expanduser("~/.claude/.corrections-pending.json")

# Kill switch: set CLAUDE_CORRECTION_BRIDGE=0 to disable file persistence
BRIDGE_ENABLED = os.environ.get("CLAUDE_CORRECTION_BRIDGE", "1") != "0"

# Minimum prompts between detections (prevent noise)
COOLDOWN_PROMPTS = 5

# Minimum prompt length to analyze
MIN_PROMPT_LENGTH = 15

# ---------------------------------------------------------------------------
# Correction patterns (user is correcting Claude's behavior)
# ---------------------------------------------------------------------------

CORRECTION_PATTERNS = [
    # Direct negation + instruction
    r"\bno[,.]?\s+(?:use|do|try|make|put|set|change|switch)\b",
    r"\bno[,.]?\s+(?:that'?s|it'?s|this is)\s+(?:wrong|incorrect|not right)\b",
    r"\bno[,.]?\s+(?:I said|I meant|I want)\b",

    # Explicit correction
    r"\bthat'?s\s+(?:wrong|incorrect|not right|not what)\b",
    r"\bthat\s+(?:was|is)\s+(?:wrong|incorrect|a mistake)\b",

    # Stop/don't directives
    r"\bstop\s+(?:doing|using|adding|creating|making|putting)\b",
    r"\bdon'?t\s+(?:do|use|add|create|make|put|ever)\b",

    # "Actually" corrections
    r"\bactually[,.]?\s+(?:you should|it should|use|we need|the)\b",

    # "Not like that" patterns
    r"\bnot\s+like\s+that\b",
    r"\bnot\s+what\s+I\s+(?:meant|asked|wanted)\b",

    # "You should have" / "should be"
    r"\byou\s+should\s+(?:have|be|use)\b",
    r"\bit\s+should\s+(?:be|use|have)\b",

    # "Instead" corrections
    r"\binstead[,.]?\s+(?:use|do|try|of)\b",

    # "Wrong" declarations
    r"\bwrong\s+(?:approach|way|method|file|path|function|variable)\b",

    # Korean correction patterns
    r"아니[요]?\s",
    r"그게\s+아니",
    r"잘못\s+(?:했|된|됐)",
    r"다시\s+해",
]

# ---------------------------------------------------------------------------
# Anti-triggers (suppress detection)
# ---------------------------------------------------------------------------

ANTI_PATTERNS = [
    # Questions (user asking, not correcting)
    r"\?\s*$",

    # Greetings / acknowledgments
    r"^(?:hi|hello|hey|thanks|thank you|great|good|nice|awesome|perfect)\b",

    # Affirmative responses
    r"^(?:yes|y|ok|okay|sure|right|correct|exactly|agreed)\b",

    # Code blocks (user pasting code, not correcting)
    r"^```",

    # Hook-observation XML injected by observer sessions — these are NOT
    # user prompts, they are structured records injected into the prompt
    # field. Matching "instead of" / "don't add" inside the body is noise.
    r"^\s*<(?:observed_from_primary_session|hook_observation|user-prompt-submit-hook|system-reminder)\b",
]


# ---------------------------------------------------------------------------
# XML-stripping excerpt helper
# ---------------------------------------------------------------------------

def extract_excerpt(prompt, match_start, match_end, window=250, max_len=600):
    """Return a match-anchored excerpt of the user prompt.

    Captures ``window`` characters before/after the matched pattern, then
    caps the total at ``max_len``. Falls back to the first ``max_len`` chars
    when no valid match position is supplied.

    Rationale: the 200-char from-start slice loses the referent when the
    match falls deep in a long prompt. Anchoring around the match preserves
    the signal needed to judge whether the correction is real and save
    useful memory content.
    """
    if match_start is None or match_end is None:
        return prompt[:max_len]
    start = max(0, match_start - window)
    end = min(len(prompt), match_end + window)
    excerpt = prompt[start:end]
    if start > 0:
        excerpt = "…" + excerpt
    if end < len(prompt):
        excerpt = excerpt + "…"
    return excerpt[:max_len]


# ---------------------------------------------------------------------------
# Cooldown management
# ---------------------------------------------------------------------------

def get_prompt_count():
    """Read the prompt counter."""
    try:
        if os.path.exists(COUNTER_PATH):
            with open(COUNTER_PATH, "r") as f:
                return int(f.read().strip())
    except (ValueError, OSError):
        pass
    return 0


def set_prompt_count(count):
    """Write the prompt counter."""
    try:
        with open(COUNTER_PATH, "w") as f:
            f.write(str(count))
    except OSError:
        pass


def persist_correction(matched_signal, prompt_excerpt):
    """Append correction to pending JSON file for /wrap consumption."""
    if not BRIDGE_ENABLED:
        return
    try:
        pending = []
        if os.path.exists(PENDING_PATH):
            with open(PENDING_PATH, "r") as f:
                pending = json.load(f)
        pending.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "matched_signal": matched_signal,
            "prompt_excerpt": prompt_excerpt,
        })
        with open(PENDING_PATH, "w") as f:
            json.dump(pending, f, indent=2)
    except (OSError, json.JSONDecodeError):
        pass  # Never fail — persistence is best-effort


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

try:
    data = json.load(sys.stdin)
    prompt = data.get("prompt", "").strip()

    # Anti-trigger: too short
    if len(prompt) < MIN_PROMPT_LENGTH:
        sys.exit(0)

    prompt_lower = prompt.lower()

    # Anti-trigger: matches suppression patterns
    for pattern in ANTI_PATTERNS:
        if re.search(pattern, prompt_lower):
            sys.exit(0)

    # Cooldown: increment counter, check if in cooldown period
    count = get_prompt_count()
    count += 1
    set_prompt_count(count)

    # Check for correction patterns
    matched = False
    matched_pattern = ""
    match_start = None
    match_end = None
    for pattern in CORRECTION_PATTERNS:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            matched = True
            matched_pattern = match.group(0)
            match_start = match.start()
            match_end = match.end()
            break

    if not matched:
        sys.exit(0)

    # Cooldown check: only fire every COOLDOWN_PROMPTS prompts
    if count % COOLDOWN_PROMPTS != 1 and count != 1:
        sys.exit(0)

    # Reset counter on detection
    set_prompt_count(0)

    # Persist to JSON for /wrap consumption (B1 bridge)
    excerpt = extract_excerpt(prompt, match_start, match_end)
    persist_correction(matched_pattern, excerpt)

    print(
        "\n[CORRECTION-DETECTED] The user appears to be correcting your "
        "approach. Consider saving a feedback memory entry so this correction "
        "persists across sessions.\n"
        f"  Detected signal: \"{matched_pattern}\"\n"
        "  Memory type: feedback\n"
        "  Include: what was wrong, why, and how to apply in future.\n"
    )

except Exception:
    pass  # Never fail — hooks must be non-blocking
