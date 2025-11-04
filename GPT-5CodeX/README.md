# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Functional Bug Detection and Correction

## Scenario Summary
This repository provides two stand-alone Python projects that simulate the lifecycle of a functional bug in an authentication workflow. Project **A** captures the defective implementation, while Project **B** contains the fully corrected and hardened version. Both projects include reproducible environments, automated tests, execution scripts, and metric logs suitable for benchmarking AI model capabilities in detecting and fixing functional defects.

## Functional Bug Description
- **Faulty Behavior (Project A)**: Passwords are lowercased before hashing, allowing incorrect credentials that differ only by case. The lockout threshold is also misapplied (`>` instead of `>=`), granting an extra retry before blocking.
- **Corrected Behavior (Project B)**: Password comparison is case-sensitive, leverages `hmac.compare_digest`, enforces strict input validation, and applies lockouts immediately on the third failed attempt.
- **Input/Output Contract**: Requests and responses are JSON-compatible dictionaries, e.g. `{"username": "alice", "password": "SecurePass123"}` ➜ `{"status": "success", "message": "Login successful."}`.

## Repository Layout
- `Project_A_Buggy/`: Buggy implementation, tests (`test_buggy.py`), environment files, and execution artifacts (`log_buggy.txt`, `time_buggy.txt`).
- `Project_B_Fixed/`: Corrected implementation with matching collateral.
- `test_data.json`: Shared dataset covering nominal, boundary, malformed, and rate-limit cases.
- `compare_report.md`: Auto-generated summary contrasting both projects.
- `run_all.sh`: Orchestrates sequential execution of both projects and regenerates `compare_report.md`.

## Reproducible Setup
Both projects rely only on `pytest`. Each setup script provisions an isolated virtual environment:
- `Project_A_Buggy/setup_buggy.sh`
- `Project_B_Fixed/setup_fixed.sh`

> **Note**: On Windows, run the scripts with Git Bash or WSL to execute the `.sh` files, or translate the commands into PowerShell equivalents if preferred.

## How to Run Tests
1. **Buggy project**
   ```bash
   cd Project_A_Buggy
   bash run_buggy.sh
   ```
   - Logs: `Project_A_Buggy/log_buggy.txt`
   - Metrics: `Project_A_Buggy/time_buggy.txt`

2. **Fixed project**
   ```bash
   cd Project_B_Fixed
   bash run_fixed.sh
   ```
   - Logs: `Project_B_Fixed/log_fixed.txt`
   - Metrics: `Project_B_Fixed/time_fixed.txt`

3. **End-to-end comparison**
   ```bash
   bash run_all.sh
   ```
   - Regenerates `compare_report.md` with up-to-date metrics and failure summaries.

## Test Coverage & Data
- Tests span valid logins, case sensitivity, missing fields, malformed payloads, and lockout behavior.
- `test_data.json` enumerates five canonical scenarios with expected outcomes for easy reuse across tools or models.

## Limitations
- In-memory user storage with seeded credentials; no database or external identity provider.
- Lockout duration (`LOCKOUT_SECONDS`) is simulated and not integrated with wall-clock timers beyond the current execution.
- Scripts assume Python 3.11+ is installed and available as `python` on the path.
