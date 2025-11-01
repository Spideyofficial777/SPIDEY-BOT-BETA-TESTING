from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import requests, traceback
from info import SPIDEY_CHANNEL as DUMP_GROUP

# Enhanced Instagram downloader with robust error handling and support for reels/posts/stories

API_ENDPOINTS = (
    "https://alphaapis.org/Instagram/dl/v1",
    "https://savein.io/api/instagram",
)

def _valid_ig_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://") and "instagram" in url

def _build_buttons(likes: str, comments: str, views: str, download_url: str) -> InlineKeyboardMarkup:
    like_cb = f"alert_like_{likes}"
    comment_cb = f"alert_comment_{comments}"
    view_cb = f"alert_view_{views}"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"❤️ {likes}", callback_data=like_cb),
            InlineKeyboardButton(f"💬 {comments}", callback_data=comment_cb),
            InlineKeyboardButton(f"👁 {views}", callback_data=view_cb)
        ],
        [InlineKeyboardButton("⬇️ Download Again", url=download_url)]
    ])

@Client.on_message(filters.regex(r'https?://[^\s]*instagram[^\s]+') & filters.incoming)
async def link_handler(Mbot, message):
    link = message.matches[0].group(0)
    if not _valid_ig_url(link):
        return

    m = await message.reply_sticker("CAACAgUAAxkBAAITAmWEcdiJs9U2WtZXtWJlqVaI8diEAAIBAAPBJDExTOWVairA1m8eBA")

    try:
        data = None
        last_error = None
        timeout = 20
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) SpideyBot/1.0"}

        for api in API_ENDPOINTS:
            try:
                resp = requests.get(api, params={"url": link}, headers=headers, timeout=timeout)
                if not resp.ok:
                    last_error = f"HTTP {resp.status_code}"
                    continue
                j = resp.json()
                # Normalize response
                if "result" in j and j.get("success"):
                    data = j
                    break
                if "medias" in j:  # savein style
                    data = {
                        "success": True,
                        "result": [{
                            "downloadLink": j["medias"][0].get("url"),
                            "type": j["medias"][0].get("type", "video")
                        }],
                        "caption": j.get("title")
                    }
                    break
            except Exception as api_err:
                last_error = str(api_err)
                continue

        if not data or not data.get("result"):
            await message.reply(
                "🚨 Spidey couldn't fetch this Instagram media right now. Please try again later."
            )
            return

        media = data["result"][0]
        media_url = media.get("downloadLink")
        if not media_url:
            await message.reply("No downloadable media found for this link.")
            return

        caption = (data.get("caption") or "Instagram Media").strip()
        stats = data.get("statistics") or {}
        views = str(stats.get("views", 0))
        likes = str(stats.get("likes", 0))
        comments = str(stats.get("comments", 0))

        kb = _build_buttons(likes, comments, views, media_url)
        media_type = (media.get("type") or "video").lower()

        if "image" in media_type or media_url.endswith((".jpg", ".jpeg", ".png")):
            sent = await message.reply_photo(
                media_url,
                caption=f"<b>{caption}</b>\n\nDownloaded by @Spideycinemax_ai_bot",
                reply_markup=kb
            )
        else:
            sent = await message.reply_video(
                media_url,
                caption=f"<b>{caption}</b>\n\nDownloaded by @Spideycinemax_ai_bot",
                reply_markup=kb
            )

        if DUMP_GROUP:
            try:
                await sent.copy(DUMP_GROUP)
                user = message.from_user
                name = user.first_name or "Unknown"
                uname = f"@{user.username}" if user.username else "No Username"
                user_id = user.id
                user_info = (
                    f"<b>✅ New Instagram Media</b>\n\n"
                    f"<b>👤 Name:</b> {name}\n"
                    f"<b>🔗 Username:</b> {uname}\n"
                    f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
                    f"<b>🌐 Link:</b> <code>{link}</code>"
                )
                await Mbot.send_message(DUMP_GROUP, user_info)
            except Exception:
                pass

    except Exception as e:
        await message.reply(f"<b>Error:</b> {str(e)}")
        if DUMP_GROUP:
            await Mbot.send_message(DUMP_GROUP, f"Instagram Error: {e}\n{traceback.format_exc()}")
    finally:
        if 'm' in locals():
            try:
                await m.delete()
            except Exception:
                pass


@Client.on_callback_query(filters.regex("^alert_"))
async def insta_callback_handler(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    if "like" in data:
        await callback_query.answer(f"❤️ Likes: {data.split('_')[-1]}", show_alert=True)
    elif "comment" in data:
        await callback_query.answer(f"💬 Comments: {data.split('_')[-1]}", show_alert=True)
    elif "view" in data:
        await callback_query.answer(f"👁 Views: {data.split('_')[-1]}", show_alert=True)
