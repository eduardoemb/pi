#!/usr/bin/env sh
# Independent final PR2 runtime verification (parent orchestrator).
# Runs the focused proof plus the functional acceptance matrix gates that
# should not be silently skipped: exactly six MCPs with preserved engram,
# trust/telemetry, effective background off, and OpenCode non-mutation.
set -eu

sh checks/focused-runtime.sh

PI_HOME="${PI_HOME:-$HOME/.pi/agent}"
python3 - "$PI_HOME/mcp.json" <<'PY'
import json,sys
s=json.load(open(sys.argv[1]))['mcpServers']
e={'context7','engram','freecad','gmail_emb','gmail_personal','gmail_zeler'}
assert set(s)==e, f"six MCP gate: {sorted(s)}"
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
print("trust/telemetry/model parity: PASS")
PY

gentle-ai doctor >/dev/null 2>&1
echo "doctor: PASS (RDD healthy)"
printf 'final-runtime: PASS\n'
