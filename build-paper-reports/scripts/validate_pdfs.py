#!/usr/bin/env python3
"""Validate PDF signatures and, when available, parse documents with PyMuPDF."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import fitz  # type: ignore
except ImportError:
    fitz = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="PDF files or directories")
    parser.add_argument("--require-text", action="store_true", help="Fail PDFs with no sampled text")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a text summary")
    return parser.parse_args()


def collect_paths(inputs: Iterable[Path]) -> list[Path]:
    found: list[Path] = []
    for item in inputs:
        path = item.expanduser().resolve()
        if path.is_dir():
            found.extend(sorted(path.rglob("*.pdf")))
        else:
            found.append(path)
    return list(dict.fromkeys(found))


def validate(path: Path, require_text: bool) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "valid": True,
        "size_bytes": None,
        "pages": None,
        "sample_text_chars": None,
        "title": None,
        "warnings": [],
        "errors": [],
    }

    if not path.is_file():
        result["errors"].append("file does not exist")
    elif path.suffix.lower() != ".pdf":
        result["errors"].append("file extension is not .pdf")
    else:
        try:
            result["size_bytes"] = path.stat().st_size
            if result["size_bytes"] < 1024:
                result["errors"].append("file is smaller than 1024 bytes")
            with path.open("rb") as stream:
                if b"%PDF-" not in stream.read(1024):
                    result["errors"].append("missing PDF signature in first 1024 bytes")
        except OSError as exc:
            result["errors"].append(f"cannot read file: {exc}")

    if not result["errors"] and fitz is None:
        result["warnings"].append("PyMuPDF is unavailable; only basic signature validation ran")
    elif not result["errors"]:
        try:
            document = fitz.open(path)
            try:
                if document.needs_pass:
                    result["errors"].append("PDF is encrypted and requires a password")
                result["pages"] = document.page_count
                if document.page_count <= 0:
                    result["errors"].append("PDF has no pages")
                else:
                    indexes = sorted({0, document.page_count // 2, document.page_count - 1})
                    text_chars = sum(len(document.load_page(index).get_text("text").strip()) for index in indexes)
                    result["sample_text_chars"] = text_chars
                    if text_chars == 0:
                        message = "sampled pages contain no extractable text; PDF may be scanned"
                        if require_text:
                            result["errors"].append(message)
                        else:
                            result["warnings"].append(message)
                    result["title"] = (document.metadata or {}).get("title") or None
            finally:
                document.close()
        except Exception as exc:  # PyMuPDF raises several format-specific exception types.
            result["errors"].append(f"PDF parser failed: {exc}")

    result["valid"] = not result["errors"]
    return result


def main() -> int:
    args = parse_args()
    paths = collect_paths(args.paths)
    if not paths:
        print("ERROR: no PDF files found", file=sys.stderr)
        return 2

    results = [validate(path, args.require_text) for path in paths]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = "OK" if result["valid"] else "FAIL"
            print(
                f"{status}: {result['path']} | bytes={result['size_bytes']} "
                f"pages={result['pages']} sample_text={result['sample_text_chars']}"
            )
            for warning in result["warnings"]:
                print(f"  WARN: {warning}")
            for error in result["errors"]:
                print(f"  ERROR: {error}")
    return 0 if all(result["valid"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
