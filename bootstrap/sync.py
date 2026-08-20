#!/usr/bin/env python3
"""Merge only declared user-owned keys into installed Pi JSON files."""
import argparse
import json
import os
import tempfile
from pathlib import Path


def load(path):
    return json.loads(path.read_text()) if path.exists() else {}


def merge_file(path, desired, kind):
    target = load(path)
    if not isinstance(target, dict) or not isinstance(desired, dict):
        raise ValueError("configuration must be an object")
    if kind == "mcp":
        key = "mcpServers"
        current = target.setdefault(key, {})
        incoming = desired.get(key, {})
        if not isinstance(current, dict) or not isinstance(incoming, dict):
            raise ValueError("mcpServers must be an object")
        for name, value in incoming.items():
            if name in current and current[name] != value:
                raise ValueError(f"conflict for {name}")
            current[name] = value
    else:
        for key, value in desired.items():
            if key in target and target[key] != value:
                raise ValueError(f"conflict for {key}")
            target[key] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(target, file, indent=2, sort_keys=True)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_path, path)
    except:
        temporary_path.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("settings", "mcp"))
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    merge_file(args.target, load(args.source), args.kind)


if __name__ == "__main__":
    main()
