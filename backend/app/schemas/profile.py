from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# --- Profile & Address ---

class UserProfileSchema(BaseModel):
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserAddressSchema(BaseModel):
    id: Optional[int] = None
    title: str
    address_line1: str
    city: str
    postal_code: Optional[str] = None
    is_default: bool = False

    class Config:
        from_attributes = True


# --- Reviews ---

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_name: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
