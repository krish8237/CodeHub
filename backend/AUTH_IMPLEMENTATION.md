# Authentication and Authorization System Implementation

## Overview

This document describes the complete implementation of the authentication and authorization system for the Online Assessment Platform, as specified in task 3 of the implementation plan.

## Implemented Components

### 1. JWT Token Generation and Validation Utilities

**File:** `app/core/security.py`

**Features:**
- JWT access token creation with configurable expiration
- JWT refresh token creation for token renewal
- Token verification and payload extraction
- Password hashing using bcrypt
- Password strength validation
- Secure token generation for email verification and password reset

**Key Functions:**
- `create_access_token()` - Creates JWT access tokens
- `create_refresh_token()` - Creates JWT refresh tokens
- `verify_token()` - Verifies and decodes JWT tokens
- `get_password_hash()` - Hashes passwords securely
- `verify_password()` - Verifies passwords against hashes
- `validate_password_strength()` - Validates password complexity

### 2. User Registration with Email Verification

**Files:** 
- `app/api/auth.py` - Registration endpoint
- `app/services/auth.py` - Registration business logic
- `app/services/email.py` - Email sending service

**Features:**
- User registration with input validation
- Automatic email verification token generation
- Email verification endpoint
- Duplicate email prevention
- Password strength enforcement

**Endpoints:**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/verify-email` - Verify email address
- `POST /api/v1/auth/resend-verification` - Resend verification email

### 3. Login/Logout Endpoints with Secure Session Management

**Files:**
- `app/api/auth.py` - Authentication endpoints
- `app/services/auth.py` - Authentication business logic

**Features:**
- Secure login with email/password
- JWT token-based session management
- Token refresh mechanism
- Account status validation (active/inactive)
- Last login tracking
- Secure logout (client-side token disposal)

**Endpoints:**
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user info

### 4. Role-Based Access Control Middleware

**File:** `app/core/deps.py`

**Features:**
- Role-based access control dependencies
- User verification status checking
- Flexible role combinations
- Optional authentication support

**Dependencies:**
- `get_current_user()` - Get authenticated user
- `get_current_verified_user()` - Get verified user
- `get_current_admin()` - Admin-only access
- `get_current_instructor()` - Instructor-only access
- `get_current_student()` - Student-only access
- `get_instructor_or_admin()` - Multiple role access
- `get_optional_user()` - Optional authentication

### 5. Password Reset Functionality with Email Notifications

**Files:**
- `app/api/auth.py` - Password reset endpoints
- `app/services/auth.py` - Password reset logic
- `app/services/email.py` - Email notifications

**Features:**
- Secure password reset token generation
- Email-based password reset flow
- Password change for authenticated users
- Security-conscious error handling (no email enumeration)

**Endpoints:**
- `POST /api/v1/auth/password-reset` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Confirm password reset
- `POST /api/v1/auth/change-password` - Change password (authenticated)

### 6. Comprehensive Test Coverage

**Files:**
- `tests/test_auth.py` - Authentication endpoint tests
- `tests/test_auth_rbac.py` - Role-based access control tests
- `tests/conftest.py` - Test fixtures and configuration

**Test Coverage:**
- User registration (success, duplicate email, weak password)
- User authentication (success, invalid credentials, inactive user)
- Token operations (refresh, invalid tokens)
- Email verification flow
- Password reset flow
- Role-based access control
- Security utilities
- Error handling

## Database Schema

### User Model Extensions

The authentication system uses the existing User model with the following fields:

```python
class User(BaseModel):
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
```

## Configuration

### Environment Variables

The following configuration options are available in `app/core/config.py`:

```python
# JWT Configuration
secret_key: str = "your-secret-key-here-change-in-production"
algorithm: str = "HS256"
access_token_expire_minutes: int = 30
refresh_token_expire_days: int = 7

# Email Configuration
mail_username: Optional[str] = None
mail_password: Optional[str] = None
mail_from: Optional[str] = None
mail_port: int = 587
mail_server: Optional[str] = None
mail_from_name: str = "Assessment Platform"

# Frontend URL for email links
frontend_url: str = "http://localhost:3000"
```

## Security Features

### Password Security
- Bcrypt hashing with automatic salt generation
- Password strength validation (minimum 8 characters, uppercase, lowercase, digit)
- Secure password reset tokens with expiration

### Token Security
- JWT tokens with configurable expiration
- Separate access and refresh tokens
- Token type validation
- Secure token generation for email operations

### Access Control
- Role-based permissions (Student, Instructor, Admin)
- Email verification requirement for sensitive operations
- Account status validation (active/inactive)
- Flexible role combination support

### Email Security
- Secure token-based email verification
- Time-limited password reset tokens
- No email enumeration in password reset
- HTML email templates with security considerations

## API Documentation

### Authentication Endpoints

All authentication endpoints are prefixed with `/api/v1/auth/`:

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | No |
| POST | `/login` | User login | No |
| POST | `/refresh` | Refresh access token | No |
| POST | `/verify-email` | Verify email address | No |
| POST | `/resend-verification` | Resend verification email | Yes |
| POST | `/password-reset` | Request password reset | No |
| POST | `/password-reset/confirm` | Confirm password reset | No |
| POST | `/change-password` | Change password | Yes (Verified) |
| GET | `/me` | Get current user info | Yes |
| POST | `/logout` | User logout | Yes |
| GET | `/protected` | Example protected route | Yes (Verified) |

### Request/Response Examples

#### User Registration
```json
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}

Response (201):
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### User Login
```json
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Error Handling

The authentication system implements comprehensive error handling:

- **400 Bad Request**: Invalid input data, weak passwords, business rule violations
- **401 Unauthorized**: Invalid credentials, expired tokens, unverified email
- **403 Forbidden**: Insufficient permissions, role-based access denied
- **404 Not Found**: User not found (in specific contexts)
- **422 Unprocessable Entity**: Validation errors

## Testing

### Running Tests

```bash
# Run all authentication tests
python -m pytest backend/tests/test_auth.py -v

# Run role-based access control tests
python -m pytest backend/tests/test_auth_rbac.py -v

# Run validation script
python backend/validate_auth.py
```

### Test Coverage

The test suite covers:
- All authentication endpoints
- Role-based access control scenarios
- Security utility functions
- Error conditions and edge cases
- Token operations and validation
- Email verification flows
- Password reset functionality

## Integration with Main Application

The authentication system is integrated into the main FastAPI application in `app/main.py`:

```python
from app.api.auth import router as auth_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
```

## Requirements Compliance

This implementation satisfies all requirements from the specification:

- **Requirement 6.1**: ✅ Email verification and strong password criteria
- **Requirement 6.2**: ✅ Secure session establishment and authentication
- **Requirement 6.3**: ✅ Role-based permissions enforcement
- **Requirement 6.4**: ✅ Authorization verification and security measures
- **Additional**: ✅ Comprehensive testing and documentation

## Next Steps

The authentication system is now ready for integration with other platform components:

1. Assessment management endpoints can use role-based dependencies
2. Code execution service can verify user permissions
3. Analytics service can implement user-specific data access
4. Frontend can integrate with authentication endpoints

## Maintenance and Security

### Regular Security Tasks
- Rotate JWT secret keys periodically
- Monitor for suspicious authentication patterns
- Update password strength requirements as needed
- Review and update email templates
- Audit role assignments and permissions

### Performance Considerations
- Token verification is stateless and fast
- Password hashing is intentionally slow for security
- Email sending is asynchronous where possible
- Database queries are optimized with proper indexing