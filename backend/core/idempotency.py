import time
from typing import Any, Dict, Optional, Tuple

# Simple thread-safe in-memory cache for idempotency keys with TTL (24 hours per SRS §3.6)
_IDEMPOTENCY_CACHE: Dict[str, Tuple[float, Any]] = {}
IDEMPOTENCY_TTL_SECONDS = 86400  # 24 hours


def get_cached_idempotent_response(key: Optional[str]) -> Optional[Any]:
    if not key:
        return None
    entry = _IDEMPOTENCY_CACHE.get(key)
    if not entry:
        return None
    created_at, response_data = entry
    if time.time() - created_at > IDEMPOTENCY_TTL_SECONDS:
        del _IDEMPOTENCY_CACHE[key]
        return None
    return response_data


def store_idempotent_response(key: Optional[str], response_data: Any) -> None:
    if not key:
        return
    _IDEMPOTENCY_CACHE[key] = (time.time(), response_data)
