import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.auth import AuthService
from app.schemas.auth import UserCreate, UserLogin
from tests.conftest import TestingSessionLocal, override_get_db

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_user_success(self, db: Session):
        """Test successful user registration"""
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123",
            "first_name": "Test",
            "last_name": "User",
            "role": "student"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert data["role"] == user_data["role"]
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert "id" in data
    
    def test_register_user_duplicate_email(self, db: Session):
        """Test registration with duplicate email"""
        # Create first user
        user_data = {
            "email": "duplicate@example.com",
            "password": "TestPass123",
            "first_name": "First",
            "last_name": "User",
            "role": "student"
        }
        
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Try to create second user with same email
        user_data["first_name"] = "Second"
        response2 = client.post("/api/v1/auth/register", json=user_data)
        
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]
    
    def test_register_user_weak_password(self, db: Session):
        """Test registration with weak password"""
        user_data = {
            "email": "weak@example.com",
            "password": "weak",
            "first_name": "Test",
            "last_name": "User",
            "role": "student"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Password must be at least 8 characters" in response.json()["detail"]
    
    def test_login_success(self, db: Session, test_user: User):
        """Test successful login"""
        login_data = {
            "email": test_user.email,
            "password": "testpass123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_invalid_credentials(self, db: Session, test_user: User):
        """Test login with invalid credentials"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, db: Session):
        """Test login with nonexistent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "testpass123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, db: Session, test_user: User):
        """Test login with inactive user"""
        # Deactivate user
        test_user.is_active = False
        db.commit()
        
        login_data = {
            "email": test_user.email,
            "password": "testpass123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Account is deactivated" in response.json()["detail"]
    
    def test_refresh_token_success(self, db: Session, test_user: User):
        """Test successful token refresh"""
        # First login to get tokens
        login_data = {
            "email": test_user.email,
            "password": "testpass123"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()
        
        # Use refresh token
        refresh_data = {
            "refresh_token": tokens["refresh_token"]
        }
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, db: Session):
        """Test refresh with invalid token"""
        refresh_data = {
            "refresh_token": "invalid_token"
        }
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]
    
    def test_get_current_user(self, db: Session, test_user: User, auth_headers: dict):
        """Test getting current user info"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id
        assert data["role"] == test_user.role.value
    
    def test_get_current_user_unauthorized(self, db: Session):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_protected_route(self, db: Session, test_user: User, auth_headers: dict):
        """Test protected route access"""
        response = client.get("/api/v1/auth/protected", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert test_user.full_name in data["message"]
        assert data["user_id"] == test_user.id
        assert data["role"] == test_user.role.value
    
    def test_protected_route_unverified_user(self, db: Session, unverified_user: User):
        """Test protected route with unverified user"""
        # Create token for unverified user
        token = create_access_token(
            subject=unverified_user.email,
            user_id=unverified_user.id,
            role=unverified_user.role.value
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/auth/protected", headers=headers)
        
        assert response.status_code == 401
        assert "Email not verified" in response.json()["detail"]
    
    def test_change_password_success(self, db: Session, test_user: User, auth_headers: dict):
        """Test successful password change"""
        password_data = {
            "current_password": "testpass123",
            "new_password": "NewPass123"
        }
        
        response = client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]
        
        # Verify password was changed
        db.refresh(test_user)
        assert verify_password("NewPass123", test_user.password_hash)
    
    def test_change_password_wrong_current(self, db: Session, test_user: User, auth_headers: dict):
        """Test password change with wrong current password"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPass123"
        }
        
        response = client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_logout(self, db: Session, auth_headers: dict):
        """Test logout endpoint"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]


class TestAuthService:
    """Test authentication service"""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, db: Session):
        """Test successful user registration"""
        auth_service = AuthService(db)
        user_data = UserCreate(
            email="service@example.com",
            password="TestPass123",
            first_name="Service",
            last_name="Test",
            role=UserRole.STUDENT
        )
        
        user = await auth_service.register_user(user_data)
        
        assert user.email == user_data.email
        assert user.first_name == user_data.first_name
        assert user.last_name == user_data.last_name
        assert user.role == user_data.role
        assert user.is_active is True
        assert user.is_verified is False
        assert verify_password(user_data.password, user.password_hash)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db: Session, test_user: User):
        """Test successful user authentication"""
        auth_service = AuthService(db)
        credentials = UserLogin(
            email=test_user.email,
            password="testpass123"
        )
        
        token = await auth_service.authenticate_user(credentials)
        
        assert token.access_token is not None
        assert token.refresh_token is not None
        assert token.token_type == "bearer"
        assert token.expires_in > 0
    
    @pytest.mark.asyncio
    async def test_request_password_reset(self, db: Session, test_user: User):
        """Test password reset request"""
        auth_service = AuthService(db)
        
        result = await auth_service.request_password_reset(test_user.email)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_request_password_reset_nonexistent_email(self, db: Session):
        """Test password reset request for nonexistent email"""
        auth_service = AuthService(db)
        
        # Should return True even for nonexistent email (security)
        result = await auth_service.request_password_reset("nonexistent@example.com")
        
        assert result is True


class TestSecurityUtils:
    """Test security utility functions"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False
    
    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        from app.core.security import verify_token
        
        token = create_access_token(
            subject="test@example.com",
            user_id=1,
            role="student"
        )
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert payload["role"] == "student"
        assert payload["type"] == "access"
    
    def test_invalid_token_verification(self):
        """Test verification of invalid token"""
        from app.core.security import verify_token
        
        payload = verify_token("invalid_token")
        
        assert payload is None