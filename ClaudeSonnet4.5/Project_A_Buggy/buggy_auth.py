"""
Buggy Authentication System - Pre-Fix Implementation
This module contains intentional functional bugs:
1. Uses insecure string comparison (==) vulnerable to timing attacks
2. Missing input validation for non-string inputs
3. No sanitization against SQL injection patterns
4. Incorrect error handling for missing fields
"""

import json
import time

# Simulated user database
USER_DATABASE = {
    "alice": "SecurePass123",
    "bob": "MyP@ssw0rd",
    "charlie": "Test1234"
}

def authenticate_user(username, password):
    """
    Buggy authentication function with multiple security and logic flaws
    """
    # BUG 1: No input type validation - crashes on non-string inputs
    # BUG 2: No sanitization - vulnerable to injection attacks
    # BUG 3: Direct string comparison - timing attack vulnerability
    # BUG 4: Poor error handling
    
    if username in USER_DATABASE:
        stored_password = USER_DATABASE[username]
        # BUG: Using == for password comparison (timing attack vulnerability)
        if password == stored_password:
            return {
                "status": "success",
                "message": "Login successful"
            }
        else:
            # BUG: Sometimes returns wrong message due to logic error
            return {
                "status": "failure",
                "message": "Login successful"  # WRONG MESSAGE!
            }
    else:
        return {
            "status": "failure",
            "message": "Invalid credentials"
        }

def process_login(login_data):
    """
    Process login request with buggy logic
    """
    try:
        # BUG: Doesn't handle missing keys properly
        username = login_data["username"]
        password = login_data["password"]
        
        result = authenticate_user(username, password)
        return result
    except KeyError as e:
        # BUG: Exposes internal error details
        return {
            "status": "error",
            "message": f"Missing field: {str(e)}"
        }
    except Exception as e:
        # BUG: Catches all exceptions and may hide critical errors
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    # Test with sample data
    test_cases = [
        {"username": "alice", "password": "SecurePass123"},
        {"username": "alice", "password": "WrongPassword"},
        {"username": "unknown", "password": "test"}
    ]
    
    for test in test_cases:
        print(f"Testing: {test}")
        result = process_login(test)
        print(f"Result: {result}\n")
