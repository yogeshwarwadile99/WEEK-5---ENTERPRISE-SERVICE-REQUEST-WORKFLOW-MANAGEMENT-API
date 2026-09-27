from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.middleware.error_handler import AppException

class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AppException("USER_NOT_FOUND", f"User with ID {user_id} not found", 404)
        return user

    @staticmethod
    def get_by_email(db: Session, email: str) -> User:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_role(db: Session, role: str):
        """Get users by role"""
        return db.query(User).filter(User.role == role).all()

    @staticmethod
    def get_by_department(db: Session, department: str):
        """Get users by department"""
        return db.query(User).filter(User.department == department).all()

    @staticmethod
    def get_active_users(db: Session):
        """Get all active users"""
        return db.query(User).filter(User.status == "ACTIVE").all()

    @staticmethod
    def create(db: Session, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user"""
        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role,
            department=user_data.department,
            status="ACTIVE"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user_id: int, update_data: dict) -> User:
        """Update user"""
        user = UserRepository.get_by_id(db, user_id)
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """Soft delete user (set status to INACTIVE)"""
        user = UserRepository.get_by_id(db, user_id)
        user.status = "INACTIVE"
        db.commit()
        return True

    @staticmethod
    def hard_delete(db: Session, user_id: int) -> bool:
        """Permanently delete user"""
        user = UserRepository.get_by_id(db, user_id)
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def count(db: Session) -> int:
        """Get total user count"""
        return db.query(User).count()

    @staticmethod
    def count_by_role(db: Session, role: str) -> int:
        """Count users by role"""
        return db.query(User).filter(User.role == role).count()

    @staticmethod
    def get_agents(db: Session):
        """Get all support agents"""
        return db.query(User).filter(User.role == "SUPPORT_AGENT", User.status == "ACTIVE").all()

    @staticmethod
    def get_managers(db: Session):
        """Get all managers"""
        return db.query(User).filter(User.role == "MANAGER", User.status == "ACTIVE").all()

    @staticmethod
    def get_employees(db: Session):
        """Get all employees"""
        return db.query(User).filter(User.role == "EMPLOYEE", User.status == "ACTIVE").all()

    @staticmethod
    def search(db: Session, search_term: str):
        """Search users by name or email"""
        return db.query(User).filter(
            (User.name.ilike(f"%{search_term}%")) | 
            (User.email.ilike(f"%{search_term}%"))
        ).all()