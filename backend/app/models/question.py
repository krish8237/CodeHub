from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class QuestionType(enum.Enum):
    CODING = "coding"
    MCQ = "mcq"
    DESCRIPTIVE = "descriptive"


class Question(BaseModel):
    __tablename__ = "questions"
    
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    type = Column(Enum(QuestionType), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # Question text/description
    points = Column(Float, default=1.0, nullable=False)
    order = Column(Integer, nullable=False)  # Order within assessment
    
    # Coding question specific fields
    language = Column(String(50), nullable=True)  # Programming language
    starter_code = Column(Text, nullable=True)  # Initial code template
    solution_code = Column(Text, nullable=True)  # Reference solution
    test_cases = Column(JSON, nullable=True)  # Test cases for coding questions
    
    # MCQ specific fields
    options = Column(JSON, nullable=True)  # MCQ options
    correct_answers = Column(JSON, nullable=True)  # Correct answer indices
    
    # General metadata
    metadata = Column(JSON, nullable=True)  # Additional question-specific data
    
    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    answers = relationship("Answer", back_populates="question")
    
    def __repr__(self):
        return f"<Question(id={self.id}, type='{self.type.value}', title='{self.title}')>"