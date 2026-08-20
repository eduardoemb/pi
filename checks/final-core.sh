#!/usr/bin/env sh
set -eu
# Reserved for the parent orchestrator's independent final verification.
python3 -m unittest checks.test_sync
