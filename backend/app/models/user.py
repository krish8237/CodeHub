from sqlalchemy import Column, String, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class UserRole(enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    created_assessments = relationship("Assessment", back_populates="creator", foreign_keys="Assessment.created_by")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"