"""
WebSocket handler for real-time inventory updates (R7).

Clients connect to ws://host/ws/inventory/{product_id} to receive
live stock updates. Updates are pushed via Redis Pub/Sub whenever
a purchase occurs (normal or flash-sale).

Why WebSocket over REST polling:
  - Flash sales generate very high-frequency stock changes
  - REST polling at 1s intervals would create 1000 req/s for 1000 users
  - WebSocket pushes updates only when stock actually changes
  - Client sees stock change in ~50ms instead of up to 1s polling lag
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.redis_client import redis_client
import redis.asyncio as redis

router = APIRouter()

# Track connected WebSocket clients per product
connections: dict[int, set[WebSocket]] = {}


@router.websocket("/ws/inventory/{product_id}")
async def inventory_websocket(websocket: WebSocket, product_id: int):
    """WebSocket endpoint for real-time inventory updates.

    The client connects and receives JSON messages whenever the
    stock for product_id changes:
        {"remaining": 42, "flash_sale_id": 1}
    """
    await websocket.accept()

    # Register connection
    if product_id not in connections:
        connections[product_id] = set()
    connections[product_id].add(websocket)

    # Subscribe to Redis channel for this product
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"inventory:{product_id}")

    try:
        # Listen for Redis pub/sub messages and forward to WebSocket
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        connections[product_id].discard(websocket)
        if not connections[product_id]:
            del connections[product_id]
        await pubsub.unsubscribe(f"inventory:{product_id}")
        await pubsub.close()
