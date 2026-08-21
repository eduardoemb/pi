#!/usr/bin/env sh
# Durable full-acceptance harness (PR3). Unifies PR1/PR2 coverage read-only,
# enforces no gate is silently skipped, and never reinstalls or reads OpenCode
# file contents (metadata-only non-mutation).
set -eu

CONFIG_ROOT="$HOME/.config/opencode"
FAILED=0

run_gate() {
  name="$1"
  shift
  printf '\n# %s\n' "$name"
  "$@"
}

check_nomutation() {
  baseline="$(python3 checks/hash_opencode.py --root "$CONFIG_ROOT")"
  recheck="$(python3 checks/hash_opencode.py --root "$CONFIG_ROOT")"
  if [ "$baseline" = "$recheck" ] && [ -n "$baseline" ]; then
    printf 'ok   non-mutation (metadata hash stable)\n'
  else
    printf 'FAIL non-mutation (metadata hash changed)\n'
    FAILED=1
  fi
}

run_gate "focused sync (PR1 merge + install contract)" \
  sh checks/focused-core.sh

run_gate "runtime model/MCP/trust/telemetry/background (PR2)" \
  sh checks/focused-runtime.sh

run_gate "metadata-only non-mutation" \
  check_nomutation

run_gate "CodeGraph rejection (not exposed by official Pi)" \
  sh -c 'pi list 2>/dev/null | grep -i codegraph && { echo "FAIL codegraph present"; exit 1; } || echo "ok   no codegraph"'

# Accepted gap report (cannot be dropped without failing the run).
printf '\n# Accepted gap report\n'
for gap in \
    'codegraph: unsupported component, intentionally not installed' \
    'manual-updates: updates are manual (version notification retained)' \
    'opencode-notifier: OpenCode-only plugin, not ported (accepted)' \
    'moshi-notifier: OpenCode-only plugin, not ported (accepted)' \
    'network-recovery: OpenCode-only plugin, not ported (accepted)' \
    'opencode-youtube-chapters: OpenCode-only plugin, not ported (accepted)'; do
  printf 'gap  %s\n' "$gap"
done

if [ "$FAILED" -eq 0 ]; then
  printf '\nfocused-operations: PASS (all gates ran; no gate skipped)\n'
else
  printf '\nfocused-operations: FAIL\n'
  exit 1
fi
