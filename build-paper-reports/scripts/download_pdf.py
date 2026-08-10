#!/usr/bin/env python3
"""Download a direct PDF URL safely through a temporary .part file."""

from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/124 Safari/537.36 CodexPaperReport/1.0"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Verified direct PDF URL")
    parser.add_argument("--output", required=True, type=Path, help="Destination .pdf path")
    parser.add_argument("--timeout", type=int, default=120, help="Network timeout in seconds")
    parser.add_argument("--min-bytes", type=int, default=1024, help="Minimum accepted file size")
    parser.add_argument("--force", action="store_true", help="Replace an existing destination")
    return parser.parse_args()


def has_pdf_header(path: Path) -> bool:
    with path.open("rb") as stream:
        return b"%PDF-" in stream.read(1024)


def main() -> int:
    args = parse_args()
    output = args.output.expanduser().resolve()
    if output.suffix.lower() != ".pdf":
        print("ERROR: --output must end in .pdf", file=sys.stderr)
        return 2
    if output.exists() and not args.force:
        print(f"ERROR: destination exists; validate/reuse it or pass --force: {output}", file=sys.stderr)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    part = output.with_name(output.name + ".part")
    if part.exists():
        part.unlink()

    request = urllib.request.Request(
        args.url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*;q=0.8"},
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response, part.open("wb") as sink:
            content_type = response.headers.get_content_type()
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                sink.write(chunk)

        size = part.stat().st_size
        if size < args.min_bytes:
            raise ValueError(f"download is too small ({size} bytes)")
        if not has_pdf_header(part):
            raise ValueError("download has no PDF header; the URL may have returned HTML")

        os.replace(part, output)
        print(f"OK: {output} ({size} bytes, content-type={content_type})")
        return 0
    except (OSError, ValueError, urllib.error.URLError) as exc:
        if part.exists():
            part.unlink()
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
