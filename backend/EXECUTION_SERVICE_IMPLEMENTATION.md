# Code Execution Service Implementation

## Overview

This document describes the implementation of the secure code execution service for the Online Assessment Platform. The service provides secure, containerized execution of code in multiple programming languages with comprehensive security measures and resource limits.

## Implemented Components

### 1. Docker Containers for Supported Languages

Created secure Docker containers for all required programming languages:

- **Python** (`Dockerfile.python`) - Python 3.11 with security hardening
- **JavaScript** (`Dockerfile.javascript`) - Node.js 18 with network restrictions
- **Java** (`Dockerfile.java`) - OpenJDK 17 with security policy
- **C++** (`Dockerfile.cpp`) - GCC 11 with compilation security flags
- **C#** (`Dockerfile.csharp`) - .NET 7 SDK with telemetry disabled
- **Go** (`Dockerfile.go`) - Go 1.21 with CGO disabled
- **Rust** (`Dockerfile.rust`) - Rust 1.74 with static linking

### 2. Security Features

Each Docker container includes:

- **Non-root user execution** - All code runs as `coderunner` user (UID 1000)
- **Resource limits** - Strict limits on processes, files, and memory
- **Network isolation** - Network access completely disabled
- **Read-only filesystem** - Containers run with read-only root filesystem
- **Temporary filesystem** - `/tmp` mounted as tmpfs with `noexec` flag
- **Removed dangerous binaries** - `wget`, `curl`, `nc`, etc. removed
- **Process limits** - Maximum 16 processes per container
- **File limits** - Maximum 32 open files per container

### 3. Code Execution API

Implemented comprehensive execution service with:

- **Multi-language support** - All 7 required languages supported
- **Test case execution** - Run code against multiple test cases
- **Resource monitoring** - Track memory usage and execution time
- **Timeout handling** - Wall-time and CPU-time limits
- **Error categorization** - Compilation, runtime, timeout, memory limit errors
- **Score calculation** - Weighted scoring based on test case results

### 4. Security Configuration

Created security configuration system:

- **Dangerous pattern detection** - Scan code for potentially harmful patterns
- **Security levels** - LOW, MEDIUM, HIGH, MAXIMUM security levels
- **Resource limit enforcement** - Dynamic resource limits based on security level
- **Output sanitization** - Remove ANSI escape sequences and control characters
- **Input validation** - Validate test case inputs for security issues

### 5. API Endpoints

Implemented REST API endpoints:

- `POST /api/v1/execution/execute` - Execute code with test cases
- `POST /api/v1/execution/validate` - Validate code syntax
- `GET /api/v1/execution/languages` - Get supported languages info
- `POST /api/v1/execution/build-images` - Build Docker images (admin only)
- `POST /api/v1/execution/cleanup` - Clean up orphaned containers (admin only)

### 6. Build Scripts

Created platform-specific build scripts:

- `scripts/build-execution-images.sh` - Linux/macOS build script
- `scripts/build-execution-images.bat` - Windows build script

## Security Measures Implemented

### Container Security

1. **User Isolation**: All code execution happens as non-root user
2. **Network Isolation**: Complete network access disabled
3. **Filesystem Security**: Read-only root filesystem with restricted tmpfs
4. **Resource Limits**: CPU, memory, process, and file limits enforced
5. **Binary Removal**: Dangerous system binaries removed from containers

### Code Security

1. **Pattern Detection**: Scan for dangerous imports and function calls
2. **Syntax Validation**: Pre-execution syntax checking
3. **Output Sanitization**: Clean execution output of control characters
4. **Input Validation**: Validate test case inputs for security issues
5. **Execution Timeouts**: Prevent infinite loops and resource exhaustion

### API Security

1. **Authentication Required**: All endpoints require valid JWT token
2. **Role-Based Access**: Admin-only endpoints for image management
3. **Request Validation**: Comprehensive input validation using Pydantic
4. **Error Handling**: Secure error messages without information leakage

## Language-Specific Configurations

### Python
- Disabled bytecode generation (`PYTHONDONTWRITEBYTECODE=1`)
- Unbuffered output (`PYTHONUNBUFFERED=1`)
- Random hash seed for security (`PYTHONHASHSEED=random`)
- Removed dangerous modules (urllib, socket, etc.)

### JavaScript
- Production environment (`NODE_ENV=production`)
- Memory limits (`--max-old-space-size=128`)
- Removed node-gyp and build tools

### Java
- Security manager enabled
- Custom security policy file
- Memory limits (`-Xmx128m`)
- Metaspace limits (`-XX:MaxMetaspaceSize=64m`)

### C++
- Stack protection enabled (`-fstack-protector-strong`)
- Fortify source (`-D_FORTIFY_SOURCE=2`)
- Position independent executable (`-fPIE -pie`)
- RELRO protection (`-Wl,-z,relro -Wl,-z,now`)

### C#
- Telemetry disabled (`DOTNET_CLI_TELEMETRY_OPTOUT=1`)
- First-time experience skipped
- Logo disabled for cleaner output

### Go
- CGO disabled for security (`CGO_ENABLED=0`)
- Direct proxy mode (`GOPROXY=direct`)
- Sum database disabled (`GOSUMDB=off`)

### Rust
- Static linking enabled (`-C target-feature=+crt-static`)
- Backtrace disabled (`RUST_BACKTRACE=0`)

## Testing

Implemented comprehensive test suite covering:

- Service initialization and configuration
- Language support validation
- Code execution with various scenarios
- Error handling and edge cases
- Security measure validation
- Container cleanup and resource management

## Usage Examples

### Execute Python Code
```python
request = CodeExecutionRequest(
    code="print(int(input()) + int(input()))",
    language=Language.PYTHON,
    test_cases=[
        TestCase(input="5\n3", expected_output="8", weight=1.0)
    ],
    resource_limits=ResourceLimits(
        memory_mb=128,
        cpu_time_seconds=5,
        wall_time_seconds=10
    )
)

result = await execution_service.execute_code(request)
```

### Validate Syntax
```python
request = ValidationRequest(
    code="print('Hello, World!')",
    language=Language.PYTHON
)

result = await execution_service.validate_syntax(request)
```

## Future Enhancements

1. **Enhanced Security**: Add more sophisticated code analysis
2. **Performance Optimization**: Implement container pooling
3. **Language Extensions**: Add support for more programming languages
4. **Monitoring**: Add detailed execution metrics and logging
5. **Caching**: Cache compilation results for better performance

## Requirements Satisfied

This implementation satisfies all requirements from task 5:

✅ **Create Docker containers for supported programming languages** - All 7 languages implemented with secure containers

✅ **Implement code execution API with resource limits and timeout controls** - Comprehensive API with configurable limits

✅ **Build test case runner that executes user code against predefined test cases** - Full test case execution with scoring

✅ **Add syntax validation and compilation error handling** - Pre-execution validation and detailed error reporting

✅ **Implement security measures to prevent container escape and resource abuse** - Multiple layers of security implemented

✅ **Create comprehensive tests for code execution including edge cases** - Extensive test suite covering all scenarios

The implementation provides a robust, secure, and scalable foundation for code execution in the Online Assessment Platform.