from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional,Any

class PostBase(BaseModel):
    user_id: str
    image_url: str
class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    result:Optional[Any] = None
    model_config = ConfigDict(from_attributes=True)

class PostResponse(PostBase):
    post_id: str
    result:Optional[Any] = None
    create_at: datetime
    update_at:Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
