#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
LOG_FILE="$SCRIPT_DIR/log_fixed.txt"
XML_REPORT="$SCRIPT_DIR/pytest_fixed.xml"
TIME_FILE="$SCRIPT_DIR/time_fixed.txt"

bash "$SCRIPT_DIR/setup_fixed.sh"
# shellcheck source=/dev/null
source "$VENV_DIR/Scripts/activate"

START_TIME=$(python - <<'PY'
import time
print(time.time())
PY
)

set +e
pytest "$SCRIPT_DIR/test_fixed.py" --maxfail=0 --disable-warnings --junitxml="$XML_REPORT" 2>&1 | tee "$LOG_FILE"
TEST_EXIT=${PIPESTATUS[0]}
set -e

END_TIME=$(python - <<'PY'
import time
print(time.time())
PY
)

python - <<PY
import json
import xml.etree.ElementTree as ET
from pathlib import Path

xml_path = Path(r"$XML_REPORT")
time_file = Path(r"$TIME_FILE")
start = float("$START_TIME")
end = float("$END_TIME")

summary = {
    "total_execution_time_seconds": round(end - start, 4),
    "tests_run": 0,
    "tests_failed": 0,
    "tests_passed": 0,
    "error_rate": 0.0,
}

if xml_path.exists():
    tree = ET.parse(xml_path)
    root = tree.getroot()
    tests = int(root.attrib.get("tests", 0))
    failures = int(root.attrib.get("failures", 0))
    errors = int(root.attrib.get("errors", 0))
    skipped = int(root.attrib.get("skipped", 0))
    summary["tests_run"] = tests
    summary["tests_failed"] = failures + errors
    summary["tests_passed"] = tests - failures - errors - skipped
    if tests:
        summary["error_rate"] = round((failures + errors) / tests, 4)

with time_file.open("w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2)
PY

exit "$TEST_EXIT"
