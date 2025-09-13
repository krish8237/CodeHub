#!/usr/bin/env python3

print("Testing minimal execution service...")

try:
    import docker
    print("✓ Docker import successful")
    
    from app.schemas.execution import Language
    print("✓ Schema import successful")
    
    # Create minimal class
    class CodeExecutionService:
        def __init__(self):
            print("Service initialized")
    
    print("✓ Class definition successful")
    
    service = CodeExecutionService()
    print("✓ Service instantiation successful")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()