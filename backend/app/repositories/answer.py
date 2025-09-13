from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app.models.answer import Answer
from .base import BaseRepository


class AnswerRepository(BaseRepository[Answer]):
    """Repository for Answer model with specific methods"""
    
    def __init__(self, db: Session):
        super().__init__(Answer, db)
    
    def get_by_attempt(self, attempt_id: int) -> List[Answer]:
        """Get all answers for an attempt"""
        return self.db.query(Answer).filter(
            Answer.attempt_id == attempt_id
        ).all()
    
    def get_by_question(self, question_id: int, skip: int = 0, limit: int = 100) -> List[Answer]:
        """Get all answers for a question"""
        return self.db.query(Answer).filter(
            Answer.question_id == question_id
        ).offset(skip).limit(limit).all()
    
    def get_by_attempt_and_question(self, attempt_id: int, question_id: int) -> Optional[Answer]:
        """Get answer for a specific attempt and question"""
        return self.db.query(Answer).filter(
            and_(
                Answer.attempt_id == attempt_id,
                Answer.question_id == question_id
            )
        ).first()
    
    def get_correct_answers(self, skip: int = 0, limit: int = 100) -> List[Answer]:
        """Get all correct answers"""
        return self.db.query(Answer).filter(
            Answer.is_correct == True
        ).offset(skip).limit(limit).all()
    
    def get_incorrect_answers(self, skip: int = 0, limit: int = 100) -> List[Answer]:
        """Get all incorrect answers"""
        return self.db.query(Answer).filter(
            Answer.is_correct == False
        ).offset(skip).limit(limit).all()
    
    def get_graded_answers(self, skip: int = 0, limit: int = 100) -> List[Answer]:
        """Get answers that have been graded"""
        return self.db.query(Answer).filter(
            Answer.score.isnot(None)
        ).offset(skip).limit(limit).all()
    
    def get_ungraded_answers(self, skip: int = 0, limit: int = 100) -> List[Answer]:
        """Get answers that haven't been graded"""
        return self.db.query(Answer).filter(
            Answer.score.is_(None)
        ).offset(skip).limit(limit).all()
    
    def save_answer(self, attempt_id: int, question_id: int, content: str, metadata: dict = None) -> Answer:
        """Save or update an answer"""
        existing_answer = self.get_by_attempt_and_question(attempt_id, question_id)
        
        answer_data = {
            "content": content,
            "submitted_at": datetime.utcnow(),
            "metadata": metadata
        }
        
        if existing_answer:
            return self.update(existing_answer.id, answer_data)
        else:
            answer_data.update({
                "attempt_id": attempt_id,
                "question_id": question_id
            })
            return self.create(answer_data)
    
    def grade_answer(self, answer_id: int, score: float, max_score: float, is_correct: bool = None, feedback: str = None) -> Optional[Answer]:
        """Grade an answer"""
        grade_data = {
            "score": score,
            "max_score": max_score,
            "feedback": feedback
        }
        if is_correct is not None:
            grade_data["is_correct"] = is_correct
        
        return self.update(answer_id, grade_data)
    
    def save_execution_result(self, answer_id: int, execution_result: dict, test_results: dict = None) -> Optional[Answer]:
        """Save code execution results"""
        return self.update(answer_id, {
            "execution_result": execution_result,
            "test_results": test_results
        })
    
    def get_answers_for_grading(self, assessment_id: int = None, skip: int = 0, limit: int = 100) -> List[Answer]:
        """Get answers that need grading, optionally filtered by assessment"""
        query = self.db.query(Answer).filter(Answer.score.is_(None))
        
        if assessment_id:
            query = query.join(Answer.attempt).filter(
                Answer.attempt.has(assessment_id=assessment_id)
            )
        
        return query.offset(skip).limit(limit).all()
    
    def bulk_grade_answers(self, answer_grades: List[dict]) -> bool:
        """Bulk grade multiple answers
        
        Args:
            answer_grades: List of dicts with keys: answer_id, score, max_score, is_correct, feedback
        """
        try:
            for grade_data in answer_grades:
                answer_id = grade_data.pop("answer_id")
                self.update(answer_id, grade_data)
            return True
        except Exception:
            self.db.rollback()
            return False