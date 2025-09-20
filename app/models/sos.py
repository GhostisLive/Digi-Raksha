from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class SOSStatus(str, Enum):
    ACTIVE = "active"
    RESPONDED = "responded"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"

class SOSBase(BaseModel):
    latitude: float
    longitude: float
    location_description: Optional[str] = None
    emergency_type: Optional[str] = None

class SOSCreate(SOSBase):
    pass

class SOSAlert(SOSBase):
    id: str
    user_id: str
    user_name: str
    status: SOSStatus = SOSStatus.ACTIVE
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SafeStatusUpdate(BaseModel):
    latitude: float
    longitude: float
    message: Optional[str] = "User marked as safe"