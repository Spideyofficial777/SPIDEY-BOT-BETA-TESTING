import sys
import glob
import importlib
from pathlib import Path
import asyncio
import logging
import logging.config
from datetime import date, datetime

import pytz
from aiohttp import web
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script
from plugins import web_server
import pyrogram

# 🕷️ Spidey imports
from Spidey.bot import SpideyBot
from Spidey.util.keepalive import ping_server
from Spidey.bot.clients import initialize_clients


# =========================
# LOGGING CONFIGURATION
# =========================
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

# =========================
# GLOBAL VARIABLES
# =========================
PLUGIN_PATH = "plugins/*.py"
files = glob.glob(PLUGIN_PATH)

pyrogram.utils.MIN_CHANNEL_ID = -1002294764885  # Optional ID setup

loop = asyncio.get_event_loop()


# =========================
# MAIN BOT START FUNCTION
# =========================
async def Spidey_start():
    print("\n🕷️ Initializing Spidey Filter Bot...\n")

    # ✅ Start the bot (Fixed)
    await SpideyBot.start()

    # ✅ Fetch bot info
    bot_info = await SpideyBot.get_me()
    SpideyBot.username = bot_info.username

    # ✅ Initialize extra clients
    await initialize_clients()

    # ✅ Load all plugins dynamically
    for file in files:
        with open(file) as f:
            path = Path(f.name)
            plugin_name = path.stem
            import_path = f"plugins.{plugin_name}"
            spec = importlib.util.spec_from_file_location(import_path, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[import_path] = module
            print(f"✅ Spidey Imported => {plugin_name}")

    # ✅ Keep server alive (for Heroku)
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # ✅ Load banned users & chats
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats

    # ✅ Ensure indexes
    await Media.ensure_indexes()

    # ✅ Store bot details
    me = await SpideyBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention
    SpideyBot.username = '@' + me.username

    logging.info(f"{me.first_name} | Pyrogram v{__version__} (Layer {layer}) started as @{me.username}.")
    logging.info(script.LOGO)

    # ✅ Restart Notification
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time_now = now.strftime("%H:%M:%S %p")

    try:
        await SpideyBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(me.mention, today, time_now))
        await SpideyBot.send_message(chat_id=SUPPORT_GROUP, text=f"<b>{me.mention} restarted 🤖</b>")
    except Exception as e:
        print(f"⚠️ Make your bot admin in log channel | {e}")

    # ✅ Start aiohttp web server
    app = await web_server()
    runner = web.AppRunner(app)
    await runner.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(runner, bind_address, PORT).start()

    # ✅ Idle (bot runs continuously)
    await idle()

    for admin in ADMINS:
        try:
            await SpideyBot.send_message(chat_id=admin, text=f"<b>{me.mention} bot restarted ✅</b>")
        except:
            pass

if __name__ == '__main__':
    try:
        loop.run_until_complete(Spidey_start())
    except KeyboardInterrupt:
        logging.info("🛑 Service Stopped — Bye 👋")
