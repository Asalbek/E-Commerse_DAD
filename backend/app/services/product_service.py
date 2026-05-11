import json
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.category import Category
from app.utils.redis_client import redis_client
from app.utils.elasticsearch_client import es_client, PRODUCT_INDEX


CACHE_TTL = 300  # 5 minutes


async def get_products(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    """List products with filtering, pagination, and caching."""
    cache_key = f"products:list:{page}:{page_size}:{category_id}:{min_price}:{max_price}:{sort_by}:{sort_order}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    query = select(Product).where(Product.is_active == True).options(selectinload(Product.category))
    count_query = select(func.count(Product.id)).where(Product.is_active == True)

    if category_id:
        query = query.where(Product.category_id == category_id)
        count_query = count_query.where(Product.category_id == category_id)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
        count_query = count_query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
        count_query = count_query.where(Product.price <= max_price)

    # Sorting
    sort_column = getattr(Product, sort_by, Product.created_at)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    products = result.scalars().all()

    data = {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "stock_quantity": p.stock_quantity,
                "sku": p.sku,
                "image_url": p.image_url,
                "is_active": p.is_active,
                "category_id": p.category_id,
                "category": {"id": p.category.id, "name": p.category.name, "slug": p.category.slug} if p.category else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in products
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size if total else 0,
    }

    await redis_client.set(cache_key, json.dumps(data), ex=CACHE_TTL)
    return data


async def get_product_by_id(db: AsyncSession, product_id: int):
    """Get single product by ID with caching."""
    cache_key = f"products:detail:{product_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(Product).where(Product.id == product_id).options(selectinload(Product.category))
    )
    product = result.scalar_one_or_none()
    if not product:
        return None

    data = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock_quantity": product.stock_quantity,
        "sku": product.sku,
        "image_url": product.image_url,
        "is_active": product.is_active,
        "category_id": product.category_id,
        "category": {"id": product.category.id, "name": product.category.name, "slug": product.category.slug} if product.category else None,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }

    await redis_client.set(cache_key, json.dumps(data), ex=CACHE_TTL)

    # Increment view counter (sorted set for trending)
    await redis_client.zincrby("products:views", 1, str(product_id))

    return data


async def invalidate_product_cache(product_id: int = None):
    """Invalidate product cache entries."""
    if product_id:
        await redis_client.delete(f"products:detail:{product_id}")
    # Invalidate all list caches
    keys = []
    async for key in redis_client.scan_iter("products:list:*"):
        keys.append(key)
    if keys:
        await redis_client.delete(*keys)


async def search_products(query: str, category: str = None, page: int = 1, page_size: int = 20):
    """Full-text search products using Elasticsearch."""
    must_clauses = [
        {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "name.autocomplete^2", "description", "category"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        }
    ]

    filter_clauses = [{"term": {"is_active": True}}]

    if category:
        filter_clauses.append({"term": {"category": category}})

    body = {
        "query": {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
            }
        },
        "from": (page - 1) * page_size,
        "size": page_size,
        "highlight": {
            "fields": {
                "name": {},
                "description": {},
            }
        },
    }

    result = await es_client.search(index=PRODUCT_INDEX, body=body)
    hits = result["hits"]

    return {
        "items": [
            {
                **hit["_source"],
                "score": hit["_score"],
                "highlights": hit.get("highlight", {}),
            }
            for hit in hits["hits"]
        ],
        "total": hits["total"]["value"],
        "page": page,
        "page_size": page_size,
    }


async def get_trending_products(limit: int = 10):
    """Get trending products based on view counts from Redis sorted set."""
    trending_ids = await redis_client.zrevrange("products:views", 0, limit - 1, withscores=True)
    return [{"product_id": int(pid), "views": int(score)} for pid, score in trending_ids]
