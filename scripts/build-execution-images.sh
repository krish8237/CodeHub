#!/bin/bash

# Build Docker images for code execution
# This script builds all the Docker images needed for secure code execution

set -e

echo "Building Docker images for code execution..."

# Array of languages and their corresponding Dockerfiles
declare -A LANGUAGES=(
    ["python"]="backend/docker/execution/Dockerfile.python"
    ["javascript"]="backend/docker/execution/Dockerfile.javascript"
    ["java"]="backend/docker/execution/Dockerfile.java"
    ["cpp"]="backend/docker/execution/Dockerfile.cpp"
    ["csharp"]="backend/docker/execution/Dockerfile.csharp"
    ["go"]="backend/docker/execution/Dockerfile.go"
    ["rust"]="backend/docker/execution/Dockerfile.rust"
)

# Build each image
for lang in "${!LANGUAGES[@]}"; do
    dockerfile="${LANGUAGES[$lang]}"
    image_name="assessment-${lang}-executor"
    
    echo "Building $image_name from $dockerfile..."
    
    if docker build -f "$dockerfile" -t "$image_name" .; then
        echo "✅ Successfully built $image_name"
    else
        echo "❌ Failed to build $image_name"
        exit 1
    fi
done

echo ""
echo "🎉 All Docker images built successfully!"
echo ""
echo "Built images:"
docker images | grep "assessment-.*-executor"

echo ""
echo "To test the images, you can run:"
echo "docker run --rm assessment-python-executor python3 --version"
echo "docker run --rm assessment-javascript-executor node --version"
echo "docker run --rm assessment-java-executor java --version"
echo "docker run --rm assessment-cpp-executor g++ --version"
echo "docker run --rm assessment-csharp-executor dotnet --version"
echo "docker run --rm assessment-go-executor go version"
echo "docker run --rm assessment-rust-executor rustc --version"