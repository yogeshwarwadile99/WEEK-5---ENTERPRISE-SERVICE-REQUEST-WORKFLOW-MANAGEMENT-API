from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate
from app.config import config
from app.middleware.error_handler import AppException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        if len(password) > 72:
            password = password[:72]
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if len(plain_password) > 72:
            plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRY_MINUTES)
        return jwt.encode({"user_id": user_id, "exp": expire}, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    
    @staticmethod
    def register(db: Session, user_data: UserCreate):
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise AppException("EMAIL_ALREADY_EXISTS", "Email already registered", 400)
        hashed = AuthService.hash_password(user_data.password)
        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed,
            role=user_data.role,
            department=user_data.department
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def login(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise AppException("INVALID_CREDENTIALS", "Invalid email or password", 401)
        if not AuthService.verify_password(password, user.password_hash):
            raise AppException("INVALID_CREDENTIALS", "Invalid email or password", 401)
        if user.status != "ACTIVE":
            raise AppException("ACCOUNT_INACTIVE", "User account is inactive", 403)
        token = AuthService.create_access_token(user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "department": user.department
            }
        }
