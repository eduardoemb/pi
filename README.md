# Pi Configuration and Operations

Declarative source and operations guide for `pi`, an independent RDD-enabled
Gentle AI host that mirrors the OpenCode workflow while leaving OpenCode
unchanged.

> Public repository: every committed artifact must be secret-free. Credentials,
> OAuth data, sessions, caches, backups, and generated package assets are
> excluded by `.gitignore` and never staged.

## Contents

`bootstrap/` (install contract + key merge), `config/pi/` (user declaratives),
`config/manifest.json` (ownership + allowlist), `checks/` (acceptance
harnesses + budget gate + non-mutation proof), `docs/migration.md`
(migration, rollback, operations).

## Quick start

The install contract has exactly three ordered commands, declared in
`bootstrap/install.sh`. Review before running anything the first time
(install happens once during onboarding; harnesses only verify an installed
runtime):

```sh
sh bootstrap/install.sh --contract
```

## Ownership

Merge by key ownership: package owns generated assets and the Engram MCP
entry; user owns model/provider, project trust, telemetry, five declared MCP
entries, per-agent `model_profiles`, and the per-profile SDD agent files.
`bootstrap/sync.py` merges only declared user keys, copies declarative agent
files, and rejects whole-file replacement. See `config/manifest.json`.

## Privacy

MCP servers reference credentials by environment reference only
(`credentialRef: env:NAME`). No credential value or secret is committed.

## Accepted gaps

Intentionally not ported and disclosed as accepted: CodeGraph (official Pi
rejects the component), manual updates (notification retained), and the
OpenCode-only plugins `opencode-notifier`, `moshi-notifier`,
`network-recovery`, `opencode-youtube-chapters`.

## Verification

```sh
sh checks/focused-operations.sh   # durable acceptance harness
sh checks/final.sh                # independent final
```

Both are read-only and shellcheck-clean. See `docs/migration.md` for the
baseline contract and rollback boundary.
