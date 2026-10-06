import json
import redis
from fastapi import WebSocket
from ..config import settings

CHANNEL_PREFIX='startuppilot:run:'

def publish_sync(run_id: str, event: dict):
    try:
        r=redis.Redis.from_url(settings.redis_url, decode_responses=True)
        r.publish(CHANNEL_PREFIX+run_id, json.dumps(event))
    except Exception:
        pass
