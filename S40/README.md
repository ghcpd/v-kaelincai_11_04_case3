# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Functional Bug Detection and Correction

## 📘 Overview
This workspace contains two isolated Python projects designed to exercise AI models on functional bug discovery and remediation. Both focus on a simplified authentication service:

- **Project_A_Buggy** – Demonstrates a faulty implementation where passwords are lowercased before hashing, leading to unintended case-insensitive authentication.
- **Project_B_Fixed** – Provides the corrected implementation that preserves password casing, tightens validation, and improves security and resilience.

## 🧪 Test Scenario
- **Faulty behavior**: The buggy implementation normalizes passwords by calling `.lower()`. As a result, `"SecurePass123"` and `"securepass123"` are treated identically.
- **Fixed behavior**: The fixed implementation hashes passwords exactly as provided, performs constant-time comparisons, and validates inputs rigorously.
- **Input format**: Python dict / JSON objects like `{ "username": "alice", "password": "SecurePass123", "client_id": "device-1" }`.
- **Expected output**: Dicts reporting `status`, `message`, and (for the fixed version) `attempts_left` metadata.

## 🗂️ Repository Structure
```
Project_A_Buggy/
  buggy_auth.py
  input_data.json
  log_buggy.txt
  requirements_buggy.txt
  run_buggy.sh
  setup_buggy.sh
  test_buggy.py
  time_buggy.txt
Project_B_Fixed/
  fixed_auth.py
  log_fixed.txt
  requirements_fixed.txt
  run_fixed.sh
  setup_fixed.sh
  test_fixed.py
  time_fixed.txt
compare_report.md
run_all.sh
test_data.json
README.md
```

## 🚀 Running the Projects
### 1. Project A – Pre-Fix
```bash
python -m venv .venv_buggy
source Project_A_Buggy/.venv_buggy/bin/activate  # or Scripts/activate on Windows
pip install -r Project_A_Buggy/requirements_buggy.txt
pytest Project_A_Buggy/test_buggy.py
```
Or use the one-click script (failure expected):
```bash
bash Project_A_Buggy/run_buggy.sh || true
```

### 2. Project B – Post-Fix
```bash
python -m venv .venv_fixed
source Project_B_Fixed/.venv_fixed/bin/activate  # or Scripts/activate on Windows
pip install -r Project_B_Fixed/requirements_fixed.txt
pytest Project_B_Fixed/test_fixed.py
```
Or run:
```bash
bash Project_B_Fixed/run_fixed.sh
```

### 3. Combined Execution
```bash
bash run_all.sh
```
This orchestrates both projects, updates log/time artifacts, and regenerates `compare_report.md` with the latest metrics.

## 📊 Test Data
Global scenarios (normal, boundary, malformed, and edge cases) are documented in `test_data.json` and reused by both projects.

## 🔁 Reproducibility
- Each project ships with its own `requirements_*.txt` and `setup_*.sh` script.
- Execution scripts provision virtual environments, run tests, and emit logs and timing metrics.
- `compare_report.md` summarizes correctness, performance, and edge-case resilience before and after the fix.

## ⚠️ Limitations
- Authentication is simulated with in-memory user data and PBKDF2 hashing; no external database is used.
- Timing metrics are coarse grained and intended for relative comparison, not benchmarking.
- Scripts are provided in Bash for portability; on Windows use Git Bash, WSL, or adapt commands to PowerShell.

## ✅ Expected Outcome
- Project A tests highlight the functional defect (failing case-sensitivity test).
- Project B tests pass completely, demonstrating restored correctness, hardened validation, and improved reliability.

For detailed metrics and insights, consult `compare_report.md` after running `run_all.sh`.
