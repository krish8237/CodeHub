"""
Integration tests for assessment management API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from app.main import app
from app.core.database import get_db
from app.models.assessment import Assessment
from app.models.question import Question, QuestionType
from app.models.attempt import AssessmentAttempt, AttemptStatus
from app.models.user import User, UserRole
from app.core.security import get_password_hash, create_access_token
from tests.conftest import override_get_db, TestingSessionLocal
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from app.core.database import Base

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
def test_user(db):
    """Create a test student user"""
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
def instructor_auth_headers(instructor_user):
    """Create authorization headers for instructor user"""
    token = create_access_token(
        subject=instructor_user.email,
        user_id=instructor_user.id,
        role=instructor_user.role.value
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers for test user"""
    token = create_access_token(
        subject=test_user.email,
        user_id=test_user.id,
        role=test_user.role.value
    )
    return {"Authorization": f"Bearer {token}"}


def test_create_assessment_as_instructor(db, instructor_user, instructor_auth_headers):
    """Test creating an assessment as an instructor"""
    assessment_data = {
        "title": "Python Programming Test",
        "description": "A comprehensive Python programming assessment",
        "instructions": "Complete all questions within the time limit",
        "time_limit": 120,
        "max_attempts": 3,
        "is_active": True,
        "settings": {
            "allow_backtrack": True,
            "shuffle_questions": False,
            "show_results_immediately": False
        }
    }
    
    response = client.post(
        "/api/v1/assessments/",
        json=assessment_data,
        headers=instructor_auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == assessment_data["title"]
    assert data["description"] == assessment_data["description"]
    assert data["created_by"] == instructor_user.id
    assert data["is_active"] is True


def test_get_assessment_by_id(db, instructor_user, instructor_auth_headers):
    """Test getting an assessment by ID"""
    # Create assessment
    assessment = Assessment(
        title="Test Assessment",
        description="Test description",
        created_by=instructor_user.id,
        is_active=True
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    response = client.get(
        f"/api/v1/assessments/{assessment.id}",
        headers=instructor_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == assessment.id
    assert data["title"] == assessment.title


def test_create_coding_question(db, instructor_user, instructor_auth_headers):
    """Test creating a coding question"""
    # Create assessment first
    assessment = Assessment(
        title="Test Assessment",
        description="Test description",
        created_by=instructor_user.id,
        is_active=True
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    question_data = {
        "type": "CODING",
        "title": "FizzBuzz Implementation",
        "content": "Implement the FizzBuzz algorithm",
        "points": 10.0,
        "order": 1,
        "language": "python",
        "starter_code": "def fizzbuzz(n):\n    pass",
        "test_cases": [
            {
                "input": "15",
                "expected_output": "FizzBuzz",
                "is_hidden": False,
                "weight": 1.0
            }
        ]
    }
    
    response = client.post(
        f"/api/v1/assessments/{assessment.id}/questions",
        json=question_data,
        headers=instructor_auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "CODING"
    assert data["title"] == question_data["title"]
    assert data["language"] == "python"
    assert len(data["test_cases"]) == 1


def test_start_assessment_attempt(db, test_user, instructor_user, auth_headers):
    """Test starting an assessment attempt"""
    # Create available assessment
    current_time = datetime.now(timezone.utc)
    assessment = Assessment(
        title="Test Assessment",
        description="Test description",
        created_by=instructor_user.id,
        is_active=True,
        max_attempts=3,
        start_time=current_time - timedelta(hours=1),
        end_time=current_time + timedelta(hours=1)
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    response = client.post(
        f"/api/v1/assessments/{assessment.id}/attempts",
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == test_user.id
    assert data["assessment_id"] == assessment.id
    assert data["status"] == "STARTED"
    assert data["attempt_number"] == 1


def test_list_assessments_as_instructor(db, instructor_user, instructor_auth_headers):
    """Test listing assessments as an instructor"""
    # Create multiple assessments
    for i in range(3):
        assessment = Assessment(
            title=f"Assessment {i+1}",
            description=f"Description {i+1}",
            created_by=instructor_user.id,
            is_active=True
        )
        db.add(assessment)
    db.commit()
    
    response = client.get(
        "/api/v1/assessments/",
        headers=instructor_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["assessments"]) == 3