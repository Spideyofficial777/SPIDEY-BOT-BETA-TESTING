from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import requests, traceback
from info import SPIDEY_CHANNEL as DUMP_GROUP

@Client.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.incoming)
async def link_handler(Mbot, message):
    link = message.matches[0].group(0)
    m = await message.reply_sticker("CAACAgUAAxkBAAITAmWEcdiJs9U2WtZXtWJlqVaI8diEAAIBAAPBJDExTOWVairA1m8eBA")

    try:
        api = "https://alphaapis.org/Instagram/dl/v1"
        response = requests.get(api, params={"url": link})

        if response.ok:
            data = response.json()
            if data.get("success") and data.get("result"):
                media = data["result"][0]
                video_url = media.get("downloadLink")
                caption = data.get("caption") or "No caption available."
                stats = data.get("statistics") or {}

                views = str(stats.get("views", 0))
                likes = str(stats.get("likes", 0))
                comments = str(stats.get("comments", 0))

                like_cb = f"alert_like_{likes}"
                comment_cb = f"alert_comment_{comments}"
                view_cb = f"alert_view_{views}"

                buttons = InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(f"❤️ {likes}", callback_data=like_cb),
                        InlineKeyboardButton(f"💬 {comments}", callback_data=comment_cb),
                        InlineKeyboardButton(f"👁 {views}", callback_data=view_cb)
                    ],
                    [
                        InlineKeyboardButton("⬇️ ᴅᴏᴡɴʟᴏᴀᴅ ᴀɢᴀɪɴ", url=video_url)
                    ]]
                )

                if "story" in media.get("type", "").lower():
                    sent = await message.reply_video(
                        video_url,
                        caption=f"<b>Instagram Story</b>\n\n<b>ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʙʏ @Spideycinemax_ai_bot</b>",
                        reply_markup=buttons
                    )
                else:
                    sent = await message.reply_video(
                        video_url,
                        caption=f"<b>{caption}</b>\n\nᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʙʏ @Spideycinemax_ai_bot</b>",
                        reply_markup=buttons
                    )

                if DUMP_GROUP:
                    await sent.copy(DUMP_GROUP)

                    # User Info
                    user = message.from_user
                    name = user.first_name or "Unknown"
                    uname = f"@{user.username}" if user.username else "No Username"
                    user_id = user.id

                    user_info = (
                        f"<b>✅ New Instagram Video Downloaded</b>\n\n"
                        f"<b>👤 Name:</b> {name}\n"
                        f"<b>🔗 Username:</b> {uname}\n"
                        f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
                        f"<b>🌐 Link:</b> <code>{link}</code>"
                    )

                    await Mbot.send_message(DUMP_GROUP, user_info)
                return

        await message.reply("🚨 ᴏᴏᴘꜱ! 🕷️ ꜱᴘɪᴅᴇʏ ᴄᴏᴜʟᴅɴ’ᴛ ғᴇᴛᴄʜ ᴛʜɪꜱ ᴛɪᴍᴇ — ✨ ᴛʀʏ ᴀɢᴀɪɴ, ᴘᴏᴡᴇʀ ᴀʟᴡᴀʏꜱ ʀᴇᴛᴜʀɴꜱ ⚡ (ᴍᴀʏʙᴇ ᴀ ꜱᴇʀᴠᴇʀ ɪꜱꜱᴜᴇ)")

    except Exception as e:
        await message.reply(f"<b>400: 🚫 Error:</b> {str(e)}")
        if DUMP_GROUP:
            await Mbot.send_message(DUMP_GROUP, f"Instagram Error: {e}\n{traceback.format_exc()}")
    finally:
        if 'm' in locals():
            await m.delete()


@Client.on_callback_query(filters.regex("^alert_"))
async def insta_callback_handler(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    if "like" in data:
        await callback_query.answer(f"❤️ Likes: {data.split('_')[-1]}", show_alert=True)
    elif "comment" in data:
        await callback_query.answer(f"💬 Comments: {data.split('_')[-1]}", show_alert=True)
    elif "view" in data:
        await callback_query.answer(f"👁 Views: {data.split('_')[-1]}", show_alert=True)
