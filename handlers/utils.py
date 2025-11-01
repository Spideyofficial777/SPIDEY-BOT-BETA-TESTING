from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional
import os


_SEARCH_RATE: Dict[int, list] = {}
SEARCH_WINDOW = 15  # seconds
SEARCH_LIMIT = 5    # max queries in window per user

# In-memory per-user concurrent delivery limiter
_DELIVERY_INFLIGHT: Dict[int, int] = {}
DELIVERY_LIMIT_PER_USER = int(os.getenv("DELIVERY_CONCURRENCY_PER_USER", "1") or "1")


def rate_limit_search(user_id: int) -> bool:
    """Return True if allowed, False if rate-limited."""
    now = time.time()
    arr = _SEARCH_RATE.setdefault(user_id, [])
    arr[:] = [t for t in arr if now - t < SEARCH_WINDOW]
    if len(arr) >= SEARCH_LIMIT:
        return False
    arr.append(now)
    return True


async def retry_async(func, *args, max_attempts=3, base_delay=0.7, **kwargs):
    last_exc = None
    for i in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exc = e
            await asyncio.sleep(base_delay * (2 ** i))
    raise last_exc


def sanitize_token(token: str, max_len: int = 128) -> str:
    token = (token or "")[:max_len]
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-:|."
    return "".join(c for c in token if c in allowed)


def can_start_delivery(user_id: int) -> bool:
    count = _DELIVERY_INFLIGHT.get(user_id, 0)
    return count < DELIVERY_LIMIT_PER_USER


def mark_delivery_start(user_id: int) -> None:
    _DELIVERY_INFLIGHT[user_id] = _DELIVERY_INFLIGHT.get(user_id, 0) + 1


def mark_delivery_end(user_id: int) -> None:
    if user_id in _DELIVERY_INFLIGHT:
        _DELIVERY_INFLIGHT[user_id] = max(0, _DELIVERY_INFLIGHT[user_id] - 1)


def get_admin_chat_id() -> Optional[int]:
    try:
        val = int(os.getenv("ADMIN_LOG_CHAT_ID", "0") or "0")
        return val or None
    except Exception:
        return None


async def admin_log_safe(client, text: str) -> None:
    chat_id = get_admin_chat_id()
    if not chat_id:
        return
    try:
        await client.send_message(chat_id, text)
    except Exception:
        # Avoid raising from admin log failures
        pass


