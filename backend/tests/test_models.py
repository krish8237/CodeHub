import pytest
from datetime import datetime
from app.models.user import User, UserRole
from app.models.assessment import Assessment
from app.models.question import Question, QuestionType
from app.models.attempt import AssessmentAttempt, AttemptStatus
from app.models.answer import Answer


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, db_session, sample_user_data):
        """Test creating a user"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == sample_user_data["email"]
        assert user.role == UserRole.STUDENT
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_full_name_property(self, db_session, sample_user_data):
        """Test user full_name property"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assert user.full_name == "John Doe"
    
    def test_user_repr(self, db_session, sample_user_data):
        """Test user string representation"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        expected_repr = f"<User(id={user.id}, email='test@example.com', role='student')>"
        assert repr(user) == expected_repr
    
    def test_user_role_enum(self, db_session):
        """Test user role enum values"""
        # Test all role types
        roles_data = [
            {"email": "student@test.com", "password_hash": "hash", "first_name": "Student", "last_name": "User", "role": UserRole.STUDENT},
            {"email": "instructor@test.com", "password_hash": "hash", "first_name": "Instructor", "last_name": "User", "role": UserRole.INSTRUCTOR},
            {"email": "admin@test.com", "password_hash": "hash", "first_name": "Admin", "last_name": "User", "role": UserRole.ADMIN},
        ]
        
        for role_data in roles_data:
            user = User(**role_data)
            db_session.add(user)
        
        db_session.commit()
        
        users = db_session.query(User).all()
        assert len(users) == 3
        assert users[0].role == UserRole.STUDENT
        assert users[1].role == UserRole.INSTRUCTOR
        assert users[2].role == UserRole.ADMIN


class TestAssessmentModel:
    """Test Assessment model"""
    
    def test_create_assessment(self, db_session, sample_user_data, sample_assessment_data):
        """Test creating an assessment"""
        # Create user first
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create assessment
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = Assessment(**assessment_data)
        db_session.add(assessment)
        db_session.commit()
        
        assert assessment.id is not None
        assert assessment.title == sample_assessment_data["title"]
        assert assessment.time_limit == 120
        assert assessment.max_attempts == 3
        assert assessment.is_active is True
        assert assessment.created_by == user.id
        assert assessment.created_at is not None
    
    def test_assessment_repr(self, db_session, sample_user_data, sample_assessment_data):
        """Test assessment string representation"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = Assessment(**assessment_data)
        db_session.add(assessment)
        db_session.commit()
        
        expected_repr = f"<Assessment(id={assessment.id}, title='Python Programming Test', created_by={user.id})>"
        assert repr(assessment) == expected_repr


class TestQuestionModel:
    """Test Question model"""
    
    def test_create_coding_question(self, db_session, sample_user_data, sample_assessment_data, sample_question_data):
        """Test creating a coding question"""
        # Create user and assessment first
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = Assessment(**assessment_data)
        db_session.add(assessment)
        db_session.commit()
        
        # Create question
        question_data = sample_question_data.copy()
        question_data["assessment_id"] = assessment.id
        question = Question(**question_data)
        db_session.add(question)
        db_session.commit()
        
        assert question.id is not None
        assert question.type == QuestionType.CODING
        assert question.title == "FizzBuzz Implementation"
        assert question.language == "python"
        assert question.points == 10.0
        assert question.order == 1
        assert question.test_cases is not None
    
    def test_create_mcq_question(self, db_session, sample_user_data, sample_assessment_data):
        """Test creating an MCQ question"""
        # Create user and assessment first
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = Assessment(**assessment_data)
        db_session.add(assessment)
        db_session.commit()
        
        # Create MCQ question
        mcq_data = {
            "assessment_id": assessment.id,
            "type": QuestionType.MCQ,
            "title": "Python Data Types",
            "content": "Which of the following are mutable data types in Python?",
            "points": 5.0,
            "order": 1,
            "options": ["List", "Tuple", "Dictionary", "String"],
            "correct_answers": [0, 2]  # List and Dictionary
        }
        question = Question(**mcq_data)
        db_session.add(question)
        db_session.commit()
        
        assert question.type == QuestionType.MCQ
        assert question.options == ["List", "Tuple", "Dictionary", "String"]
        assert question.correct_answers == [0, 2]
    
    def test_question_type_enum(self, db_session, sample_user_data, sample_assessment_data):
        """Test question type enum values"""
        # Create user and assessment first
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = Assessment(**assessment_data)
        db_session.add(assessment)
        db_session.commit()
        
        # Test all question types
        questions_data = [
            {"assessment_id": assessment.id, "type": QuestionType.CODING, "title": "Code Question", "content": "Write code", "points": 10.0, "order": 1},
            {"assessment_id": assessment.id, "type": QuestionType.MCQ, "title": "MCQ Question", "content": "Choose answer", "points": 5.0, "order": 2},
            {"assessment_id": assessment.id, "type": QuestionType.DESCRIPTIVE, "title": "Essay Question", "content": "Explain concept", "points": 15.0, "order": 3},
        ]
        
        for question_data in questions_data:
            question = Question(**question_data)
            db_session.add(question)
        
        db_session.commit()
        
        questions = db_session.query(Question).all()
        assert len(questions) == 3
        assert questions[0].type == QuestionType.CODING
        assert questions[1].type == QuestionType.MCQ
        assert questions[2].type == QuestionType.DESCRIPTIVE


