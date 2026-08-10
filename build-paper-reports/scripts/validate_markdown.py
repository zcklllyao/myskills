#!/usr/bin/env python3
"""Check research-report Markdown for common structural and encoding errors."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


HEADING = re.compile(r"^(#{1,6})\s+\S")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
PLACEHOLDER = re.compile(r"\bTODO\b|\[TODO[^\]]*\]|<待填写>|\[待填写\]", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories")
    parser.add_argument("--min-chars", type=int, default=3000, help="Warn below this character count")
    return parser.parse_args()


def collect_paths(inputs: Iterable[Path]) -> list[Path]:
    found: list[Path] = []
    for item in inputs:
        path = item.expanduser().resolve()
        if path.is_dir():
            found.extend(sorted(path.rglob("*.md")))
        else:
            found.append(path)
    return list(dict.fromkeys(found))


def inspect(path: Path, min_chars: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return [f"not valid UTF-8: {exc}"], warnings
    except OSError as exc:
        return [f"cannot read file: {exc}"], warnings

    if "\ufffd" in text:
        errors.append("contains Unicode replacement character U+FFFD")
    if PLACEHOLDER.search(text):
        errors.append("contains unfinished placeholder text")
    if len(text.strip()) < min_chars:
        warnings.append(f"only {len(text.strip())} characters; expected at least {min_chars}")
    if not text.endswith("\n"):
        warnings.append("file does not end with a newline")
    if re.search(r"\]\(\s*\)", text):
        errors.append("contains an empty Markdown link target")

    h1_count = 0
    previous_level: int | None = None
    open_fence: tuple[str, int] | None = None
    display_math_count = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)
            marker_char = marker[0]
            if open_fence is None:
                open_fence = (marker_char, line_number)
            elif open_fence[0] == marker_char:
                open_fence = None
            continue
        if open_fence is not None:
            continue

        display_math_count += line.count("$$")
        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            if level == 1:
                h1_count += 1
            if previous_level is not None and level > previous_level + 1:
                warnings.append(
                    f"heading level jumps from H{previous_level} to H{level} at line {line_number}"
                )
            previous_level = level

    if open_fence is not None:
        errors.append(f"unclosed code fence opened at line {open_fence[1]}")
    if display_math_count % 2:
        errors.append("unmatched $$ display-math delimiter")
    if h1_count != 1:
        errors.append(f"expected exactly one H1 heading, found {h1_count}")
    return errors, warnings


def main() -> int:
    args = parse_args()
    paths = collect_paths(args.paths)
    if not paths:
        print("ERROR: no Markdown files found", file=sys.stderr)
        return 2

    failed = False
    for path in paths:
        if not path.is_file() or path.suffix.lower() != ".md":
            errors, warnings = ["path is not a Markdown file"], []
        else:
            errors, warnings = inspect(path, args.min_chars)
        status = "FAIL" if errors else "OK"
        print(f"{status}: {path}")
        for warning in warnings:
            print(f"  WARN: {warning}")
        for error in errors:
            print(f"  ERROR: {error}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
