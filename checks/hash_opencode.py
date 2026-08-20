#!/usr/bin/env python3
"""Emit a deterministic aggregate hash from public metadata (no content reads).

Never reads file contents, credentials, configuration, plugins, or sessions.
Hashes only public filesystem metadata: each relative path and its byte size.
A change in any path or size proves non-mutation without exposing the payload.
"""
import argparse
import hashlib
from pathlib import Path


def aggregate_metadata(root: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(path.stat().st_size).encode("utf-8"))
        digest.update(b"\0")
    return len(files), digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if not args.root.is_dir():
        raise SystemExit("OpenCode root is unavailable")
    files, digest = aggregate_metadata(args.root)
    print(f"files={files} metadata_sha256={digest}")


if __name__ == "__main__":
    main()
