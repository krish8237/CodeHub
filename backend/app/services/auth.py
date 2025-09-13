from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    generate_password_reset_token,
    generate_email_verification_token,
    validate_password_strength
)
from app.schemas.auth import UserCreate, UserLogin, Token
from app.services.email import EmailService
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.email_service = EmailService()
    
    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user with email verification"""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        if not validate_password_strength(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with uppercase, lowercase, and digit"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            is_active=True,
            is_verified=False
        )
        
        created_user = await self.user_repo.create(user)
        
        # Send verification email
        await self._send_verification_email(created_user)
        
        logger.info("User registered", user_id=created_user.id, email=created_user.email)
        return created_user
    
    async def authenticate_user(self, credentials: UserLogin) -> Token:
        """Authenticate user and return tokens"""
        user = await self.user_repo.get_by_email(credentials.email)
        
        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.user_repo.update(user)
        
        # Create tokens
        access_token = create_access_token(
            subject=user.email,
            user_id=user.id,
            role=user.role.value
        )
        
        refresh_token = create_refresh_token(
            subject=user.email,
            user_id=user.id
        )
        
        logger.info("User authenticated", user_id=user.id, email=user.email)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        payload = verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token = create_access_token(
            subject=user.email,
            user_id=user.id,
            role=user.role.value
        )
        
        new_refresh_token = create_refresh_token(
            subject=user.email,
            user_id=user.id
        )
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        # In a real implementation, you'd store verification tokens in database
        # For now, we'll use a simple JWT-based approach
        payload = verify_token(token)
        
        if not payload or payload.get("type") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload"
            )
        
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        user.is_verified = True
        await self.user_repo.update(user)
        
        logger.info("Email verified", user_id=user.id, email=user.email)
        return True
    
    async def request_password_reset(self, email: str) -> bool:
        """Request password reset for user"""
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            # Don't reveal if email exists or not
            return True
        
        # Send password reset email
        await self._send_password_reset_email(user)
        
        logger.info("Password reset requested", user_id=user.id, email=user.email)
        return True
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password with token"""
        if not validate_password_strength(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with uppercase, lowercase, and digit"
            )
        
        payload = verify_token(token)
        
        if not payload or payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload"
            )
        
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        await self.user_repo.update(user)
        
        logger.info("Password reset completed", user_id=user.id, email=user.email)
        return True
    
    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        if not validate_password_strength(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with uppercase, lowercase, and digit"
            )
        
        user.password_hash = get_password_hash(new_password)
        await self.user_repo.update(user)
        
        logger.info("Password changed", user_id=user.id, email=user.email)
        return True
    
    async def _send_verification_email(self, user: User):
        """Send email verification email"""
        # Create verification token
        token_payload = {
            "user_id": user.id,
            "type": "email_verification",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        from jose import jwt
        token = jwt.encode(token_payload, settings.secret_key, algorithm=settings.algorithm)
        
        # Send email
        await self.email_service.send_verification_email(user.email, user.first_name, token)
    
    async def _send_password_reset_email(self, user: User):
        """Send password reset email"""
        # Create reset token
        token_payload = {
            "user_id": user.id,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        from jose import jwt
        token = jwt.encode(token_payload, settings.secret_key, algorithm=settings.algorithm)
        
        # Send email
        await self.email_service.send_password_reset_email(user.email, user.first_name, token)