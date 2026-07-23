import time
from collections import defaultdict

from fastapi import HTTPException, Request

RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 600

_request_log: dict[str, list[float]] = defaultdict(list)


def enforce_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS

    timestamps = _request_log[ip]
    while timestamps and timestamps[0] < cutoff:
        timestamps.pop(0)

    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many messages sent. Please wait a bit and try again."
        )

    timestamps.append(now)
