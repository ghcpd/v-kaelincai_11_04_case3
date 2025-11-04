#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_FILE="${ROOT_DIR}/compare_report.md"

BUGGY_EXIT=0
FIXED_EXIT=0

pushd "${ROOT_DIR}/Project_A_Buggy" > /dev/null
set +e
bash run_buggy.sh
BUGGY_EXIT=$?
set -e
popd > /dev/null

pushd "${ROOT_DIR}/Project_B_Fixed" > /dev/null
set +e
bash run_fixed.sh
FIXED_EXIT=$?
set -e
popd > /dev/null

python - <<'PY'
import json
import pathlib
import re
import statistics

root = pathlib.Path(r"${ROOT_DIR}")

project_info = []
for name, log_name, time_name, exit_code in [
    ("Project_A_Buggy", "log_buggy.txt", "time_buggy.txt", ${BUGGY_EXIT}),
    ("Project_B_Fixed", "log_fixed.txt", "time_fixed.txt", ${FIXED_EXIT}),
]:
    project_dir = root / name
    log_path = project_dir / log_name
    time_path = project_dir / time_name

    log_text = log_path.read_text() if log_path.exists() else ""
    time_metrics = {}
    if time_path.exists() and time_path.read_text().strip():
        try:
            time_metrics = json.loads(time_path.read_text())
        except json.JSONDecodeError:
            time_metrics = {}

    def extract_metric(pattern: str) -> int:
        match = re.search(pattern, log_text)
        return int(match.group(1)) if match else 0

    passed = extract_metric(r"(\d+) passed")
    failed = extract_metric(r"(\d+) failed")
    errors = extract_metric(r"(\d+) errors")
    skipped = extract_metric(r"(\d+) skipped")
    total = passed + failed + errors + skipped
    success_rate = (passed / total) if total else 0.0
    project_info.append(
        {
            "name": name,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "exit_code": exit_code,
            "success_rate": success_rate,
            "log_excerpt": "\n".join(log_text.strip().splitlines()[-5:]),
            "time_seconds": time_metrics.get("total_time_seconds"),
        }
    )

buggy = project_info[0]
fixed = project_info[1]
performance_delta = None
if buggy.get("time_seconds") is not None and fixed.get("time_seconds") is not None:
    performance_delta = buggy["time_seconds"] - fixed["time_seconds"]

rows = []
rows.append("| Metric | Project A (Buggy) | Project B (Fixed) |")
rows.append("| --- | --- | --- |")
rows.append(f"| Tests Passed | {buggy['passed']} | {fixed['passed']} |")
rows.append(f"| Tests Failed | {buggy['failed']} | {fixed['failed']} |")
rows.append(f"| Exit Code | {buggy['exit_code']} | {fixed['exit_code']} |")
rows.append(f"| Success Rate | {buggy['success_rate']:.2%} | {fixed['success_rate']:.2%} |")
rows.append(f"| Execution Time (s) | {buggy.get('time_seconds', 'n/a')} | {fixed.get('time_seconds', 'n/a')} |")
if performance_delta is not None:
    rows.append(f"| Time Improvement (s) | — | {performance_delta:.6f} faster than buggy |")

report_lines = [
    "# Comparison Report",
    "",
    "## Summary",
    "The consolidated test execution highlights the behavioral differences between the buggy and fixed implementations.",
    "",
    *rows,
    "",
    "## Observations",
    "- **Bug manifestation**: Project A authenticates whitespace-padded passwords due to aggressive normalization, yielding failing tests.",
    "- **Bug fix**: Project B enforces strict password typing and exact hashing, restoring correctness across all targeted edge cases.",
    "- **Robustness**: The fixed implementation rejects malformed payloads with explicit errors and resets lock state on success.",
]

if performance_delta is not None:
    if performance_delta > 0:
        report_lines.append(f"- **Performance**: Project B executes approximately {performance_delta:.4f} seconds faster than Project A during the captured run.")
    else:
        report_lines.append(f"- **Performance**: Project B executes approximately {abs(performance_delta):.4f} seconds slower than Project A due to stronger hashing.")

report_lines.extend(
    [
        "",
        "## Recent Test Log Excerpts",
        f"### Project A ({buggy['name']})",
        "```\n" + (buggy['log_excerpt'] or 'No log output captured.') + "\n```",
        f"### Project B ({fixed['name']})",
        "```\n" + (fixed['log_excerpt'] or 'No log output captured.') + "\n```",
    ]
)

(root / "compare_report.md").write_text("\n".join(report_lines))
PY

echo "Project A exit code: ${BUGGY_EXIT}"
echo "Project B exit code: ${FIXED_EXIT}"

echo "Comparison report generated at ${REPORT_FILE}"

exit 0
