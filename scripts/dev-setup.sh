#!/bin/bash

# Development setup script for Online Assessment Platform

echo "🚀 Setting up Online Assessment Platform development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend .env file..."
    cp backend/.env.example backend/.env
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend .env file..."
    cp frontend/.env.example frontend/.env
fi

# Start the development environment
echo "🐳 Starting Docker containers..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🔍 Checking service health..."
docker-compose ps

echo "✅ Development environment is ready!"
echo ""
echo "📋 Next steps:"
echo "1. Start the backend: cd backend && uvicorn app.main:app --reload"
echo "2. Start the frontend: cd frontend && npm install && npm run dev"
echo ""
echo "🌐 Access points:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- PostgreSQL: localhost:5432"
echo "- Redis: localhost:6379"