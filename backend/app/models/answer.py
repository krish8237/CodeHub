from sqlalchemy import Column, Integer, ForeignKey, Text, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Answer(BaseModel):
    __tablename__ = "answers"
    
    attempt_id = Column(Integer, ForeignKey("assessment_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    content = Column(Text, nullable=True)  # Answer content (code, text, selected options)
    score = Column(Float, nullable=True)  # Points awarded
    max_score = Column(Float, nullable=True)  # Maximum possible points
    is_correct = Column(Boolean, nullable=True)  # For MCQ questions
    feedback = Column(Text, nullable=True)  # Grading feedback
    submitted_at = Column(DateTime(timezone=True), nullable=False)
    
    # Coding question specific fields
    execution_result = Column(JSON, nullable=True)  # Code execution results
    test_results = Column(JSON, nullable=True)  # Test case results
    
    # Additional metadata
    answer_metadata = Column(JSON, nullable=True)  # Additional answer-specific data
    
    # Relationships
    attempt = relationship("AssessmentAttempt", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    
    def __repr__(self):
        return f"<Answer(id={self.id}, attempt_id={self.attempt_id}, question_id={self.question_id}, score={self.score})>"
    
    @property
    def score_percentage(self):
        if self.score is not None and self.max_score is not None and self.max_score > 0:
            return (self.score / self.max_score) * 100
        return None