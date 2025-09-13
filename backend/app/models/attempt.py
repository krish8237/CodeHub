from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Float, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class AttemptStatus(enum.Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"
    EXPIRED = "expired"


class AssessmentAttempt(BaseModel):
    __tablename__ = "assessment_attempts"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)  # Which attempt (1, 2, 3, etc.)
    status = Column(Enum(AttemptStatus), default=AttemptStatus.STARTED, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    time_taken = Column(Integer, nullable=True)  # in seconds
    total_score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    attempt_metadata = Column(JSON, nullable=True)  # Additional attempt data
    
    # Relationships
    user = relationship("User", back_populates="assessment_attempts")
    assessment = relationship("Assessment", back_populates="attempts")
    answers = relationship("Answer", back_populates="attempt", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AssessmentAttempt(id={self.id}, user_id={self.user_id}, assessment_id={self.assessment_id}, status='{self.status.value}')>"
    
    @property
    def score_percentage(self):
        if self.total_score is not None and self.max_score is not None and self.max_score > 0:
            return (self.total_score / self.max_score) * 100
        return None