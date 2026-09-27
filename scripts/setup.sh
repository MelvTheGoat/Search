#!/usr/bin/env bash
# One-time setup on a new machine or a fresh cloud sandbox.
# Uses the CPU build of PyTorch, which is much smaller than the default.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install -q -r requirements.txt
echo "Setup done. Try: .venv/bin/python hunt.py stats"
