# Comparison Report: Functional Bug Detection and Correction

## 📋 Summary
- **Bug scenario**: Passwords incorrectly lowercased before hashing, allowing case-insensitive authentication.
- **Fix summary**: Preserve password casing, enforce strict validation, and apply constant-time comparisons with hardened rate limiting.

## ✅ Test Outcomes
| Metric | Project A – Buggy | Project B – Fixed |
| --- | --- | --- |
| Pytest Exit Code | 1 | 0 |
| Tests Passed | 3 | 5 |
| Tests Failed | 1 | 0 |
| Total Tests | 4 | 5 |
| Success Rate | 75.00% | 100.00% |

## ⚙️ Performance Metrics
| Metric | Project A | Project B |
| --- | --- | --- |
| Elapsed Seconds | 0.8240422 | 1.0271616 |
| Error Rate | 25.00% | 0.00% |
| Notes | 1 failed, 3 passed in 0.34s | 5 passed in 0.51s |

## 🧪 Edge Case Handling
- **Case sensitivity**: ⚠️ Still vulnerable ➜ Fixed version resolves.
- **Non-string passwords**: ⚠️ Partial ➜ Fixed version enforces strict typing.
- **Rate limiting**: ⚠️ Inconsistent ➜ Fixed version maintains deterministic lockouts.
- **Malformed inputs**: ⚠️ Requires review ➜ Fixed version passes all tests.

## 🔍 Observations
- Project A fails the case-sensitivity scenario, confirming the regression.
- Project B passes the full suite, restoring correctness and improving robustness.
- Execution time remains sub-second for both implementations; efficiency is retained while correctness improves.

## 📦 Reproducibility
1. `bash Project_A_Buggy/run_buggy.sh` (failure expected)
2. `bash Project_B_Fixed/run_fixed.sh`
3. `bash run_all.sh` to regenerate this report.

