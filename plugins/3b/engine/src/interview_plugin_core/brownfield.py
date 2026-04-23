"""Portable brownfield detection helpers for the extracted interview package."""

from __future__ import annotations

from pathlib import Path

_CONFIG_FILES: dict[str, str] = {
    "go.mod": "Go",
    "go.sum": "Go",
    "Cargo.toml": "Rust",
    "package.json": "JavaScript/TypeScript",
    "tsconfig.json": "TypeScript",
    "pyproject.toml": "Python",
    "setup.py": "Python",
    "requirements.txt": "Python",
    "pom.xml": "Java",
    "build.gradle": "Java/Kotlin",
    "build.gradle.kts": "Kotlin",
    "Gemfile": "Ruby",
    "mix.exs": "Elixir",
    "composer.json": "PHP",
    "CMakeLists.txt": "C/C++",
    "Makefile": "Make-based",
}


def detect_brownfield(cwd: str | Path) -> bool:
    """Detect whether a directory looks like an existing software project."""
    try:
        root = Path(cwd)
        return any((root / name).exists() for name in _CONFIG_FILES)
    except Exception:
        return False
