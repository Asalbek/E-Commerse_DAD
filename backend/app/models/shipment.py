import datetime
from sqlalchemy import String, ForeignKey, DateTime, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id"), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(String(50), default="preparing", nullable=False)
    tracking_number: Mapped[str] = mapped_column(String(255), nullable=True)
    carrier: Mapped[str] = mapped_column(String(100), nullable=True)
    shipped_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    order = relationship("Order", back_populates="shipment")
