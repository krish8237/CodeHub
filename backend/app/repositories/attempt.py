from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from datetime import datetime
from app.models.attempt import AssessmentAttempt, AttemptStatus
from .base import BaseRepository


class AssessmentAttemptRepository(BaseRepository[AssessmentAttempt]):
    """Repository for AssessmentAttempt model with specific methods"""
    
    def __init__(self, db: Session):
        super().__init__(AssessmentAttempt, db)
    
    def get_with_answers(self, attempt_id: int) -> Optional[AssessmentAttempt]:
        """Get attempt with all answers loaded"""
        return self.db.query(AssessmentAttempt).options(
            joinedload(AssessmentAttempt.answers)
        ).filter(AssessmentAttempt.id == attempt_id).first()
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[AssessmentAttempt]:
        """Get attempts by user"""
        return self.db.query(AssessmentAttempt).filter(
            AssessmentAttempt.user_id == user_id
        ).order_by(AssessmentAttempt.started_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_assessment(self, assessment_id: int, skip: int = 0, limit: int = 100) -> List[AssessmentAttempt]:
        """Get attempts by assessment"""
        return self.db.query(AssessmentAttempt).filter(
            AssessmentAttempt.assessment_id == assessment_id
        ).order_by(AssessmentAttempt.started_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_user_and_assessment(self, user_id: int, assessment_id: int) -> List[AssessmentAttempt]:
        """Get all attempts by a user for a specific assessment"""
        return self.db.query(AssessmentAttempt).filter(
            and_(
                AssessmentAttempt.user_id == user_id,
                AssessmentAttempt.assessment_id == assessment_id
            )
        ).order_by(AssessmentAttempt.attempt_number).all()
    
    def get_latest_attempt(self, user_id: int, assessment_id: int) -> Optional[AssessmentAttempt]:
        """Get the latest attempt by a user for an assessment"""
        return self.db.query(AssessmentAttempt).filter(
            and_(
                AssessmentAttempt.user_id == user_id,
                AssessmentAttempt.assessment_id == assessment_id
            )
        ).order_by(AssessmentAttempt.attempt_number.desc()).first()
    
    def get_by_status(self, status: AttemptStatus, skip: int = 0, limit: int = 100) -> List[AssessmentAttempt]:
        """Get attempts by status"""
        return self.db.query(AssessmentAttempt).filter(
            AssessmentAttempt.status == status
        ).offset(skip).limit(limit).all()
    
    def get_active_attempts(self, skip: int = 0, limit: int = 100) -> List[AssessmentAttempt]:
        """Get active attempts (started or in progress)"""
        return self.db.query(AssessmentAttempt).filter(
            AssessmentAttempt.status.in_([AttemptStatus.STARTED, AttemptStatus.IN_PROGRESS])
        ).offset(skip).limit(limit).all()
    
    def get_completed_attempts(self, skip: int = 0, limit: int = 100) -> List[AssessmentAttempt]:
        """Get completed attempts (submitted or graded)"""
        return self.db.query(AssessmentAttempt).filter(
            AssessmentAttempt.status.in_([AttemptStatus.SUBMITTED, AttemptStatus.GRADED])
        ).offset(skip).limit(limit).all()
    
    def count_user_attempts(self, user_id: int, assessment_id: int) -> int:
        """Count attempts by a user for an assessment"""
        return self.db.query(AssessmentAttempt).filter(
            and_(
                AssessmentAttempt.user_id == user_id,
                AssessmentAttempt.assessment_id == assessment_id
            )
        ).count()
    
    def get_next_attempt_number(self, user_id: int, assessment_id: int) -> int:
        """Get the next attempt number for a user and assessment"""
        max_attempt = self.db.query(func.max(AssessmentAttempt.attempt_number)).filter(
            and_(
                AssessmentAttempt.user_id == user_id,
                AssessmentAttempt.assessment_id == assessment_id
            )
        ).scalar()
        return (max_attempt or 0) + 1
    
    def start_attempt(self, user_id: int, assessment_id: int) -> AssessmentAttempt:
        """Start a new assessment attempt"""
        attempt_number = self.get_next_attempt_number(user_id, assessment_id)
        attempt_data = {
            "user_id": user_id,
            "assessment_id": assessment_id,
            "attempt_number": attempt_number,
            "status": AttemptStatus.STARTED,
            "started_at": datetime.utcnow()
        }
        return self.create(attempt_data)
    
    def submit_attempt(self, attempt_id: int) -> Optional[AssessmentAttempt]:
        """Submit an attempt"""
        attempt = self.get(attempt_id)
        if attempt and attempt.status in [AttemptStatus.STARTED, AttemptStatus.IN_PROGRESS]:
            submitted_at = datetime.utcnow()
            time_taken = int((submitted_at - attempt.started_at).total_seconds())
            return self.update(attempt_id, {
                "status": AttemptStatus.SUBMITTED,
                "submitted_at": submitted_at,
                "time_taken": time_taken
            })
        return None
    
    def expire_attempt(self, attempt_id: int) -> Optional[AssessmentAttempt]:
        """Mark an attempt as expired"""
        return self.update(attempt_id, {"status": AttemptStatus.EXPIRED})
    
    def grade_attempt(self, attempt_id: int, total_score: float, max_score: float) -> Optional[AssessmentAttempt]:
        """Grade an attempt"""
        return self.update(attempt_id, {
            "status": AttemptStatus.GRADED,
            "total_score": total_score,
            "max_score": max_score
        })