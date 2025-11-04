# Comparison Report

## Overview
- **Scenario**: Authentication workflow with case-sensitive password validation and account lockout policy.
- **Bug Summary**: Project A lowercased passwords before hashing and delayed lockout enforcement, allowing incorrect credentials and bypassing throttling. Project B restores case sensitivity, validates input types, and enforces lockouts strictly.

## Test Outcomes
| Metric | Project A (Buggy) | Project B (Fixed) |
| --- | --- | --- |
| Tests Run | 5 | 7 |
| Tests Passed | 3 | 7 |
| Tests Failed | 2 | 0 |
| Error Rate | 40% | 0% |
| Execution Time (s) | 0.42 | 0.38 |

## Notable Failures (Project A)
- Accepted passwords that only differed by case (`SecurePass123` vs `securepass123`).
- Did not lock accounts after three failed attempts, permitting unlimited retries.

## Fix Highlights (Project B)
- Removed lowercase normalization; comparisons now use `hmac.compare_digest` for timing-safe equality.
- Added strict type checks and input sanitation.
- Enforced lockout after the configured number of failures and added cooldown windows.

## Edge Case Handling
- Rejects non-string passwords instead of coercing them.
- Gracefully handles malformed payloads with consistent error messaging.
- Ensures SQL-injection-style strings behave like normal failed credentials with no leakage.

## Performance Observations
- Minor execution-time improvement due to early validation and reduced repeated hashing from unnecessary retries.
- Deterministic failure handling reduces log noise and stabilizes error rates.

## Reliability Assessment
- Project B restores correctness across all targeted scenarios, meeting functional requirements and hardening against abuse patterns highlighted in the test suite.
