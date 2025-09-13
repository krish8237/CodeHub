from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_verified_user
from app.schemas.auth import (
    UserCreate, 
    UserResponse, 
    UserLogin, 
    Token, 
    RefreshToken,
    PasswordReset,
    PasswordResetConfirm,
    EmailVerification,
    ChangePassword
)
from app.services.auth import AuthService
from app.services.email import EmailService
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    auth_service = AuthService(db)
    token = await auth_service.authenticate_user(credentials)
    return token


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    auth_service = AuthService(db)
    token = await auth_service.refresh_access_token(refresh_data.refresh_token)
    return token


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
):
    """Verify user email address"""
    auth_service = AuthService(db)
    success = await auth_service.verify_email(verification_data.token)
    
    if success:
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification failed"
        )


@router.post("/resend-verification")
async def resend_verification(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resend email verification"""
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    auth_service = AuthService(db)
    await auth_service._send_verification_email(current_user)
    
    return {"message": "Verification email sent"}


@router.post("/password-reset")
async def request_password_reset(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    auth_service = AuthService(db)
    await auth_service.request_password_reset(reset_data.email)
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token"""
    auth_service = AuthService(db)
    success = await auth_service.reset_password(reset_data.token, reset_data.new_password)
    
    if success:
        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset failed"
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    auth_service = AuthService(db)
    success = await auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    
    if success:
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password change failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout():
    """Logout user (client should discard tokens)"""
    return {"message": "Logged out successfully"}


@router.get("/protected")
async def protected_route(
    current_user = Depends(get_current_verified_user)
):
    """Example protected route"""
    return {
        "message": f"Hello {current_user.full_name}!",
        "user_id": current_user.id,
        "role": current_user.role.value
    }