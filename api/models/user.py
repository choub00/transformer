"""
SQLAlchemy 用户模型（同步）
"""

from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Column
from api.db import Base


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(50), unique=True, index=True, nullable=False)
    email: str = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(255), nullable=False)
    is_active: bool = Column(Boolean, default=True)
    is_admin: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
