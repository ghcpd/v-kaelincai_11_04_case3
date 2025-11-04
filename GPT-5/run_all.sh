#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(pwd)"

echo "[RunAll] Executing Project_A_Buggy"
( cd Project_A_Buggy && bash run_buggy.sh ) || echo "[RunAll] Buggy project finished with failures (expected)."

echo "[RunAll] Executing Project_B_Fixed"
( cd Project_B_Fixed && bash run_fixed.sh )

echo "[RunAll] Aggregating results"
BUGGY_TIME_FILE="Project_A_Buggy/time_buggy.txt"
FIXED_TIME_FILE="Project_B_Fixed/time_fixed.txt"
BUGGY_LOG="Project_A_Buggy/log_buggy.txt"
FIXED_LOG="Project_B_Fixed/log_fixed.txt"

buggy_elapsed=$(grep -E '^elapsed_seconds=' "$BUGGY_TIME_FILE" | cut -d'=' -f2 || echo 0)
fixed_elapsed=$(grep -E '^elapsed_seconds=' "$FIXED_TIME_FILE" | cut -d'=' -f2 || echo 0)
buggy_failures=$(grep -E '^failures=' "$BUGGY_TIME_FILE" | cut -d'=' -f2 || echo 0)
fixed_failures=$(grep -E '^failures=' "$FIXED_TIME_FILE" | cut -d'=' -f2 || echo 0)

buggy_tests=$(grep -c '::' "$BUGGY_LOG" || echo 0)
fixed_tests=$(grep -c '::' "$FIXED_LOG" || echo 0)

cat > compare_report.md <<EOF
# Compare Report

## Summary
- Buggy elapsed (s): $buggy_elapsed
- Fixed elapsed (s): $fixed_elapsed
- Buggy failures: $buggy_failures / $buggy_tests tests
- Fixed failures: $fixed_failures / $fixed_tests tests

## Interpretation
The pre-fix implementation shows functional errors (false positives, weak validation). The post-fix implementation restores correctness, rejects malformed inputs, enforces strict password rules, and adds basic rate limiting.

## Improvements
- Password comparison: substring/case-insensitive -> salted hash + constant-time compare
- Input validation: permissive casting -> strict type & length checks
- Security: no rate limiting -> basic attempt limiting
- Reliability: inconsistent responses -> deterministic JSON schema

## Detailed Logs
### Buggy (excerpt)
$(grep -E 'FAILED|ERROR' "$BUGGY_LOG" | head -n 15)

### Fixed (excerpt)
$(grep -E 'FAILED|ERROR' "$FIXED_LOG" | head -n 15)

## Metrics
| Metric | Buggy | Fixed |
|--------|-------|-------|
| Elapsed (s) | $buggy_elapsed | $fixed_elapsed |
| Failure Count | $buggy_failures | $fixed_failures |
| Success Rate | $((buggy_tests - buggy_failures))/$buggy_tests | $((fixed_tests - fixed_failures))/$fixed_tests |

EOF

echo "[RunAll] Report generated: compare_report.md"
