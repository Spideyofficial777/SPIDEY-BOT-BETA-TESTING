from __future__ import annotations

from typing import Any, Dict

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from . import db_adapter as db
from .session_manager import is_expired, extend_session
from .utils import sanitize_token, retry_async, can_start_delivery, mark_delivery_start, mark_delivery_end, admin_log_safe
from .moderation import moderate_file


def _kb_quality(sid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("360p", callback_data=f"mv_q:{sid}:360p"),
         InlineKeyboardButton("480p", callback_data=f"mv_q:{sid}:480p"),
         InlineKeyboardButton("720p", callback_data=f"mv_q:{sid}:720p")],
        [InlineKeyboardButton("1080p", callback_data=f"mv_q:{sid}:1080p"),
         InlineKeyboardButton("4K", callback_data=f"mv_q:{sid}:2160p")]
    ])


@Client.on_callback_query(filters.regex(r"^mv_src:"))
async def cb_choose_source(client: Client, cq):
    await cq.answer()
    _, sid, source = cq.data.split(":", 2)
    sid = sanitize_token(sid)
    source = sanitize_token(source)
    sess = await db.get_pending_session(sid)
    if not sess or await is_expired(sess):
        await cq.message.reply_text("Session expired. Please /search again.")
        return
    sess["source"] = source
    await extend_session(sid)
    await cq.message.reply_text("Choose quality:", reply_markup=_kb_quality(sid))


@Client.on_callback_query(filters.regex(r"^mv_q:"))
async def cb_choose_quality(client: Client, cq):
    await cq.answer()
    _, sid, quality = cq.data.split(":", 2)
    sid = sanitize_token(sid)
    quality = sanitize_token(quality)
    sess = await db.get_pending_session(sid)
    if not sess or await is_expired(sess):
        await cq.message.reply_text("Session expired. Please /search again.")
        return
    sess["quality"] = quality
    await extend_session(sid)

    title = sess.get("title")
    review = (
        f"<b>Review</b>\n\n"
        f"Title: {title}\n"
        f"Source: {sess.get('source')}\n"
        f"Quality: {sess.get('quality')}\n\n"
        "Press Request Download to proceed."
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Request Download", callback_data=f"mv_go:{sid}")]])
    await cq.message.reply_text(review, reply_markup=kb)


@Client.on_callback_query(filters.regex(r"^mv_go:"))
async def cb_request_download(client: Client, cq):
    await cq.answer()
    _, sid = cq.data.split(":", 1)
    sid = sanitize_token(sid)

    # Per-user concurrency limiter (fast-fail before lock)
    user_id = cq.from_user.id
    if not can_start_delivery(user_id):
        await cq.message.reply_text("Please wait for the current delivery to finish.")
        return
    mark_delivery_start(user_id)

    # Acquire lock (server-side idempotency)
    if not await db.lock_session(sid):
        await cq.message.reply_text("Another request is processing. Please wait.")
        mark_delivery_end(user_id)
        return

    try:
        sess = await db.get_pending_session(sid)
        if not sess or await is_expired(sess):
            await cq.message.reply_text("Session expired. Please /search again.")
            return

        # Enforce verification & premium on server side
        if not await db.is_user_verified(user_id):
            await cq.message.reply_text("You're not verified yet. Complete verification and try again.")
            return

        selection = {
            "movie_id": sess.get("movie_id"),
            "source": sess.get("source"),
            "quality": sess.get("quality"),
        }

        file_rec = await retry_async(db.get_file_record_by_selection, selection, max_attempts=3)
        if not file_rec:
            await cq.message.reply_text("File not available for this selection.")
            return

        # Premium gating
        if file_rec.get("premium_only") and not await db.is_user_premium(user_id):
            await cq.message.reply_text("This content is for premium users. Please upgrade to proceed.")
            return

        # Moderation
        mod = moderate_file({
            "name": file_rec.get("file_name"),
            "caption": file_rec.get("caption"),
            "size": file_rec.get("file_size"),
            "mime": file_rec.get("mime_type"),
        })
        if not mod["allowed"]:
            await cq.message.reply_text(f"Delivery blocked by moderation: {mod['reason']}")
            print(f"MODERATION_REJECTED: file='{file_rec.get('file_name')}' reason='{mod['reason']}'")
            await admin_log_safe(client, f"MODERATION_REJECTED: file='{file_rec.get('file_name')}' reason='{mod['reason']}'")
            await db.store_delivery_log({"sid": sid, "user": user_id, "blocked": True, "reason": mod['reason']})
            return

        # Idempotency: mark processing then deliver
        if sess.get("state") == "delivered":
            await cq.message.reply_text("This session was already delivered.")
            return

        await db.mark_session_processing(sid)
        print(f"LOCK_ACQUIRED: sid={sid}")
        await admin_log_safe(client, f"LOCK_ACQUIRED: sid={sid}")
        print(f"DELIVERY_STARTED: sid={sid} user={user_id}")
        await admin_log_safe(client, f"DELIVERY_STARTED: sid={sid} user={user_id}")

        # Delivery (by telegram_file_id preferred)
        tg_file_id = file_rec.get("telegram_file_id")
        caption = file_rec.get("caption") or sess.get("title")
        if tg_file_id:
            await cq.message.reply_document(tg_file_id, caption=caption)
        else:
            await cq.message.reply_text("Stored file is missing Telegram file_id. Please re-index.")
            return

        await db.mark_session_delivered(sid, {"file_id": file_rec.get("_id")})
        await db.store_delivery_log({"sid": sid, "user": user_id, "delivered": True, "file": file_rec.get("_id")})
        print(f"DELIVERY_SUCCESS: sid={sid} db_id={file_rec.get('_id')}")
        await admin_log_safe(client, f"DELIVERY_SUCCESS: sid={sid} db_id={file_rec.get('_id')}")
    finally:
        await db.unlock_session(sid)
        mark_delivery_end(user_id)


