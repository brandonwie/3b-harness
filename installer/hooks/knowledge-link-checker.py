#!/usr/bin/env python3
"""C1: Knowledge health check — broken `related:` link detection.

Scans markdown files for `related:` frontmatter entries and verifies each
`path:` resolves to an existing file. Reports broken links with the source
file, target path, and suggested fix.

Usage:
  python3 knowledge-link-checker.py [--root PATH] [--fix-suggestions]

The root path resolves from (priority order):
  1. --root CLI argument
  2. FORGE_3B_ROOT env var
  3. Otherwise: exit 0 (fail-open; non-3B installs are a no-op).
"""
import argparse
import os
import re
import sys


def extract_related_paths(file_path):
    """Extract related: path entries from YAML frontmatter using regex."""
    paths = []
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Extract frontmatter block
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            return paths

        frontmatter = fm_match.group(1)

        # Find all `- path:` entries (handles both quoted and unquoted values)
        for match in re.finditer(r"-\s+path:\s*[\"']?([^\s\"'\n]+)[\"']?", frontmatter):
            paths.append(match.group(1))

    except OSError:
        pass

    return paths


def resolve_path(source_file, relative_path):
    """Resolve a relative path from the source file's directory."""
    source_dir = os.path.dirname(source_file)
    resolved = os.path.normpath(os.path.join(source_dir, relative_path))
    return resolved


def find_similar_file(root, filename):
    """Search for a file with the same basename anywhere under root."""
    basename = os.path.basename(filename)
    matches = []
    for dirpath, _, filenames in os.walk(root):
        if basename in filenames:
            matches.append(os.path.join(dirpath, basename))
    return matches


def main():
    parser = argparse.ArgumentParser(description="Knowledge broken link checker")
    parser.add_argument(
        "--root",
        default=os.environ.get("FORGE_3B_ROOT"),
        help="Knowledge repo root (defaults to $FORGE_3B_ROOT)",
    )
    parser.add_argument(
        "--fix-suggestions",
        action="store_true",
        help="Search for possible correct paths for broken links",
    )
    args = parser.parse_args()

    if not args.root:
        # No 3B configured — link check is a no-op. Matches the fail-open
        # contract documented in installer/README.md for sibling hooks.
        sys.exit(0)

    scan_dirs = [
        os.path.join(args.root, "knowledge"),
        os.path.join(args.root, "guides"),
        os.path.join(args.root, "personal"),
        os.path.join(args.root, "projects"),
    ]

    total_files = 0
    total_links = 0
    broken_links = []

    for scan_dir in scan_dirs:
        if not os.path.isdir(scan_dir):
            continue
        for dirpath, _, filenames in os.walk(scan_dir):
            for filename in filenames:
                if not filename.endswith(".md"):
                    continue
                file_path = os.path.join(dirpath, filename)
                total_files += 1

                related_paths = extract_related_paths(file_path)
                for rel_path in related_paths:
                    total_links += 1
                    resolved = resolve_path(file_path, rel_path)
                    if not os.path.exists(resolved):
                        broken_links.append({
                            "source": os.path.relpath(file_path, args.root),
                            "target": rel_path,
                            "resolved": os.path.relpath(resolved, args.root),
                        })

    print("=" * 60)
    print("KNOWLEDGE LINK HEALTH CHECK")
    print("=" * 60)
    print(f"\nScanned: {total_files} files")
    print(f"Total related: links: {total_links}")
    print(f"Broken links: {len(broken_links)}")

    if broken_links:
        print(f"\n--- BROKEN LINKS ({len(broken_links)}) ---\n")
        for bl in broken_links:
            print(f"  Source: {bl['source']}")
            print(f"  Target: {bl['target']}")
            print(f"  Resolved to: {bl['resolved']} (NOT FOUND)")
            if args.fix_suggestions:
                basename = os.path.basename(bl["target"])
                matches = find_similar_file(args.root, basename)
                if matches:
                    print(f"  Suggestion: {', '.join(os.path.relpath(m, args.root) for m in matches[:3])}")
            print()
    else:
        print("\nAll links resolve correctly.")

    print(f"{'=' * 60}")
    return 1 if broken_links else 0


if __name__ == "__main__":
    sys.exit(main())
