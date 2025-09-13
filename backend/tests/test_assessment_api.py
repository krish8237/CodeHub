import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from app.main import app
from app.core.database import get_db
from app.models.assessment import Assessment
from app.models.question import Question, QuestionType
from app.models.attempt import AssessmentAttempt, AttemptStatus
from app.models.user import UserRole
from tests.conftest import override_get_db


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


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


def test_create_assessment_as_student_forbidden(db, test_user, auth_headers):
    """Test that students cannot create assessments"""
    assessment_data = {
        "title": "Test Assessment",
        "description": "Test description",
        "is_active": True
    }
    
    response = client.post(
        "/api/v1/assessments/",
        json=assessment_data,
        headers=auth_headers
    )
    
    assert response.status_code == 403


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


def test_update_assessment(db, instructor_user, instructor_auth_headers):
    """Test updating an assessment"""
    # Create assessment
    assessment = Assessment(
        title="Original Title",
        description="Original description",
        created_by=instructor_user.id,
        is_active=True
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    update_data = {
        "title": "Updated Title",
        "description": "Updated description",
        "time_limit": 90
    }
    
    response = client.put(
        f"/api/v1/assessments/{assessment.id}",
        json=update_data,
        headers=instructor_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["time_limit"] == 90


def test_delete_assessment(db, instructor_user, instructor_auth_headers):
    """Test deleting an assessment"""
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
    
    response = client.delete(
        f"/api/v1/assessments/{assessment.id}",
        headers=instructor_auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify assessment is deleted
    response = client.get(
        f"/api/v1/assessments/{assessment.id}",
        headers=instructor_auth_headers
    )
    assert response.status_code == 404


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


def test_create_mcq_question(db, instructor_user, instructor_auth_headers):
    """Test creating an MCQ question"""
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
        "type": "MCQ",
        "title": "Python Data Types",
        "content": "Which of the following is a mutable data type in Python?",
        "points": 5.0,
        "order": 1,
        "options": [
            {"text": "String", "is_correct": False},
            {"text": "Tuple", "is_correct": False},
            {"text": "List", "is_correct": True},
            {"text": "Integer", "is_correct": False}
        ]
    }
    
    response = client.post(
        f"/api/v1/assessments/{assessment.id}/questions",
        json=question_data,
        headers=instructor_auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "MCQ"
    assert data["title"] == question_data["title"]
    assert len(data["options"]) == 4
    assert len(data["correct_answers"]) == 1
    assert data["correct_answers"][0] == 2  # List is at index 2


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


def test_start_attempt_on_inactive_assessment(db, test_user, instructor_user, auth_headers):
    """Test starting attempt on inactive assessment"""
    assessment = Assessment(
        title="Test Assessment",
        description="Test description",
        created_by=instructor_user.id,
        is_active=False,
        max_attempts=3
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    response = client.post(
        f"/api/v1/assessments/{assessment.id}/attempts",
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "not active" in response.json()["detail"]


def test_assessment_with_time_limit(db, instructor_user, instructor_auth_headers):
    """Test creating assessment with time limit"""
    assessment_data = {
        "title": "Timed Assessment",
        "description": "Assessment with time limit",
        "time_limit": 60,  # 1 hour
        "max_attempts": 1,
        "is_active": True
    }
    
    response = client.post(
        "/api/v1/assessments/",
        json=assessment_data,
        headers=instructor_auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["time_limit"] == 60


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