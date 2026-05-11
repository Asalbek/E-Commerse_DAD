from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.shipment import Shipment
from app.models.cart import CartItem
from app.models.product import Product
from app.from_scratch.snowflake_id import generate_id
from app.utils.rabbitmq_client import publish_message
from app.services.cart_service import clear_cart
from app.services.product_service import invalidate_product_cache


async def create_order(db: AsyncSession, user_id: int, shipping_address: str, notes: str = None, payment_method: str = "card"):
    """Create an order from the user's cart.

    Flow: validate stock → create order → deduct stock → clear cart → publish to RabbitMQ
    """
    # Get cart items
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
    )
    cart_items = result.scalars().all()

    if not cart_items:
        raise ValueError("Cart is empty")

    # Validate stock for all items
    total_amount = 0.0
    order_items_data = []
    for item in cart_items:
        product = item.product
        if product.stock_quantity < item.quantity:
            raise ValueError(f"Insufficient stock for {product.name}")
        subtotal = product.price * item.quantity
        total_amount += subtotal
        order_items_data.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": product.price,
        })

    # Generate Snowflake ID for the order
    order_id = generate_id()
    shipment_id = generate_id()

    # Create order
    order = Order(
        id=order_id,
        user_id=user_id,
        status="pending",
        total_amount=round(total_amount, 2),
        shipping_address=shipping_address,
        notes=notes,
    )
    db.add(order)

    # Create order items and deduct stock
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order_id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
        )
        db.add(order_item)

        # Deduct stock
        item_data["product"].stock_quantity -= item_data["quantity"]
        await invalidate_product_cache(item_data["product"].id)

    # Create payment record
    payment = Payment(
        order_id=order_id,
        method=payment_method,
        status="pending",
        amount=round(total_amount, 2),
    )
    db.add(payment)

    # Create shipment record
    shipment = Shipment(
        id=shipment_id,
        order_id=order_id,
        status="preparing",
    )
    db.add(shipment)

    await db.commit()

    # Clear user's cart
    await clear_cart(db, user_id)

    # Publish order event to RabbitMQ for async processing
    await publish_message("order.placed", {
        "order_id": order_id,
        "user_id": user_id,
        "total_amount": round(total_amount, 2),
        "payment_method": payment_method,
        "items": [
            {
                "product_id": item_data["product"].id,
                "quantity": item_data["quantity"],
                "unit_price": item_data["unit_price"],
            }
            for item_data in order_items_data
        ],
    })

    return await get_order(db, order_id, user_id)


async def get_order(db: AsyncSession, order_id: int, user_id: int = None):
    """Get single order with all related data."""
    query = (
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.payment),
            selectinload(Order.shipment),
        )
    )
    if user_id:
        query = query.where(Order.user_id == user_id)

    result = await db.execute(query)
    order = result.scalar_one_or_none()
    if not order:
        return None

    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "shipping_address": order.shipping_address,
        "notes": order.notes,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else None,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in order.items
        ],
        "payment": {
            "id": order.payment.id,
            "method": order.payment.method,
            "status": order.payment.status,
            "amount": order.payment.amount,
            "transaction_id": order.payment.transaction_id,
            "paid_at": order.payment.paid_at.isoformat() if order.payment.paid_at else None,
        } if order.payment else None,
        "shipment": {
            "id": order.shipment.id,
            "status": order.shipment.status,
            "tracking_number": order.shipment.tracking_number,
            "carrier": order.shipment.carrier,
            "shipped_at": order.shipment.shipped_at.isoformat() if order.shipment.shipped_at else None,
            "delivered_at": order.shipment.delivered_at.isoformat() if order.shipment.delivered_at else None,
        } if order.shipment else None,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }


async def get_user_orders(db: AsyncSession, user_id: int):
    """Get all orders for a user."""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.payment),
            selectinload(Order.shipment),
        )
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()

    return {
        "items": [
            {
                "id": o.id,
                "user_id": o.user_id,
                "status": o.status,
                "total_amount": o.total_amount,
                "shipping_address": o.shipping_address,
                "items": [
                    {"id": i.id, "product_id": i.product_id, "product_name": i.product.name if i.product else None, "quantity": i.quantity, "unit_price": i.unit_price}
                    for i in o.items
                ],
                "payment": {"id": o.payment.id, "status": o.payment.status, "method": o.payment.method, "amount": o.payment.amount} if o.payment else None,
                "shipment": {"id": o.shipment.id, "status": o.shipment.status, "tracking_number": o.shipment.tracking_number} if o.shipment else None,
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "updated_at": o.updated_at.isoformat() if o.updated_at else None,
            }
            for o in orders
        ],
        "total": len(orders),
    }
