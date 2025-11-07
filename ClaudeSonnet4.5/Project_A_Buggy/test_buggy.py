"""
Test suite for buggy authentication system
These tests will expose the functional bugs in the implementation
"""

import pytest
import json
import time
from buggy_auth import process_login, authenticate_user

# Load test data
with open('../test_data.json', 'r') as f:
    TEST_DATA = json.load(f)

def test_valid_login():
    """Test valid login credentials"""
    result = process_login({"username": "alice", "password": "SecurePass123"})
    assert result["status"] == "success"
    assert result["message"] == "Login successful"

def test_invalid_password():
    """Test invalid password - WILL FAIL DUE TO BUG"""
    result = process_login({"username": "alice", "password": "WrongPassword"})
    # This test will FAIL because buggy code returns wrong message
    assert result["status"] == "failure"
    assert result["message"] == "Invalid credentials"

def test_empty_password():
    """Test empty password"""
    result = process_login({"username": "alice", "password": ""})
    assert result["status"] == "failure"

def test_sql_injection():
    """Test SQL injection attempt"""
    result = process_login({"username": "admin' OR '1'='1", "password": "anything"})
    assert result["status"] == "failure"

def test_case_sensitive_password():
    """Test case sensitivity"""
    result = process_login({"username": "alice", "password": "securepass123"})
    assert result["status"] == "failure"

def test_non_string_password():
    """Test non-string password - WILL FAIL DUE TO TYPE ERROR"""
    result = process_login({"username": "alice", "password": 12345})
    # This will crash due to missing type validation
    assert result["status"] == "failure"

def test_missing_username():
    """Test missing username field"""
    result = process_login({"password": "SecurePass123"})
    assert result["status"] in ["failure", "error"]

def run_all_tests():
    """Run all tests and collect results"""
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "start_time": time.time()
    }
    
    test_functions = [
        test_valid_login,
        test_invalid_password,
        test_empty_password,
        test_sql_injection,
        test_case_sensitive_password,
        test_non_string_password,
        test_missing_username
    ]
    
    for test_func in test_functions:
        results["total"] += 1
        try:
            test_func()
            results["passed"] += 1
            print(f"[PASS] {test_func.__name__} PASSED")
        except AssertionError as e:
            results["failed"] += 1
            print(f"[FAIL] {test_func.__name__} FAILED: {str(e)}")
        except Exception as e:
            results["errors"] += 1
            print(f"[ERROR] {test_func.__name__} ERROR: {str(e)}")
    
    results["end_time"] = time.time()
    results["duration"] = results["end_time"] - results["start_time"]
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("Running Buggy Implementation Tests")
    print("=" * 60)
    results = run_all_tests()
    print("\n" + "=" * 60)
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Errors: {results['errors']}")
    print(f"Duration: {results['duration']:.4f} seconds")
    print("=" * 60)
