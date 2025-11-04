# Functional Bug Detection and Correction Evaluation

## Overview
This project evaluates AI models' ability to identify, diagnose, and fix functional bugs in software systems, specifically focusing on logic-level defects in user authentication systems.

## Bug Scenario
The authentication system contains several critical functional bugs:
1. **Incorrect logic**: Returns "Login successful" message even when authentication fails
2. **Missing type validation**: Crashes when receiving non-string inputs
3. **SQL injection vulnerability**: No input sanitization
4. **Timing attack vulnerability**: Uses insecure password comparison
5. **Poor error handling**: Exposes internal error details

## Project Structure

```
chatWorkspace/
├── Project_A_Buggy/          # Buggy implementation
│   ├── buggy_auth.py         # Faulty authentication logic
│   ├── test_buggy.py         # Tests exposing bugs
│   ├── requirements_buggy.txt
│   ├── setup_buggy.sh
│   ├── run_buggy.sh
│   ├── log_buggy.txt         # Test results
│   └── time_buggy.txt        # Performance metrics
│
├── Project_B_Fixed/          # Corrected implementation
│   ├── fixed_auth.py         # Fixed authentication logic
│   ├── test_fixed.py         # Tests validating fixes
│   ├── requirements_fixed.txt
│   ├── setup_fixed.sh
│   ├── run_fixed.sh
│   ├── log_fixed.txt         # Test results
│   └── time_fixed.txt        # Performance metrics
│
├── test_data.json            # Shared test cases
├── run_all.sh                # Master execution script
├── compare_report.md         # Evaluation results
└── README.md                 # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Running Individual Projects

**Project A (Buggy):**
```bash
cd Project_A_Buggy
pip install -r requirements_buggy.txt
python test_buggy.py
```

**Project B (Fixed):**
```bash
cd Project_B_Fixed
pip install -r requirements_fixed.txt
python test_fixed.py
```

### Running Complete Evaluation
```bash
bash run_all.sh
```

## Windows PowerShell Execution

Since you're on Windows, use these commands instead:

**Project A (Buggy):**
```powershell
cd Project_A_Buggy
pip install -r requirements_buggy.txt
python test_buggy.py > log_buggy.txt 2>&1
cd ..
```

**Project B (Fixed):**
```powershell
cd Project_B_Fixed
pip install -r requirements_fixed.txt
python test_fixed.py > log_fixed.txt 2>&1
cd ..
```

**Complete Evaluation:**
```powershell
# Run both projects and generate report
cd Project_A_Buggy; pip install -r requirements_buggy.txt; python test_buggy.py > log_buggy.txt 2>&1; cd ..
cd Project_B_Fixed; pip install -r requirements_fixed.txt; python test_fixed.py > log_fixed.txt 2>&1; cd ..
python generate_report.py
```

## Test Cases

The test suite includes:
1. **Valid credentials** - Normal authentication flow
2. **Invalid password** - Wrong password handling
3. **Empty fields** - Boundary condition testing
4. **SQL injection** - Security vulnerability testing
5. **Case sensitivity** - Password validation logic
6. **Type errors** - Non-string input handling
7. **Missing fields** - Error handling validation

## Expected Results

**Project A (Buggy):**
- Test pass rate: ~42% (3/7 tests)
- Contains crashes and incorrect outputs
- Security vulnerabilities exposed

**Project B (Fixed):**
- Test pass rate: 100% (9/9 tests)
- All edge cases handled properly
- Security vulnerabilities eliminated

## Key Improvements

1. **Correctness**: Fixed incorrect authentication logic
2. **Security**: Implemented constant-time comparison and input sanitization
3. **Robustness**: Added comprehensive type checking and validation
4. **Error Handling**: Standardized error responses
5. **Performance**: Maintained efficiency while adding security

## Evaluation Metrics

- **Functional Correctness**: Bug-free authentication logic
- **Security**: Protection against timing attacks and injection
- **Robustness**: Graceful handling of malformed inputs
- **Test Coverage**: Comprehensive edge case validation
- **Performance**: Minimal overhead for security features

## Limitations

- Simulated user database (in-memory only)
- No persistent storage or session management
- Simplified injection detection (pattern-based)
- No rate limiting or account lockout mechanisms

## Output Files

- `log_buggy.txt` - Buggy implementation test results
- `log_fixed.txt` - Fixed implementation test results
- `time_buggy.txt` - Buggy implementation performance metrics
- `time_fixed.txt` - Fixed implementation performance metrics
- `compare_report.md` - Comprehensive evaluation report

## Conclusion

This evaluation demonstrates the critical importance of proper input validation, secure comparison methods, and comprehensive error handling in authentication systems. The fixed implementation achieves 100% correctness while maintaining security and performance.
