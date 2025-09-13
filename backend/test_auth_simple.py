#!/usr/bin/env python3
"""
Simple test script to verify authentication system functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    verify_token,
    validate_password_strength
)
from app.models.user import UserRole

def test_password_operations():
    """Test password hashing and verification"""
    print("Testing password operations...")
    
    password = "TestPassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password, "Password should be hashed"
    assert verify_password(password, hashed), "Password verification should work"
    assert not verify_password("wrong", hashed), "Wrong password should fail"
    
    print("✓ Password operations work correctly")

def test_password_strength():
    """Test password strength validation"""
    print("Testing password strength validation...")
    
    assert validate_password_strength("TestPass123"), "Strong password should pass"
    assert not validate_password_strength("weak"), "Weak password should fail"
    assert not validate_password_strength("nodigits"), "Password without digits should fail"
    assert not validate_password_strength("NOLOWER123"), "Password without lowercase should fail"
    assert not validate_password_strength("noupper123"), "Password without uppercase should fail"
    
    print("✓ Password strength validation works correctly")

def test_token_operations():
    """Test JWT token creation and verification"""
    print("Testing token operations...")
    
    token = create_access_token(
        subject="test@example.com",
        user_id=1,
        role=UserRole.STUDENT.value
    )
    
    assert token is not None, "Token should be created"
    
    payload = verify_token(token)
    assert payload is not None, "Token should be verifiable"
    assert payload["sub"] == "test@example.com", "Subject should match"
    assert payload["user_id"] == 1, "User ID should match"
    assert payload["role"] == UserRole.STUDENT.value, "Role should match"
    assert payload["type"] == "access", "Token type should be access"
    
    # Test invalid token
    invalid_payload = verify_token("invalid_token")
    assert invalid_payload is None, "Invalid token should return None"
    
    print("✓ Token operations work correctly")

def test_user_roles():
    """Test user role enum"""
    print("Testing user roles...")
    
    assert UserRole.STUDENT.value == "student"
    assert UserRole.INSTRUCTOR.value == "instructor"
    assert UserRole.ADMIN.value == "admin"
    
    print("✓ User roles work correctly")

def main():
    """Run all tests"""
    print("Running authentication system tests...\n")
    
    try:
        test_password_operations()
        test_password_strength()
        test_token_operations()
        test_user_roles()
        
        print("\n✅ All authentication tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)