#!/usr/bin/env bash
set -e

echo "==> Validating documentation manifests..."
python documentation/validate.py

# Add more checks here as project grows:
# echo "==> Running linters..."
# echo "==> Running type checks..."
# echo "==> Running smoke tests..."

echo "OK: all checks passed"
