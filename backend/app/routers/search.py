from typing import Optional
from fastapi import APIRouter, Query

from app.services.product_service import search_products

router = APIRouter(prefix="/api/v1/search", tags=["Search"])


@router.get("")
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Full-text search products using Elasticsearch.

    Supports fuzzy matching, autocomplete, and category filtering.
    """
    return await search_products(q, category, page, page_size)
