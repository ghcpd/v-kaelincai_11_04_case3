"""
Fixed Authentication System - Post-Fix Implementation
This module corrects all functional bugs from the buggy version:
1. Uses constant-time comparison to prevent timing attacks
2. Implements strict input validation
3. Sanitizes inputs against injection attacks
4. Proper error handling for all edge cases
"""

import json
import time
import hmac
import hashlib

# Simulated user database
USER_DATABASE = {
    "alice": "SecurePass123",
    "bob": "MyP@ssw0rd",
    "charlie": "Test1234"
}

def constant_time_compare(a, b):
    """
    Constant-time string comparison to prevent timing attacks
    """
    if not isinstance(a, str) or not isinstance(b, str):
        return False
    return hmac.compare_digest(a.encode(), b.encode())

def validate_input(username, password):
    """
    Validate input types and sanitize against injection attacks
    """
    # Type validation
    if not isinstance(username, str) or not isinstance(password, str):
        return False, "Invalid input type"
    
    # Length validation
    if len(username) == 0 or len(password) == 0:
        return False, "Empty credentials"
    
    if len(username) > 100 or len(password) > 100:
        return False, "Input too long"
    
    # Basic injection pattern detection
    injection_patterns = ["'", '"', "--", ";", "/*", "*/", "xp_", "OR", "AND"]
    for pattern in injection_patterns:
        if pattern.lower() in username.lower():
            return False, "Invalid characters detected"
    
    return True, "Valid"

def authenticate_user(username, password):
    """
    Fixed authentication function with proper security measures
    """
    # Validate inputs first
    is_valid, validation_message = validate_input(username, password)
    if not is_valid:
        return {
            "status": "failure",
            "message": "Invalid credentials"
        }
    
    # Check if user exists
    if username in USER_DATABASE:
        stored_password = USER_DATABASE[username]
        
        # FIX: Use constant-time comparison
        if constant_time_compare(password, stored_password):
            return {
                "status": "success",
                "message": "Login successful"
            }
        else:
            # FIX: Correct error message
            return {
                "status": "failure",
                "message": "Invalid credentials"
            }
    else:
        return {
            "status": "failure",
            "message": "Invalid credentials"
        }

def process_login(login_data):
    """
    Process login request with proper error handling
    """
    try:
        # FIX: Proper handling of missing keys
        if not isinstance(login_data, dict):
            return {
                "status": "failure",
                "message": "Invalid credentials"
            }
        
        username = login_data.get("username", "")
        password = login_data.get("password", "")
        
        # FIX: Convert non-string inputs to empty strings
        if not isinstance(username, str):
            username = ""
        if not isinstance(password, str):
            password = ""
        
        result = authenticate_user(username, password)
        return result
        
    except Exception as e:
        # FIX: Don't expose internal errors
        return {
            "status": "failure",
            "message": "Invalid credentials"
        }

if __name__ == "__main__":
    # Test with sample data
    test_cases = [
        {"username": "alice", "password": "SecurePass123"},
        {"username": "alice", "password": "WrongPassword"},
        {"username": "unknown", "password": "test"},
        {"username": "alice", "password": 12345},
        {"password": "SecurePass123"}
    ]
    
    for test in test_cases:
        print(f"Testing: {test}")
        result = process_login(test)
        print(f"Result: {result}\n")
