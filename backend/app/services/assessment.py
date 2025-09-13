from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.assessment import Assessment
from app.models.question import Question, QuestionType
from app.models.attempt import AssessmentAttempt, AttemptStatus
from app.models.user import User, UserRole
from app.repositories.assessment import AssessmentRepository
from app.repositories.question import QuestionRepository
from app.repositories.attempt import AssessmentAttemptRepository
from app.schemas.assessment import (
    AssessmentCreate, AssessmentUpdate, QuestionCreate, QuestionUpdate,
    AssessmentAttemptCreate, AssessmentAttemptUpdate
)


class AssessmentService:
    """Service class for assessment management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.assessment_repo = AssessmentRepository(db)
        self.question_repo = QuestionRepository(db)
        self.attempt_repo = AssessmentAttemptRepository(db)
    
    # Assessment CRUD operations
    def create_assessment(self, assessment_data: AssessmentCreate, creator_id: int) -> Assessment:
        """Create a new assessment"""
        # Convert settings to dict if provided
        settings_dict = None
        if assessment_data.settings:
            settings_dict = assessment_data.settings.dict()
        
        assessment_dict = assessment_data.dict(exclude={'settings'})
        assessment_dict['settings'] = settings_dict
        assessment_dict['created_by'] = creator_id
        
        return self.assessment_repo.create(assessment_dict)
    
    def get_assessment(self, assessment_id: int, user_id: int, user_role: UserRole) -> Optional[Assessment]:
        """Get assessment by ID with access control"""
        assessment = self.assessment_repo.get(assessment_id)
        if not assessment:
            return None
        
        # Check access permissions
        if user_role == UserRole.STUDENT:
            # Students can only see active assessments
            if not assessment.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Assessment is not available"
                )
        elif user_role == UserRole.INSTRUCTOR:
            # Instructors can only see their own assessments
            if assessment.created_by != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only access your own assessments"
                )
        # Admins can see all assessments
        
        return assessment
    
    def get_assessment_with_questions(self, assessment_id: int, user_id: int, user_role: UserRole) -> Optional[Assessment]:
        """Get assessment with questions"""
        assessment = self.get_assessment(assessment_id, user_id, user_role)
        if not assessment:
            return None
        
        return self.assessment_repo.get_with_questions(assessment_id)
    
    def update_assessment(self, assessment_id: int, assessment_data: AssessmentUpdate, user_id: int, user_role: UserRole) -> Optional[Assessment]:
        """Update assessment"""
        assessment = self.get_assessment(assessment_id, user_id, user_role)
        if not assessment:
            return None
        
        # Only creators and admins can update
        if user_role == UserRole.INSTRUCTOR and assessment.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own assessments"
            )
        elif user_role == UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot update assessments"
            )
        
        # Convert settings to dict if provided
        update_dict = assessment_data.dict(exclude_unset=True)
        if 'settings' in update_dict and update_dict['settings']:
            update_dict['settings'] = update_dict['settings'].dict()
        
        return self.assessment_repo.update(assessment_id, update_dict)
    
    def delete_assessment(self, assessment_id: int, user_id: int, user_role: UserRole) -> bool:
        """Delete assessment"""
        assessment = self.get_assessment(assessment_id, user_id, user_role)
        if not assessment:
            return False
        
        # Only creators and admins can delete
        if user_role == UserRole.INSTRUCTOR and assessment.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own assessments"
            )
        elif user_role == UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot delete assessments"
            )
        
        return self.assessment_repo.delete(assessment_id)
    
    def list_assessments(self, user_id: int, user_role: UserRole, skip: int = 0, limit: int = 100) -> tuple[List[Assessment], int]:
        """List assessments based on user role"""
        if user_role == UserRole.STUDENT:
            # Students see available assessments
            assessments = self.assessment_repo.get_available_assessments(skip=skip, limit=limit)
            total = len(self.assessment_repo.get_available_assessments())
        elif user_role == UserRole.INSTRUCTOR:
            # Instructors see their own assessments
            assessments = self.assessment_repo.get_by_creator(user_id, skip=skip, limit=limit)
            total = len(self.assessment_repo.get_by_creator(user_id))
        else:  # Admin
            # Admins see all assessments
            assessments = self.assessment_repo.get_all(skip=skip, limit=limit)
            total = self.assessment_repo.count()
        
        return assessments, total
    
    def get_available_assessments(self, skip: int = 0, limit: int = 100) -> tuple[List[Assessment], int]:
        """Get assessments available for taking"""
        assessments = self.assessment_repo.get_available_assessments(skip=skip, limit=limit)
        total = len(self.assessment_repo.get_available_assessments())
        return assessments, total
    
    def search_assessments(self, search_term: str, user_id: int, user_role: UserRole, skip: int = 0, limit: int = 100) -> tuple[List[Assessment], int]:
        """Search assessments"""
        if user_role == UserRole.INSTRUCTOR:
            # For instructors, filter by creator after search
            all_results = self.assessment_repo.search_assessments(search_term)
            assessments = [a for a in all_results if a.created_by == user_id][skip:skip+limit]
            total = len([a for a in all_results if a.created_by == user_id])
        else:
            assessments = self.assessment_repo.search_assessments(search_term, skip=skip, limit=limit)
            total = len(self.assessment_repo.search_assessments(search_term))
        
        return assessments, total
    
    # Question management
    def create_question(self, question_data: QuestionCreate, user_id: int, user_role: UserRole) -> Question:
        """Create a new question"""
        # Check if user can modify this assessment
        assessment = self.get_assessment(question_data.assessment_id, user_id, user_role)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        if user_role == UserRole.INSTRUCTOR and assessment.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only add questions to your own assessments"
            )
        elif user_role == UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot create questions"
            )
        
        # Convert complex fields to JSON
        question_dict = question_data.dict()
        if question_dict.get('test_cases'):
            question_dict['test_cases'] = [tc.dict() if hasattr(tc, 'dict') else tc for tc in question_dict['test_cases']]
        if question_dict.get('options'):
            question_dict['options'] = [opt.dict() if hasattr(opt, 'dict') else opt for opt in question_dict['options']]
            # Extract correct answers for MCQ
            question_dict['correct_answers'] = [i for i, opt in enumerate(question_dict['options']) if opt.get('is_correct', False)]
        
        return self.question_repo.create(question_dict)
    
    def get_question(self, question_id: int, user_id: int, user_role: UserRole) -> Optional[Question]:
        """Get question by ID"""
        question = self.question_repo.get(question_id)
        if not question:
            return None
        
        # Check access to parent assessment
        assessment = self.get_assessment(question.assessment_id, user_id, user_role)
        if not assessment:
            return None
        
        return question
    
    def update_question(self, question_id: int, question_data: QuestionUpdate, user_id: int, user_role: UserRole) -> Optional[Question]:
        """Update question"""
        question = self.get_question(question_id, user_id, user_role)
        if not question:
            return None
        
        assessment = self.get_assessment(question.assessment_id, user_id, user_role)
        if user_role == UserRole.INSTRUCTOR and assessment.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update questions in your own assessments"
            )
        elif user_role == UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot update questions"
            )
        
        # Convert complex fields to JSON
        update_dict = question_data.dict(exclude_unset=True)
        if 'test_cases' in update_dict and update_dict['test_cases']:
            update_dict['test_cases'] = [tc.dict() if hasattr(tc, 'dict') else tc for tc in update_dict['test_cases']]
        if 'options' in update_dict and update_dict['options']:
            update_dict['options'] = [opt.dict() if hasattr(opt, 'dict') else opt for opt in update_dict['options']]
            # Extract correct answers for MCQ
            update_dict['correct_answers'] = [i for i, opt in enumerate(update_dict['options']) if opt.get('is_correct', False)]
        
        return self.question_repo.update(question_id, update_dict)
    
    def delete_question(self, question_id: int, user_id: int, user_role: UserRole) -> bool:
        """Delete question"""
        question = self.get_question(question_id, user_id, user_role)
        if not question:
            return False
        
        assessment = self.get_assessment(question.assessment_id, user_id, user_role)
        if user_role == UserRole.INSTRUCTOR and assessment.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete questions from your own assessments"
            )
        elif user_role == UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot delete questions"
            )
        
        return self.question_repo.delete(question_id)
    
    def list_questions(self, assessment_id: int, user_id: int, user_role: UserRole, skip: int = 0, limit: int = 100) -> tuple[List[Question], int]:
        """List questions for an assessment"""
        # Check access to assessment
        assessment = self.get_assessment(assessment_id, user_id, user_role)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        questions = self.question_repo.get_by_assessment(assessment_id, skip=skip, limit=limit)
        total = len(self.question_repo.get_by_assessment(assessment_id))
        return questions, total
    
    # Assessment attempt management
    def start_assessment_attempt(self, attempt_data: AssessmentAttemptCreate, user_id: int) -> AssessmentAttempt:
        """Start a new assessment attempt"""
        assessment = self.assessment_repo.get(attempt_data.assessment_id)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        # Check if assessment is available
        current_time = datetime.now(timezone.utc)
        if not assessment.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment is not active"
            )
        
        if assessment.start_time and current_time < assessment.start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment has not started yet"
            )
        
        if assessment.end_time and current_time > assessment.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment has ended"
            )
        
        # Check attempt limits
        existing_attempts = self.attempt_repo.get_by_user_and_assessment(user_id, attempt_data.assessment_id)
        if len(existing_attempts) >= assessment.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum number of attempts reached"
            )
        
        # Check for active attempts
        active_attempts = [a for a in existing_attempts if a.status in [AttemptStatus.STARTED, AttemptStatus.IN_PROGRESS]]
        if active_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an active attempt for this assessment"
            )
        
        # Create new attempt
        attempt_dict = {
            'user_id': user_id,
            'assessment_id': attempt_data.assessment_id,
            'attempt_number': len(existing_attempts) + 1,
            'status': AttemptStatus.STARTED,
            'started_at': current_time
        }
        
        return self.attempt_repo.create(attempt_dict)
    
    def get_assessment_attempt(self, attempt_id: int, user_id: int, user_role: UserRole) -> Optional[AssessmentAttempt]:
        """Get assessment attempt"""
        attempt = self.attempt_repo.get(attempt_id)
        if not attempt:
            return None
        
        # Check access permissions
        if user_role == UserRole.STUDENT and attempt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own attempts"
            )
        elif user_role == UserRole.INSTRUCTOR:
            # Instructors can see attempts for their assessments
            assessment = self.assessment_repo.get(attempt.assessment_id)
            if assessment and assessment.created_by != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only access attempts for your own assessments"
                )
        # Admins can see all attempts
        
        return attempt
    
    def update_assessment_attempt(self, attempt_id: int, attempt_data: AssessmentAttemptUpdate, user_id: int, user_role: UserRole) -> Optional[AssessmentAttempt]:
        """Update assessment attempt"""
        attempt = self.get_assessment_attempt(attempt_id, user_id, user_role)
        if not attempt:
            return None
        
        # Students can only update their own attempts and limited fields
        if user_role == UserRole.STUDENT:
            if attempt.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own attempts"
                )
            # Students can only update status and submission time
            allowed_fields = {'status', 'submitted_at', 'time_taken', 'attempt_metadata'}
            update_dict = {k: v for k, v in attempt_data.dict(exclude_unset=True).items() if k in allowed_fields}
        else:
            # Instructors and admins can update all fields
            update_dict = attempt_data.dict(exclude_unset=True)
        
        return self.attempt_repo.update(attempt_id, update_dict)
    
    def list_assessment_attempts(self, assessment_id: int, user_id: int, user_role: UserRole, skip: int = 0, limit: int = 100) -> tuple[List[AssessmentAttempt], int]:
        """List attempts for an assessment"""
        # Check access to assessment
        assessment = self.get_assessment(assessment_id, user_id, user_role)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        if user_role == UserRole.STUDENT:
            # Students see only their own attempts
            attempts = self.attempt_repo.get_by_user_and_assessment(user_id, assessment_id, skip=skip, limit=limit)
            total = len(self.attempt_repo.get_by_user_and_assessment(user_id, assessment_id))
        else:
            # Instructors and admins see all attempts for the assessment
            attempts = self.attempt_repo.get_by_assessment(assessment_id, skip=skip, limit=limit)
            total = len(self.attempt_repo.get_by_assessment(assessment_id))
        
        return attempts, total
    
    def get_user_attempts(self, user_id: int, requesting_user_id: int, user_role: UserRole, skip: int = 0, limit: int = 100) -> tuple[List[AssessmentAttempt], int]:
        """Get all attempts by a user"""
        if user_role == UserRole.STUDENT and user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own attempts"
            )
        
        attempts = self.attempt_repo.get_by_user(user_id, skip=skip, limit=limit)
        total = len(self.attempt_repo.get_by_user(user_id))
        return attempts, total