#!/usr/bin/env python3
"""E2: Hook registry verification script.

Diffs settings.json hook definitions against hooks-registry.md documentation.
Surfaces:
  - Undocumented: hooks in settings.json but not in registry
  - Stale docs: hooks in registry but not in settings.json
  - Count mismatches: different hook counts per event

Usage:
  python3 verify-registry.py [--settings PATH] [--registry PATH]

Defaults:
  --settings  ~/dev/personal/3b/.claude/global-claude-setup/settings.json
  --registry  ~/dev/personal/3b/projects/3b/reference/hooks-registry.md
"""
import argparse
import json
import os
import re
import sys


def extract_scripts_from_settings(settings_path):
    """Extract hook scripts from settings.json.

    Returns: {event_name: [(script_name, matcher), ...]}
    """
    with open(settings_path, "r") as f:
        data = json.load(f)

    hooks = data.get("hooks", {})
    result = {}

    for event, entries in hooks.items():
        scripts = []
        for entry in entries:
            matcher = entry.get("matcher", "*")
            for hook in entry.get("hooks", []):
                cmd = hook.get("command", "")
                # Extract script filename from command
                m = re.search(r"([\w-]+\.(?:py|sh))", cmd)
                if m:
                    script_name = m.group(1)
                    # Handle scripts with args (e.g., "track-plugin-usage.py slash")
                    arg_match = re.search(
                        re.escape(script_name) + r"\s+(\w+)", cmd
                    )
                    if arg_match:
                        script_name = f"{script_name} {arg_match.group(1)}"
                    scripts.append((script_name, matcher))
        result[event] = scripts

    return result


def extract_scripts_from_registry(registry_path):
    """Extract hook scripts from hooks-registry.md.

    Returns: {event_name: [(script_name, matcher), ...]}
    """
    result = {}
    current_event = None

    with open(registry_path, "r") as f:
        for line in f:
            # Detect event headers like "## SessionStart (2)"
            header = re.match(r"^## (\w+)\s+\((\d+)\)", line)
            if header:
                current_event = header.group(1)
                result[current_event] = []
                continue

            # Stop at non-event headers
            if line.startswith("## ") and current_event:
                if not re.match(r"^## (\w+)\s+\(", line):
                    current_event = None
                continue

            # Parse table rows
            if current_event and line.startswith("|"):
                cols = [c.strip() for c in line.split("|")]
                if len(cols) >= 4:
                    script_cell = cols[1].strip().strip("`")
                    matcher_cell = cols[2].strip().strip("`")
                    # Skip header/separator rows
                    if script_cell and not script_cell.startswith("-") and script_cell != "Hook":
                        result[current_event].append(
                            (script_cell, matcher_cell)
                        )

    return result


def main():
    parser = argparse.ArgumentParser(description="Hook registry verification")
    parser.add_argument(
        "--settings",
        default=os.path.expanduser(
            "~/dev/personal/3b/.claude/global-claude-setup/settings.json"
        ),
    )
    parser.add_argument(
        "--registry",
        default=os.path.expanduser(
            "~/dev/personal/3b/projects/3b/reference/hooks-registry.md"
        ),
    )
    args = parser.parse_args()

    if not os.path.exists(args.settings):
        print(f"Error: {args.settings} not found", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.registry):
        print(f"Error: {args.registry} not found", file=sys.stderr)
        sys.exit(1)

    settings_hooks = extract_scripts_from_settings(args.settings)
    registry_hooks = extract_scripts_from_registry(args.registry)

    print("=" * 60)
    print("HOOK REGISTRY VERIFICATION")
    print("=" * 60)

    all_events = sorted(set(list(settings_hooks.keys()) + list(registry_hooks.keys())))
    has_issues = False

    for event in all_events:
        s_scripts = {name for name, _ in settings_hooks.get(event, [])}
        r_scripts = {name for name, _ in registry_hooks.get(event, [])}

        undocumented = s_scripts - r_scripts
        stale = r_scripts - s_scripts
        count_settings = len(s_scripts)
        count_registry = len(r_scripts)

        if undocumented or stale or count_settings != count_registry:
            has_issues = True
            print(f"\n--- {event} ---")
            print(f"  settings.json: {count_settings} hooks")
            print(f"  registry.md:   {count_registry} hooks")

            if undocumented:
                print(f"\n  UNDOCUMENTED (in settings, not in registry):")
                for name in sorted(undocumented):
                    print(f"    + {name}")

            if stale:
                print(f"\n  STALE DOCS (in registry, not in settings):")
                for name in sorted(stale):
                    print(f"    - {name}")
        else:
            print(f"\n--- {event}: OK ({count_settings} hooks match) ---")

    # Summary
    total_settings = sum(len(v) for v in settings_hooks.values())
    total_registry = sum(len(v) for v in registry_hooks.values())

    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"  Total in settings.json: {total_settings}")
    print(f"  Total in registry.md:   {total_registry}")
    if has_issues:
        print(f"  STATUS: DRIFT DETECTED — registry needs update")
    else:
        print(f"  STATUS: IN SYNC")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
