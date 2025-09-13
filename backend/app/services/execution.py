import asyncio
import json
import logging
import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import docker
from docker.errors import ContainerError, ImageNotFound

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
# from app.core.execution_security import ExecutionSecurityConfig, ExecutionSecurityMiddleware, SecurityLevel

logger = logging.getLogger(__name__)

print("DEBUG: About to define CodeExecutionService class")

class CodeExecutionService:
    """Secure code execution service using Docker containers."""
    
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}")
            self.docker_client = None
        
        self.language_configs = self._get_language_configs()
        # self.security_middleware = ExecutionSecurityMiddleware(SecurityLevel.HIGH)
        # self.security_config = ExecutionSecurityConfig()
        
        if self.docker_client:
            self._ensure_images_exist()
    
    def _get_language_configs(self) -> Dict[Language, Dict]:
        """Get configuration for each supported language."""
        return {
            Language.PYTHON: {
                "image": "assessment-python-executor",
                "dockerfile": "backend/docker/execution/Dockerfile.python",
                "file_extension": ".py",
                "compile_command": None,
                "run_command": "python3 {filename}",
                "version_command": "python3 --version"
            },
            Language.JAVASCRIPT: {
                "image": "assessment-js-executor",
                "dockerfile": "backend/docker/execution/Dockerfile.javascript",
                "file_extension": ".js",
                "compile_command": None,
                "run_command": "node {filename}",
                "version_command": "node --version"
            },
            Language.JAVA: {
                "image": "assessment-java-executor",
                "dockerfile": "backend/docker/execution/Dockerfile.java",
                "file_extension": ".java",
                "compile_command": "javac {filename}",
                "run_command": "java {classname}",
                "version_command": "java --version"
            },
            Language.CPP: {
                "image": "assessment-cpp-executor",
                "dockerfile": "backend/docker/execution/Dockerfile.cpp",
                "file_extension": ".cpp",
                "compile_command": "g++ -o {output} {filename} -std=c++17 -Wall",
                "run_command": "./{output}",
                "version_command": "g++ --version"
            },
            Language.CSHARP: {
                "image": "assessment-csharp-executor",
                "dockerfile": "backend/docker/execution/Dockerfile.csharp",
                "file_extension": ".cs",
                "compile_command": "dotnet build -o /tmp/output",
                "run_command": "dotnet /tmp/output/program.dll",
                "version_command": "dotnet --version"
            },
            Language.GO: {
                "image": "assessment-go-executor",
                "dockerfile": "backend/docker/execution/Dockerfile.go",
                "file_extension": ".go",
                "compile_command": "go build -o {output} {filename}",
                "run_command": "./{output}",
                "version_command": "go version"
            },
            Language.RUST: {
                "image": "assessment-rust-executor",
                "dockerfile": "backend/docker/execution/Dockerfile.rust",
                "file_extension": ".rs",
                "compile_command": "rustc {filename} -o {output}",
                "run_command": "./{output}",
                "version_command": "rustc --version"
            }
        }
    
    def _ensure_images_exist(self):
        """Ensure all Docker images are built."""
        if not self.docker_client:
            logger.warning("Docker client not available, skipping image check")
            return
            
        for language, config in self.language_configs.items():
            try:
                self.docker_client.images.get(config["image"])
                logger.info(f"Docker image {config['image']} exists")
            except ImageNotFound:
                logger.warning(f"Docker image {config['image']} not found. Please build it first.")
            except Exception as e:
                logger.warning(f"Error checking image {config['image']}: {e}")
    
    async def execute_code(self, request: CodeExecutionRequest) -> ExecutionResult:
        """Execute code with test cases in a secure container."""
        start_time = time.time()
        
        try:
            # Validate language support
            if request.language not in self.language_configs:
                return ExecutionResult(
                    status=ExecutionStatus.INTERNAL_ERROR,
                    total_execution_time_ms=0,
                    total_memory_used_mb=0,
                    passed_tests=0,
                    total_tests=len(request.test_cases),
                    score=0.0,
                    error_message=f"Unsupported language: {request.language}"
                )
            
            # TODO: Apply security validation
            # security_result = self.security_middleware.validate_request(
            #     request.code, request.language, request.test_cases
            # )
            
            config = self.language_configs[request.language]
            
            # Compile code if needed
            compilation_result = None
            if config["compile_command"]:
                compilation_result = await self._compile_code(request.code, request.language, config)
                if not compilation_result.success:
                    return ExecutionResult(
                        status=ExecutionStatus.COMPILATION_ERROR,
                        compilation=compilation_result,
                        total_execution_time_ms=int((time.time() - start_time) * 1000),
                        total_memory_used_mb=0,
                        passed_tests=0,
                        total_tests=len(request.test_cases),
                        score=0.0,
                        error_message=compilation_result.error_message
                    )
            
            # Execute test cases
            test_results = []
            total_memory = 0.0
            passed_tests = 0
            
            for test_case in request.test_cases:
                result = await self._execute_test_case(
                    request.code, 
                    request.language, 
                    test_case, 
                    config,
                    request.resource_limits
                )
                test_results.append(result)
                total_memory += result.memory_used_mb
                if result.passed:
                    passed_tests += 1
            
            # Calculate score
            total_weight = sum(tc.weight for tc in request.test_cases)
            weighted_score = sum(
                tc.weight for tc, result in zip(request.test_cases, test_results) 
                if result.passed
            )
            score = (weighted_score / total_weight * 100) if total_weight > 0 else 0.0
            
            # Determine overall status
            if all(result.passed for result in test_results):
                status = ExecutionStatus.SUCCESS
            elif any(result.status == ExecutionStatus.TIMEOUT for result in test_results):
                status = ExecutionStatus.TIMEOUT
            elif any(result.status == ExecutionStatus.MEMORY_LIMIT_EXCEEDED for result in test_results):
                status = ExecutionStatus.MEMORY_LIMIT_EXCEEDED
            elif any(result.status == ExecutionStatus.SECURITY_VIOLATION for result in test_results):
                status = ExecutionStatus.SECURITY_VIOLATION
            else:
                status = ExecutionStatus.RUNTIME_ERROR
            
            return ExecutionResult(
                status=status,
                test_results=test_results,
                compilation=compilation_result,
                total_execution_time_ms=int((time.time() - start_time) * 1000),
                total_memory_used_mb=total_memory,
                passed_tests=passed_tests,
                total_tests=len(request.test_cases),
                score=score
            )
            
        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            return ExecutionResult(
                status=ExecutionStatus.INTERNAL_ERROR,
                total_execution_time_ms=int((time.time() - start_time) * 1000),
                total_memory_used_mb=0,
                passed_tests=0,
                total_tests=len(request.test_cases),
                score=0.0,
                error_message=f"Internal error: {str(e)}"
            )
    
    async def _compile_code(self, code: str, language: Language, config: Dict) -> CompilationResult:
        """Compile code if compilation is required."""
        execution_id = str(uuid.uuid4())
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write code to file
                filename = f"code{config['file_extension']}"
                code_path = Path(temp_dir) / filename
                code_path.write_text(code)
                
                # Prepare compilation command
                compile_cmd = config["compile_command"]
                if language == Language.JAVA:
                    # Extract class name for Java
                    class_name = self._extract_java_class_name(code)
                    if not class_name:
                        return CompilationResult(
                            success=False,
                            output="",
                            error_message="No public class found in Java code"
                        )
                    filename = f"{class_name}.java"
                    code_path = Path(temp_dir) / filename
                    code_path.write_text(code)
                    compile_cmd = compile_cmd.format(filename=filename)
                else:
                    output_name = "program"
                    compile_cmd = compile_cmd.format(
                        filename=filename,
                        output=output_name
                    )
                
                # Run compilation in container
                container = self.docker_client.containers.run(
                    config["image"],
                    command=f"sh -c 'echo \"{code}\" > {filename} && {compile_cmd}'",
                    detach=True,
                    mem_limit="256m",
                    cpu_period=100000,
                    cpu_quota=50000,  # 50% CPU
                    network_disabled=True,
                    read_only=True,
                    tmpfs={"/tmp": "size=100m,noexec"},
                    user="coderunner"
                )
                
                # Wait for compilation with timeout
                try:
                    result = container.wait(timeout=30)
                    logs = container.logs().decode('utf-8')
                    
                    if result['StatusCode'] == 0:
                        return CompilationResult(
                            success=True,
                            output=logs
                        )
                    else:
                        return CompilationResult(
                            success=False,
                            output=logs,
                            error_message="Compilation failed"
                        )
                        
                except Exception as e:
                    return CompilationResult(
                        success=False,
                        output="",
                        error_message=f"Compilation timeout or error: {str(e)}"
                    )
                finally:
                    try:
                        container.remove(force=True)
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Compilation error: {str(e)}")
            return CompilationResult(
                success=False,
                output="",
                error_message=f"Compilation error: {str(e)}"
            )
    
    async def _execute_test_case(
        self, 
        code: str, 
        language: Language, 
        test_case: TestCase, 
        config: Dict,
        resource_limits: ResourceLimits
    ) -> TestCaseResult:
        """Execute a single test case."""
        start_time = time.time()
        
        try:
            # Prepare execution environment
            execution_id = str(uuid.uuid4())
            filename = f"code{config['file_extension']}"
            
            # Build run command
            run_cmd = config["run_command"]
            if language == Language.JAVA:
                class_name = self._extract_java_class_name(code)
                if not class_name:
                    return TestCaseResult(
                        input=test_case.input,
                        expected_output=test_case.expected_output,
                        actual_output="",
                        status=ExecutionStatus.COMPILATION_ERROR,
                        execution_time_ms=0,
                        memory_used_mb=0,
                        passed=False,
                        error_message="No public class found"
                    )
                filename = f"{class_name}.java"
                run_cmd = run_cmd.format(classname=class_name)
            elif language in [Language.CPP, Language.CSHARP, Language.GO, Language.RUST]:
                run_cmd = run_cmd.format(output="program")
            else:
                run_cmd = run_cmd.format(filename=filename)
            
            # Create secure execution command
            full_command = self._build_execution_command(
                code, filename, run_cmd, test_case.input, resource_limits
            )
            
            # Run in container with security restrictions
            container = self.docker_client.containers.run(
                config["image"],
                command=full_command,
                detach=True,
                mem_limit=f"{resource_limits.memory_mb}m",
                cpu_period=100000,
                cpu_quota=int(resource_limits.cpu_time_seconds * 10000),  # CPU quota
                network_disabled=True,
                read_only=True,
                tmpfs={"/tmp": f"size={resource_limits.memory_mb}m,noexec"},
                user="coderunner",
                pids_limit=resource_limits.max_processes,
                ulimits=[
                    docker.types.Ulimit(name='nproc', soft=resource_limits.max_processes, hard=resource_limits.max_processes),
                    docker.types.Ulimit(name='nofile', soft=resource_limits.max_files, hard=resource_limits.max_files),
                ]
            )
            
            # Wait for execution with timeout
            try:
                result = container.wait(timeout=resource_limits.wall_time_seconds)
                logs = container.logs().decode('utf-8')
                stats = container.stats(stream=False)
                
                # Parse memory usage
                memory_used_mb = 0
                if 'memory' in stats and 'usage' in stats['memory']:
                    memory_used_mb = stats['memory']['usage'] / (1024 * 1024)
                
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                # Check execution result
                if result['StatusCode'] == 0:
                    # TODO: Sanitize output for security
                    actual_output = logs.strip()
                    expected_output = test_case.expected_output.strip()
                    passed = actual_output == expected_output
                    
                    return TestCaseResult(
                        input=test_case.input,
                        expected_output=test_case.expected_output,
                        actual_output=actual_output,
                        status=ExecutionStatus.SUCCESS if passed else ExecutionStatus.RUNTIME_ERROR,
                        execution_time_ms=execution_time_ms,
                        memory_used_mb=memory_used_mb,
                        passed=passed,
                        error_message=None if passed else "Output mismatch"
                    )
                else:
                    # Check for specific error types
                    if "killed" in logs.lower() or result['StatusCode'] == 137:
                        status = ExecutionStatus.MEMORY_LIMIT_EXCEEDED
                        error_msg = "Memory limit exceeded"
                    elif result['StatusCode'] == 124:
                        status = ExecutionStatus.TIMEOUT
                        error_msg = "Execution timeout"
                    else:
                        status = ExecutionStatus.RUNTIME_ERROR
                        error_msg = f"Runtime error (exit code: {result['StatusCode']})"
                    
                    return TestCaseResult(
                        input=test_case.input,
                        expected_output=test_case.expected_output,
                        actual_output=logs,
                        status=status,
                        execution_time_ms=execution_time_ms,
                        memory_used_mb=memory_used_mb,
                        passed=False,
                        error_message=error_msg
                    )
                    
            except Exception as e:
                if "timeout" in str(e).lower():
                    status = ExecutionStatus.TIMEOUT
                    error_msg = "Execution timeout"
                else:
                    status = ExecutionStatus.INTERNAL_ERROR
                    error_msg = f"Execution error: {str(e)}"
                
                return TestCaseResult(
                    input=test_case.input,
                    expected_output=test_case.expected_output,
                    actual_output="",
                    status=status,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    memory_used_mb=0,
                    passed=False,
                    error_message=error_msg
                )
            finally:
                try:
                    container.remove(force=True)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Test case execution error: {str(e)}")
            return TestCaseResult(
                input=test_case.input,
                expected_output=test_case.expected_output,
                actual_output="",
                status=ExecutionStatus.INTERNAL_ERROR,
                execution_time_ms=int((time.time() - start_time) * 1000),
                memory_used_mb=0,
                passed=False,
                error_message=f"Internal error: {str(e)}"
            )
    
    def _build_execution_command(
        self, 
        code: str, 
        filename: str, 
        run_cmd: str, 
        input_data: str,
        resource_limits: ResourceLimits
    ) -> str:
        """Build secure execution command with input handling."""
        # Escape code and input for shell safety
        escaped_code = code.replace('"', '\\"').replace('`', '\\`').replace('\n', '\\n')
        escaped_input = input_data.replace('"', '\\"').replace('`', '\\`').replace('\n', '\\n')
        
        # Build command with timeout and resource limits
        command = f'''sh -c '
            echo "{escaped_code}" > {filename} && 
            timeout {resource_limits.wall_time_seconds}s sh -c "
                echo \\"{escaped_input}\\" | {run_cmd}
            "
        ' '''
        
        return command
    
    def _extract_java_class_name(self, code: str) -> Optional[str]:
        """Extract public class name from Java code."""
        import re
        match = re.search(r'public\s+class\s+(\w+)', code)
        return match.group(1) if match else None
    
    async def validate_syntax(self, request: ValidationRequest) -> ValidationResult:
        """Validate code syntax without execution."""
        try:
            if request.language not in self.language_configs:
                return ValidationResult(
                    is_valid=False,
                    syntax_errors=[f"Unsupported language: {request.language}"]
                )
            
            config = self.language_configs[request.language]
            
            # For compiled languages, try compilation
            if config["compile_command"]:
                compilation_result = await self._compile_code(request.code, request.language, config)
                if compilation_result.success:
                    return ValidationResult(
                        is_valid=True,
                        warnings=compilation_result.warnings
                    )
                else:
                    return ValidationResult(
                        is_valid=False,
                        syntax_errors=[compilation_result.error_message or "Compilation failed"]
                    )
            
            # For interpreted languages, do basic syntax check
            if request.language == Language.PYTHON:
                return self._validate_python_syntax(request.code)
            elif request.language == Language.JAVASCRIPT:
                return self._validate_javascript_syntax(request.code)
            else:
                # For other interpreted languages, assume valid if no obvious issues
                return ValidationResult(is_valid=True)
                
        except Exception as e:
            logger.error(f"Syntax validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                syntax_errors=[f"Validation error: {str(e)}"]
            )
    
    def _validate_python_syntax(self, code: str) -> ValidationResult:
        """Validate Python syntax."""
        try:
            compile(code, '<string>', 'exec')
            return ValidationResult(is_valid=True)
        except SyntaxError as e:
            return ValidationResult(
                is_valid=False,
                syntax_errors=[f"Syntax error at line {e.lineno}: {e.msg}"]
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                syntax_errors=[f"Validation error: {str(e)}"]
            )
    
    def _validate_javascript_syntax(self, code: str) -> ValidationResult:
        """Validate JavaScript syntax using Node.js."""
        try:
            # Use Node.js to check syntax
            config = self.language_configs[Language.JAVASCRIPT]
            container = self.docker_client.containers.run(
                config["image"],
                command=f'sh -c \'echo "{code.replace(chr(34), chr(92)+chr(34))}" | node --check\'',
                detach=True,
                mem_limit="64m",
                network_disabled=True,
                read_only=True,
                user="coderunner"
            )
            
            result = container.wait(timeout=10)
            logs = container.logs().decode('utf-8')
            container.remove(force=True)
            
            if result['StatusCode'] == 0:
                return ValidationResult(is_valid=True)
            else:
                return ValidationResult(
                    is_valid=False,
                    syntax_errors=[logs.strip()]
                )
                
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                syntax_errors=[f"JavaScript validation error: {str(e)}"]
            )
    
    def get_supported_languages(self) -> List[LanguageInfo]:
        """Get information about supported languages."""
        languages = []
        for lang, config in self.language_configs.items():
            languages.append(LanguageInfo(
                name=lang.value,
                version="latest",  # Could be made dynamic
                file_extension=config["file_extension"],
                compile_command=config["compile_command"],
                run_command=config["run_command"],
                supported_features=["syntax_highlighting", "auto_completion", "error_detection"]
            ))
        return languages
    
    async def build_docker_images(self):
        """Build all Docker images for code execution."""
        for language, config in self.language_configs.items():
            try:
                logger.info(f"Building Docker image for {language.value}...")
                self.docker_client.images.build(
                    path=".",
                    dockerfile=config["dockerfile"],
                    tag=config["image"],
                    rm=True
                )
                logger.info(f"Successfully built {config['image']}")
            except Exception as e:
                logger.error(f"Failed to build {config['image']}: {str(e)}")
                raise
    
    def cleanup_containers(self):
        """Clean up any orphaned containers."""
        try:
            containers = self.docker_client.containers.list(
                all=True,
                filters={"ancestor": list(config["image"] for config in self.language_configs.values())}
            )
            for container in containers:
                try:
                    container.remove(force=True)
                    logger.info(f"Removed orphaned container: {container.id}")
                except Exception as e:
                    logger.warning(f"Failed to remove container {container.id}: {str(e)}")
        except Exception as e:
            logger.error(f"Container cleanup error: {str(e)}")


print("DEBUG: CodeExecutionService class defined successfully")

# Global instance
print("DEBUG: About to create global instance")
execution_service = CodeExecutionService()
print("DEBUG: Global instance created successfully")