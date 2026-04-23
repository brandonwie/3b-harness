#!/usr/bin/env python3
"""B2: Skill routing refinement script.

Compares skill-usage.json (actual invocations) against the CLAUDE.md routing
table (documented routes). Surfaces:
  - Missing routes: skills invoked but not in the routing table
  - Dead routes: skills in the table but never invoked
  - Frequency data: usage counts for prioritization

Usage:
  python3 skill-routing-diff.py [--claude-md PATH] [--usage PATH]

Defaults:
  --claude-md  ~/dev/personal/3b/CLAUDE.md
  --usage      ~/.claude/skill-usage.json
"""
import argparse
import json
import os
import re
import sys


def parse_routing_table(claude_md_path):
    """Extract skill names from the CLAUDE.md Skill Routing table."""
    skills = set()
    in_table = False
    with open(claude_md_path, "r") as f:
        for line in f:
            if "## Skill Routing" in line:
                in_table = True
                continue
            if in_table and line.startswith("## "):
                break
            if in_table and line.startswith("|"):
                # Extract /skill-name from the second column
                cols = [c.strip() for c in line.split("|")]
                if len(cols) >= 3:
                    skill = cols[2].strip()
                    if skill.startswith("/") and skill != "Skill":
                        skills.add(skill.lstrip("/"))
    return skills


def parse_usage(usage_path):
    """Read skill-usage.json and return {skill_name: count}."""
    with open(usage_path, "r") as f:
        data = json.load(f)
    result = {}
    for name, info in data.items():
        if isinstance(info, dict):
            result[name] = info.get("count", 0)
        else:
            result[name] = 0
    return result


def main():
    parser = argparse.ArgumentParser(description="Skill routing table diff")
    parser.add_argument(
        "--claude-md",
        default=os.path.expanduser("~/dev/personal/3b/CLAUDE.md"),
    )
    parser.add_argument(
        "--usage",
        default=os.path.expanduser("~/.claude/skill-usage.json"),
    )
    args = parser.parse_args()

    if not os.path.exists(args.claude_md):
        print(f"Error: {args.claude_md} not found", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.usage):
        print(f"Error: {args.usage} not found", file=sys.stderr)
        sys.exit(1)

    routed = parse_routing_table(args.claude_md)
    usage = parse_usage(args.usage)
    used_names = set(usage.keys())

    # Normalize: routing table uses kebab-case, usage may use colon namespaces
    # Strip namespace prefixes for matching (e.g., "superpowers:brainstorm" → skip)
    first_party_used = {n for n in used_names if ":" not in n}
    namespaced_used = {n for n in used_names if ":" in n}

    missing_routes = first_party_used - routed
    dead_routes = routed - first_party_used

    print("=" * 60)
    print("SKILL ROUTING DIFF")
    print("=" * 60)

    print(f"\nRouted skills (in CLAUDE.md):  {len(routed)}")
    print(f"Used skills (in usage.json):   {len(used_names)}")
    print(f"  First-party:                 {len(first_party_used)}")
    print(f"  Namespaced (plugins):        {len(namespaced_used)}")

    if missing_routes:
        print(f"\n--- MISSING ROUTES ({len(missing_routes)}) ---")
        print("Skills invoked but NOT in the routing table:\n")
        for name in sorted(missing_routes):
            count = usage.get(name, 0)
            print(f"  /{name:<30} invoked {count}x")
    else:
        print("\n--- No missing routes ---")

    if dead_routes:
        print(f"\n--- DEAD ROUTES ({len(dead_routes)}) ---")
        print("Skills in routing table but NEVER invoked:\n")
        for name in sorted(dead_routes):
            print(f"  /{name}")
    else:
        print("\n--- No dead routes ---")

    if namespaced_used:
        print(f"\n--- NAMESPACED SKILLS ({len(namespaced_used)}) ---")
        print("Plugin skills (not expected in routing table):\n")
        for name in sorted(namespaced_used):
            count = usage.get(name, 0)
            print(f"  /{name:<40} invoked {count}x")

    print(f"\n--- USAGE FREQUENCY (top 10) ---\n")
    sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
    for name, count in sorted_usage[:10]:
        routed_mark = "✓" if name in routed else " "
        print(f"  {routed_mark} /{name:<35} {count:>4}x")

    print()


if __name__ == "__main__":
    main()
