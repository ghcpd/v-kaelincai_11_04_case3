#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv_buggy
if [[ "$(uname -s)" == CYGWIN* || "$(uname -s)" == MINGW* || "$(uname -s)" == MSYS* ]]; then
  source .venv_buggy/Scripts/activate
else
  source .venv_buggy/bin/activate
fi
pip install --upgrade pip
pip install -r requirements_buggy.txt
