from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Dict, Tuple

from pyrogram import Client

# Use the new modular DB adapter for verification status
from handlers import db_adapter as db

# Simple in-memory cache to reduce DB hits
_VERIFY_CACHE: Dict[int, Tuple[bool, float]] = {}
_VERIFY_TTL = 60.0  # seconds


def _is_private_chat(chat_id: Any) -> bool:
	try:
		cid = int(chat_id)
		# Telegram: users are positive integers; groups/channels are negative
		return cid > 0
	except Exception:
		return False


async def ensure_verified(client: Client, chat_id: Any) -> bool:
	"""Return True if allowed to send to chat; False if blocked (and notify)."""
	if not _is_private_chat(chat_id):
		return True
	user_id = int(chat_id)
	
	# Cache first
	cached = _VERIFY_CACHE.get(user_id)
	now = time.time()
	if cached and now - cached[1] < _VERIFY_TTL:
		return cached[0]
	
	try:
		ok = await db.is_user_verified(user_id)
		_VERIFY_CACHE[user_id] = (ok, now)
		if ok:
			return True
		# Block and notify
		await client.send_message(user_id, "You are not verified yet. Please complete verification and try again.")
		return False
	except Exception:
		# Fail-safe: if verification check errors, block to be safe
		return False


def _wrap_send(method: Callable):
	async def wrapper(self: Client, *args, **kwargs):
		chat_id = kwargs.get("chat_id")
		if chat_id is None and len(args) > 0:
			chat_id = args[0]
		if not await ensure_verified(self, chat_id):
			return None
		return await method(self, *args, **kwargs)
	return wrapper


def install_verification_gate(app: Client) -> None:
	"""Monkey-patch selected Client send/copy/forward methods with verification guard."""
	targets = [
		"send_document", "send_video", "send_audio", "send_photo", "send_animation",
		"send_voice", "send_video_note", "send_media_group", "copy_message", "forward_messages"
	]
	for name in targets:
		orig = getattr(app.__class__, name, None)
		if orig and asyncio.iscoroutinefunction(orig):
			setattr(app.__class__, name, _wrap_send(orig))
