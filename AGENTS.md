# Agent Operating Guide

This file tells agents and maintainers how to operate on this repository.

## Hard constraints

- **Do not modify OpenCode.** Never read, edit, or install OpenCode config,
  credentials, plugins, or sessions. Non-mutation is proven by metadata-only
  hashing (`checks/hash_opencode.py`).
- **Do not commit secrets.** Credentials, OAuth data, sessions, caches,
  backups, and generated package assets are excluded and never staged.
- **Do not reinstall the Pi runtime.** The install contract is in
  `bootstrap/install.sh`, runs once during onboarding; harnesses only verify.
- **Repository is public.** Every committed artifact must be secret-free.

## Ownership

- Merge `~/.pi/agent/settings.json` and `~/.pi/agent/mcp.json` by key only via
  `bootstrap/sync.py`; preserve package-owned entries; never replace whole
  files.
- Apply `config/pi/*.user.json` declaratives; never hand-edit
  package-managed paths.
- Keep the publish allowlist in `config/manifest.json` accurate.

## Baseline contract

`~/.config/opencode` (paths + byte sizes) is the metadata baseline. Before and
after any runtime step, run `python3 checks/hash_opencode.py --root
"$HOME/.config/opencode"` and confirm the digest is unchanged; record it.

## Acceptance gates (no silent skip)

`checks/focused-operations.sh` runs every gate and fails if any is skipped:
focused sync, runtime model/MCP/trust/telemetry/background parity,
metadata-only non-mutation, CodeGraph rejection, and the accepted-gap report.
`checks/final.sh` is the independent final and must pass before delivery.

## Rollback

- Runtime: `gentle-ai uninstall --agent pi`, or restore the Pi backup.
- Repository: revert only repository-owned Pi files; never restore over
  unchanged OpenCode; re-run the non-mutation hash after rollback.

## Privacy

MCP servers use `credentialRef: env:NAME` references only; no credential value
is committed. See `docs/migration.md` for the full operations guide.