"""Kafka client wrapper with AIOKafkaProducer/Consumer, retries, and connection pooling.

Supports both local Redpanda (no auth) and cloud Redpanda (SASL/SSL).
"""

import asyncio
import json
import logging
from typing import Callable, Optional

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError

from config import settings

logger = logging.getLogger(__name__)

# Singleton instances
_producer: Optional[AIOKafkaProducer] = None
_consumers: list[AIOKafkaConsumer] = []


def _get_kafka_config() -> dict:
    """Build Kafka connection config from settings."""
    config = {
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    }

    # Cloud SASL config (Redpanda Cloud Serverless)
    if settings.KAFKA_SECURITY_PROTOCOL:
        config["security_protocol"] = settings.KAFKA_SECURITY_PROTOCOL
        config["sasl_mechanism"] = settings.KAFKA_SASL_MECHANISM
        config["sasl_plain_username"] = settings.KAFKA_SASL_USERNAME
        config["sasl_plain_password"] = settings.KAFKA_SASL_PASSWORD

    return config


async def get_producer() -> Optional[AIOKafkaProducer]:
    """Get or create a singleton Kafka producer."""
    global _producer
    if _producer is not None:
        return _producer

    try:
        config = _get_kafka_config()
        _producer = AIOKafkaProducer(
            **config,
            value_serializer=lambda v: json.dumps(v).encode("utf-8") if isinstance(v, dict) else v,
            key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
            acks="all",
            retries=3,
            retry_backoff_ms=200,
        )
        await _producer.start()
        logger.info("Kafka producer started: %s", settings.KAFKA_BOOTSTRAP_SERVERS)
        return _producer
    except KafkaConnectionError as e:
        logger.warning("Kafka producer connection failed (will retry on next publish): %s", e)
        _producer = None
        return None
    except Exception as e:
        logger.warning("Kafka producer init failed: %s", e)
        _producer = None
        return None


async def create_consumer(
    topic: str,
    group_id: str,
    callback: Callable,
) -> Optional[AIOKafkaConsumer]:
    """Create a Kafka consumer for a topic with a callback handler."""
    try:
        config = _get_kafka_config()
        consumer = AIOKafkaConsumer(
            topic,
            **config,
            group_id=group_id,
            auto_offset_reset="latest",
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        await consumer.start()
        _consumers.append(consumer)
        logger.info("Kafka consumer started: topic=%s group=%s", topic, group_id)

        # Start consuming in background
        asyncio.create_task(_consume_loop(consumer, callback, topic))
        return consumer
    except Exception as e:
        logger.warning("Kafka consumer creation failed for topic %s: %s", topic, e)
        return None


async def _consume_loop(consumer: AIOKafkaConsumer, callback: Callable, topic: str):
    """Background loop that consumes messages and dispatches to callback."""
    try:
        async for msg in consumer:
            try:
                await callback(msg.value)
            except Exception as e:
                logger.error("Error processing message from %s: %s", topic, e)
    except Exception as e:
        logger.error("Consumer loop for %s terminated: %s", topic, e)


async def publish_message(topic: str, value: dict, key: Optional[str] = None) -> bool:
    """Publish a message to a Kafka topic. Returns True on success."""
    producer = await get_producer()
    if producer is None:
        logger.warning("Kafka unavailable, message not published to %s", topic)
        return False

    try:
        key_bytes = key.encode("utf-8") if key else None
        value_bytes = json.dumps(value).encode("utf-8")
        await producer.send_and_wait(topic, value=value_bytes, key=key_bytes)
        logger.debug("Published to %s: key=%s", topic, key)
        return True
    except Exception as e:
        logger.error("Failed to publish to %s: %s", topic, e)
        return False


async def stop_all():
    """Gracefully stop all Kafka clients."""
    global _producer
    if _producer:
        try:
            await _producer.stop()
        except Exception:
            pass
        _producer = None

    for consumer in _consumers:
        try:
            await consumer.stop()
        except Exception:
            pass
    _consumers.clear()
    logger.info("All Kafka clients stopped")
