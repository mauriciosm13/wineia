#!/usr/bin/env python3
"""Fail if Python imports use parentheses or span more than one line."""

import ast
import sys
from pathlib import Path

ROOTS = ("api", "core", "domain", "infrastructure", "tests", "quality")
SKIP_PARTS = {".venv", "google-cloud-sdk", ".agents", "__pycache__"}


def import_style_errors(source: str, filename: str = "<string>") -> list[str]:
    errors: list[str] = []
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return [f"{filename}: syntax error: {exc.msg}"]

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        end_lineno = node.end_lineno or node.lineno
        if node.lineno != end_lineno:
            errors.append(f"{filename}:{node.lineno}: import must be a single line (no line break)")
            continue
        segment = ast.get_source_segment(source, node) or ""
        if "(" in segment or ")" in segment:
            errors.append(f"{filename}:{node.lineno}: import must not use parentheses")
    return errors


def iter_python_files(roots: tuple[str, ...] = ROOTS) -> list[Path]:
    files: list[Path] = []
    for root_name in roots:
        root = Path(root_name)
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            files.append(path)
    return sorted(files)


def main() -> int:
    all_errors: list[str] = []
    for path in iter_python_files():
        all_errors.extend(import_style_errors(path.read_text(encoding="utf-8"), str(path)))
    if all_errors:
        print("Import style violations (single line, no parentheses):")
        for error in all_errors:
            print(error)
        return 1
    print("Import style OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