class TestAssessmentAttemptModel:
    """Test AssessmentAttempt model"""
    
    def test_create_attempt(self, db_session, sample_user_data, sample_assessment_data):
        """Test creating an assessment attempt"""
        # Create user and assessment first
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = Assessment(**assessment_data)
        db_session.add(assessment)
        db_session.commit()
        
        # Create attempt
        attempt_data = {
            "user_id": user.id,
            "assessment_id": assessment.id,
            "attempt_number": 1,
            "status": AttemptStatus.STARTED,
            "started_at": datetime.utcnow()
        }
        attempt = AssessmentAttempt(**attempt_data)
        db_session.add(attempt)
        db_session.commit()
        
        assert attempt.id is not None
        assert attempt.user_id == user.id
        assert attempt.assessment_id == assessment.id
        assert attempt.attempt_number == 1
        assert attempt.status == AttemptStatus.STARTED
        assert attempt.started_at is not None
    
    def test_attempt_score_percentage_property(self, db_session, sample_user_data, sample_assessment_data):
        """Test attempt score percentage property"""
        # Create user and assessment first
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = Assessment(**assessment_data)
        db_session.add(assessment)
        db_session.commit()
        
        # Create attempt with scores
        attempt_data = {
            "user_id": user.id,
            "assessment_id": assessment.id,
            "attempt_number": 1,
            "status": AttemptStatus.GRADED,
            "started_at": datetime.utcnow(),
            "total_score": 75.0,
            "max_score": 100.0
        }
        attempt = AssessmentAttempt(**attempt_data)
        db_session.add(attempt)
        db_session.commit()
        
        assert attempt.score_percentage == 75.0
    
    def test_attempt_status_enum(self, db_session, sample_user_data, sample_assessment_data):
        """Test attempt status enum values"""
        # Create user and assessment first
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = Assessment(**assessment_data)
        db_session.add(assessment)
        db_session.commit()
        
        # Test all status types
        statuses = [AttemptStatus.STARTED, AttemptStatus.IN_PROGRESS, AttemptStatus.SUBMITTED, AttemptStatus.GRADED, AttemptStatus.EXPIRED]
        
        for i, status in enumerate(statuses):
            attempt_data = {
                "user_id": user.id,
                "assessment_id": assessment.id,
                "attempt_number": i + 1,
                "status": status,
                "started_at": datetime.utcnow()
            }
            attempt = AssessmentAttempt(**attempt_data)
            db_session.add(attempt)
        
        db_session.commit()
        
        attempts = db_session.query(AssessmentAttempt).all()
        assert len(attempts) == 5
        for i, attempt in enumerate(attempts):
            assert attempt.status == statuses[i]


class TestAnswerModel:
    """Test Answer model"""
    
    def test_create_answer(self, db_session, sample_user_data, sample_assessment_data, sample_question_data):
        """Test creating an answer"""
        # Create user, assessment, question, and attempt first
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = Assessment(**assessment_data)
        db_session.add(assessment)
        db_session.commit()
        
        question_data = sample_question_data.copy()
        question_data["assessment_id"] = assessment.id
        question = Question(**question_data)
        db_session.add(question)
        db_session.commit()
        
        attempt_data = {
            "user_id": user.id,
            "assessment_id": assessment.id,
            "attempt_number": 1,
            "status": AttemptStatus.IN_PROGRESS,
            "started_at": datetime.utcnow()
        }
        attempt = AssessmentAttempt(**attempt_data)
        db_session.add(attempt)
        db_session.commit()
        
        # Create answer
        answer_data = {
            "attempt_id": attempt.id,
            "question_id": question.id,
            "content": "def fizzbuzz(n):\n    return 'FizzBuzz'",
            "score": 8.0,
            "max_score": 10.0,
            "is_correct": True,
            "submitted_at": datetime.utcnow()
        }
        answer = Answer(**answer_data)
        db_session.add(answer)
        db_session.commit()
        
        assert answer.id is not None
        assert answer.attempt_id == attempt.id
        assert answer.question_id == question.id
        assert answer.score == 8.0
        assert answer.max_score == 10.0
        assert answer.is_correct is True
    
    def test_answer_score_percentage_property(self, db_session, sample_user_data, sample_assessment_data, sample_question_data):
        """Test answer score percentage property"""
        # Create necessary objects
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assessment_data = sample_assessment_data.copy()
        assessment_data["created_by"] = user.id
        assessment = Assessment(**assessment_data)
        db_session.add(assessment)
        db_session.commit()
        
        question_data = sample_question_data.copy()
        question_data["assessment_id"] = assessment.id
        question = Question(**question_data)
        db_session.add(question)
        db_session.commit()
        
        attempt_data = {
            "user_id": user.id,
            "assessment_id": assessment.id,
            "attempt_number": 1,
            "status": AttemptStatus.IN_PROGRESS,
            "started_at": datetime.utcnow()
        }
        attempt = AssessmentAttempt(**attempt_data)
        db_session.add(attempt)
        db_session.commit()
        
        # Create answer with scores
        answer_data = {
            "attempt_id": attempt.id,
            "question_id": question.id,
            "content": "def fizzbuzz(n):\n    return 'FizzBuzz'",
            "score": 7.5,
            "max_score": 10.0,
            "submitted_at": datetime.utcnow()
        }
        answer = Answer(**answer_data)
        db_session.add(answer)
        db_session.commit()
        
        assert answer.score_percentage == 75.0