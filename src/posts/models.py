from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, text,JSON,func
from sqlalchemy.orm import relationship
import uuid
from src.core.auth import Base

class Post(Base):
    __tablename__ = "post"

    post_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user.user_id",
                                        ondelete="CASCADE"), nullable=False)
    image_url = Column(String, nullable=False)
    result = Column(JSON, nullable=False)
    create_at = Column(TIMESTAMP(timezone=True),
                       server_default=text("CURRENT_TIMESTAMP"))
    update_at = Column(TIMESTAMP(timezone=True),nullable=True)
    # Relasi ke User
    owner = relationship("User", back_populates="posts")
