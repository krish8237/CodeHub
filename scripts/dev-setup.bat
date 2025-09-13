@echo off
REM Development setup script for Online Assessment Platform (Windows)

echo 🚀 Setting up Online Assessment Platform development environment...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create environment files if they don't exist
if not exist backend\.env (
    echo 📝 Creating backend .env file...
    copy backend\.env.example backend\.env
)

if not exist frontend\.env (
    echo 📝 Creating frontend .env file...
    copy frontend\.env.example frontend\.env
)

REM Start the development environment
echo 🐳 Starting Docker containers...
docker-compose up -d postgres redis

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are healthy
echo 🔍 Checking service health...
docker-compose ps

echo ✅ Development environment is ready!
echo.
echo 📋 Next steps:
echo 1. Start the backend: cd backend ^&^& uvicorn app.main:app --reload
echo 2. Start the frontend: cd frontend ^&^& npm install ^&^& npm run dev
echo.
echo 🌐 Access points:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo - PostgreSQL: localhost:5432
echo - Redis: localhost:6379

pause