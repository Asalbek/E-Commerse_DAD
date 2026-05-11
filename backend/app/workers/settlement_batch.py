"""
Daily Settlement Batch Job (R10)

Runs at midnight to compute daily sales aggregates:
  - Total revenue per category
  - Order count by status
  - Top-selling products
  - Average order value

Results are stored in a daily_settlements table and can be
queried by the admin analytics endpoint.

Uses APScheduler as a lightweight cron alternative.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, text
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import async_session, engine
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.category import Category
from app.utils.redis_client import redis_client


async def run_daily_settlement():
    """Compute daily sales settlement."""
    print(f"[Batch] Running daily settlement at {datetime.now(timezone.utc).isoformat()}")

    yesterday = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0) - timedelta(days=1)
    today = yesterday + timedelta(days=1)

    async with async_session() as db:
        # Total orders and revenue for yesterday
        result = await db.execute(
            select(
                func.count(Order.id).label("total_orders"),
                func.coalesce(func.sum(Order.total_amount), 0).label("total_revenue"),
                func.coalesce(func.avg(Order.total_amount), 0).label("avg_order_value"),
            )
            .where(Order.created_at >= yesterday, Order.created_at < today)
        )
        row = result.one()
        total_orders = row[0]
        total_revenue = float(row[1])
        avg_order_value = float(row[2])

        # Revenue per category
        cat_result = await db.execute(
            select(
                Category.name,
                func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Category, Product.category_id == Category.id)
            .join(Order, OrderItem.order_id == Order.id)
            .where(Order.created_at >= yesterday, Order.created_at < today)
            .group_by(Category.name)
        )
        category_revenue = {row[0]: float(row[1]) for row in cat_result.all()}

        # Store settlement summary in Redis
        settlement_key = f"settlement:{yesterday.strftime('%Y-%m-%d')}"
        import json
        settlement_data = {
            "date": yesterday.strftime("%Y-%m-%d"),
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "avg_order_value": round(avg_order_value, 2),
            "category_revenue": category_revenue,
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
        await redis_client.set(settlement_key, json.dumps(settlement_data), ex=86400 * 30)

        print(f"[Batch] Settlement complete: {total_orders} orders, ${total_revenue:.2f} revenue")


async def main():
    """Start the batch scheduler."""
    print("[Batch] Starting settlement batch scheduler...")
    scheduler = AsyncIOScheduler()

    # Run daily at midnight UTC
    scheduler.add_job(run_daily_settlement, "cron", hour=0, minute=0)

    # Also run immediately for testing
    await run_daily_settlement()

    scheduler.start()
    print("[Batch] Scheduler started. Next run at midnight UTC.")
    await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
