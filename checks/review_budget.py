#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path

UNITS = {
    "pr1": {
        ".gitignore", ".github/PULL_REQUEST_TEMPLATE.md", ".github/workflows/validate.yml",
        "bootstrap/install.sh", "bootstrap/sync.py", "checks/final-core.sh", "checks/focused-core.sh",
        "checks/review_budget.py", "checks/test_sync.py", "config/manifest.json",
        "config/pi/mcp.user.json", "config/pi/settings.user.json",
    },
    "pr2": {
        "bootstrap/install.sh", "checks/final-runtime.sh", "checks/focused-runtime.sh",
        "checks/hash_opencode.py", "checks/review_budget.py", "config/manifest.json",
        "config/pi/models.user.json", "config/pi/settings.user.json",
    },
    "pr3": {
        "AGENTS.md", "README.md", "checks/final.sh", "checks/focused-operations.sh",
        "checks/review_budget.py", "config/manifest.json", "docs/migration.md",
    },
}


def allowed_path(path, unit="pr1"):
    return path in UNITS[unit] and not path.lower().endswith((".mdx", ".sh.md"))


def canonical_root(actual, expected):
    return Path(actual).resolve() == Path(expected).resolve()


def expected_remote(remote):
    return remote in ("https://github.com/eduardoemb/pi.git", "git@github.com:eduardoemb/pi.git")


def expected_refspec(refspec):
    return refspec == "origin feat/pi-bootstrap-core:feat/pi-bootstrap-core"


def pr_target(repo, base, head):
    return repo == "eduardoemb/pi" and base == "main" and head == "feat/pi-bootstrap-core"


def run(*args):
    return subprocess.check_output(args, text=True).splitlines()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", required=True, choices=("pr1", "pr2", "pr3"))
    parser.add_argument("--max", type=int, default=400)
    args = parser.parse_args()
    root = run("git", "rev-parse", "--show-toplevel")[0]
    if not canonical_root(Path.cwd(), root) or not expected_remote(run("git", "remote", "get-url", "origin")[0]):
        raise SystemExit("unsafe repository or remote")
    paths = run("git", "diff", "--cached", "--name-only")
    stats = run("git", "diff", "--cached", "--numstat")
    if not paths or any(not allowed_path(path, args.unit) for path in paths) or any("-" in row.split("\t")[:2] for row in stats):
        raise SystemExit("unsafe staged manifest")
    total = sum(int(row.split("\t")[0]) + int(row.split("\t")[1]) for row in stats)
    if total > args.max:
        raise SystemExit(f"review budget exceeded: {total}>{args.max}")
    print(f"{args.unit}: {total}/{args.max} changed lines")


if __name__ == "__main__":
    main()
