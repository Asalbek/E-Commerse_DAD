from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import CartItem
from app.models.product import Product


async def get_cart(db: AsyncSession, user_id: int):
    """Get user's cart with product details."""
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
        .order_by(CartItem.added_at.desc())
    )
    items = result.scalars().all()

    cart_items = []
    total = 0.0
    for item in items:
        subtotal = item.product.price * item.quantity
        total += subtotal
        cart_items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "product_price": item.product.price,
            "product_image": item.product.image_url,
            "quantity": item.quantity,
            "subtotal": round(subtotal, 2),
            "added_at": item.added_at.isoformat() if item.added_at else None,
        })

    return {
        "items": cart_items,
        "total": round(total, 2),
        "item_count": len(cart_items),
    }


async def add_to_cart(db: AsyncSession, user_id: int, product_id: int, quantity: int):
    """Add product to cart or update quantity if already in cart."""
    # Verify product exists and has stock
    product = await db.get(Product, product_id)
    if not product or not product.is_active:
        raise ValueError("Product not found")
    if product.stock_quantity < quantity:
        raise ValueError("Insufficient stock")

    # Check if already in cart
    result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.quantity += quantity
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(cart_item)

    await db.commit()
    return await get_cart(db, user_id)


async def update_cart_item(db: AsyncSession, user_id: int, item_id: int, quantity: int):
    """Update cart item quantity."""
    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise ValueError("Cart item not found")

    if quantity <= 0:
        await db.delete(item)
    else:
        item.quantity = quantity

    await db.commit()
    return await get_cart(db, user_id)


async def remove_from_cart(db: AsyncSession, user_id: int, item_id: int):
    """Remove item from cart."""
    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise ValueError("Cart item not found")

    await db.delete(item)
    await db.commit()
    return await get_cart(db, user_id)


async def clear_cart(db: AsyncSession, user_id: int):
    """Clear all items from user's cart."""
    await db.execute(delete(CartItem).where(CartItem.user_id == user_id))
    await db.commit()
