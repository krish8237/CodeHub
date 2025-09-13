from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.question import QuestionType
from app.models.attempt import AttemptStatus


# Assessment Schemas
class AssessmentSettings(BaseModel):
    """Assessment configuration settings"""
    allow_backtrack: bool = True
    shuffle_questions: bool = False
    show_results_immediately: bool = False
    require_webcam: bool = False
    browser_lockdown: bool = False
    plagiarism_detection: bool = False
    auto_submit: bool = True


class AssessmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    time_limit: Optional[int] = Field(None, ge=1)  # in minutes
    max_attempts: int = Field(1, ge=1, le=10)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: bool = True
    settings: Optional[AssessmentSettings] = None

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('End time must be after start time')
        return v


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    time_limit: Optional[int] = Field(None, ge=1)
    max_attempts: Optional[int] = Field(None, ge=1, le=10)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None
    settings: Optional[AssessmentSettings] = None

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('End time must be after start time')
        return v


class AssessmentInDB(AssessmentBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Assessment(AssessmentInDB):
    questions_count: Optional[int] = None
    attempts_count: Optional[int] = None


class AssessmentWithQuestions(AssessmentInDB):
    questions: List['Question'] = []


class AssessmentWithAttempts(AssessmentInDB):
    attempts: List['AssessmentAttempt'] = []


# Question Schemas
class TestCase(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False
    weight: float = Field(1.0, ge=0.1, le=10.0)


class MCQOption(BaseModel):
    text: str
    is_correct: bool = False


class QuestionBase(BaseModel):
    type: QuestionType
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    points: float = Field(1.0, ge=0.1, le=100.0)
    order: int = Field(..., ge=1)
    
    # Coding question fields
    language: Optional[str] = None
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    test_cases: Optional[List[TestCase]] = None
    
    # MCQ fields
    options: Optional[List[MCQOption]] = None
    
    # General metadata
    question_metadata: Optional[Dict[str, Any]] = None

    @validator('language')
    def validate_language(cls, v, values):
        if values.get('type') == QuestionType.CODING and not v:
            raise ValueError('Language is required for coding questions')
        return v

    @validator('test_cases')
    def validate_test_cases(cls, v, values):
        if values.get('type') == QuestionType.CODING and (not v or len(v) == 0):
            raise ValueError('At least one test case is required for coding questions')
        return v

    @validator('options')
    def validate_options(cls, v, values):
        if values.get('type') == QuestionType.MCQ:
            if not v or len(v) < 2:
                raise ValueError('At least 2 options are required for MCQ questions')
            correct_count = sum(1 for opt in v if opt.is_correct)
            if correct_count == 0:
                raise ValueError('At least one correct option is required for MCQ questions')
        return v


class QuestionCreate(QuestionBase):
    assessment_id: int


class QuestionUpdate(BaseModel):
    type: Optional[QuestionType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    points: Optional[float] = Field(None, ge=0.1, le=100.0)
    order: Optional[int] = Field(None, ge=1)
    language: Optional[str] = None
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    test_cases: Optional[List[TestCase]] = None
    options: Optional[List[MCQOption]] = None
    question_metadata: Optional[Dict[str, Any]] = None


class QuestionInDB(QuestionBase):
    id: int
    assessment_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Question(QuestionInDB):
    pass


# Assessment Attempt Schemas
class AssessmentAttemptBase(BaseModel):
    attempt_number: int = Field(..., ge=1)
    status: AttemptStatus = AttemptStatus.STARTED
    started_at: datetime
    submitted_at: Optional[datetime] = None
    time_taken: Optional[int] = None  # in seconds
    total_score: Optional[float] = None
    max_score: Optional[float] = None
    attempt_metadata: Optional[Dict[str, Any]] = None


class AssessmentAttemptCreate(BaseModel):
    assessment_id: int


class AssessmentAttemptUpdate(BaseModel):
    status: Optional[AttemptStatus] = None
    submitted_at: Optional[datetime] = None
    time_taken: Optional[int] = None
    total_score: Optional[float] = None
    max_score: Optional[float] = None
    attempt_metadata: Optional[Dict[str, Any]] = None


class AssessmentAttemptInDB(AssessmentAttemptBase):
    id: int
    user_id: int
    assessment_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssessmentAttempt(AssessmentAttemptInDB):
    score_percentage: Optional[float] = None


class AssessmentAttemptWithAnswers(AssessmentAttemptInDB):
    answers: List['Answer'] = []


# Response schemas for lists
class AssessmentListResponse(BaseModel):
    assessments: List[Assessment]
    total: int
    skip: int
    limit: int


class QuestionListResponse(BaseModel):
    questions: List[Question]
    total: int
    skip: int
    limit: int


class AssessmentAttemptListResponse(BaseModel):
    attempts: List[AssessmentAttempt]
    total: int
    skip: int
    limit: int


# Import Answer schema
from .answer import Answer

# Forward references
AssessmentWithQuestions.model_rebuild()
AssessmentWithAttempts.model_rebuild()
AssessmentAttemptWithAnswers.model_rebuild()