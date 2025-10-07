from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PostBase(BaseModel):
    user_id: str
    image_url: str

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    post_id: str
    create_at: datetime
    model_config = ConfigDict(from_attributes=True)
