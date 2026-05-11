from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.audit import ProductReview
from app.schemas.profile import ReviewCreate, ReviewResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/v1/products", tags=["Reviews"])


@router.get("/{product_id}/reviews", response_model=List[ReviewResponse])
async def get_product_reviews(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get all reviews for a specific product."""
    result = await db.execute(
        select(ProductReview, User.name)
        .join(User, ProductReview.user_id == User.id)
        .where(ProductReview.product_id == product_id)
        .order_by(ProductReview.created_at.desc())
    )
    
    reviews = []
    for row in result.all():
        review, user_name = row
        reviews.append({
            "id": review.id,
            "user_name": user_name,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at
        })
    return reviews


@router.post("/{product_id}/reviews", response_model=ReviewResponse)
async def create_review(
    product_id: int, 
    data: ReviewCreate, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Post a product review."""
    review = ProductReview(
        product_id=product_id,
        user_id=user.id,
        rating=data.rating,
        comment=data.comment
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    return {
        "id": review.id,
        "user_name": user.name,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at
    }
