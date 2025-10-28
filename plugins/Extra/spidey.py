import requests
from pyrogram import Client, filters
import time
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
from MukeshAPI import api
@Client.on_message(filters.command(["spidey","spideyai","soldier"],  prefixes=["+", ".", "/", "-", "?", "$","#","&"]))
async def chat_gpt(bot, message):
    
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            await message.reply_text(
            "<b>ʜᴇʏ! ɪ'ᴍ sᴘɪᴅᴇʏ. ʜᴏᴡ ᴄᴀɴ ɪ ᴀssɪsᴛ ʏᴏᴜ ᴛᴏᴅᴀʏ?</b>")
        else:
            a = message.text.split(' ', 1)[1]
            r=api.gemini(a)["results"]
            await message.reply_text(f" {r} \n\n🎉ᴘᴏᴡᴇʀᴇᴅ ʙʏ @SPIDEYOFFICIAL777 ", parse_mode=ParseMode.MARKDOWN)     
    except Exception as e:
        await message.reply_text(f"**ᴇʀʀᴏʀ: {e} ")

__mod_name__ = "Cʜᴀᴛɢᴘᴛ"
__help__ = """
 Cʜᴀᴛɢᴘᴛ ᴄᴀɴ ᴀɴsᴡᴇʀ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ  ᴀɴᴅ sʜᴏᴡs ʏᴏᴜ ᴛʜᴇ ʀᴇsᴜʟᴛ

 ❍ /chatgpt  *:* ʀᴇᴘʟʏ ᴛo ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ
 
 """
