"""Seed database with sample data for development and demo."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.database import async_session
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.flash_sale import FlashSale
from app.services.auth_service import hash_password
from datetime import datetime, timedelta, timezone


CATEGORIES = [
    {"name": "Electronics", "slug": "electronics", "description": "Smartphones, laptops, and gadgets"},
    {"name": "Clothing", "slug": "clothing", "description": "Fashion and apparel"},
    {"name": "Home & Garden", "slug": "home-garden", "description": "Furniture and decor"},
    {"name": "Sports", "slug": "sports", "description": "Athletic gear and equipment"},
    {"name": "Books", "slug": "books", "description": "Physical and digital books"},
    {"name": "Beauty", "slug": "beauty", "description": "Skincare and cosmetics"},
    {"name": "Toys", "slug": "toys", "description": "Games and children toys"},
    {"name": "Automotive", "slug": "automotive", "description": "Car parts and accessories"},
    {"name": "Food & Beverages", "slug": "food-beverages", "description": "Gourmet food and drinks"},
    {"name": "Office", "slug": "office", "description": "Office supplies and furniture"},
]

PRODUCTS = [
    {"name": "iPhone 16 Pro", "description": "Latest Apple flagship with A18 Pro chip, titanium design, and 48MP camera system.", "price": 1199.99, "stock_quantity": 150, "sku": "ELEC-IP16P", "image_url": "https://picsum.photos/seed/iphone/400/400", "category_slug": "electronics"},
    {"name": "MacBook Air M3", "description": "Ultra-thin laptop with M3 chip, 18-hour battery, and Liquid Retina display.", "price": 1299.99, "stock_quantity": 80, "sku": "ELEC-MBA3", "image_url": "https://picsum.photos/seed/macbook/400/400", "category_slug": "electronics"},
    {"name": "Sony WH-1000XM5", "description": "Industry-leading noise cancelling headphones with 30-hour battery.", "price": 349.99, "stock_quantity": 200, "sku": "ELEC-SXMS", "image_url": "https://picsum.photos/seed/headphones/400/400", "category_slug": "electronics"},
    {"name": "Samsung Galaxy S25 Ultra", "description": "Premium Android phone with S Pen, 200MP camera, and AI features.", "price": 1299.99, "stock_quantity": 120, "sku": "ELEC-SGS25", "image_url": "https://picsum.photos/seed/galaxy/400/400", "category_slug": "electronics"},
    {"name": "iPad Pro 13-inch", "description": "The most powerful iPad ever with M4 chip and OLED display.", "price": 1099.99, "stock_quantity": 90, "sku": "ELEC-IPDP", "image_url": "https://picsum.photos/seed/ipad/400/400", "category_slug": "electronics"},
    {"name": "Premium Cotton T-Shirt", "description": "Soft organic cotton crew neck tee, perfect for everyday wear.", "price": 29.99, "stock_quantity": 500, "sku": "CLTH-PCTS", "image_url": "https://picsum.photos/seed/tshirt/400/400", "category_slug": "clothing"},
    {"name": "Slim Fit Chinos", "description": "Modern slim-fit chinos in stretch cotton twill.", "price": 59.99, "stock_quantity": 300, "sku": "CLTH-SFCH", "image_url": "https://picsum.photos/seed/chinos/400/400", "category_slug": "clothing"},
    {"name": "Leather Jacket", "description": "Classic biker leather jacket in genuine lambskin.", "price": 299.99, "stock_quantity": 50, "sku": "CLTH-LKJK", "image_url": "https://picsum.photos/seed/jacket/400/400", "category_slug": "clothing"},
    {"name": "Running Sneakers", "description": "Lightweight running shoes with responsive cushioning.", "price": 129.99, "stock_quantity": 250, "sku": "CLTH-RNSN", "image_url": "https://picsum.photos/seed/sneakers/400/400", "category_slug": "clothing"},
    {"name": "Wool Overcoat", "description": "Tailored wool blend overcoat for cold weather.", "price": 199.99, "stock_quantity": 75, "sku": "CLTH-WOOC", "image_url": "https://picsum.photos/seed/overcoat/400/400", "category_slug": "clothing"},
    {"name": "Ergonomic Office Chair", "description": "Adjustable lumbar support, breathable mesh, and armrests.", "price": 449.99, "stock_quantity": 60, "sku": "HOME-EOCH", "image_url": "https://picsum.photos/seed/chair/400/400", "category_slug": "home-garden"},
    {"name": "Standing Desk", "description": "Electric height-adjustable desk with memory presets.", "price": 599.99, "stock_quantity": 40, "sku": "HOME-STDK", "image_url": "https://picsum.photos/seed/desk/400/400", "category_slug": "home-garden"},
    {"name": "Smart LED Bulbs (4-pack)", "description": "WiFi-enabled color-changing LED bulbs, voice control compatible.", "price": 39.99, "stock_quantity": 400, "sku": "HOME-SLDB", "image_url": "https://picsum.photos/seed/bulbs/400/400", "category_slug": "home-garden"},
    {"name": "Yoga Mat Premium", "description": "Extra-thick non-slip yoga mat with carrying strap.", "price": 49.99, "stock_quantity": 350, "sku": "SPRT-YGMT", "image_url": "https://picsum.photos/seed/yogamat/400/400", "category_slug": "sports"},
    {"name": "Adjustable Dumbbells", "description": "Space-saving adjustable dumbbells, 5-52.5 lbs per hand.", "price": 349.99, "stock_quantity": 100, "sku": "SPRT-ADJD", "image_url": "https://picsum.photos/seed/dumbbells/400/400", "category_slug": "sports"},
    {"name": "Resistance Bands Set", "description": "5-level resistance bands with door anchor and handles.", "price": 24.99, "stock_quantity": 600, "sku": "SPRT-RSBD", "image_url": "https://picsum.photos/seed/bands/400/400", "category_slug": "sports"},
    {"name": "Clean Code", "description": "A Handbook of Agile Software Craftsmanship by Robert C. Martin.", "price": 34.99, "stock_quantity": 200, "sku": "BOOK-CLCD", "image_url": "https://picsum.photos/seed/cleancode/400/400", "category_slug": "books"},
    {"name": "Designing Data-Intensive Apps", "description": "The big ideas behind reliable, scalable systems by Martin Kleppmann.", "price": 44.99, "stock_quantity": 150, "sku": "BOOK-DDIA", "image_url": "https://picsum.photos/seed/ddia/400/400", "category_slug": "books"},
    {"name": "Vitamin C Serum", "description": "Brightening and anti-aging serum with 20% vitamin C.", "price": 28.99, "stock_quantity": 300, "sku": "BEAU-VCSR", "image_url": "https://picsum.photos/seed/serum/400/400", "category_slug": "beauty"},
    {"name": "Mechanical Keyboard", "description": "RGB mechanical keyboard with hot-swappable switches.", "price": 89.99, "stock_quantity": 180, "sku": "ELEC-MKBD", "image_url": "https://picsum.photos/seed/keyboard/400/400", "category_slug": "electronics"},
]


async def seed():
    async with async_session() as db:
        # Check if already seeded
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("[Seed] Database already seeded, skipping.")
            return

        # Seed users
        users = [
            User(email="admin@flashcart.com", password_hash=hash_password("admin123"), name="Admin User", role="admin"),
            User(email="customer@flashcart.com", password_hash=hash_password("customer123"), name="John Doe", role="customer"),
            User(email="jane@flashcart.com", password_hash=hash_password("jane123"), name="Jane Smith", role="customer"),
            User(email="bob@flashcart.com", password_hash=hash_password("bob123"), name="Bob Wilson", role="customer"),
            User(email="alice@flashcart.com", password_hash=hash_password("alice123"), name="Alice Chen", role="customer"),
        ]
        db.add_all(users)
        await db.flush()

        # Seed categories
        cat_map = {}
        for cat_data in CATEGORIES:
            cat = Category(**cat_data)
            db.add(cat)
            await db.flush()
            cat_map[cat.slug] = cat.id

        # Seed products
        for prod_data in PRODUCTS:
            slug = prod_data.pop("category_slug")
            prod = Product(**prod_data, category_id=cat_map[slug])
            db.add(prod)

        await db.flush()

        # Create a flash sale (starts now, ends in 7 days)
        now = datetime.now(timezone.utc)
        flash_sale = FlashSale(
            product_id=1, sale_price=899.99, stock_limit=50,
            start_time=now, end_time=now + timedelta(days=7), is_active=True,
        )
        db.add(flash_sale)

        flash_sale2 = FlashSale(
            product_id=3, sale_price=199.99, stock_limit=100,
            start_time=now, end_time=now + timedelta(days=3), is_active=True,
        )
        db.add(flash_sale2)

        await db.commit()
        print("[Seed] Database seeded successfully with 5 users, 10 categories, 20 products, 2 flash sales")


if __name__ == "__main__":
    asyncio.run(seed())
