import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.models import *  # Import all models
from app.models.user import User, UserRole
from app.core.security import get_password_hash, create_access_token


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
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
def test_user(db):
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        first_name="John",
        last_name="Doe",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def unverified_user(db):
    """Create an unverified test user"""
    user = User(
        email="unverified@example.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Unverified",
        last_name="User",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def instructor_user(db):
    """Create a test instructor user"""
    user = User(
        email="instructor@example.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Jane",
        last_name="Instructor",
        role=UserRole.INSTRUCTOR,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    """Create a test admin user"""
    user = User(
        email="admin@example.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers for test user"""
    token = create_access_token(
        subject=test_user.email,
        user_id=test_user.id,
        role=test_user.role.value
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def instructor_auth_headers(instructor_user):
    """Create authorization headers for instructor user"""
    token = create_access_token(
        subject=instructor_user.email,
        user_id=instructor_user.id,
        role=instructor_user.role.value
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(admin_user):
    """Create authorization headers for admin user"""
    token = create_access_token(
        subject=admin_user.email,
        user_id=admin_user.id,
        role=admin_user.role.value
    )
    return {"Authorization": f"Bearer {token}"}


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