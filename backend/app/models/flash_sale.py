import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class FlashSale(Base):
    __tablename__ = "flash_sales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, unique=True, index=True
    )
    sale_price: Mapped[float] = mapped_column(Float, nullable=False)
    stock_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    sold_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    start_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    product = relationship("Product", back_populates="flash_sale")
    orders = relationship("FlashSaleOrder", back_populates="flash_sale")


class FlashSaleOrder(Base):
    __tablename__ = "flash_sale_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flash_sale_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("flash_sales.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ordered_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    flash_sale = relationship("FlashSale", back_populates="orders")
    user = relationship("User")
