#!/usr/bin/env sh
# PR1 declares the PR2 contract only; it never runs an installation.
set -eu
case "${1:-}" in
  --contract)
    printf '%s\n' \
      'npm install -g --ignore-scripts @earendil-works/pi-coding-agent' \
      'gentle-ai install --agent pi --channel stable --pi-background-subagents=auto --dry-run' \
      'gentle-ai install --agent pi --channel stable --pi-background-subagents=auto'
    ;;
  *) printf '%s\n' 'Usage: bootstrap/install.sh --contract' >&2; exit 64 ;;
esac
