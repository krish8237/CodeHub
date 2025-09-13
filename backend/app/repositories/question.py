from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.question import Question, QuestionType
from .base import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    """Repository for Question model with specific methods"""
    
    def __init__(self, db: Session):
        super().__init__(Question, db)
    
    def get_by_assessment(self, assessment_id: int, ordered: bool = True) -> List[Question]:
        """Get all questions for an assessment, optionally ordered"""
        query = self.db.query(Question).filter(Question.assessment_id == assessment_id)
        if ordered:
            query = query.order_by(Question.order)
        return query.all()
    
    def get_by_type(self, question_type: QuestionType, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get questions by type"""
        return self.db.query(Question).filter(
            Question.type == question_type
        ).offset(skip).limit(limit).all()
    
    def get_coding_questions(self, language: str = None, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get coding questions, optionally filtered by language"""
        query = self.db.query(Question).filter(Question.type == QuestionType.CODING)
        if language:
            query = query.filter(Question.language == language)
        return query.offset(skip).limit(limit).all()
    
    def get_mcq_questions(self, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get MCQ questions"""
        return self.db.query(Question).filter(
            Question.type == QuestionType.MCQ
        ).offset(skip).limit(limit).all()
    
    def get_descriptive_questions(self, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get descriptive questions"""
        return self.db.query(Question).filter(
            Question.type == QuestionType.DESCRIPTIVE
        ).offset(skip).limit(limit).all()
    
    def get_questions_by_assessment_and_type(self, assessment_id: int, question_type: QuestionType) -> List[Question]:
        """Get questions by assessment and type"""
        return self.db.query(Question).filter(
            and_(
                Question.assessment_id == assessment_id,
                Question.type == question_type
            )
        ).order_by(Question.order).all()
    
    def get_max_order_in_assessment(self, assessment_id: int) -> int:
        """Get the maximum order number in an assessment"""
        result = self.db.query(Question.order).filter(
            Question.assessment_id == assessment_id
        ).order_by(Question.order.desc()).first()
        return result[0] if result else 0
    
    def reorder_questions(self, assessment_id: int, question_orders: List[tuple]) -> bool:
        """Reorder questions in an assessment
        
        Args:
            assessment_id: The assessment ID
            question_orders: List of tuples (question_id, new_order)
        """
        try:
            for question_id, new_order in question_orders:
                self.db.query(Question).filter(
                    and_(
                        Question.id == question_id,
                        Question.assessment_id == assessment_id
                    )
                ).update({"order": new_order})
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def duplicate_question(self, question_id: int, new_assessment_id: int = None) -> Optional[Question]:
        """Duplicate a question, optionally to a different assessment"""
        original = self.get(question_id)
        if not original:
            return None
        
        # Create new question data
        question_data = {
            "assessment_id": new_assessment_id or original.assessment_id,
            "type": original.type,
            "title": f"Copy of {original.title}",
            "content": original.content,
            "points": original.points,
            "order": self.get_max_order_in_assessment(new_assessment_id or original.assessment_id) + 1,
            "language": original.language,
            "starter_code": original.starter_code,
            "solution_code": original.solution_code,
            "test_cases": original.test_cases,
            "options": original.options,
            "correct_answers": original.correct_answers,
            "metadata": original.metadata,
        }
        
        return self.create(question_data)