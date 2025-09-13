from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime
from app.models.assessment import Assessment
from app.models.user import User
from .base import BaseRepository


class AssessmentRepository(BaseRepository[Assessment]):
    """Repository for Assessment model with specific methods"""
    
    def __init__(self, db: Session):
        super().__init__(Assessment, db)
    
    def get_with_questions(self, assessment_id: int) -> Optional[Assessment]:
        """Get assessment with all questions loaded"""
        return self.db.query(Assessment).options(
            joinedload(Assessment.questions)
        ).filter(Assessment.id == assessment_id).first()
    
    def get_by_creator(self, creator_id: int, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get assessments created by a specific user"""
        return self.db.query(Assessment).filter(
            Assessment.created_by == creator_id
        ).offset(skip).limit(limit).all()
    
    def get_active_assessments(self, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get active assessments"""
        return self.db.query(Assessment).filter(
            Assessment.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_available_assessments(self, current_time: datetime = None, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get assessments that are currently available for taking"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.db.query(Assessment).filter(
            and_(
                Assessment.is_active == True,
                or_(
                    Assessment.start_time.is_(None),
                    Assessment.start_time <= current_time
                ),
                or_(
                    Assessment.end_time.is_(None),
                    Assessment.end_time >= current_time
                )
            )
        ).offset(skip).limit(limit).all()
    
    def get_upcoming_assessments(self, current_time: datetime = None, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get assessments that will be available in the future"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.db.query(Assessment).filter(
            and_(
                Assessment.is_active == True,
                Assessment.start_time > current_time
            )
        ).offset(skip).limit(limit).all()
    
    def get_expired_assessments(self, current_time: datetime = None, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get assessments that have expired"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        return self.db.query(Assessment).filter(
            and_(
                Assessment.is_active == True,
                Assessment.end_time < current_time
            )
        ).offset(skip).limit(limit).all()
    
    def search_assessments(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Search assessments by title or description"""
        search_pattern = f"%{search_term}%"
        return self.db.query(Assessment).filter(
            or_(
                Assessment.title.ilike(search_pattern),
                Assessment.description.ilike(search_pattern)
            )
        ).offset(skip).limit(limit).all()
    
    def get_assessments_with_attempts(self, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get assessments with attempt information loaded"""
        return self.db.query(Assessment).options(
            joinedload(Assessment.attempts)
        ).offset(skip).limit(limit).all()
    
    def activate_assessment(self, assessment_id: int) -> Optional[Assessment]:
        """Activate an assessment"""
        return self.update(assessment_id, {"is_active": True})
    
    def deactivate_assessment(self, assessment_id: int) -> Optional[Assessment]:
        """Deactivate an assessment"""
        return self.update(assessment_id, {"is_active": False})