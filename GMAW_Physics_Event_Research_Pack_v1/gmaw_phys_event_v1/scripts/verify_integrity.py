#!/usr/bin/env python3
"""Verify the release file checksums without importing machine-learning packages."""
from pathlib import Path
import hashlib
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = root / "SHA256SUMS"
    if not manifest.is_file():
        raise SystemExit("SHA256SUMS is missing; use the full release archive.")
    checked, failed = 0, []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            failed.append(relative + ": missing or outside package")
            continue
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        checked += 1
        if digest.hexdigest() != expected:
            failed.append(relative + ": checksum changed")
    print(f"Checked {checked} release files; mismatches={len(failed)}")
    for message in failed:
        print(message)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
