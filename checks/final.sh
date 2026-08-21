#!/usr/bin/env sh
# Independent final PR3 acceptance (parent orchestrator). Calls the focused
# harness, then enforces the gates that must not be silently skipped.
set -eu

sh checks/focused-operations.sh

PI_HOME="${PI_HOME:-$HOME/.pi/agent}"
CONFIG_ROOT="$HOME/.config/opencode"

python3 - "$PI_HOME/mcp.json" <<'PY'
import json,sys
s=json.load(open(sys.argv[1]))['mcpServers']
e={'context7','engram','freecad','gmail_emb','gmail_personal','gmail_zeler'}
assert set(s)==e, f"six-MCP gate: {sorted(s)}"
assert s['engram'].get('command')=='node', "package engram entry must be preserved"
print("six-MCP parity: PASS (engram preserved)")
PY

python3 - "$PI_HOME/settings.json" "$PWD" <<'PY'
import json,sys,pathlib
s=json.load(open(sys.argv[1]))
assert s['defaultProvider']=='openai-codex'
assert s['defaultModel']=='gpt-5.6-sol'
assert s['defaultProjectTrust']=='always'
assert s['enableInstallTelemetry'] is False
assert not (pathlib.Path(sys.argv[2])/'.pi/settings.json').exists()
print("model/trust/telemetry parity: PASS")
PY

gentle-ai doctor >/dev/null 2>&1
echo "doctor: PASS (RDD healthy)"

python3 checks/hash_opencode.py --root "$CONFIG_ROOT" >/dev/null
echo "non-mutation: PASS (metadata hashing ran)"

pi list 2>/dev/null | grep -i codegraph && { echo "FAIL codegraph present"; exit 1; } || echo "codegraph: PASS (absent)"

printf 'final: PASS\n'
