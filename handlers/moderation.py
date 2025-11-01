"""
Moderation heuristics and hook for content safety.
Do NOT process NSFW/illegal content.
"""

from __future__ import annotations

from typing import Dict

NSFW_KEYWORDS = [
    "porn", "sex", "nude", "xxx", "18+", "xnxx", "xvideos",
    "rape", "cp", "child porn", "bestiality", "beastiality"
]


def moderate_file(file_meta: Dict) -> Dict:
    """Basic moderation. Returns {allowed: bool, reason: str}.
    file_meta may include: name, caption, size, mime, tags
    """
    name = (file_meta.get("name") or "").lower()
    caption = (file_meta.get("caption") or "").lower()
    size = int(file_meta.get("size") or 0)
    mime = (file_meta.get("mime") or "").lower()

    for k in NSFW_KEYWORDS:
        if k in name or k in caption:
            return {"allowed": False, "reason": f"blocked keyword: {k}"}

    # Heuristic: extremely small unknown binaries can be suspicious
    if size > 0 and size < 1024 and mime == "application/octet-stream":
        return {"allowed": False, "reason": "suspicious tiny binary"}

    return {"allowed": True, "reason": "ok"}


