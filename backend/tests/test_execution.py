import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from docker.errors import ImageNotFound, ContainerError

from app.services.execution import CodeExecutionService
from app.schemas.execution import (
    CodeExecutionRequest,
    ValidationRequest,
    Language,
    TestCase,
    ResourceLimits,
    ExecutionStatus,
    ExecutionResult,
    ValidationResult,
    CompilationResult
)


@pytest.fixture
def execution_service():
    """Create execution service instance for testing."""
    with patch('app.services.execution.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        service = CodeExecutionService()
        service.docker_client = mock_client
        return service


@pytest.fixture
def sample_test_cases():
    """Sample test cases for testing."""
    return [
        TestCase(
            input="5\n3",
            expected_output="8",
            weight=1.0
        ),
        TestCase(
            input="10\n20",
            expected_output="30",
            weight=1.0
        )
    ]


@pytest.fixture
def sample_resource_limits():
    """Sample resource limits for testing."""
    return ResourceLimits(
        memory_mb=128,
        cpu_time_seconds=5,
        wall_time_seconds=10,
        max_processes=1,
        max_files=10
    )


class TestCodeExecutionService:
    """Test cases for CodeExecutionService."""

    def test_get_language_configs(self, execution_service):
        """Test language configuration retrieval."""
        configs = execution_service._get_language_configs()
        
        # Check all required languages are present
        expected_languages = [
            Language.PYTHON, Language.JAVASCRIPT, Language.JAVA,
            Language.CPP, Language.CSHARP, Language.GO, Language.RUST
        ]
        
        for lang in expected_languages:
            assert lang in configs
            config = configs[lang]
            assert "image" in config
            assert "dockerfile" in config
            assert "file_extension" in config
            assert "run_command" in config

    def test_get_supported_languages(self, execution_service):
        """Test supported languages retrieval."""
        languages = execution_service.get_supported_languages()
        
        assert len(languages) == 7
        language_names = [lang.name for lang in languages]
        
        expected_names = ["python", "javascript", "java", "cpp", "csharp", "go", "rust"]
        for name in expected_names:
            assert name in language_names

    @pytest.mark.asyncio
    async def test_execute_code_unsupported_language(self, execution_service, sample_test_cases, sample_resource_limits):
        """Test execution with unsupported language."""
        request = CodeExecutionRequest(
            code="print('hello')",
            language="unsupported",  # Invalid language
            test_cases=sample_test_cases,
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.status == ExecutionStatus.INTERNAL_ERROR
        assert "Unsupported language" in result.error_message
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_execute_python_code_success(self, execution_service, sample_test_cases, sample_resource_limits):
        """Test successful Python code execution."""
        # Mock container behavior
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"8"
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024 * 10}}  # 10MB
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        request = CodeExecutionRequest(
            code="a = int(input())\nb = int(input())\nprint(a + b)",
            language=Language.PYTHON,
            test_cases=[sample_test_cases[0]],  # Only first test case
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.passed_tests == 1
        assert result.total_tests == 1
        assert result.score == 100.0
        assert len(result.test_results) == 1
        assert result.test_results[0].passed

    @pytest.mark.asyncio
    async def test_execute_code_compilation_error(self, execution_service, sample_test_cases, sample_resource_limits):
        """Test code execution with compilation error."""
        # Mock compilation failure
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 1}
        mock_container.logs.return_value = b"compilation error: syntax error"
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        request = CodeExecutionRequest(
            code="public class Test { invalid syntax }",
            language=Language.JAVA,
            test_cases=sample_test_cases,
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.status == ExecutionStatus.COMPILATION_ERROR
        assert result.compilation is not None
        assert not result.compilation.success
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_execute_code_timeout(self, execution_service, sample_test_cases, sample_resource_limits):
        """Test code execution timeout."""
        # Mock timeout behavior
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 124}  # Timeout exit code
        mock_container.logs.return_value = b"timeout"
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024}}
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        request = CodeExecutionRequest(
            code="while True: pass",  # Infinite loop
            language=Language.PYTHON,
            test_cases=sample_test_cases,
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.status == ExecutionStatus.TIMEOUT
        assert result.passed_tests == 0
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_execute_code_memory_limit_exceeded(self, execution_service, sample_test_cases, sample_resource_limits):
        """Test code execution with memory limit exceeded."""
        # Mock memory limit exceeded
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 137}  # Killed by signal
        mock_container.logs.return_value = b"killed"
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024 * 200}}  # 200MB
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        request = CodeExecutionRequest(
            code="data = [0] * (10**8)",  # Memory intensive code
            language=Language.PYTHON,
            test_cases=sample_test_cases,
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.status == ExecutionStatus.MEMORY_LIMIT_EXCEEDED
        assert result.passed_tests == 0
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_execute_code_runtime_error(self, execution_service, sample_test_cases, sample_resource_limits):
        """Test code execution with runtime error."""
        # Mock runtime error
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 1}
        mock_container.logs.return_value = b"ZeroDivisionError: division by zero"
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024}}
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        request = CodeExecutionRequest(
            code="print(1/0)",  # Division by zero
            language=Language.PYTHON,
            test_cases=sample_test_cases,
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.status == ExecutionStatus.RUNTIME_ERROR
        assert result.passed_tests == 0
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_execute_code_partial_success(self, execution_service, sample_resource_limits):
        """Test code execution with partial success."""
        # Mock mixed results - first test passes, second fails
        mock_container = Mock()
        
        def mock_wait_side_effect(*args, **kwargs):
            if mock_container.wait.call_count == 1:
                return {'StatusCode': 0}  # First test passes
            else:
                return {'StatusCode': 1}  # Second test fails
        
        def mock_logs_side_effect(*args, **kwargs):
            if mock_container.logs.call_count == 1:
                return b"8"  # Correct output for first test
            else:
                return b"wrong"  # Wrong output for second test
        
        mock_container.wait.side_effect = mock_wait_side_effect
        mock_container.logs.side_effect = mock_logs_side_effect
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024}}
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        test_cases = [
            TestCase(input="5\n3", expected_output="8", weight=1.0),
            TestCase(input="10\n20", expected_output="30", weight=1.0)
        ]
        
        request = CodeExecutionRequest(
            code="a = int(input())\nb = int(input())\nprint(a + b)",
            language=Language.PYTHON,
            test_cases=test_cases,
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.passed_tests == 1
        assert result.total_tests == 2
        assert result.score == 50.0  # 50% success rate

    @pytest.mark.asyncio
    async def test_validate_python_syntax_valid(self, execution_service):
        """Test Python syntax validation with valid code."""
        request = ValidationRequest(
            code="print('Hello, World!')",
            language=Language.PYTHON
        )
        
        result = await execution_service.validate_syntax(request)
        
        assert result.is_valid
        assert len(result.syntax_errors) == 0

    @pytest.mark.asyncio
    async def test_validate_python_syntax_invalid(self, execution_service):
        """Test Python syntax validation with invalid code."""
        request = ValidationRequest(
            code="print('Hello, World!'",  # Missing closing parenthesis
            language=Language.PYTHON
        )
        
        result = await execution_service.validate_syntax(request)
        
        assert not result.is_valid
        assert len(result.syntax_errors) > 0
        assert "Syntax error" in result.syntax_errors[0]

    @pytest.mark.asyncio
    async def test_validate_javascript_syntax(self, execution_service):
        """Test JavaScript syntax validation."""
        # Mock Node.js syntax check
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b""
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        request = ValidationRequest(
            code="console.log('Hello, World!');",
            language=Language.JAVASCRIPT
        )
        
        result = await execution_service.validate_syntax(request)
        
        assert result.is_valid
        assert len(result.syntax_errors) == 0

    def test_extract_java_class_name(self, execution_service):
        """Test Java class name extraction."""
        code = "public class HelloWorld { public static void main(String[] args) { } }"
        class_name = execution_service._extract_java_class_name(code)
        assert class_name == "HelloWorld"
        
        # Test with no public class
        code_no_class = "class Test { }"
        class_name = execution_service._extract_java_class_name(code_no_class)
        assert class_name is None

    def test_build_execution_command(self, execution_service, sample_resource_limits):
        """Test execution command building."""
        code = "print('hello')"
        filename = "test.py"
        run_cmd = "python3 test.py"
        input_data = "test input"
        
        command = execution_service._build_execution_command(
            code, filename, run_cmd, input_data, sample_resource_limits
        )
        
        assert "echo" in command
        assert filename in command
        assert str(sample_resource_limits.wall_time_seconds) in command
        assert "timeout" in command

    @pytest.mark.asyncio
    async def test_build_docker_images(self, execution_service):
        """Test Docker image building."""
        # Mock successful image building
        mock_build = Mock()
        execution_service.docker_client.images.build = mock_build
        
        await execution_service.build_docker_images()
        
        # Should call build for each language
        assert mock_build.call_count == 7

    def test_cleanup_containers(self, execution_service):
        """Test container cleanup."""
        # Mock containers list
        mock_container1 = Mock()
        mock_container2 = Mock()
        mock_containers = [mock_container1, mock_container2]
        
        execution_service.docker_client.containers.list.return_value = mock_containers
        
        execution_service.cleanup_containers()
        
        # Should remove all containers
        mock_container1.remove.assert_called_once_with(force=True)
        mock_container2.remove.assert_called_once_with(force=True)

    @pytest.mark.asyncio
    async def test_execute_code_with_weighted_test_cases(self, execution_service, sample_resource_limits):
        """Test code execution with weighted test cases."""
        # Mock successful execution for all tests
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"correct"
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024}}
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        # Create test cases with different weights
        test_cases = [
            TestCase(input="1", expected_output="correct", weight=1.0),
            TestCase(input="2", expected_output="correct", weight=2.0),
            TestCase(input="3", expected_output="correct", weight=3.0)
        ]
        
        request = CodeExecutionRequest(
            code="print('correct')",
            language=Language.PYTHON,
            test_cases=test_cases,
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.passed_tests == 3
        assert result.total_tests == 3
        assert result.score == 100.0

    @pytest.mark.asyncio
    async def test_execute_code_security_measures(self, execution_service, sample_test_cases, sample_resource_limits):
        """Test that security measures are applied during execution."""
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"8"
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024}}
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        request = CodeExecutionRequest(
            code="print('test')",
            language=Language.PYTHON,
            test_cases=[sample_test_cases[0]],
            resource_limits=sample_resource_limits
        )
        
        await execution_service.execute_code(request)
        
        # Verify security parameters were used
        call_args = execution_service.docker_client.containers.run.call_args
        kwargs = call_args[1]
        
        assert kwargs['network_disabled'] is True
        assert kwargs['read_only'] is True
        assert kwargs['user'] == 'coderunner'
        assert 'mem_limit' in kwargs
        assert 'cpu_quota' in kwargs
        assert 'pids_limit' in kwargs
        assert 'ulimits' in kwargs

    @pytest.mark.asyncio
    async def test_execute_code_container_cleanup(self, execution_service, sample_test_cases, sample_resource_limits):
        """Test that containers are properly cleaned up after execution."""
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"8"
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024}}
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        request = CodeExecutionRequest(
            code="print('test')",
            language=Language.PYTHON,
            test_cases=[sample_test_cases[0]],
            resource_limits=sample_resource_limits
        )
        
        await execution_service.execute_code(request)
        
        # Verify container was removed
        mock_container.remove.assert_called_with(force=True)

    @pytest.mark.asyncio
    async def test_execute_code_exception_handling(self, execution_service, sample_test_cases, sample_resource_limits):
        """Test exception handling during code execution."""
        # Mock Docker exception
        execution_service.docker_client.containers.run.side_effect = Exception("Docker error")
        
        request = CodeExecutionRequest(
            code="print('test')",
            language=Language.PYTHON,
            test_cases=sample_test_cases,
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.status == ExecutionStatus.INTERNAL_ERROR
        assert "Internal error" in result.error_message
        assert result.score == 0.0


class TestExecutionEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_empty_code_execution(self, execution_service, sample_test_cases, sample_resource_limits):
        """Test execution with empty code."""
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 1}
        mock_container.logs.return_value = b"No output"
        mock_container.stats.return_value = {'memory': {'usage': 1024}}
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        request = CodeExecutionRequest(
            code="",
            language=Language.PYTHON,
            test_cases=sample_test_cases,
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.passed_tests == 0
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_large_output_handling(self, execution_service, sample_resource_limits):
        """Test handling of large output."""
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 0}
        # Simulate large output
        large_output = "x" * 10000
        mock_container.logs.return_value = large_output.encode()
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024}}
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        test_case = TestCase(
            input="test",
            expected_output=large_output,
            weight=1.0
        )
        
        request = CodeExecutionRequest(
            code="print('x' * 10000)",
            language=Language.PYTHON,
            test_cases=[test_case],
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.test_results[0].actual_output == large_output
        assert result.test_results[0].passed

    @pytest.mark.asyncio
    async def test_special_characters_in_code(self, execution_service, sample_resource_limits):
        """Test handling of special characters in code."""
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"Hello, World!"
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024}}
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        # Code with special characters
        code_with_special_chars = 'print("Hello, World! $@#%^&*()")'
        
        test_case = TestCase(
            input="",
            expected_output="Hello, World!",
            weight=1.0
        )
        
        request = CodeExecutionRequest(
            code=code_with_special_chars,
            language=Language.PYTHON,
            test_cases=[test_case],
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        # Should handle special characters without issues
        assert result.status == ExecutionStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_multiline_input_output(self, execution_service, sample_resource_limits):
        """Test handling of multiline input and output."""
        mock_container = Mock()
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"line1\nline2\nline3"
        mock_container.stats.return_value = {'memory': {'usage': 1024 * 1024}}
        
        execution_service.docker_client.containers.run.return_value = mock_container
        
        test_case = TestCase(
            input="input1\ninput2\ninput3",
            expected_output="line1\nline2\nline3",
            weight=1.0
        )
        
        request = CodeExecutionRequest(
            code="for i in range(3): print(f'line{i+1}')",
            language=Language.PYTHON,
            test_cases=[test_case],
            resource_limits=sample_resource_limits
        )
        
        result = await execution_service.execute_code(request)
        
        assert result.test_results[0].passed
        assert "line1\nline2\nline3" in result.test_results[0].actual_output