"""
Database adapter contract for Movie Search → Session → Quality → Delivery flow.

All functions are async and should be implemented against your MongoDB.
Replace the TODO sections with real DB queries. Keep signatures identical.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta


# =========================
# SEARCH
# =========================
async def search_movies(query: str, page: int = 1) -> List[Dict[str, Any]]:
    """Return a list of movie results for a search query.
    Each result should include at least: {id, title, year, poster, sessions}
    sessions: list of sources, e.g. ["webdl", "bluray", "hdrip"].
    TODO: Implement DB-backed search.
    """
    # TODO: connect to your existing movie index/collection
    return []


# =========================
# SESSIONS
# =========================
_INMEM_SESSIONS: Dict[str, Dict[str, Any]] = {}
_DELIVERY_LOG: List[Dict[str, Any]] = []

async def create_pending_session(session_obj: Dict[str, Any]) -> str:
    """Create a pending session and return its session_id.
    session_obj: {user_id, movie_id, title, page, source?, quality?, state, expires_at}
    """
    # TODO: persist in DB, return generated id
    sid = session_obj.get("session_id") or f"sid_{int(datetime.utcnow().timestamp()*1000)}"
    _INMEM_SESSIONS[sid] = session_obj
    return sid


async def get_pending_session(session_id: str) -> Optional[Dict[str, Any]]:
    # TODO: fetch from DB
    sess = _INMEM_SESSIONS.get(session_id)
    if not sess:
        return None
    return sess


async def lock_session(session_id: str) -> bool:
    """Acquire a lock for the given session. Return True if acquired."""
    # TODO: implement atomic DB-based mutex (e.g., findOneAndUpdate with lock flag)
    sess = _INMEM_SESSIONS.get(session_id)
    if not sess:
        return False
    if sess.get("locked"):
        return False
    sess["locked"] = True
    return True


async def unlock_session(session_id: str) -> None:
    # TODO: release DB-based lock
    sess = _INMEM_SESSIONS.get(session_id)
    if sess:
        sess["locked"] = False


async def mark_session_processing(session_id: str) -> bool:
    # TODO: set state in DB
    sess = _INMEM_SESSIONS.get(session_id)
    if not sess:
        return False
    sess["state"] = "processing"
    return True


async def mark_session_delivered(session_id: str, info: Dict[str, Any]) -> bool:
    # TODO: set delivered state and store delivery info
    sess = _INMEM_SESSIONS.get(session_id)
    if not sess:
        return False
    sess["state"] = "delivered"
    sess["delivered_info"] = info
    return True


# =========================
# USER STATUS
# =========================
async def is_user_verified(user_id: int) -> bool:
    # TODO: hook to your verification DB/logic
    return True


async def is_user_premium(user_id: int) -> bool:
    # TODO: hook to your premium DB/logic
    return False


# =========================
# FILE LOOKUP
# =========================
async def get_file_record_by_selection(selection: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Map selection -> file. selection contains {movie_id, source, quality}.
    Should return {telegram_file_id, file_name, file_size, premium_only:bool, ...}
    TODO: Implement DB lookup.
    """
    # TODO: Implement real DB lookup.
    # Dummy record for wiring tests
    if selection.get("movie_id") and selection.get("source") and selection.get("quality"):
        return {
            "_id": f"{selection['movie_id']}-{selection['source']}-{selection['quality']}",
            "telegram_file_id": "CAADBAADwADw0e4GAAE7MpzQ8mF2Ag",  # TODO replace with real file_id
            "file_name": f"{selection['movie_id']}.{selection['source']}.{selection['quality']}.mkv",
            "file_size": 1024 * 1024 * 10,
            "caption": f"{selection['movie_id']} {selection['source']} {selection['quality']}",
            "mime_type": "video/x-matroska",
            "premium_only": False,
        }
    return None


# =========================
# LOGGING
# =========================
async def store_delivery_log(entry: Dict[str, Any]) -> None:
    # TODO: persist to DB
    _DELIVERY_LOG.append(entry)


