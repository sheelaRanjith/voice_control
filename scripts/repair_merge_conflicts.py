#!/usr/bin/env python3
"""Repair git-merge conflict markers in a text file.

Default behavior keeps the "ours" side (top block) between:
<<<<<<<
=======
>>>>>>>

Usage:
  python scripts/repair_merge_conflicts.py backend/app.py
  python scripts/repair_merge_conflicts.py backend/app.py --take theirs
"""

from __future__ import annotations

import argparse
from pathlib import Path


def resolve_conflicts(text: str, take: str) -> str:
    lines = text.splitlines(keepends=True)
    out = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith("<<<<<<<"):
            out.append(line)
            i += 1
            continue

        i += 1
        ours = []
        while i < len(lines) and not lines[i].startswith("======="):
            ours.append(lines[i])
            i += 1

        if i >= len(lines):
            raise ValueError("Malformed conflict block: missing =======")

        i += 1
        theirs = []
        while i < len(lines) and not lines[i].startswith(">>>>>>>"):
            theirs.append(lines[i])
            i += 1

        if i >= len(lines):
            raise ValueError("Malformed conflict block: missing >>>>>>>")

        i += 1
        out.extend(ours if take == "ours" else theirs)

    return "".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair git merge conflict markers in a file")
    parser.add_argument("path", help="Path to file containing conflict markers")
    parser.add_argument("--take", choices=["ours", "theirs"], default="ours")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"[ERROR] File not found: {path}")
        return 1

    original = path.read_text(encoding="utf-8")
    if "<<<<<<<" not in original:
        print(f"No conflict markers found in {path}.")
        return 0

    repaired = resolve_conflicts(original, take=args.take)
    path.write_text(repaired, encoding="utf-8")
    print(f"Repaired {path} by keeping '{args.take}' sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
