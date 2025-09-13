from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model with specific methods"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        return self.db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users"""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    async def get_verified_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get verified users"""
        return self.db.query(User).filter(User.is_verified == True).offset(skip).limit(limit).all()
    
    async def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by name or email"""
        search_pattern = f"%{search_term}%"
        return self.db.query(User).filter(
            (User.email.ilike(search_pattern)) |
            (User.first_name.ilike(search_pattern)) |
            (User.last_name.ilike(search_pattern))
        ).offset(skip).limit(limit).all()
    
    async def activate_user(self, user_id: int) -> Optional[User]:
        """Activate a user account"""
        user = await self.get_by_id(user_id)
        if user:
            user.is_active = True
            return await self.update(user)
        return None
    
    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user account"""
        user = await self.get_by_id(user_id)
        if user:
            user.is_active = False
            return await self.update(user)
        return None
    
    async def verify_user(self, user_id: int) -> Optional[User]:
        """Verify a user account"""
        user = await self.get_by_id(user_id)
        if user:
            user.is_verified = True
            return await self.update(user)
        return None
    
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.db.query(User).filter(User.email == email).first() is not None