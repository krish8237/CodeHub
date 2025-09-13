import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base
from app.models import *  # Import all models


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password_hash": "hashed_password",
        "first_name": "John",
        "last_name": "Doe",
        "role": "STUDENT",
        "is_active": True,
        "is_verified": False
    }


@pytest.fixture
def sample_assessment_data():
    """Sample assessment data for testing"""
    return {
        "title": "Python Programming Test",
        "description": "A comprehensive Python programming assessment",
        "instructions": "Complete all questions within the time limit",
        "time_limit": 120,  # 2 hours
        "max_attempts": 3,
        "is_active": True,
        "created_by": 1,
        "settings": {"allow_code_execution": True}
    }


@pytest.fixture
def sample_question_data():
    """Sample question data for testing"""
    return {
        "assessment_id": 1,
        "type": "CODING",
        "title": "FizzBuzz Implementation",
        "content": "Implement the FizzBuzz algorithm",
        "points": 10.0,
        "order": 1,
        "language": "python",
        "starter_code": "def fizzbuzz(n):\n    pass",
        "test_cases": [
            {"input": "15", "expected_output": "FizzBuzz", "is_hidden": False, "weight": 1.0}
        ]
    }