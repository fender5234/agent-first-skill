#!/usr/bin/env bash
set -e

echo "==> Validating documentation manifests..."
python documentation/validate.py

echo "==> Checking AF sections in agent instructions..."
python documentation/check-claude-md-sections.py

# Add more checks here as project grows:
# echo "==> Running linters..."
# echo "==> Running type checks..."
# echo "==> Running smoke tests..."
#
# Project-specific Hard Rule checks belong here too, once each has a script.
# Rule of thumb: a check that is not wired into this script or a hook will go
# red unnoticed. Do not add one you are not ready to gate on.

echo "OK: all checks passed"
