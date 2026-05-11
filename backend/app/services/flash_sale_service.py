import json
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flash_sale import FlashSale, FlashSaleOrder
from app.models.product import Product
from app.utils.redis_client import redis_client
from app.from_scratch.snowflake_id import generate_id
from app.utils.rabbitmq_client import publish_message


FLASH_SALE_STOCK_PREFIX = "flash_sale:stock:"


async def init_flash_sale_stock(flash_sale_id: int, stock_limit: int):
    """Initialize flash sale stock in Redis for atomic decrements."""
    key = f"{FLASH_SALE_STOCK_PREFIX}{flash_sale_id}"
    await redis_client.set(key, stock_limit)


async def get_active_flash_sales(db: AsyncSession):
    """Get all currently active flash sales."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(FlashSale, Product)
        .join(Product, FlashSale.product_id == Product.id)
        .where(
            FlashSale.is_active == True,
            FlashSale.start_time <= now,
            FlashSale.end_time >= now,
        )
        .order_by(FlashSale.end_time.asc())
    )
    rows = result.all()

    sales = []
    for flash_sale, product in rows:
        # Get real-time remaining stock from Redis
        key = f"{FLASH_SALE_STOCK_PREFIX}{flash_sale.id}"
        remaining = await redis_client.get(key)
        if remaining is None:
            remaining = flash_sale.stock_limit - flash_sale.sold_count
            await redis_client.set(key, remaining)
        else:
            remaining = int(remaining)

        sales.append({
            "id": flash_sale.id,
            "product_id": product.id,
            "product_name": product.name,
            "product_image": product.image_url,
            "original_price": product.price,
            "sale_price": flash_sale.sale_price,
            "stock_limit": flash_sale.stock_limit,
            "sold_count": flash_sale.sold_count,
            "remaining": remaining,
            "start_time": flash_sale.start_time.isoformat(),
            "end_time": flash_sale.end_time.isoformat(),
            "is_active": flash_sale.is_active,
            "created_at": flash_sale.created_at.isoformat() if flash_sale.created_at else None,
        })

    return sales


async def purchase_flash_sale(db: AsyncSession, flash_sale_id: int, user_id: int, quantity: int = 1):
    """Atomic flash sale purchase using Redis DECRBY.

    This ensures no overselling under high concurrency.
    Redis is the source of truth for remaining stock during the sale.
    """
    key = f"{FLASH_SALE_STOCK_PREFIX}{flash_sale_id}"

    # Atomic decrement in Redis
    remaining = await redis_client.decrby(key, quantity)

    if remaining < 0:
        # Oversold — rollback
        await redis_client.incrby(key, quantity)
        return {
            "success": False,
            "message": "Flash sale sold out!",
            "remaining_stock": max(0, remaining + quantity),
        }

    # Get flash sale details
    result = await db.execute(
        select(FlashSale).where(FlashSale.id == flash_sale_id)
    )
    flash_sale = result.scalar_one_or_none()

    if not flash_sale or not flash_sale.is_active:
        await redis_client.incrby(key, quantity)
        return {"success": False, "message": "Flash sale not found or inactive"}

    now = datetime.now(timezone.utc)
    if now < flash_sale.start_time or now > flash_sale.end_time:
        await redis_client.incrby(key, quantity)
        return {"success": False, "message": "Flash sale is not currently active"}

    # Record the flash sale order
    fs_order = FlashSaleOrder(
        flash_sale_id=flash_sale_id,
        user_id=user_id,
        quantity=quantity,
    )
    db.add(fs_order)

    # Update sold count in DB
    flash_sale.sold_count += quantity

    await db.commit()

    # Publish stock update event for WebSocket broadcast
    await publish_message("inventory.updated", {
        "type": "flash_sale_stock",
        "flash_sale_id": flash_sale_id,
        "product_id": flash_sale.product_id,
        "remaining": remaining,
    })

    # Publish to Redis pub/sub for real-time WebSocket updates
    await redis_client.publish(
        f"inventory:{flash_sale.product_id}",
        json.dumps({"remaining": remaining, "flash_sale_id": flash_sale_id})
    )

    return {
        "success": True,
        "message": "Purchase successful!",
        "order_id": fs_order.id,
        "remaining_stock": remaining,
    }


async def create_flash_sale(db: AsyncSession, product_id: int, sale_price: float, stock_limit: int, start_time: datetime, end_time: datetime):
    """Admin: create a new flash sale."""
    product = await db.get(Product, product_id)
    if not product:
        raise ValueError("Product not found")

    flash_sale = FlashSale(
        product_id=product_id,
        sale_price=sale_price,
        stock_limit=stock_limit,
        start_time=start_time,
        end_time=end_time,
        is_active=True,
    )
    db.add(flash_sale)
    await db.commit()
    await db.refresh(flash_sale)

    # Init Redis stock counter
    await init_flash_sale_stock(flash_sale.id, stock_limit)

    return {
        "id": flash_sale.id,
        "product_id": product_id,
        "product_name": product.name,
        "sale_price": sale_price,
        "stock_limit": stock_limit,
        "sold_count": 0,
        "remaining": stock_limit,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "is_active": True,
        "created_at": flash_sale.created_at.isoformat() if flash_sale.created_at else None,
    }
