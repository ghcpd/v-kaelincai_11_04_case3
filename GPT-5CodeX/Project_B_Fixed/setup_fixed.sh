#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

python -m venv "$VENV_DIR"
# shellcheck source=/dev/null
source "$VENV_DIR/Scripts/activate"
python -m pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements_fixed.txt"
