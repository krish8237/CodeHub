#!/usr/bin/env python3
"""
Debug import issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Python path:", sys.path)
print("Current directory:", os.getcwd())

try:
    print("1. Testing basic imports...")
    from app.models.user import User, UserRole
    print("✅ User models imported")
    
    from app.core.security import get_password_hash
    print("✅ Security utils imported")
    
    from app.schemas.auth import UserCreate
    print("✅ Auth schemas imported")
    
    from app.services.auth import AuthService
    print("✅ Auth service imported")
    
    from app.api.auth import router
    print("✅ Auth router imported")
    
    from app.main import app
    print("✅ Main app imported")
    
    print("All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()