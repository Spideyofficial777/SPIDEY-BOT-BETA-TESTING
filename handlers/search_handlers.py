from __future__ import annotations

from typing import Any, Dict, List

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from . import db_adapter as db
from .session_manager import create_session
from .utils import rate_limit_search, admin_log_safe


def _kb_results(results: List[Dict[str, Any]], page: int) -> InlineKeyboardMarkup:
    rows = []
    for r in results[:9]:
        rows.append([InlineKeyboardButton(r.get("title", "Untitled"), callback_data=f"mv_sel:{r.get('id')}:{page}")])
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"mv_pg:{page-1}"))
    nav.append(InlineKeyboardButton("➡️ Next", callback_data=f"mv_pg:{page+1}"))
    rows.append(nav)
    return InlineKeyboardMarkup(rows)


@Client.on_message(filters.private & filters.command("search"))
async def cmd_search(client: Client, message):
    user_id = message.from_user.id
    query = (" ".join(message.command[1:])).strip()
    if not query:
        await message.reply_text("Usage: /search <movie name>")
        return

    if not rate_limit_search(user_id):
        await message.reply_text("You're searching too fast. Please try again shortly.")
        return

    page = 1
    results = await db.search_movies(query, page)
    print(f"SEARCH: user={user_id} query='{query}' page={page}")
    await admin_log_safe(client, f"SEARCH: user={user_id} query='{query}' page={page}")
    await message.reply_text(
        f"Results for: {query}",
        reply_markup=_kb_results(results, page)
    )


@Client.on_callback_query(filters.regex(r"^mv_pg:"))
async def cb_page(client: Client, cq):
    await cq.answer()
    parts = cq.data.split(":")
    page = max(1, int(parts[1]))
    text = cq.message.text or ""
    query = text.replace("Results for: ", "").strip()
    results = await db.search_movies(query, page)
    await cq.message.edit_reply_markup(_kb_results(results, page))


@Client.on_callback_query(filters.regex(r"^mv_sel:"))
async def cb_select_movie(client: Client, cq):
    await cq.answer()
    _, movie_id, page_s = cq.data.split(":", 2)
    page = int(page_s)

    # TODO: fetch actual movie by id
    movie = {"id": movie_id, "title": "Selected Movie"}

    sid = await create_session(cq.from_user.id, movie, page)
    print(f"SESSION_CREATED: sid={sid} user={cq.from_user.id} movie='{movie.get('title')}'")
    await admin_log_safe(client, f"SESSION_CREATED: sid={sid} user={cq.from_user.id} movie='{movie.get('title')}'")

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("WEB-DL", callback_data=f"mv_src:{sid}:webdl"),
         InlineKeyboardButton("BLURAY", callback_data=f"mv_src:{sid}:bluray"),
         InlineKeyboardButton("HDRip", callback_data=f"mv_src:{sid}:hdrip")]
    ])
    await cq.message.reply_text(f"Session created. Choose a source for: {movie.get('title')}", reply_markup=kb)


