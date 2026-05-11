from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.user import User, UserProfile, UserAddress
from app.schemas.profile import UserProfileSchema, UserAddressSchema
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


@router.get("", response_model=UserProfileSchema)
async def get_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get or create user profile."""
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        
    return profile


@router.get("/addresses", response_model=List[UserAddressSchema])
async def list_addresses(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List all saved addresses for user."""
    result = await db.execute(select(UserAddress).where(UserAddress.user_id == user.id))
    return result.scalars().all()


@router.post("/addresses", response_model=UserAddressSchema)
async def add_address(data: UserAddressSchema, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Add a new shipping address."""
    address = UserAddress(
        user_id=user.id,
        title=data.title,
        address_line1=data.address_line1,
        city=data.city,
        postal_code=data.postal_code,
        is_default=data.is_default
    )
    db.add(address)
    await db.commit()
    await db.refresh(address)
    return address
