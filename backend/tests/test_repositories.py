import pytest
from datetime import datetime, timedelta
from app.models.user import User, UserRole
from app.models.assessment import Assessment
from app.models.question import Question, QuestionType
from app.models.attempt import AssessmentAttempt, AttemptStatus
from app.models.answer import Answer
from app.repositories.user import UserRepository
from app.repositories.assessment import AssessmentRepository
from app.repositories.question import QuestionRepository
from app.repositories.attempt import AssessmentAttemptRepository
from app.repositories.answer import AnswerRepository


class TestUserRepository:
    """Test UserRepository"""
    
    def test_create_user(self, db_session, sample_user_data):
        """Test creating a user through repository"""
        repo = UserRepository(db_session)
        user = repo.create(sample_user_data)
        
        assert user.id is not None
        assert user.email == sample_user_data["email"]
        assert user.role == UserRole.STUDENT
    
    def test_get_user_by_email(self, db_session, sample_user_data):
        """Test getting user by email"""
        repo = UserRepository(db_session)
        created_user = repo.create(sample_user_data)
        
        found_user = repo.get_by_email(sample_user_data["email"])
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == sample_user_data["email"]
    
    def test_get_user_by_role(self, db_session):
        """Test getting users by role"""
        repo = UserRepository(db_session)
        
        # Create users with different roles
        student_data = {"email": "student@test.com", "password_hash": "hash", "first_name": "Student", "last_name": "User", "role": UserRole.STUDENT}
        instructor_data = {"email": "instructor@test.com", "password_hash": "hash", "first_name": "Instructor", "last_name": "User", "role": UserRole.INSTRUCTOR}
        
        repo.create(student_data)
        repo.create(instructor_data)
        
        students = repo.get_by_role(UserRole.STUDENT)
        instructors = repo.get_by_role(UserRole.INSTRUCTOR)
        
        assert len(students) == 1
        assert len(instructors) == 1
        assert students[0].role == UserRole.STUDENT
        assert instructors[0].role == UserRole.INSTRUCTOR
    
    def test_search_users(self, db_session):
        """Test searching users"""
        repo = UserRepository(db_session)
        
        users_data = [
            {"email": "john.doe@test.com", "password_hash": "hash", "first_name": "John", "last_name": "Doe", "role": UserRole.STUDENT},
            {"email": "jane.smith@test.com", "password_hash": "hash", "first_name": "Jane", "last_name": "Smith", "role": UserRole.STUDENT},
            {"email": "bob.johnson@test.com", "password_hash": "hash", "first_name": "Bob", "last_name": "Johnson", "role": UserRole.INSTRUCTOR},
        ]
        
        for user_data in users_data:
            repo.create(user_data)
        
        # Search by first name
        john_results = repo.search_users("John")
        assert len(john_results) == 1
        assert john_results[0].first_name == "John"
        
        # Search by email
        jane_results = repo.search_users("jane.smith")
        assert len(jane_results) == 1
        assert jane_results[0].email == "jane.smith@test.com"
    
    def test_email_exists(self, db_session, sample_user_data):
        """Test checking if email exists"""
        repo = UserRepository(db_session)
        
        # Email should not exist initially
        assert not repo.email_exists(sample_user_data["email"])
        
        # Create user
        repo.create(sample_user_data)
        
        # Email should now exist
        assert repo.email_exists(sample_user_data["email"])
    
    def test_activate_deactivate_user(self, db_session, sample_user_data):
        """Test activating and deactivating users"""
        repo = UserRepository(db_session)
        user = repo.create(sample_user_data)
        
        # Deactivate user
        deactivated_user = repo.deactivate_user(user.id)
        assert deactivated_user.is_active is False
        
        # Activate user
        activated_user = repo.activate_user(user.id)
        assert activated_user.is_active is True


