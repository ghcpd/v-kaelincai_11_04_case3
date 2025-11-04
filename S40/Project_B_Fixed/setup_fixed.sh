#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv_fixed
if [[ "$(uname -s)" == CYGWIN* || "$(uname -s)" == MINGW* || "$(uname -s)" == MSYS* ]]; then
  source .venv_fixed/Scripts/activate
else
  source .venv_fixed/bin/activate
fi
pip install --upgrade pip
pip install -r requirements_fixed.txt
