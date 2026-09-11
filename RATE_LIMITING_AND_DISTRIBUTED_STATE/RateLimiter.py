import time
import uuid

from fastapi import HTTPException, Request

from RedisClient import get_redis


LIMIT = 5
WINDOW = 60


def rate_limiter(request: Request):
    redis_client = get_redis()

    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    current_time = time.time()
    window_start = current_time - WINDOW

    redis_client.zremrangebyscore(
        key,
        0,
        window_start
    )

    request_count = redis_client.zcard(key)

    if request_count >= LIMIT:
        request.state.rate_limit = {
            "limit": LIMIT,
            "remaining": 0,
            "reset": WINDOW
        }

        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

    redis_client.zadd(
        key,
        {f"{current_time}:{uuid.uuid4()}": current_time}
    )

    redis_client.expire(key, WINDOW)

    remaining = LIMIT - request_count - 1

    request.state.rate_limit = {
        "limit": LIMIT,
        "remaining": remaining,
        "reset": WINDOW
    }

    return request.state.rate_limit