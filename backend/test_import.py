#!/usr/bin/env python3

try:
    print("Testing imports...")
    
    print("1. Testing basic imports...")
    import asyncio
    import json
    import logging
    import os
    import tempfile
    import time
    import uuid
    from pathlib import Path
    from typing import Dict, List, Optional
    print("✓ Basic imports successful")
    
    print("2. Testing docker import...")
    import docker
    from docker.errors import ContainerError, ImageNotFound
    print("✓ Docker imports successful")
    
    print("3. Testing schema imports...")
    from app.schemas.execution import (
        CodeExecutionRequest,
        ExecutionResult,
        ExecutionStatus,
        Language,
        LanguageInfo,
        TestCase,
        TestCaseResult,
        ValidationRequest,
        ValidationResult,
        CompilationResult,
        ResourceLimits
    )
    print("✓ Schema imports successful")
    
    print("4. Testing security imports...")
    from app.core.execution_security import ExecutionSecurityConfig, ExecutionSecurityMiddleware, SecurityLevel
    print("✓ Security imports successful")
    
    print("5. Testing service import...")
    from app.services.execution import CodeExecutionService
    print("✓ Service import successful")
    
    print("6. Testing service instantiation...")
    # Mock docker client to avoid connection issues
    import unittest.mock
    with unittest.mock.patch('app.services.execution.docker.from_env'):
        service = CodeExecutionService()
        print("✓ Service instantiation successful")
    
    print("\nAll imports successful!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()