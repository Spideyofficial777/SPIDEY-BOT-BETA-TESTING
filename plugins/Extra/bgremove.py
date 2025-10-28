import os
import aiohttp
import aiofiles
from aiohttp import ContentTypeError
from pyrogram import Client, filters

def check_filename(filroid):
    if os.path.exists(filroid):
        no = 1
        while True:
            ult = "{0}_{2}{1}".format(*os.path.splitext(filroid) + (no,))
            if os.path.exists(ult):
                no += 1
            else:
                return ult
    return filroid

async def RemoveBG(input_file_name):
    headers = {"X-API-Key": "M8ViZgeq6vyJdVHUx7Si2mTh"}
    files = {"image_file": open(input_file_name, "rb").read()}
    async with aiohttp.ClientSession() as ses:
        async with ses.post(
            "https://api.remove.bg/v1.0/removebg", headers=headers, data=files
        ) as y:
            contentType = y.headers.get("content-type")
            if "image" not in contentType:
                return False, (await y.json())

            name = check_filename("ꜱᴘɪᴅᴇʏ.png")
            file = await aiofiles.open(name, "wb")
            await file.write(await y.read())
            await file.close()
            return True, name


@Client.on_message(filters.command("rmbg"))
async def rmbg(bot, message):
  rmbg = await message.reply("ᴘʀᴏᴄᴇꜱꜱɪɴɢ...") 
  replied = message.reply_to_message
  if not replied:
      return await rmbg.edit("Reply to a photo to Remove it's Backgroud")

  if replied.photo:
      photo = await bot.download_media(replied)
      x, y = await RemoveBG(photo)
      os.remove(photo)
      if not x:
          bruh = y["errors"][0]
          details = bruh.get("detail", "")
          return await rmbg.edit(f"ERROR ~ {bruh['title']},\n{details}")
      await message.reply_photo(photo=y,caption="<b>🌟ᴛᴀ-ᴅᴀ! ʏᴏᴜʀ ɪᴍᴀɢᴇ ɪꜱ ɴᴏᴡ ꜰʟᴀᴡʟᴇꜱꜱʟʏ ᴛʀᴀɴꜱꜰᴏʀᴍᴇᴅ ᴡɪᴛʜ ᴛʜᴇ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ʀᴇᴍᴏᴠᴇᴅ, ᴍᴀᴋɪɴɢ ɪᴛ ꜱʜɪɴᴇ ʙʀɪɢʜᴛᴇʀ ᴛʜᴀɴ ᴇᴠᴇʀ! ✨💎 ᴘᴇʀꜰᴇᴄᴛʟʏ ᴄʀᴀꜰᴛᴇᴅ ꜰᴏʀ ᴀɴ ᴇxᴛʀᴀᴏʀᴅɪɴᴀʀʏ ʟᴏᴏᴋ.🌈🔥\n\nᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/hacker_x_official_777'>ʜᴀᴄᴋᴇʀ_x_ᴏꜰꜰɪᴄɪᴀʟ_𝟽𝟽𝟽</a></b>")
      await message.reply_document(document=y)
      await rmbg.delete()
      return os.remove(y)
  await rmbg.edit("Reply only to a photo to Remove it's Background")
