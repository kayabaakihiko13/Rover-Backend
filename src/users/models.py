from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
import uuid
from src.core.db import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String, nullable=False)
    create_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    update_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    # Relasi ke Post
    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan")
