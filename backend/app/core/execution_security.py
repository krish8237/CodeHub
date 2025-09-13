"""
Security configuration and utilities for code execution service.
"""

import re
from typing import List, Dict, Set
from enum import Enum

from app.schemas.execution import Language


class SecurityLevel(str, Enum):
    """Security levels for code execution."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class ExecutionSecurityConfig:
    """Security configuration for code execution."""
    
    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = {
        Language.PYTHON: [
            r'import\s+os',
            r'import\s+subprocess',
            r'import\s+sys',
            r'import\s+socket',
            r'import\s+urllib',
            r'import\s+requests',
            r'import\s+http',
            r'from\s+os\s+import',
            r'from\s+subprocess\s+import',
            r'from\s+socket\s+import',
            r'__import__\s*\(',
            r'eval\s*\(',
            r'exec\s*\(',
            r'compile\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(\s*["\'][^"\']*["\']',  # input with prompts that might be malicious
        ],
        Language.JAVASCRIPT: [
            r'require\s*\(\s*["\']fs["\']',
            r'require\s*\(\s*["\']child_process["\']',
            r'require\s*\(\s*["\']net["\']',
            r'require\s*\(\s*["\']http["\']',
            r'require\s*\(\s*["\']https["\']',
            r'require\s*\(\s*["\']url["\']',
            r'process\.exit',
            r'process\.kill',
            r'eval\s*\(',
            r'Function\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\(',
        ],
        Language.JAVA: [
            r'import\s+java\.io\.',
            r'import\s+java\.net\.',
            r'import\s+java\.nio\.',
            r'import\s+java\.lang\.reflect\.',
            r'import\s+java\.lang\.Runtime',
            r'Runtime\.getRuntime\(\)',
            r'ProcessBuilder',
            r'System\.exit',
            r'System\.setProperty',
            r'Class\.forName',
            r'Thread\s*\(',
        ],
        Language.CPP: [
            r'#include\s*<fstream>',
            r'#include\s*<filesystem>',
            r'#include\s*<cstdlib>',
            r'#include\s*<unistd\.h>',
            r'#include\s*<sys/',
            r'system\s*\(',
            r'exec\w*\s*\(',
            r'fork\s*\(',
            r'pthread_create',
            r'std::thread',
        ],
        Language.CSHARP: [
            r'using\s+System\.IO',
            r'using\s+System\.Net',
            r'using\s+System\.Diagnostics',
            r'using\s+System\.Reflection',
            r'using\s+System\.Threading',
            r'Process\.Start',
            r'File\.',
            r'Directory\.',
            r'Environment\.Exit',
            r'Assembly\.Load',
        ],
        Language.GO: [
            r'import\s+"os"',
            r'import\s+"os/exec"',
            r'import\s+"net"',
            r'import\s+"net/http"',
            r'import\s+"syscall"',
            r'import\s+"unsafe"',
            r'os\.Exit',
            r'exec\.Command',
            r'syscall\.',
        ],
        Language.RUST: [
            r'use\s+std::process',
            r'use\s+std::fs',
            r'use\s+std::net',
            r'use\s+std::thread',
            r'std::process::Command',
            r'std::fs::File',
            r'std::net::TcpStream',
            r'unsafe\s*{',
            r'std::process::exit',
        ]
    }
    
    # Maximum limits for different security levels
    SECURITY_LIMITS = {
        SecurityLevel.LOW: {
            "memory_mb": 512,
            "cpu_time_seconds": 30,
            "wall_time_seconds": 60,
            "max_processes": 5,
            "max_files": 50,
            "max_output_size": 1024 * 1024,  # 1MB
        },
        SecurityLevel.MEDIUM: {
            "memory_mb": 256,
            "cpu_time_seconds": 15,
            "wall_time_seconds": 30,
            "max_processes": 3,
            "max_files": 25,
            "max_output_size": 512 * 1024,  # 512KB
        },
        SecurityLevel.HIGH: {
            "memory_mb": 128,
            "cpu_time_seconds": 10,
            "wall_time_seconds": 20,
            "max_processes": 2,
            "max_files": 15,
            "max_output_size": 256 * 1024,  # 256KB
        },
        SecurityLevel.MAXIMUM: {
            "memory_mb": 64,
            "cpu_time_seconds": 5,
            "wall_time_seconds": 10,
            "max_processes": 1,
            "max_files": 10,
            "max_output_size": 128 * 1024,  # 128KB
        }
    }
    
    # Allowed standard library modules/packages
    ALLOWED_IMPORTS = {
        Language.PYTHON: {
            "math", "random", "datetime", "json", "re", "string", "collections",
            "itertools", "functools", "operator", "copy", "heapq", "bisect",
            "array", "struct", "decimal", "fractions", "statistics"
        },
        Language.JAVASCRIPT: {
            # Built-in objects are generally safe
            "Math", "Date", "JSON", "Array", "Object", "String", "Number", "Boolean"
        },
        Language.JAVA: {
            "java.util.*", "java.math.*", "java.text.*", "java.time.*"
        },
        Language.CPP: {
            "iostream", "vector", "string", "algorithm", "map", "set", "queue",
            "stack", "deque", "list", "array", "numeric", "cmath", "climits"
        },
        Language.CSHARP: {
            "System", "System.Collections.Generic", "System.Linq", "System.Text",
            "System.Math", "System.DateTime"
        },
        Language.GO: {
            "fmt", "math", "sort", "strings", "strconv", "time", "regexp"
        },
        Language.RUST: {
            "std::collections", "std::cmp", "std::fmt", "std::str", "std::vec",
            "std::option", "std::result"
        }
    }

    @classmethod
    def check_code_security(cls, code: str, language: Language) -> Dict[str, List[str]]:
        """
        Check code for security violations.
        
        Args:
            code: The code to check
            language: Programming language
            
        Returns:
            Dictionary with 'violations' and 'warnings' lists
        """
        violations = []
        warnings = []
        
        if language not in cls.DANGEROUS_PATTERNS:
            return {"violations": violations, "warnings": warnings}
        
        patterns = cls.DANGEROUS_PATTERNS[language]
        
        for pattern in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                violations.append(
                    f"Line {line_num}: Potentially dangerous pattern '{match.group()}' detected"
                )
        
        # Check for excessively long lines (potential obfuscation)
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 500:
                warnings.append(f"Line {i}: Unusually long line ({len(line)} characters)")
        
        # Check for excessive nesting (potential complexity attack)
        max_nesting = cls._calculate_max_nesting(code, language)
        if max_nesting > 10:
            warnings.append(f"Excessive nesting depth: {max_nesting} levels")
        
        return {"violations": violations, "warnings": warnings}
    
    @classmethod
    def _calculate_max_nesting(cls, code: str, language: Language) -> int:
        """Calculate maximum nesting depth in code."""
        if language == Language.PYTHON:
            return cls._calculate_python_nesting(code)
        elif language in [Language.JAVA, Language.CSHARP, Language.CPP, Language.RUST, Language.GO]:
            return cls._calculate_brace_nesting(code)
        elif language == Language.JAVASCRIPT:
            return cls._calculate_brace_nesting(code)
        return 0
    
    @classmethod
    def _calculate_python_nesting(cls, code: str) -> int:
        """Calculate nesting depth for Python code."""
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Calculate indentation level
            indent_level = (len(line) - len(stripped)) // 4
            
            # Check for control structures
            if any(stripped.startswith(keyword) for keyword in 
                   ['if', 'elif', 'else:', 'for', 'while', 'try:', 'except', 'finally:', 'with', 'def', 'class']):
                current_depth = indent_level + 1
                max_depth = max(max_depth, current_depth)
        
        return max_depth
    
    @classmethod
    def _calculate_brace_nesting(cls, code: str) -> int:
        """Calculate nesting depth for brace-based languages."""
        depth = 0
        max_depth = 0
        
        for char in code:
            if char == '{':
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == '}':
                depth = max(0, depth - 1)
        
        return max_depth
    
    @classmethod
    def get_security_limits(cls, security_level: SecurityLevel) -> Dict:
        """Get resource limits for a security level."""
        return cls.SECURITY_LIMITS.get(security_level, cls.SECURITY_LIMITS[SecurityLevel.HIGH])
    
    @classmethod
    def sanitize_output(cls, output: str, max_size: int = 1024 * 1024) -> str:
        """
        Sanitize execution output.
        
        Args:
            output: Raw output from code execution
            max_size: Maximum allowed output size
            
        Returns:
            Sanitized output
        """
        if len(output) > max_size:
            truncated_size = max_size - 100  # Leave room for truncation message
            output = output[:truncated_size] + "\n... [Output truncated due to size limit]"
        
        # Remove potential ANSI escape sequences
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)
        
        # Remove null bytes and other control characters
        output = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', output)
        
        return output
    
    @classmethod
    def validate_test_case_input(cls, input_data: str) -> bool:
        """
        Validate test case input for potential security issues.
        
        Args:
            input_data: Input data for test case
            
        Returns:
            True if input is safe, False otherwise
        """
        # Check for excessively large input
        if len(input_data) > 10 * 1024:  # 10KB limit
            return False
        
        # Check for binary data
        try:
            input_data.encode('utf-8')
        except UnicodeEncodeError:
            return False
        
        # Check for potential injection patterns
        dangerous_patterns = [
            r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]',  # Control characters
            r'\\x[0-9a-fA-F]{2}',  # Hex escape sequences
            r'\\[0-7]{3}',  # Octal escape sequences
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, input_data):
                return False
        
        return True


# Security middleware for execution requests
class ExecutionSecurityMiddleware:
    """Middleware to apply security checks to execution requests."""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.HIGH):
        self.security_level = security_level
        self.config = ExecutionSecurityConfig()
    
    def validate_request(self, code: str, language: Language, test_cases: List) -> Dict[str, any]:
        """
        Validate an execution request for security issues.
        
        Returns:
            Dictionary with validation results
        """
        result = {
            "is_valid": True,
            "violations": [],
            "warnings": [],
            "modified_limits": None
        }
        
        # Check code security
        security_check = self.config.check_code_security(code, language)
        result["violations"].extend(security_check["violations"])
        result["warnings"].extend(security_check["warnings"])
        
        # If violations found, mark as invalid
        if security_check["violations"]:
            result["is_valid"] = False
        
        # Validate test case inputs
        for i, test_case in enumerate(test_cases):
            if not self.config.validate_test_case_input(test_case.input):
                result["violations"].append(f"Test case {i+1}: Invalid input data")
                result["is_valid"] = False
        
        # Apply security level limits
        limits = self.config.get_security_limits(self.security_level)
        result["modified_limits"] = limits
        
        return result