class TestAssessmentRepository:
    """Test AssessmentRepository"""
    
    def test_create_assessment(self, db_session, sample_user_data, sample_assessment_data):
        """Test creating an assessment through repository"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        assert assessment.id is not None
        assert assessment.title == sample_assessment_data["title"]
        assert assessment.created_by == user.id
    
    def test_get_by_creator(self, db_session, sample_user_data, sample_assessment_data):
        """Test getting assessments by creator"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        
        # Create multiple assessments
        assessment1 = assessment_repo.create(assessment_data)
        assessment_data["title"] = "Second Assessment"
        assessment2 = assessment_repo.create(assessment_data)
        
        creator_assessments = assessment_repo.get_by_creator(user.id)
        assert len(creator_assessments) == 2
        assert all(a.created_by == user.id for a in creator_assessments)
    
    def test_get_available_assessments(self, db_session, sample_user_data, sample_assessment_data):
        """Test getting available assessments"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        current_time = datetime.utcnow()
        
        # Create assessments with different availability windows
        available_data = sample_assessment_data.copy()
        available_data.update({
            "created_by": user.id,
            "start_time": current_time - timedelta(hours=1),
            "end_time": current_time + timedelta(hours=1),
            "is_active": True
        })
        
        future_data = sample_assessment_data.copy()
        future_data.update({
            "created_by": user.id,
            "title": "Future Assessment",
            "start_time": current_time + timedelta(hours=1),
            "end_time": current_time + timedelta(hours=2),
            "is_active": True
        })
        
        expired_data = sample_assessment_data.copy()
        expired_data.update({
            "created_by": user.id,
            "title": "Expired Assessment",
            "start_time": current_time - timedelta(hours=2),
            "end_time": current_time - timedelta(hours=1),
            "is_active": True
        })
        
        assessment_repo.create(available_data)
        assessment_repo.create(future_data)
        assessment_repo.create(expired_data)
        
        available_assessments = assessment_repo.get_available_assessments(current_time)
        assert len(available_assessments) == 1
        assert available_assessments[0].title == "Python Programming Test"
    
    def test_search_assessments(self, db_session, sample_user_data, sample_assessment_data):
        """Test searching assessments"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        
        # Create assessments with different titles
        assessments_data = [
            {**sample_assessment_data, "created_by": user.id, "title": "Python Programming Test", "description": "Learn Python basics"},
            {**sample_assessment_data, "created_by": user.id, "title": "JavaScript Fundamentals", "description": "Web development with JS"},
            {**sample_assessment_data, "created_by": user.id, "title": "Data Structures", "description": "Python data structures"},
        ]
        
        for assessment_data in assessments_data:
            assessment_repo.create(assessment_data)
        
        # Search by title
        python_results = assessment_repo.search_assessments("Python")
        assert len(python_results) == 2
        
        # Search by description
        js_results = assessment_repo.search_assessments("JavaScript")
        assert len(js_results) == 1
        assert js_results[0].title == "JavaScript Fundamentals"


class TestQuestionRepository:
    """Test QuestionRepository"""
    
    def test_create_question(self, db_session, sample_user_data, sample_assessment_data, sample_question_data):
        """Test creating a question through repository"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        question_repo = QuestionRepository(db_session)
        question_data = sample_question_data.copy()
        question_data["assessment_id"] = assessment.id
        question = question_repo.create(question_data)
        
        assert question.id is not None
        assert question.assessment_id == assessment.id
        assert question.type == QuestionType.CODING
    
    def test_get_by_assessment(self, db_session, sample_user_data, sample_assessment_data, sample_question_data):
        """Test getting questions by assessment"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        question_repo = QuestionRepository(db_session)
        
        # Create multiple questions
        for i in range(3):
            question_data = sample_question_data.copy()
            question_data.update({
                "assessment_id": assessment.id,
                "title": f"Question {i+1}",
                "order": i+1
            })
            question_repo.create(question_data)
        
        questions = question_repo.get_by_assessment(assessment.id)
        assert len(questions) == 3
        assert all(q.assessment_id == assessment.id for q in questions)
        # Check if ordered correctly
        assert questions[0].order == 1
        assert questions[1].order == 2
        assert questions[2].order == 3
    
    def test_get_by_type(self, db_session, sample_user_data, sample_assessment_data):
        """Test getting questions by type"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        question_repo = QuestionRepository(db_session)
        
        # Create questions of different types
        questions_data = [
            {"assessment_id": assessment.id, "type": QuestionType.CODING, "title": "Code Q", "content": "Write code", "points": 10.0, "order": 1},
            {"assessment_id": assessment.id, "type": QuestionType.MCQ, "title": "MCQ Q", "content": "Choose answer", "points": 5.0, "order": 2},
            {"assessment_id": assessment.id, "type": QuestionType.DESCRIPTIVE, "title": "Essay Q", "content": "Explain", "points": 15.0, "order": 3},
        ]
        
        for question_data in questions_data:
            question_repo.create(question_data)
        
        coding_questions = question_repo.get_by_type(QuestionType.CODING)
        mcq_questions = question_repo.get_by_type(QuestionType.MCQ)
        descriptive_questions = question_repo.get_by_type(QuestionType.DESCRIPTIVE)
        
        assert len(coding_questions) == 1
        assert len(mcq_questions) == 1
        assert len(descriptive_questions) == 1
        assert coding_questions[0].type == QuestionType.CODING
        assert mcq_questions[0].type == QuestionType.MCQ
        assert descriptive_questions[0].type == QuestionType.DESCRIPTIVE


class TestAssessmentAttemptRepository:
    """Test AssessmentAttemptRepository"""
    
    def test_start_attempt(self, db_session, sample_user_data, sample_assessment_data):
        """Test starting an assessment attempt"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        attempt_repo = AssessmentAttemptRepository(db_session)
        attempt = attempt_repo.start_attempt(user.id, assessment.id)
        
        assert attempt.id is not None
        assert attempt.user_id == user.id
        assert attempt.assessment_id == assessment.id
        assert attempt.attempt_number == 1
        assert attempt.status == AttemptStatus.STARTED
    
    def test_get_next_attempt_number(self, db_session, sample_user_data, sample_assessment_data):
        """Test getting next attempt number"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        attempt_repo = AssessmentAttemptRepository(db_session)
        
        # First attempt should be 1
        next_attempt = attempt_repo.get_next_attempt_number(user.id, assessment.id)
        assert next_attempt == 1
        
        # Create first attempt
        attempt_repo.start_attempt(user.id, assessment.id)
        
        # Next attempt should be 2
        next_attempt = attempt_repo.get_next_attempt_number(user.id, assessment.id)
        assert next_attempt == 2
    
    def test_submit_attempt(self, db_session, sample_user_data, sample_assessment_data):
        """Test submitting an attempt"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        attempt_repo = AssessmentAttemptRepository(db_session)
        attempt = attempt_repo.start_attempt(user.id, assessment.id)
        
        # Submit the attempt
        submitted_attempt = attempt_repo.submit_attempt(attempt.id)
        
        assert submitted_attempt.status == AttemptStatus.SUBMITTED
        assert submitted_attempt.submitted_at is not None
        assert submitted_attempt.time_taken is not None
    
    def test_get_by_user_and_assessment(self, db_session, sample_user_data, sample_assessment_data):
        """Test getting attempts by user and assessment"""
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        attempt_repo = AssessmentAttemptRepository(db_session)
        
        # Create multiple attempts
        attempt1 = attempt_repo.start_attempt(user.id, assessment.id)
        attempt2 = attempt_repo.start_attempt(user.id, assessment.id)
        
        attempts = attempt_repo.get_by_user_and_assessment(user.id, assessment.id)
        assert len(attempts) == 2
        assert attempts[0].attempt_number == 1
        assert attempts[1].attempt_number == 2


