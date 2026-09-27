from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String(100), unique=True, nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)