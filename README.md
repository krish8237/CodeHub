# Online Assessment Platform (CodeHub)

A comprehensive web-based application for creating, managing, and conducting various types of assessments including coding challenges, multiple-choice questions (MCQ), and descriptive questions.

## Features

- **Multi-type Assessments**: Support for coding, MCQ, and descriptive questions
- **Advanced Code Editor**: Integrated Monaco Editor (VS Code) with syntax highlighting
- **Secure Code Execution**: Docker-based sandboxed code execution
- **Real-time Analytics**: Detailed performance metrics and reporting
- **Multi-format Export**: PDF, Excel, CSV, and JSON export capabilities
- **Tutorial System**: Built-in documentation for popular programming languages
- **Role-based Access**: Support for students, instructors, and administrators

## Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Primary database for structured data
- **Redis**: Caching and session management
- **Celery**: Background task processing
- **Docker**: Secure code execution environment
- **SQLAlchemy**: ORM for database operations

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and development server
- **Material-UI**: Component library
- **Redux Toolkit**: State management
- **Monaco Editor**: VS Code editor integration

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd online-assessment-platform
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   
   # Frontend
   cp frontend/.env.example frontend/.env
   ```

3. **Start development environment**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── store/          # Redux store
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   └── package.json        # Node dependencies
├── database/               # Database initialization
├── nginx/                  # Nginx configuration
└── docker-compose.yml      # Development environment
```

## Development Commands

### Backend
```bash
# Run tests
pytest

# Format code
black app/
isort app/

# Type checking
mypy app/

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend
```bash
# Run tests
npm test

# Build for production
npm run build

# Lint code
npm run lint

# Type checking
npx tsc --noEmit
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request
