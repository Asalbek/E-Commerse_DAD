import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id"), nullable=False, unique=True
    )
    method: Mapped[str] = mapped_column(String(50), default="card", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_id: Mapped[str] = mapped_column(String(255), nullable=True)
    paid_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    order = relationship("Order", back_populates="payment")
