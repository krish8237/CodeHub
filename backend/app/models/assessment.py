from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Assessment(BaseModel):
    __tablename__ = "assessments"
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    time_limit = Column(Integer, nullable=True)  # in minutes
    max_attempts = Column(Integer, default=1, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    settings = Column(JSON, nullable=True)  # Additional assessment settings
    
    # Relationships
    creator = relationship("User", back_populates="created_assessments", foreign_keys=[created_by])
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    attempts = relationship("AssessmentAttempt", back_populates="assessment")
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, title='{self.title}', created_by={self.created_by})>"