from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model with specific methods"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        return self.db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users"""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def get_verified_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get verified users"""
        return self.db.query(User).filter(User.is_verified == True).offset(skip).limit(limit).all()
    
    def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by name or email"""
        search_pattern = f"%{search_term}%"
        return self.db.query(User).filter(
            (User.email.ilike(search_pattern)) |
            (User.first_name.ilike(search_pattern)) |
            (User.last_name.ilike(search_pattern))
        ).offset(skip).limit(limit).all()
    
    def activate_user(self, user_id: int) -> Optional[User]:
        """Activate a user account"""
        return self.update(user_id, {"is_active": True})
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user account"""
        return self.update(user_id, {"is_active": False})
    
    def verify_user(self, user_id: int) -> Optional[User]:
        """Verify a user account"""
        return self.update(user_id, {"is_verified": True})
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.db.query(User).filter(User.email == email).first() is not None