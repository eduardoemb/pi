#!/usr/bin/env python3
"""Merge only declared user-owned keys into installed Pi JSON files."""
import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path


def load(path):
    return json.loads(path.read_text()) if path.exists() else {}


def _atomic_write_json(path, target):
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


def merge_file(path, desired, kind):
    target = load(path)
    if not isinstance(target, dict) or not isinstance(desired, dict):
        raise ValueError("configuration must be an object")
    if kind in ("mcp", "models", "subagents"):
        key = {
            "mcp": "mcpServers",
            "models": "providers",
            "subagents": "model_profiles",
        }[kind]
        current = target.setdefault(key, {})
        incoming = desired.get(key, {})
        if not isinstance(current, dict) or not isinstance(incoming, dict):
            raise ValueError(f"{key} must be an object")
        for name, value in incoming.items():
            if kind == "mcp" and name in current and current[name] != value:
                raise ValueError(f"conflict for {name}")
            current[name] = value
    else:
        for key, value in desired.items():
            if key in target and target[key] != value:
                raise ValueError(f"conflict for {key}")
            target[key] = value
    _atomic_write_json(path, target)


def sync_agents(source, target):
    """Copy declarative `.md` agent definitions into the installed agents
    directory. Only files ending in `.md` are copied; foreign files at the
    target (package-owned agents) are never removed or overwritten."""
    if not source.is_dir() or not target.is_dir():
        raise ValueError("agents source and target must be directories")
    target.mkdir(parents=True, exist_ok=True)
    for child in sorted(source.iterdir()):
        if not child.is_file() or child.suffix != ".md":
            continue
        shutil.copyfile(child, target / child.name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("settings", "mcp", "models", "subagents", "agents"))
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    if args.kind == "agents":
        sync_agents(args.source, args.target)
    else:
        merge_file(args.target, load(args.source), args.kind)


if __name__ == "__main__":
    main()