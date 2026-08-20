#!/usr/bin/env sh
set -eu
python3 -m unittest checks.test_sync
test "$(sh bootstrap/install.sh --contract)" = "$(cat <<'EOF'
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
gentle-ai install --agent pi --channel stable --pi-background-subagents=auto --dry-run
gentle-ai install --agent pi --channel stable --pi-background-subagents=auto
EOF
)"
