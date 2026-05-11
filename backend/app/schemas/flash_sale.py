from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class FlashSaleCreate(BaseModel):
    product_id: int
    sale_price: float
    stock_limit: int
    start_time: datetime
    end_time: datetime


class FlashSaleResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    original_price: Optional[float] = None
    sale_price: float
    stock_limit: int
    sold_count: int
    remaining: Optional[int] = None
    start_time: datetime
    end_time: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FlashSalePurchase(BaseModel):
    quantity: int = 1


class FlashSalePurchaseResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[int] = None
    remaining_stock: Optional[int] = None
