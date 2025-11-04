#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/log_buggy.txt"
TIME_FILE="${SCRIPT_DIR}/time_buggy.txt"

bash "${SCRIPT_DIR}/setup_buggy.sh"

if [[ "${OS:-}" == "Windows_NT" ]]; then
  # shellcheck disable=SC1091
  source "${SCRIPT_DIR}/.venv_buggy/Scripts/activate"
else
  # shellcheck disable=SC1091
  source "${SCRIPT_DIR}/.venv_buggy/bin/activate"
fi

export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

START_TIME=$(python - <<'PY'
import time
print(time.perf_counter())
PY
)

set +e
pytest -q "${SCRIPT_DIR}/test_buggy.py" | tee "${LOG_FILE}"
EXIT_CODE=${PIPESTATUS[0]}
set -e

END_TIME=$(python - <<'PY'
import time
print(time.perf_counter())
PY
)

python - <<PY
start = float(${START_TIME})
end = float(${END_TIME})
exit_code = int(${EXIT_CODE})
metrics = {
    "total_time_seconds": round(end - start, 6),
    "tests_passed": exit_code == 0,
    "exit_code": exit_code,
}
from pathlib import Path
import json
Path(r"${TIME_FILE}").write_text(json.dumps(metrics, indent=2))
PY

deactivate

exit ${EXIT_CODE}
