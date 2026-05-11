from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartResponse
from app.services.auth_service import get_current_user
from app.services.cart_service import get_cart, add_to_cart, update_cart_item, remove_from_cart

router = APIRouter(prefix="/api/v1/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
async def view_cart(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """View the current user's cart."""
    return await get_cart(db, user.id)


@router.post("/items", response_model=CartResponse)
async def add_item(
    data: CartItemAdd,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add an item to the cart."""
    try:
        return await add_to_cart(db, user.id, data.product_id, data.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/items/{item_id}", response_model=CartResponse)
async def update_item(
    item_id: int,
    data: CartItemUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update cart item quantity."""
    try:
        return await update_cart_item(db, user.id, item_id, data.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/items/{item_id}", response_model=CartResponse)
async def delete_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove an item from the cart."""
    try:
        return await remove_from_cart(db, user.id, item_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
