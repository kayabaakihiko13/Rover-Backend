import uuid
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship
from src.core.db import Base


class Admin(Base):
    __tablename__ = "admin"

    admin_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="moderator")  # superadmin, moderator
    is_active = Column(Boolean, default=True)
    create_at = Column(TIMESTAMP, server_default=func.now())
    update_at = Column(TIMESTAMP, server_default=func.now())

    news = relationship("News", back_populates="admin", cascade="all, delete-orphan")


class News(Base):
    __tablename__ = "news"

    news_id = Column(String, primary_key=True, index=True)
    admin_id = Column(String, ForeignKey("admin.admin_id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))
    create_at = Column(TIMESTAMP, server_default=func.now())
    update_at = Column(TIMESTAMP, server_default=func.now())

    admin = relationship("Admin", back_populates="news")
