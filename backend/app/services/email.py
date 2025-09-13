from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class EmailService:
    def __init__(self):
        if settings.mail_server and settings.mail_username:
            self.conf = ConnectionConfig(
                MAIL_USERNAME=settings.mail_username,
                MAIL_PASSWORD=settings.mail_password,
                MAIL_FROM=settings.mail_from or settings.mail_username,
                MAIL_PORT=settings.mail_port,
                MAIL_SERVER=settings.mail_server,
                MAIL_FROM_NAME=settings.mail_from_name,
                MAIL_STARTTLS=True,
                MAIL_SSL_TLS=False,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True
            )
            self.fastmail = FastMail(self.conf)
        else:
            self.fastmail = None
            logger.warning("Email configuration not found, emails will not be sent")
    
    async def send_verification_email(self, email: str, name: str, token: str):
        """Send email verification email"""
        if not self.fastmail:
            logger.info("Email verification would be sent", email=email, token=token)
            return
        
        verification_url = f"{settings.frontend_url}/verify-email?token={token}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Assessment Platform!</h2>
            <p>Hi {name},</p>
            <p>Thank you for registering with our platform. Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}">Verify Email Address</a></p>
            <p>If you didn't create an account, please ignore this email.</p>
            <p>This link will expire in 24 hours.</p>
            <br>
            <p>Best regards,<br>Assessment Platform Team</p>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Verify Your Email Address",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
        
        try:
            await self.fastmail.send_message(message)
            logger.info("Verification email sent", email=email)
        except Exception as e:
            logger.error("Failed to send verification email", email=email, error=str(e))
    
    async def send_password_reset_email(self, email: str, name: str, token: str):
        """Send password reset email"""
        if not self.fastmail:
            logger.info("Password reset email would be sent", email=email, token=token)
            return
        
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {name},</p>
            <p>You requested to reset your password. Please click the link below to set a new password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>This link will expire in 1 hour.</p>
            <br>
            <p>Best regards,<br>Assessment Platform Team</p>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
        
        try:
            await self.fastmail.send_message(message)
            logger.info("Password reset email sent", email=email)
        except Exception as e:
            logger.error("Failed to send password reset email", email=email, error=str(e))
    
    async def send_welcome_email(self, email: str, name: str):
        """Send welcome email after email verification"""
        if not self.fastmail:
            logger.info("Welcome email would be sent", email=email)
            return
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Assessment Platform!</h2>
            <p>Hi {name},</p>
            <p>Your email has been verified successfully. You can now access all features of our platform.</p>
            <p><a href="{settings.frontend_url}/login">Login to Your Account</a></p>
            <br>
            <p>Best regards,<br>Assessment Platform Team</p>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Welcome to Assessment Platform",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
        
        try:
            await self.fastmail.send_message(message)
            logger.info("Welcome email sent", email=email)
        except Exception as e:
            logger.error("Failed to send welcome email", email=email, error=str(e))