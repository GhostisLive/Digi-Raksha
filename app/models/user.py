from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    city: str
    phone_number: str
    gov_id_type: str
    gov_id_number: str

class UserCreate(UserBase):
    password: str
    photo_url: Optional[str] = None

class UserLogin(BaseModel):
    gov_id_number: str
    password: str

class User(UserBase):
    id: str
    phone_number: str
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    gov_id_number: Optional[str] = None