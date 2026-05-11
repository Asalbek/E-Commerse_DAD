"""
Prometheus Metrics Setup (R12)

Exposes /metrics endpoint for Prometheus scraping.
Uses prometheus-fastapi-instrumentator for automatic
request metrics collection.
"""

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram

# Custom business metrics
orders_total = Counter(
    "flashcart_orders_total",
    "Total number of orders placed",
    ["status"]
)

flash_sale_purchases = Counter(
    "flashcart_flash_sale_purchases_total",
    "Total flash sale purchase attempts",
    ["result"]
)

search_latency = Histogram(
    "flashcart_search_latency_seconds",
    "Search query latency",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

cache_hits = Counter(
    "flashcart_cache_hits_total",
    "Cache hit count",
    ["cache_type"]
)

cache_misses = Counter(
    "flashcart_cache_misses_total",
    "Cache miss count",
    ["cache_type"]
)


def setup_metrics(app):
    """Initialize Prometheus metrics for the FastAPI app."""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/health", "/metrics"],
        inprogress_name="flashcart_requests_inprogress",
        inprogress_labels=True,
    )
    instrumentator.instrument(app).expose(app, include_in_schema=False)
