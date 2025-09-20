from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class PostCategory(str, Enum):
    FOOD = "Food"
    WATER = "Water"
    MEDICAL = "Medical"
    RESCUE = "Rescue"
    VOLUNTEER = "Volunteer"
    ANNOUNCEMENT = "Announcement"

class CommunityPostBase(BaseModel):
    category: PostCategory
    message: str
    location: Optional[str] = None

class CommunityPostCreate(CommunityPostBase):
    pass

class CommunityPost(CommunityPostBase):
    id: str
    user_id: str
    user_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True