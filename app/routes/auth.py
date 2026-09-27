from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = AuthService.register(db, user_data)
        return {
            "success": True,
            "message": "User registered successfully",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "department": user.department
            }
        }
    except Exception as e:
        return {"success": False, "error": {"code": "REGISTRATION_FAILED", "message": str(e)}}

@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        result = AuthService.login(db, login_data.email, login_data.password)
        return {"success": True, "message": "Login successful", "data": result}
    except Exception as e:
        return {"success": False, "error": {"code": "LOGIN_FAILED", "message": str(e)}}

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
            "department": current_user.department
        }
    }
