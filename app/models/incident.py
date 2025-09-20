from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class IncidentType(str, Enum):
    FLOOD = "Flood"
    FIRE = "Fire"
    BUILDING_COLLAPSE = "Building Collapse"
    ROAD_ACCIDENT = "Road Accident"
    OTHER = "Other"

class IncidentStatus(str, Enum):
    REPORTED = "reported"
    VERIFIED = "verified"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class IncidentBase(BaseModel):
    incident_type: IncidentType
    description: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class IncidentCreate(IncidentBase):
    photo_url: Optional[str] = None

class Incident(IncidentBase):
    id: str
    user_id: str
    photo_url: Optional[str] = None
    status: IncidentStatus = IncidentStatus.REPORTED
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True