class TestAnswerRepository:
    """Test AnswerRepository"""
    
    def test_save_answer(self, db_session, sample_user_data, sample_assessment_data, sample_question_data):
        """Test saving an answer"""
        # Setup
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        question_repo = QuestionRepository(db_session)
        question_data = sample_question_data.copy()
        question_data["assessment_id"] = assessment.id
        question = question_repo.create(question_data)
        
        attempt_repo = AssessmentAttemptRepository(db_session)
        attempt = attempt_repo.start_attempt(user.id, assessment.id)
        
        # Test saving answer
        answer_repo = AnswerRepository(db_session)
        answer = answer_repo.save_answer(attempt.id, question.id, "def fizzbuzz(n): return 'FizzBuzz'")
        
        assert answer.id is not None
        assert answer.attempt_id == attempt.id
        assert answer.question_id == question.id
        assert answer.content == "def fizzbuzz(n): return 'FizzBuzz'"
    
    def test_grade_answer(self, db_session, sample_user_data, sample_assessment_data, sample_question_data):
        """Test grading an answer"""
        # Setup
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        question_repo = QuestionRepository(db_session)
        question_data = sample_question_data.copy()
        question_data["assessment_id"] = assessment.id
        question = question_repo.create(question_data)
        
        attempt_repo = AssessmentAttemptRepository(db_session)
        attempt = attempt_repo.start_attempt(user.id, assessment.id)
        
        answer_repo = AnswerRepository(db_session)
        answer = answer_repo.save_answer(attempt.id, question.id, "def fizzbuzz(n): return 'FizzBuzz'")
        
        # Grade the answer
        graded_answer = answer_repo.grade_answer(answer.id, 8.0, 10.0, True, "Good solution!")
        
        assert graded_answer.score == 8.0
        assert graded_answer.max_score == 10.0
        assert graded_answer.is_correct is True
        assert graded_answer.feedback == "Good solution!"
    
    def test_get_by_attempt_and_question(self, db_session, sample_user_data, sample_assessment_data, sample_question_data):
        """Test getting answer by attempt and question"""
        # Setup
        user_repo = UserRepository(db_session)
        user = user_repo.create(sample_user_data)
        
        assessment_repo = AssessmentRepository(db_session)
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = assessment_repo.create(assessment_data)
        
        question_repo = QuestionRepository(db_session)
        question_data = sample_question_data.copy()
        question_data["assessment_id"] = assessment.id
        question = question_repo.create(question_data)
        
        attempt_repo = AssessmentAttemptRepository(db_session)
        attempt = attempt_repo.start_attempt(user.id, assessment.id)
        
        answer_repo = AnswerRepository(db_session)
        created_answer = answer_repo.save_answer(attempt.id, question.id, "def fizzbuzz(n): return 'FizzBuzz'")
        
        # Get answer by attempt and question
        found_answer = answer_repo.get_by_attempt_and_question(attempt.id, question.id)
        
        assert found_answer is not None
        assert found_answer.id == created_answer.id
        assert found_answer.attempt_id == attempt.id
        assert found_answer.question_id == question.id