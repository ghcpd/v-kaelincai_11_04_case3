# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Functional Bug Detection and Correction

## Overview
This workspace contains two standalone Python projects used to benchmark AI-assisted
functional bug localization and remediation. Both projects simulate a secure login
service. **Project A – Pre-Fix (Buggy Implementation)** retains a known logic flaw
that incorrectly accepts whitespace-padded credentials. **Project B – Post-Fix
(Corrected Implementation)** remedies the defect with strict payload validation,
constant-time hashing, and rate-limit resilience.

The repository delivers the following artifacts:

- Full source for buggy (`Project_A_Buggy`) and corrected (`Project_B_Fixed`) services
- Automated test suites that expose the regression and verify the fix
- Environment setup scripts, per-project dependency manifests, and execution
  wrappers for reproducible runs
- Shared structured test data (`test_data.json`) spanning normal, boundary,
  malformed, and rate-limit scenarios
- Aggregated reporting (`compare_report.md`) generated through the master
  automation script (`run_all.sh`)

## Functional Bug Scenario
- **Faulty behavior (Project A):** Trailing spaces or case differences in the
  password are silently normalized before hashing. This allows attackers to bypass
  strict credential matching by appending whitespace or adjusting case.
- **Corrected behavior (Project B):** Passwords remain byte-exact. Non-string or
  empty credentials trigger validation errors. Account lockouts honor cooldowns
  and are reset on successful authentication.
- **Input format:** JSON dictionaries, e.g. `{ "username": "alice", "password": "SecurePass123!" }`
- **Expected output:** Structured dictionaries/JSON mirroring `{"status": "success"|"failure", "message": "..."}` with audit metadata.

## Project Layout
```
Project_A_Buggy/
  buggy_auth.py
  input_data.json
  requirements_buggy.txt
  run_buggy.sh
  setup_buggy.sh
  test_buggy.py
  log_buggy.txt
  time_buggy.txt

Project_B_Fixed/
  fixed_auth.py
  requirements_fixed.txt
  run_fixed.sh
  setup_fixed.sh
  test_fixed.py
  log_fixed.txt
  time_fixed.txt

compare_report.md  # Generated summary (populated after running automation)
run_all.sh         # Master execution script
test_data.json     # Shared regression scenarios
README.md          # This documentation
```

## Reproducible Environment
1. Ensure Python 3.10+ is installed alongside a POSIX shell (`bash`). On Windows,
   Git Bash or WSL is recommended for running the `.sh` scripts.
2. Execute the per-project setup scripts to create isolated virtual environments:
   ```bash
   cd Project_A_Buggy && bash setup_buggy.sh
   cd ../Project_B_Fixed && bash setup_fixed.sh
   ```
3. Each setup installs dependencies listed in the respective `requirements_*.txt`
   files (`pytest`, `rich`).

## Running Tests Individually
Run the corresponding script from each project directory:

```bash
cd Project_A_Buggy
bash run_buggy.sh   # Expected to surface failing tests

cd ../Project_B_Fixed
bash run_fixed.sh   # Expected to pass all tests
```

> **Tip:** Set `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` in your shell prior to running
> the scripts (or rely on the export already in the scripts) to avoid
> interference from globally installed PyTest plugins.

Each script performs environment setup, executes the tests, and records:
- `log_*.txt`: Pytest console output (pass/fail trace)
- `time_*.txt`: Execution statistics (`total_time_seconds`, `tests_passed`, etc.)

## Combined Execution & Reporting
To generate the consolidated comparison, from the repository root run:

```bash
bash run_all.sh
```

The orchestration script runs both projects sequentially, tolerates the expected
failures in Project A, and produces `compare_report.md` summarizing:
- Success/error counts and exit codes
- Relative execution times
- Observed functional regressions vs. the corrected behavior
- Recent log excerpts assisting triage

## Test Data
`test_data.json` captures at least six scenarios spanning:
- ✅ Valid authentication
- ✅ Boundary handling (case sensitivity, whitespace)
- ✅ Malformed payload attempts (SQL injection, non-string passwords)
- ✅ Rate-limit enforcement with repeated failures

These cases may be marshalled by other harnesses or extended for additional
experiments.

## Limitations
- The authentication service uses in-memory data structures only; no persistent
  storage is provided.
- Rate-limiting timestamps rely on system time and a coarse cooldown simulation;
  production systems should integrate monotonic clocks and distributed lock
  management.
- Shell scripts assume a Bash-compatible environment. On native Windows CMD,
  invoke them via `bash` explicitly.

## Next Steps
- Integrate additional telemetry (e.g., coverage reports) with `pytest --cov`
  for deeper quality signals.
- Expand malformed input suites (XML, binary payloads) to explore parser safety.
- Connect to CI pipelines for automated regression detection when future model
  iterations propose modifications.
