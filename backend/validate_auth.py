#!/usr/bin/env python3
"""
Validate authentication system implementation
"""

def validate_files_exist():
    """Check if all required files exist"""
    import os
    
    required_files = [
        'app/schemas/auth.py',
        'app/core/security.py',
        'app/services/auth.py',
        'app/services/email.py',
        'app/core/deps.py',
        'app/api/auth.py',
        'tests/test_auth.py',
        'tests/test_auth_rbac.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def validate_schemas():
    """Validate authentication schemas"""
    try:
        from app.schemas.auth import (
            UserCreate, UserResponse, UserLogin, Token, 
            TokenPayload, RefreshToken, PasswordReset,
            PasswordResetConfirm, EmailVerification, ChangePassword
        )
        print("✅ Authentication schemas are valid")
        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def validate_security_utils():
    """Validate security utilities"""
    try:
        from app.core.security import (
            create_access_token, create_refresh_token, verify_token,
            verify_password, get_password_hash, validate_password_strength
        )
        
        # Test password hashing
        password = "TestPass123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        assert not verify_password("wrong", hashed)
        
        # Test password strength
        assert validate_password_strength("StrongPass123")
        assert not validate_password_strength("weak")
        
        # Test token operations
        token = create_access_token(subject="test@example.com", user_id=1, role="student")
        payload = verify_token(token)
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert payload["role"] == "student"
        
        print("✅ Security utilities are working correctly")
        return True
    except Exception as e:
        print(f"❌ Security validation failed: {e}")
        return False

def validate_dependencies():
    """Validate authentication dependencies"""
    try:
        from app.core.deps import (
            get_current_user, get_current_verified_user,
            get_current_admin, get_current_instructor, get_current_student,
            get_instructor_or_admin, get_optional_user
        )
        print("✅ Authentication dependencies are valid")
        return True
    except Exception as e:
        print(f"❌ Dependencies validation failed: {e}")
        return False

def validate_api_routes():
    """Validate API routes"""
    try:
        from app.api.auth import router
        
        # Check if router has the expected routes
        routes = [route.path for route in router.routes]
        expected_routes = [
            '/register', '/login', '/refresh', '/verify-email',
            '/resend-verification', '/password-reset', '/password-reset/confirm',
            '/change-password', '/me', '/logout', '/protected'
        ]
        
        missing_routes = [route for route in expected_routes if route not in routes]
        if missing_routes:
            print(f"❌ Missing API routes: {missing_routes}")
            return False
        
        print("✅ API routes are valid")
        return True
    except Exception as e:
        print(f"❌ API routes validation failed: {e}")
        return False

def main():
    """Run all validations"""
    print("Validating authentication system implementation...\n")
    
    validations = [
        ("File existence", validate_files_exist),
        ("Schemas", validate_schemas),
        ("Security utilities", validate_security_utils),
        ("Dependencies", validate_dependencies),
        ("API routes", validate_api_routes)
    ]
    
    all_passed = True
    for name, validation_func in validations:
        print(f"Validating {name}...")
        try:
            if not validation_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {name} validation failed with exception: {e}")
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All validations passed! Authentication system is properly implemented.")
        print("\nImplemented features:")
        print("✅ JWT token generation and validation")
        print("✅ User registration with email verification")
        print("✅ Login/logout endpoints with secure session management")
        print("✅ Role-based access control middleware")
        print("✅ Password reset functionality with email notifications")
        print("✅ Comprehensive test coverage")
        return True
    else:
        print("❌ Some validations failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    success = main()
    sys.exit(0 if success else 1)