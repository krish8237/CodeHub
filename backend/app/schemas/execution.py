from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"


class TestCase(BaseModel):
    input: str = Field(..., description="Input for the test case")
    expected_output: str = Field(..., description="Expected output")
    is_hidden: bool = Field(default=False, description="Whether this test case is hidden from students")
    weight: float = Field(default=1.0, ge=0, description="Weight of this test case in scoring")
    timeout: Optional[int] = Field(default=5, ge=1, le=30, description="Timeout in seconds")


class ResourceLimits(BaseModel):
    memory_mb: int = Field(default=128, ge=16, le=512, description="Memory limit in MB")
    cpu_time_seconds: int = Field(default=5, ge=1, le=30, description="CPU time limit in seconds")
    wall_time_seconds: int = Field(default=10, ge=1, le=60, description="Wall time limit in seconds")
    max_processes: int = Field(default=1, ge=1, le=5, description="Maximum number of processes")
    max_files: int = Field(default=10, ge=1, le=50, description="Maximum number of files")


class CodeExecutionRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000, description="Code to execute")
    language: Language = Field(..., description="Programming language")
    test_cases: List[TestCase] = Field(..., min_items=1, max_items=20, description="Test cases to run")
    resource_limits: Optional[ResourceLimits] = Field(default_factory=ResourceLimits, description="Resource limits")
    compile_only: bool = Field(default=False, description="Only compile, don't execute")


class ValidationRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000, description="Code to validate")
    language: Language = Field(..., description="Programming language")


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    COMPILATION_ERROR = "compilation_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    SECURITY_VIOLATION = "security_violation"
    INTERNAL_ERROR = "internal_error"


class TestCaseResult(BaseModel):
    input: str
    expected_output: str
    actual_output: str
    status: ExecutionStatus
    execution_time_ms: int
    memory_used_mb: float
    passed: bool
    error_message: Optional[str] = None


class CompilationResult(BaseModel):
    success: bool
    output: str
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    status: ExecutionStatus
    test_results: List[TestCaseResult] = Field(default_factory=list)
    compilation: Optional[CompilationResult] = None
    total_execution_time_ms: int
    total_memory_used_mb: float
    passed_tests: int
    total_tests: int
    score: float = Field(ge=0, le=100, description="Score as percentage")
    error_message: Optional[str] = None
    security_violations: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    is_valid: bool
    syntax_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class LanguageInfo(BaseModel):
    name: str
    version: str
    file_extension: str
    compile_command: Optional[str] = None
    run_command: str
    supported_features: List[str] = Field(default_factory=list)