"""Index all products from PostgreSQL to Elasticsearch."""
import asyncio
from sqlalchemy import select
from app.database import async_session
from app.models.product import Product
from app.models.category import Category
from app.utils.elasticsearch_client import es_client, PRODUCT_INDEX, create_product_index


async def index_all_products():
    """Fetch all products from DB and index them into Elasticsearch."""
    await create_product_index()

    async with async_session() as session:
        result = await session.execute(
            select(Product, Category.name.label("category_name"))
            .join(Category, Product.category_id == Category.id)
            .where(Product.is_active == True)
        )
        rows = result.all()

        for product, category_name in rows:
            doc = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock_quantity": product.stock_quantity,
                "category": category_name,
                "category_id": product.category_id,
                "sku": product.sku,
                "image_url": product.image_url,
                "is_active": product.is_active,
                "created_at": product.created_at.isoformat() if product.created_at else None,
            }
            await es_client.index(index=PRODUCT_INDEX, id=str(product.id), document=doc)

    await es_client.indices.refresh(index=PRODUCT_INDEX)
    print(f"Indexed {len(rows)} products into Elasticsearch")


if __name__ == "__main__":
    asyncio.run(index_all_products())
