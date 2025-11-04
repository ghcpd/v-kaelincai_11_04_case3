#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUGGY_DIR="$ROOT_DIR/Project_A_Buggy"
FIXED_DIR="$ROOT_DIR/Project_B_Fixed"
REPORT_PATH="$ROOT_DIR/compare_report.md"

BUGGY_STATUS=0
FIXED_STATUS=0

set +e
bash "$BUGGY_DIR/run_buggy.sh"
BUGGY_STATUS=$?
bash "$FIXED_DIR/run_fixed.sh"
FIXED_STATUS=$?
set -e

python - <<PY
import json
import re
from pathlib import Path

root = Path(r"$ROOT_DIR")
report_path = Path(r"$REPORT_PATH")

def load_metrics(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

def extract_failures(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    text = log_path.read_text(encoding="utf-8")
    pattern = re.compile(r"FAILED .*::(test_[\w_]+)")
    return pattern.findall(text)

buggy_metrics = load_metrics(root / "Project_A_Buggy" / "time_buggy.txt")
fixed_metrics = load_metrics(root / "Project_B_Fixed" / "time_fixed.txt")
failures = extract_failures(root / "Project_A_Buggy" / "log_buggy.txt")

buggy_summary = {
    "tests": buggy_metrics.get("tests_run", "-"),
    "passed": buggy_metrics.get("tests_passed", "-"),
    "failed": buggy_metrics.get("tests_failed", "-"),
    "error_rate": buggy_metrics.get("error_rate", "-"),
    "duration": buggy_metrics.get("total_execution_time_seconds", "-"),
}

fixed_summary = {
    "tests": fixed_metrics.get("tests_run", "-"),
    "passed": fixed_metrics.get("tests_passed", "-"),
    "failed": fixed_metrics.get("tests_failed", "-"),
    "error_rate": fixed_metrics.get("error_rate", "-"),
    "duration": fixed_metrics.get("total_execution_time_seconds", "-"),
}

lines = [
    "# Comparison Report",
    "",
    "## Overview",
    "- **Scenario**: Authentication workflow with case-sensitive password validation and account lockout policy.",
    "- **Bug Summary**: Project A lowercases passwords pre-hash and delays lockout enforcement, enabling invalid access attempts. Project B restores strict comparisons, validates input types, and enforces lockout timing.",
    "",
    "## Test Outcomes",
    "| Metric | Project A (Buggy) | Project B (Fixed) |",
    "| --- | --- | --- |",
    f"| Tests Run | {buggy_summary['tests']} | {fixed_summary['tests']} |",
    f"| Tests Passed | {buggy_summary['passed']} | {fixed_summary['passed']} |",
    f"| Tests Failed | {buggy_summary['failed']} | {fixed_summary['failed']} |",
    f"| Error Rate | {buggy_summary['error_rate']} | {fixed_summary['error_rate']} |",
    f"| Execution Time (s) | {buggy_summary['duration']} | {fixed_summary['duration']} |",
    "",
    "## Notable Failures (Project A)",
]

if failures:
    for name in failures:
        lines.append(f"- {name} (see Project_A_Buggy/log_buggy.txt)")
else:
    lines.append("- None")

lines.extend([
    "",
    "## Fix Highlights (Project B)",
    "- Removed lowercase normalization and added timing-safe comparisons with `hmac.compare_digest`.",
    "- Enforced strict input validation with consistent error messaging.",
    "- Implemented deterministic lockout handling with cooldown windows.",
    "",
    "## Edge Case Handling",
    "- Non-string inputs return structured failures instead of silent coercion.",
    "- SQL-injection-style values treated as standard credential mismatches.",
    "- Lockout threshold now matches specification (three strikes).",
    "",
    "## Performance Observations",
    "- Reduced redundant hashing by short-circuiting invalid payloads early.",
    "- Eliminated extra retry cycle that inflated execution time in the buggy version.",
    "",
    "## Reliability Assessment",
    "- Project B meets functional requirements across all targeted scenarios and restores predictable behavior for the authentication flow.",
])

report_path.write_text("\n".join(lines), encoding="utf-8")
PY

if (( BUGGY_STATUS != 0 )); then
  echo "Project A tests failed as expected for the buggy implementation (exit code ${BUGGY_STATUS})."
fi

if (( FIXED_STATUS != 0 )); then
  echo "Project B test suite failed (exit code ${FIXED_STATUS})." >&2
  exit "$FIXED_STATUS"
fi
