"""
Order Processing Pipeline Worker (R10)

Consumes messages from RabbitMQ queues and processes the order
through multiple stages:

  order.placed → Payment Verification
  order.paid   → Inventory Confirmation
  order.fulfilled → Shipment Creation

Each stage publishes to the next queue, forming a pipeline.
"""

import json
import asyncio
import uuid
from datetime import datetime, timezone
import aio_pika
from sqlalchemy import select, update

from app.config import get_settings
from app.database import async_session
from app.models.order import Order
from app.models.payment import Payment
from app.models.shipment import Shipment

settings = get_settings()


async def process_order_placed(message: aio_pika.IncomingMessage):
    """Stage 1: Verify payment for a placed order."""
    async with message.process():
        data = json.loads(message.body)
        order_id = data["order_id"]
        print(f"[Worker] Processing payment for order {order_id}")

        async with async_session() as db:
            # Simulate payment verification (in production: call Stripe/PayPal)
            result = await db.execute(
                select(Payment).where(Payment.order_id == order_id)
            )
            payment = result.scalar_one_or_none()
            if payment:
                payment.status = "completed"
                payment.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
                payment.paid_at = datetime.now(timezone.utc)

                # Update order status
                order = await db.get(Order, order_id)
                if order:
                    order.status = "paid"

                await db.commit()
                print(f"[Worker] Payment verified for order {order_id}")

        # Publish to next stage
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()
        await channel.declare_queue("order.paid", durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({"order_id": order_id}).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key="order.paid",
        )
        await connection.close()


async def process_order_paid(message: aio_pika.IncomingMessage):
    """Stage 2: Confirm inventory and prepare for shipment."""
    async with message.process():
        data = json.loads(message.body)
        order_id = data["order_id"]
        print(f"[Worker] Fulfilling order {order_id}")

        async with async_session() as db:
            order = await db.get(Order, order_id)
            if order:
                order.status = "fulfilled"
                await db.commit()
                print(f"[Worker] Order {order_id} fulfilled")

        # Publish to shipment stage
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()
        await channel.declare_queue("order.fulfilled", durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({"order_id": order_id}).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key="order.fulfilled",
        )
        await connection.close()


async def process_order_fulfilled(message: aio_pika.IncomingMessage):
    """Stage 3: Create shipment and assign tracking number."""
    async with message.process():
        data = json.loads(message.body)
        order_id = data["order_id"]
        print(f"[Worker] Creating shipment for order {order_id}")

        async with async_session() as db:
            result = await db.execute(
                select(Shipment).where(Shipment.order_id == order_id)
            )
            shipment = result.scalar_one_or_none()
            if shipment:
                shipment.status = "shipped"
                shipment.tracking_number = f"FC-{uuid.uuid4().hex[:10].upper()}"
                shipment.carrier = "FlashCart Express"
                shipment.shipped_at = datetime.now(timezone.utc)

                order = await db.get(Order, order_id)
                if order:
                    order.status = "shipped"

                await db.commit()
                print(f"[Worker] Shipment created for order {order_id}: {shipment.tracking_number}")


async def main():
    """Start all order pipeline consumers."""
    print("[Worker] Starting order processing pipeline...")
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()

    # Set prefetch for fair dispatch
    await channel.set_qos(prefetch_count=1)

    # Declare and consume from all queues
    queue_placed = await channel.declare_queue("order.placed", durable=True)
    queue_paid = await channel.declare_queue("order.paid", durable=True)
    queue_fulfilled = await channel.declare_queue("order.fulfilled", durable=True)

    await queue_placed.consume(process_order_placed)
    await queue_paid.consume(process_order_paid)
    await queue_fulfilled.consume(process_order_fulfilled)

    print("[Worker] Pipeline ready. Waiting for messages...")
    await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
