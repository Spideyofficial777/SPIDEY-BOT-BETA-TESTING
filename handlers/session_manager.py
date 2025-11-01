from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from . import db_adapter as db
from .utils import admin_log_safe

SESSION_TTL_SECONDS = 600  # 10 minutes


def _expiry() -> str:
    return (datetime.utcnow() + timedelta(seconds=SESSION_TTL_SECONDS)).isoformat()


async def create_session(user_id: int, movie: Dict[str, Any], page: int) -> str:
    session = {
        "session_id": None,
        "user_id": user_id,
        "movie_id": movie.get("id"),
        "title": movie.get("title"),
        "page": page,
        "state": "pending",
        "expires_at": _expiry(),
    }
    sid = await db.create_pending_session(session)
    return sid


async def is_expired(session: Dict[str, Any]) -> bool:
    try:
        return datetime.utcnow() > datetime.fromisoformat(session.get("expires_at"))
    except Exception:
        return True


async def extend_session(session_id: str) -> None:
    sess = await db.get_pending_session(session_id)
    if not sess:
        return
    sess["expires_at"] = _expiry()
    # Optionally log extension to admin for monitoring hot sessions
    # await admin_log_safe(client, f"SESSION_EXTENDED: sid={session_id}")


