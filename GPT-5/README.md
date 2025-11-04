# Functional Bug Detection & Correction Evaluation

Title: Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Functional Bug Detection and Correction

## Scenario
We evaluate AI models on identifying and fixing a functional bug in a simple user authentication module. The buggy implementation performs insecure, incorrect password validation (substring, case-insensitive, permissive casting) which leads to false positives and poor handling of malformed inputs. The fixed implementation applies strict validation, secure hashing with constant-time comparison, rate limiting, and consistent structured responses.

## Bug Summary
- Buggy logic incorrectly authenticates users when the provided password is merely a substring (e.g., "Secure" passes for "SecurePass123").
- Case-insensitive comparison allows unintended matches.
- Non-string inputs are coerced unsafely.
- Missing field handling is inconsistent.
- No length constraints or edge-case rejection.

## Fix Summary
- Enforces presence and type of `username` and `password`.
- Rejects empty, overly long (>128 chars), or non-string passwords.
- Uses salted SHA-256 hashing per user and constant-time comparison via `hmac.compare_digest`.
- Adds simple in-memory rate limiting (max 5 failed attempts per user per run).
- Provides deterministic JSON responses with `status` and `message`.

## File Structure
Root:
- `test_data.json` (shared structured test cases)
- `run_all.sh` (runs both projects & produces `compare_report.md`)
- `compare_report.md` (generated after execution)
- `README.md` (this document)

Project A – Pre-Fix (`Project_A_Buggy`):
- `buggy_auth.py`
- `input_data.json`
- `requirements_buggy.txt`
- `setup_buggy.sh`
- `test_buggy.py`
- `run_buggy.sh`
- `log_buggy.txt` (generated)
- `time_buggy.txt` (metrics)

Project B – Post-Fix (`Project_B_Fixed`):
- `fixed_auth.py`
- `requirements_fixed.txt`
- `setup_fixed.sh`
- `test_fixed.py`
- `run_fixed.sh`
- `log_fixed.txt` (generated)
- `time_fixed.txt` (metrics)

## Shared Test Case Format (in `test_data.json`)
Each test object contains:
- `id`
- `case`
- `input`
- `expected_output`
- `expected_status`
- `expected_result_buggy` ("pass" or "fail" expectation for buggy impl)
- `expected_result_fixed` (always "pass")

## Running Projects Individually
### Buggy
```bash
bash Project_A_Buggy/run_buggy.sh
```
Outputs: `Project_A_Buggy/log_buggy.txt`, `Project_A_Buggy/time_buggy.txt`.

### Fixed
```bash
bash Project_B_Fixed/run_fixed.sh
```
Outputs: `Project_B_Fixed/log_fixed.txt`, `Project_B_Fixed/time_fixed.txt`.

## Full Experiment
```bash
bash run_all.sh
```
Generates `compare_report.md` summarizing accuracy, failure counts, and performance deltas.

## Environment
Both projects use isolated virtual environments (`python -m venv .venv`). Dependencies kept minimal (`pytest`). Scripts attempt cross-platform activation (Windows Git Bash / WSL / Unix).

## Limitations
- In-memory rate limiting resets per process run.
- No real database; static user registry.
- Hashing uses salted SHA-256 (demo), not adaptive hashing (bcrypt/argon2) to keep setup lightweight.

## Reproducibility Steps (Manual Alternative)
1. `cd Project_A_Buggy && python -m venv .venv && source .venv/bin/activate || source .venv/Scripts/activate`
2. `pip install -r requirements_buggy.txt`
3. `pytest -vv`
4. Repeat similarly for `Project_B_Fixed`.

## Expected Outcome
- Buggy project shows multiple failing tests (false positives & validation gaps).
- Fixed project passes all tests including edge and malformed cases.
- Report highlights improved correctness, stability, and reduced false acceptance.

## Next Step
Run `bash run_all.sh` after ensuring a bash-compatible shell (Git Bash / WSL) is available on Windows.
