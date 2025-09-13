from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AnswerBase(BaseModel):
    content: Optional[str] = None
    score: Optional[float] = Field(None, ge=0)
    max_score: Optional[float] = Field(None, ge=0)
    is_correct: Optional[bool] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    execution_result: Optional[Dict[str, Any]] = None
    test_results: Optional[Dict[str, Any]] = None
    answer_metadata: Optional[Dict[str, Any]] = None


class AnswerCreate(BaseModel):
    attempt_id: int
    question_id: int
    content: Optional[str] = None
    submitted_at: Optional[datetime] = None


class AnswerUpdate(BaseModel):
    content: Optional[str] = None
    score: Optional[float] = Field(None, ge=0)
    max_score: Optional[float] = Field(None, ge=0)
    is_correct: Optional[bool] = None
    feedback: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    test_results: Optional[Dict[str, Any]] = None
    answer_metadata: Optional[Dict[str, Any]] = None


class AnswerInDB(AnswerBase):
    id: int
    attempt_id: int
    question_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Answer(AnswerInDB):
    score_percentage: Optional[float] = None