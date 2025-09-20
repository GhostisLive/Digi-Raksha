from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class MissingPersonStatus(str, Enum):
    MISSING = "missing"
    FOUND = "found"
    INVESTIGATING = "investigating"

class MissingPersonBase(BaseModel):
    name: str
    age: int
    last_seen_location: str
    description: str
    reporter_contact: str

class MissingPersonCreate(MissingPersonBase):
    photo_url: Optional[str] = None

class MissingPerson(MissingPersonBase):
    id: str
    user_id: str
    photo_url: Optional[str] = None
    status: MissingPersonStatus = MissingPersonStatus.MISSING
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True