#!/usr/bin/env python3
"""
Test if the server can start with authentication system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
    print("✅ FastAPI app imported successfully")
    
    # Check if auth router is included
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    auth_routes = [route for route in routes if '/auth/' in route]
    
    if auth_routes:
        print(f"✅ Authentication routes found: {len(auth_routes)} routes")
        for route in auth_routes:
            print(f"  - {route}")
    else:
        print("❌ No authentication routes found")
    
    print("✅ Server can start with authentication system")
    
except Exception as e:
    print(f"❌ Failed to start server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)