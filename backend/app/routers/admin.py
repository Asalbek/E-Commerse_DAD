from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order, OrderItem
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.flash_sale import FlashSaleCreate, FlashSaleResponse
from app.services.auth_service import require_admin
from app.services.product_service import invalidate_product_cache
from app.services.flash_sale_service import create_flash_sale
from app.utils.elasticsearch_client import es_client, PRODUCT_INDEX

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/products")
async def admin_list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: list all products including inactive."""
    count_result = await db.execute(select(func.count(Product.id)))
    total = count_result.scalar()

    result = await db.execute(
        select(Product)
        .order_by(Product.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    products = result.scalars().all()

    return {
        "items": [ProductResponse.model_validate(p) for p in products],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/products", response_model=ProductResponse, status_code=201)
async def admin_create_product(
    data: ProductCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: create a new product."""
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)

    # Index in Elasticsearch
    category = await db.get(Category, product.category_id)
    doc = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock_quantity": product.stock_quantity,
        "category": category.name if category else "",
        "category_id": product.category_id,
        "sku": product.sku,
        "image_url": product.image_url,
        "is_active": product.is_active,
    }
    await es_client.index(index=PRODUCT_INDEX, id=str(product.id), document=doc)

    await invalidate_product_cache()
    return ProductResponse.model_validate(product)


@router.put("/products/{product_id}", response_model=ProductResponse)
async def admin_update_product(
    product_id: int,
    data: ProductUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: update a product."""
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)

    # Update Elasticsearch
    category = await db.get(Category, product.category_id)
    doc = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock_quantity": product.stock_quantity,
        "category": category.name if category else "",
        "category_id": product.category_id,
        "sku": product.sku,
        "image_url": product.image_url,
        "is_active": product.is_active,
    }
    await es_client.index(index=PRODUCT_INDEX, id=str(product.id), document=doc)

    await invalidate_product_cache(product_id)
    return ProductResponse.model_validate(product)


@router.post("/flash-sales", response_model=FlashSaleResponse, status_code=201)
async def admin_create_flash_sale(
    data: FlashSaleCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: create a new flash sale."""
    try:
        return await create_flash_sale(
            db, data.product_id, data.sale_price, data.stock_limit, data.start_time, data.end_time
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics/sales")
async def admin_sales_analytics(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: get sales analytics summary."""
    # Total orders and revenue
    total_result = await db.execute(
        select(func.count(Order.id), func.sum(Order.total_amount))
    )
    total_orders, total_revenue = total_result.one()

    # Orders by status
    status_result = await db.execute(
        select(Order.status, func.count(Order.id))
        .group_by(Order.status)
    )
    orders_by_status = {row[0]: row[1] for row in status_result.all()}

    # Top selling products
    top_products_result = await db.execute(
        select(
            Product.name,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue"),
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .group_by(Product.name)
        .order_by(text("total_sold DESC"))
        .limit(10)
    )
    top_products = [
        {"name": row[0], "total_sold": int(row[1]), "revenue": float(row[2])}
        for row in top_products_result.all()
    ]

    return {
        "total_orders": total_orders or 0,
        "total_revenue": float(total_revenue or 0),
        "orders_by_status": orders_by_status,
        "top_products": top_products,
    }
