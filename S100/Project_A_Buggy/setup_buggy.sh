#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${SCRIPT_DIR}/.venv_buggy"

if [ ! -d "${VENV_PATH}" ]; then
  python -m venv "${VENV_PATH}"
fi

if [[ "${OS:-}" == "Windows_NT" ]]; then
  # shellcheck disable=SC1091
  source "${VENV_PATH}/Scripts/activate"
else
  # shellcheck disable=SC1091
  source "${VENV_PATH}/bin/activate"
fi

pip install --upgrade pip > /dev/null
pip install -r "${SCRIPT_DIR}/requirements_buggy.txt"

deactivate
