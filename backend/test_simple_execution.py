#!/usr/bin/env python3

import pytest
from app.services.execution import CodeExecutionService

def test_service_creation():
    """Test that the service can be created."""
    service = CodeExecutionService()
    assert service is not None
    assert hasattr(service, 'language_configs')

def test_get_supported_languages():
    """Test getting supported languages."""
    service = CodeExecutionService()
    languages = service.get_supported_languages()
    assert len(languages) == 7
    
    language_names = [lang.name for lang in languages]
    expected_names = ["python", "javascript", "java", "cpp", "csharp", "go", "rust"]
    for name in expected_names:
        assert name in language_names

if __name__ == "__main__":
    test_service_creation()
    test_get_supported_languages()
    print("All tests passed!")