import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.models.user import User, UserRole
from app.core.deps import (
    get_current_user,
    get_current_verified_user,
    get_current_admin,
    get_current_instructor,
    get_current_student,
    get_instructor_or_admin
)
from tests.conftest import override_get_db

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestRoleBasedAccessControl:
    """Test role-based access control"""
    
    def test_admin_access_only(self, db: Session, admin_auth_headers: dict, instructor_auth_headers: dict, auth_headers: dict):
        """Test endpoint that requires admin access only"""
        from fastapi import APIRouter, Depends
        from app.core.deps import get_current_admin
        
        # Create a test router with admin-only endpoint
        test_router = APIRouter()
        
        @test_router.get("/admin-only")
        async def admin_only_endpoint(current_user: User = Depends(get_current_admin)):
            return {"message": "Admin access granted", "user_id": current_user.id}
        
        # Add router to app temporarily
        app.include_router(test_router, prefix="/test")
        
        try:
            # Test admin access - should succeed
            response = client.get("/test/admin-only", headers=admin_auth_headers)
            assert response.status_code == 200
            assert "Admin access granted" in response.json()["message"]
            
            # Test instructor access - should fail
            response = client.get("/test/admin-only", headers=instructor_auth_headers)
            assert response.status_code == 403
            assert "Access denied" in response.json()["detail"]
            
            # Test student access - should fail
            response = client.get("/test/admin-only", headers=auth_headers)
            assert response.status_code == 403
            assert "Access denied" in response.json()["detail"]
            
        finally:
            # Remove test router
            app.router.routes = [route for route in app.router.routes if not hasattr(route, 'path') or not route.path.startswith('/test')]
    
    def test_instructor_access_only(self, db: Session, admin_auth_headers: dict, instructor_auth_headers: dict, auth_headers: dict):
        """Test endpoint that requires instructor access only"""
        from fastapi import APIRouter, Depends
        from app.core.deps import get_current_instructor
        
        # Create a test router with instructor-only endpoint
        test_router = APIRouter()
        
        @test_router.get("/instructor-only")
        async def instructor_only_endpoint(current_user: User = Depends(get_current_instructor)):
            return {"message": "Instructor access granted", "user_id": current_user.id}
        
        # Add router to app temporarily
        app.include_router(test_router, prefix="/test")
        
        try:
            # Test instructor access - should succeed
            response = client.get("/test/instructor-only", headers=instructor_auth_headers)
            assert response.status_code == 200
            assert "Instructor access granted" in response.json()["message"]
            
            # Test admin access - should fail (admin is not instructor)
            response = client.get("/test/instructor-only", headers=admin_auth_headers)
            assert response.status_code == 403
            assert "Access denied" in response.json()["detail"]
            
            # Test student access - should fail
            response = client.get("/test/instructor-only", headers=auth_headers)
            assert response.status_code == 403
            assert "Access denied" in response.json()["detail"]
            
        finally:
            # Remove test router
            app.router.routes = [route for route in app.router.routes if not hasattr(route, 'path') or not route.path.startswith('/test')]
    
    def test_instructor_or_admin_access(self, db: Session, admin_auth_headers: dict, instructor_auth_headers: dict, auth_headers: dict):
        """Test endpoint that allows both instructor and admin access"""
        from fastapi import APIRouter, Depends
        from app.core.deps import get_instructor_or_admin
        
        # Create a test router with instructor or admin endpoint
        test_router = APIRouter()
        
        @test_router.get("/instructor-or-admin")
        async def instructor_or_admin_endpoint(current_user: User = Depends(get_instructor_or_admin)):
            return {"message": "Access granted", "user_id": current_user.id, "role": current_user.role.value}
        
        # Add router to app temporarily
        app.include_router(test_router, prefix="/test")
        
        try:
            # Test admin access - should succeed
            response = client.get("/test/instructor-or-admin", headers=admin_auth_headers)
            assert response.status_code == 200
            assert "Access granted" in response.json()["message"]
            assert response.json()["role"] == "admin"
            
            # Test instructor access - should succeed
            response = client.get("/test/instructor-or-admin", headers=instructor_auth_headers)
            assert response.status_code == 200
            assert "Access granted" in response.json()["message"]
            assert response.json()["role"] == "instructor"
            
            # Test student access - should fail
            response = client.get("/test/instructor-or-admin", headers=auth_headers)
            assert response.status_code == 403
            assert "Access denied" in response.json()["detail"]
            
        finally:
            # Remove test router
            app.router.routes = [route for route in app.router.routes if not hasattr(route, 'path') or not route.path.startswith('/test')]
    
    def test_student_access_only(self, db: Session, admin_auth_headers: dict, instructor_auth_headers: dict, auth_headers: dict):
        """Test endpoint that requires student access only"""
        from fastapi import APIRouter, Depends
        from app.core.deps import get_current_student
        
        # Create a test router with student-only endpoint
        test_router = APIRouter()
        
        @test_router.get("/student-only")
        async def student_only_endpoint(current_user: User = Depends(get_current_student)):
            return {"message": "Student access granted", "user_id": current_user.id}
        
        # Add router to app temporarily
        app.include_router(test_router, prefix="/test")
        
        try:
            # Test student access - should succeed
            response = client.get("/test/student-only", headers=auth_headers)
            assert response.status_code == 200
            assert "Student access granted" in response.json()["message"]
            
            # Test instructor access - should fail
            response = client.get("/test/student-only", headers=instructor_auth_headers)
            assert response.status_code == 403
            assert "Access denied" in response.json()["detail"]
            
            # Test admin access - should fail
            response = client.get("/test/student-only", headers=admin_auth_headers)
            assert response.status_code == 403
            assert "Access denied" in response.json()["detail"]
            
        finally:
            # Remove test router
            app.router.routes = [route for route in app.router.routes if not hasattr(route, 'path') or not route.path.startswith('/test')]
    
    def test_verified_user_access(self, db: Session, auth_headers: dict, unverified_user: User):
        """Test endpoint that requires verified user"""
        from fastapi import APIRouter, Depends
        from app.core.deps import get_current_verified_user
        from app.core.security import create_access_token
        
        # Create a test router with verified user endpoint
        test_router = APIRouter()
        
        @test_router.get("/verified-only")
        async def verified_only_endpoint(current_user: User = Depends(get_current_verified_user)):
            return {"message": "Verified user access granted", "user_id": current_user.id}
        
        # Add router to app temporarily
        app.include_router(test_router, prefix="/test")
        
        try:
            # Test verified user access - should succeed
            response = client.get("/test/verified-only", headers=auth_headers)
            assert response.status_code == 200
            assert "Verified user access granted" in response.json()["message"]
            
            # Test unverified user access - should fail
            unverified_token = create_access_token(
                subject=unverified_user.email,
                user_id=unverified_user.id,
                role=unverified_user.role.value
            )
            unverified_headers = {"Authorization": f"Bearer {unverified_token}"}
            
            response = client.get("/test/verified-only", headers=unverified_headers)
            assert response.status_code == 401
            assert "Email not verified" in response.json()["detail"]
            
        finally:
            # Remove test router
            app.router.routes = [route for route in app.router.routes if not hasattr(route, 'path') or not route.path.startswith('/test')]
    
    def test_no_authentication_required(self, db: Session):
        """Test public endpoint that doesn't require authentication"""
        response = client.get("/")
        assert response.status_code == 200
        
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_invalid_token(self, db: Session):
        """Test access with invalid token"""
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/api/v1/auth/me", headers=invalid_headers)
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_missing_token(self, db: Session):
        """Test access without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401