import json
import aio_pika
from app.config import get_settings

settings = get_settings()

_connection = None
_channel = None


async def get_rabbitmq_channel() -> aio_pika.Channel:
    """Get or create a RabbitMQ channel."""
    global _connection, _channel
    if _connection is None or _connection.is_closed:
        _connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    if _channel is None or _channel.is_closed:
        _channel = await _connection.channel()
    return _channel


async def publish_message(queue_name: str, message: dict):
    """Publish a JSON message to a RabbitMQ queue."""
    channel = await get_rabbitmq_channel()
    queue = await channel.declare_queue(queue_name, durable=True)

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(message).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        ),
        routing_key=queue_name,
    )


async def close_rabbitmq():
    global _connection, _channel
    if _channel and not _channel.is_closed:
        await _channel.close()
    if _connection and not _connection.is_closed:
        await _connection.close()
