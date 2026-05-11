from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.flash_sale import FlashSaleCreate, FlashSaleResponse, FlashSalePurchase, FlashSalePurchaseResponse
from app.services.auth_service import get_current_user
from app.services.flash_sale_service import get_active_flash_sales, purchase_flash_sale

router = APIRouter(prefix="/api/v1/flash-sales", tags=["Flash Sales"])


@router.get("/active", response_model=list[FlashSaleResponse])
async def list_active_sales(db: AsyncSession = Depends(get_db)):
    """List all currently active flash sales."""
    return await get_active_flash_sales(db)


@router.post("/{flash_sale_id}/purchase", response_model=FlashSalePurchaseResponse)
async def buy_flash_sale(
    flash_sale_id: int,
    data: FlashSalePurchase,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Purchase from a flash sale with atomic stock decrement."""
    result = await purchase_flash_sale(db, flash_sale_id, user.id, data.quantity)
    if not result["success"]:
        raise HTTPException(status_code=409, detail=result["message"])
    return result
