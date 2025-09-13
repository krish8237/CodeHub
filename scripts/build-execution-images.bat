@echo off
REM Build Docker images for code execution
REM This script builds all the Docker images needed for secure code execution

echo Building Docker images for code execution...

REM Define languages and their Dockerfiles
set "languages=python javascript java cpp csharp go rust"
set "dockerfile_python=backend/docker/execution/Dockerfile.python"
set "dockerfile_javascript=backend/docker/execution/Dockerfile.javascript"
set "dockerfile_java=backend/docker/execution/Dockerfile.java"
set "dockerfile_cpp=backend/docker/execution/Dockerfile.cpp"
set "dockerfile_csharp=backend/docker/execution/Dockerfile.csharp"
set "dockerfile_go=backend/docker/execution/Dockerfile.go"
set "dockerfile_rust=backend/docker/execution/Dockerfile.rust"

REM Build each image
for %%l in (%languages%) do (
    call :build_image %%l
    if errorlevel 1 (
        echo Failed to build assessment-%%l-executor
        exit /b 1
    )
)

echo.
echo All Docker images built successfully!
echo.
echo Built images:
docker images | findstr "assessment-.*-executor"

echo.
echo To test the images, you can run:
echo docker run --rm assessment-python-executor python3 --version
echo docker run --rm assessment-javascript-executor node --version
echo docker run --rm assessment-java-executor java --version
echo docker run --rm assessment-cpp-executor g++ --version
echo docker run --rm assessment-csharp-executor dotnet --version
echo docker run --rm assessment-go-executor go version
echo docker run --rm assessment-rust-executor rustc --version

goto :eof

:build_image
set lang=%1
call set dockerfile=%%dockerfile_%lang%%%
set image_name=assessment-%lang%-executor

echo Building %image_name% from %dockerfile%...

docker build -f "%dockerfile%" -t "%image_name%" .
if errorlevel 1 (
    echo Failed to build %image_name%
    exit /b 1
)

echo Successfully built %image_name%
goto :eof