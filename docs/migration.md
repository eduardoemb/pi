# Pi Migration and Operations Guide

This guide documents how this repository migrates the OpenCode workflow to
`pi`: ownership, privacy, baseline contract, rollback, acceptance gates, and
accepted gaps.

## Migration and publication nuance

The repository is the declarative source and validation project for an
independent Pi host. It publishes only secret-free, repository-owned assets.
This repository is **public**, so the secret-free rules apply with higher
priority: `.gitignore` excludes `.atl/`, `.opencode/`, `.pi/`, and secret
paths. No credentials, sessions, caches, backups, or generated assets are
committed.

## Ownership model

Configuration is merged by key, never replaced whole-file. `settings.json`:
package owns generated entries; user owns provider, model, project trust, and
telemetry (trust never in a project-level `.pi/settings.json`). `mcp.json`:
package owns the Engram entry; user owns the other five servers (six total).
`bootstrap/sync.py` merges by key and rejects conflicts and whole-file
replacement; `config/manifest.json` records the split.

## Privacy

MCP servers declare `credentialRef: env:NAME` references only; credential
values come from the environment and are never stored or committed.

## Baseline contract

OpenCode stays unchanged. The baseline is `~/.config/opencode`, proven by
metadata-only hashing of paths and byte sizes:

```sh
python3 checks/hash_opencode.py --root "$HOME/.config/opencode"
```

Record the digest before and after any runtime step and confirm it matches;
a change proves mutation and must stop the step.

## Acceptance gates

`checks/focused-operations.sh` enforces every gate and fails if any is
skipped (focused sync, runtime parity, non-mutation, CodeGraph rejection,
accepted-gap report). `checks/final.sh` is the independent final; both are
documented in `AGENTS.md`.

## Accepted gaps

Intentionally not ported and disclosed, not hidden: CodeGraph (official Pi
rejects the component), manual updates (notification retained; updates are
manual), and the OpenCode-only plugins `opencode-notifier`, `moshi-notifier`,
`network-recovery`, `opencode-youtube-chapters`. The harness lists each gap.

## Rollback

- Runtime: `gentle-ai uninstall --agent pi`, or restore the Pi backup.
- Repository: revert only repository-owned Pi files; never restore over
  unchanged OpenCode; re-run the non-mutation hash after rollback.
