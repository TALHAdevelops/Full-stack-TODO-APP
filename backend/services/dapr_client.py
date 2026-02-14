"""Dapr client wrapper with pub/sub abstraction and fallback to direct Kafka.

When USE_DAPR=true, publishes events via Dapr sidecar HTTP API.
When USE_DAPR=false, falls back to direct Kafka via kafka_client.
"""

import json
import logging
from typing import Optional

import aiohttp

from config import settings

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = 3500
DAPR_PUBSUB_NAME = "kafka-pubsub"


async def publish_event_dapr(topic: str, data: dict, content_type: str = "application/json") -> bool:
    """Publish an event via Dapr sidecar HTTP API.

    Dapr publish URL: http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{pubsub_name}/{topic}
    """
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{DAPR_PUBSUB_NAME}/{topic}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=data,
                headers={"Content-Type": content_type},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status in (200, 204):
                    logger.debug("Dapr published to %s/%s", DAPR_PUBSUB_NAME, topic)
                    return True
                else:
                    body = await resp.text()
                    logger.error("Dapr publish failed: status=%d body=%s", resp.status, body)
                    return False
    except aiohttp.ClientConnectorError:
        logger.warning("Dapr sidecar not available at port %d", DAPR_HTTP_PORT)
        return False
    except Exception as e:
        logger.error("Dapr publish error: %s", e)
        return False


async def is_dapr_available() -> bool:
    """Check if Dapr sidecar is accessible."""
    if not settings.USE_DAPR:
        return False

    try:
        url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/healthz"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as resp:
                return resp.status == 200
    except Exception:
        return False
