from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.assessment import AssessmentService
from app.schemas.assessment import (
    Assessment, AssessmentCreate, AssessmentUpdate, AssessmentWithQuestions,
    AssessmentListResponse, Question, QuestionCreate, QuestionUpdate, QuestionListResponse,
    AssessmentAttempt, AssessmentAttemptCreate, AssessmentAttemptUpdate, AssessmentAttemptListResponse
)

router = APIRouter()


# Assessment endpoints
@router.post("/", response_model=Assessment, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_data: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new assessment"""
    service = AssessmentService(db)
    return service.create_assessment(assessment_data, current_user.id)


@router.get("/", response_model=AssessmentListResponse)
async def list_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List assessments based on user role and permissions"""
    service = AssessmentService(db)
    
    if search:
        assessments, total = service.search_assessments(search, current_user.id, current_user.role, skip, limit)
    else:
        assessments, total = service.list_assessments(current_user.id, current_user.role, skip, limit)
    
    return AssessmentListResponse(
        assessments=assessments,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/available", response_model=AssessmentListResponse)
async def list_available_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List assessments available for taking"""
    service = AssessmentService(db)
    assessments, total = service.get_available_assessments(skip, limit)
    
    return AssessmentListResponse(
        assessments=assessments,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{assessment_id}", response_model=Assessment)
async def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assessment by ID"""
    service = AssessmentService(db)
    assessment = service.get_assessment(assessment_id, current_user.id, current_user.role)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    return assessment


@router.get("/{assessment_id}/with-questions", response_model=AssessmentWithQuestions)
async def get_assessment_with_questions(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assessment with all questions"""
    service = AssessmentService(db)
    assessment = service.get_assessment_with_questions(assessment_id, current_user.id, current_user.role)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    return assessment


@router.put("/{assessment_id}", response_model=Assessment)
async def update_assessment(
    assessment_id: int,
    assessment_data: AssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update assessment"""
    service = AssessmentService(db)
    assessment = service.update_assessment(assessment_id, assessment_data, current_user.id, current_user.role)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    return assessment


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete assessment"""
    service = AssessmentService(db)
    success = service.delete_assessment(assessment_id, current_user.id, current_user.role)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )


# Question endpoints
@router.post("/{assessment_id}/questions", response_model=Question, status_code=status.HTTP_201_CREATED)
async def create_question(
    assessment_id: int,
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new question for an assessment"""
    # Ensure the assessment_id in the URL matches the one in the data
    question_data.assessment_id = assessment_id
    
    service = AssessmentService(db)
    return service.create_question(question_data, current_user.id, current_user.role)


@router.get("/{assessment_id}/questions", response_model=QuestionListResponse)
async def list_questions(
    assessment_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List questions for an assessment"""
    service = AssessmentService(db)
    questions, total = service.list_questions(assessment_id, current_user.id, current_user.role, skip, limit)
    
    return QuestionListResponse(
        questions=questions,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{assessment_id}/questions/{question_id}", response_model=Question)
async def get_question(
    assessment_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get question by ID"""
    service = AssessmentService(db)
    question = service.get_question(question_id, current_user.id, current_user.role)
    
    if not question or question.assessment_id != assessment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question


@router.put("/{assessment_id}/questions/{question_id}", response_model=Question)
async def update_question(
    assessment_id: int,
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update question"""
    service = AssessmentService(db)
    question = service.update_question(question_id, question_data, current_user.id, current_user.role)
    
    if not question or question.assessment_id != assessment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question


@router.delete("/{assessment_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    assessment_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete question"""
    service = AssessmentService(db)
    success = service.delete_question(question_id, current_user.id, current_user.role)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )


# Assessment attempt endpoints
@router.post("/{assessment_id}/attempts", response_model=AssessmentAttempt, status_code=status.HTTP_201_CREATED)
async def start_assessment_attempt(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new assessment attempt"""
    attempt_data = AssessmentAttemptCreate(assessment_id=assessment_id)
    service = AssessmentService(db)
    return service.start_assessment_attempt(attempt_data, current_user.id)


@router.get("/{assessment_id}/attempts", response_model=AssessmentAttemptListResponse)
async def list_assessment_attempts(
    assessment_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List attempts for an assessment"""
    service = AssessmentService(db)
    attempts, total = service.list_assessment_attempts(assessment_id, current_user.id, current_user.role, skip, limit)
    
    return AssessmentAttemptListResponse(
        attempts=attempts,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{assessment_id}/attempts/{attempt_id}", response_model=AssessmentAttempt)
async def get_assessment_attempt(
    assessment_id: int,
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assessment attempt by ID"""
    service = AssessmentService(db)
    attempt = service.get_assessment_attempt(attempt_id, current_user.id, current_user.role)
    
    if not attempt or attempt.assessment_id != assessment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment attempt not found"
        )
    
    return attempt


@router.put("/{assessment_id}/attempts/{attempt_id}", response_model=AssessmentAttempt)
async def update_assessment_attempt(
    assessment_id: int,
    attempt_id: int,
    attempt_data: AssessmentAttemptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update assessment attempt"""
    service = AssessmentService(db)
    attempt = service.update_assessment_attempt(attempt_id, attempt_data, current_user.id, current_user.role)
    
    if not attempt or attempt.assessment_id != assessment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment attempt not found"
        )
    
    return attempt


# User attempts endpoint
@router.get("/attempts/user/{user_id}", response_model=AssessmentAttemptListResponse)
async def get_user_attempts(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all attempts by a specific user"""
    service = AssessmentService(db)
    attempts, total = service.get_user_attempts(user_id, current_user.id, current_user.role, skip, limit)
    
    return AssessmentAttemptListResponse(
        attempts=attempts,
        total=total,
        skip=skip,
        limit=limit
    )