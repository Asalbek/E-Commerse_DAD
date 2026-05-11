"""
FlashCart — E-Commerce with Real-Time Inventory
Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import structlog
import time

from app.config import get_settings
from app.from_scratch.snowflake_id import init_generator
from app.from_scratch.rate_limiter import TokenBucketRateLimiter
from app.utils.redis_client import redis_client, close_redis
from app.utils.elasticsearch_client import close_elasticsearch
from app.utils.rabbitmq_client import close_rabbitmq
from app.observability.tracing import setup_tracing
from app.observability.metrics import setup_metrics

# Routers
from app.routers import auth, products, cart, orders, flash_sales, search, admin
from app.routers.profile import router as profile_router
from app.routers.reviews import router as reviews_router
from app.websocket.inventory_ws import router as ws_router

settings = get_settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    logger.info("Starting FlashCart", machine_id=settings.MACHINE_ID)
    init_generator(settings.MACHINE_ID)

    # Initialize rate limiter
    app.state.rate_limiter = TokenBucketRateLimiter(
        redis_client=redis_client,
        capacity=settings.RATE_LIMIT_REQUESTS,
        refill_rate=settings.RATE_LIMIT_REQUESTS / settings.RATE_LIMIT_WINDOW_SECONDS,
    )

    yield

    # Shutdown
    logger.info("Shutting down FlashCart")
    await close_redis()
    await close_elasticsearch()
    await close_rabbitmq()


app = FastAPI(
    title="FlashCart API",
    description="E-Commerce platform with real-time inventory management and flash sales",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup observability
setup_tracing(app)
setup_metrics(app)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply token-bucket rate limiting per client IP."""
    if request.url.path in ("/health", "/metrics", "/docs", "/redoc", "/openapi.json"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    rate_limiter: TokenBucketRateLimiter = request.app.state.rate_limiter

    try:
        allowed, remaining = await rate_limiter.allow_request(client_ip)
        response = await call_next(request) if allowed else Response(
            content='{"detail":"Rate limit exceeded"}',
            status_code=429,
            media_type="application/json",
        )
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
    except Exception:
        # If Redis is down, allow the request
        return await call_next(request)


# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2),
    )
    return response


# Register routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(flash_sales.router)
app.include_router(search.router)
app.include_router(admin.router)
app.include_router(profile_router)
app.include_router(reviews_router)
app.include_router(ws_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker and load balancer."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}
