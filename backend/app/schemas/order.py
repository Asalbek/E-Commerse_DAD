from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class OrderCreate(BaseModel):
    shipping_address: str
    notes: Optional[str] = None
    payment_method: str = "card"


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    id: int
    method: str
    status: str
    amount: float
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ShipmentResponse(BaseModel):
    id: int
    status: str
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: float
    shipping_address: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemResponse] = []
    payment: Optional[PaymentResponse] = None
    shipment: Optional[ShipmentResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: List[OrderResponse]
    total: int
