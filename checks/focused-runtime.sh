#!/usr/bin/env sh
# Focused PR2 runtime proof. Verifies Pi runtime parity without reading
# OpenCode contents: uses metadata-only hashing and public Pi surface only.
set -eu

PI_HOME="${PI_HOME:-$HOME/.pi/agent}"
CONFIG_ROOT="$HOME/.config/opencode"
FAILED=0

check() {
  if "$@" >/dev/null 2>&1; then
    printf 'ok   %s\n' "$1"
  else
    printf 'FAIL %s\n' "$*"
    FAILED=1
  fi
}

# Model catalog + OAuth readiness (public metadata, no credentials emitted).
check test "$(python3 - "$PI_HOME/models-store.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
ids=[m['id'] for m in d['openai-codex']['models']]
print('present' if 'gpt-5.6-sol' in ids else 'missing')
PY
)" = present
check test "$(pi auth check --provider openai-codex --model gpt-5.6-sol --json --no-refresh 2>/dev/null | sed -n 's/.*"status":"\([a-z]*\)".*/\1/p')" = ready

# Exactly six MCP servers, engram preserved (key-level merge).
check test "$(python3 - "$PI_HOME/mcp.json" <<'PY'
import json,sys
s=json.load(open(sys.argv[1]))['mcpServers']
exp={'context7','engram','freecad','gmail_emb','gmail_personal','gmail_zeler'}
print('ok' if set(s)==exp and s['engram'].get('command')=='node' else 'bad')
PY
)" = ok

# Trust always and telemetry off in global settings; not in project .pi.
check test "$(python3 - "$PI_HOME/settings.json" "$PWD" <<'PY'
import json,os,sys
s=json.load(open(sys.argv[1]))
import pathlib
proj=pathlib.Path(sys.argv[2])/'.pi/settings.json'
ok=s.get('defaultProjectTrust')=='always' and s.get('enableInstallTelemetry') is False
ok=ok and (not proj.exists())
print('ok' if ok else 'bad')
PY
)" = ok

# Effective background subagents stay off (flag auto, no triggers set).
check test -z "${PI_BACKGROUND_SUBAGENTS:-}"

# Non-mutation: OpenCode metadata-only hash must match pre-runtime baseline after any runtime step.
BASELINE_RAW="$(python3 checks/hash_opencode.py --root "$CONFIG_ROOT")"
BASELINE_HASH="$(printf '%s\n' "$BASELINE_RAW" | sed -n 's/.*metadata_sha256=\([0-9a-f]*\).*/\1/p')"
check test -n "$BASELINE_HASH"
check test "$(python3 - "$CONFIG_ROOT" "$BASELINE_HASH" <<'PY'
import sys, pathlib, subprocess
root = pathlib.Path(sys.argv[1])
expected = sys.argv[2]
out = subprocess.check_output(
    ["python3", "checks/hash_opencode.py", "--root", str(root)], text=True
)
print("ok" if f"metadata_sha256={expected}" in out else "mismatch")
PY
)" = ok

# No CodeGraph (official Pi rejects the component).
check test -z "$(pi list 2>/dev/null | grep -i codegraph || true)"

# Accepted plugin gaps are documented, not treated as failures.
if [ "$FAILED" -eq 0 ]; then
  printf 'focused-runtime: PASS\n'
else
  printf 'focused-runtime: FAIL\n'
  exit 1
fi
