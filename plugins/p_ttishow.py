import time
import psutil
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import * #ADMINS, LOG_CHANNEL, SUPPORT_CHAT, OWNER_LNK, MELCOW_NEW_USERS, MELCOW_VID, CHNL_LNK, GRP_LNK
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings
from Script import script
from pyrogram.errors import ChatAdminRequired
import asyncio 
import traceback

"""-----------------------------------------https://t.me/spideyofficial777--------------------------------------"""
# ✅ Group Join Handler
@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    try:
        new_users = message.new_chat_members
        joined_ids = [u.id for u in new_users]

        if temp.ME in joined_ids:
            if not await db.get_chat(message.chat.id):
                total = await bot.get_chat_members_count(message.chat.id)
                joined_by = message.from_user.mention if message.from_user else "Anonymous"
                await bot.send_message(
                    LOG_CHANNEL,
                    script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, joined_by)
                )
                await db.add_chat(message.chat.id, message.chat.title)

            if message.chat.id in temp.BANNED_CHATS:
                buttons = [[
                    InlineKeyboardButton('• ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ •', url='https://t.me/codeflixsupport')
                ]]
                await message.reply(
                    text='<b>ᴄʜᴀᴛ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ 🐞\n\nᴍʏ ᴀᴅᴍɪɴꜱ ʜᴀꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ ᴍᴇ ꜰʀᴏᴍ ᴡᴏʀᴋɪɴɢ ʜᴇʀᴇ !</b>',
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                await bot.leave_chat(message.chat.id)
                return

            buttons = [[
                InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', url='https://t.me/spideyofficial777'),
                InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇꜱ', url='https://t.me/spideyofficialupdatez')
            ]]
            await message.reply_text(
                text=f"<b>Thank you for adding me to {message.chat.title} ❣️\n\nNeed help? Contact support below.</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        else:
            settings = await get_settings(message.chat.id)
            if settings.get("welcome", True):
                for u in new_users:
                    try:
                        if temp.MELCOW.get('welcome'):
                            await temp.MELCOW['welcome'].delete()
                    except:
                        pass

                    caption = script.MELCOW_ENG.format(u.mention, message.chat.title)
                    buttons = [[
                        InlineKeyboardButton('• ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇꜱ •', url='https://t.me/spideyofficialupdatez')
                    ]]
                    try:
                        temp.MELCOW['welcome'] = await message.reply_photo(
                            photo=MELCOW_VID,
                            caption=caption,
                            reply_markup=InlineKeyboardMarkup(buttons),
                            parse_mode=enums.ParseMode.HTML
                        )
                    except Exception as e:
                        print("[!] Welcome image error:", e)

            if settings.get("auto_delete", False):
                await asyncio.sleep(600)
                try:
                    await temp.MELCOW['welcome'].delete()
                except:
                    pass

    except Exception as e:
        print("ERROR in save_group")
        traceback.print_exc()
        try:
            await bot.send_message(
                LOG_CHANNEL,
                f"<b>Error in group join:</b>\n<code>{e}</code>",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass

@Client.on_message(filters.left_chat_member & filters.group)
async def user_left(bot, message):
    try:
        user = message.left_chat_member

        if user.id == temp.ME:
            # Bot removed from group
            total = await bot.get_chat_members_count(message.chat.id)
            msg = (
                f"<b>Bot removed from group: {message.chat.title}</b>\n\n"
                f"<b>ID:</b> <code>{message.chat.id}</code>\n"
                f"<b>Total Members:</b> <code>{total}</code>"
            )
            await bot.send_message(LOG_CHANNEL, msg)

        else:
            # Regular user left
            name = user.first_name
            username = f"@{user.username}" if user.username else "NoUsername"
            caption = f"<b>{name} ({username}) has left the group.\nWe will miss you!</b>"

            buttons = [[
                InlineKeyboardButton('• ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇꜱ •', url='https://t.me/spideyofficialUpdatez')
            ]]

            await message.reply_photo(
                photo=MELCOW_VID,  # Use same image as welcome
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )

    except Exception as e:
        print("ERROR in user_left")
        traceback.print_exc()
        try:
            await bot.send_message(
                LOG_CHANNEL,
                f"<b>Error in user leave:</b>\n<code>{e}</code>",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass

        
@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat Successfully Disabled')
    try:
        buttons = [[
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', url='https://telegram.me/spideyofficial_777')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_, 
            text=f'<b>ʜᴇʟʟᴏ ꜰʀɪᴇɴᴅꜱ, \nᴍʏ ᴀᴅᴍɪɴ ʜᴀꜱ ᴛᴏʟᴅ ᴍᴇ ᴛᴏ ʟᴇᴀᴠᴇ ꜰʀᴏᴍ ɢʀᴏᴜᴘ, ꜱᴏ ɪ ʜᴀᴠᴇ ᴛᴏ ɢᴏ ! \nɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ᴍᴇ ᴀɢᴀɪɴ ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ..</b> \nReason : <code>{reason}</code>',
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat Not Found In DB !")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat Successfully re-enabled")


@Client.on_message(filters.command('stats') & filters.user(ADMINS) & filters.incoming)
async def get_ststs(bot, message):
    users = await db.total_users_count()
    groups = await db.total_chat_count()
    size = get_size(await db.get_db_size())
    free = get_size(536870912)
    files = await Media.count_documents()
    db2_size = get_size(await get_files_db_size())
    db2_free = get_size(536870912)
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - time.time()))
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent()
    await message.reply_text(script.STATUS_TXT.format(users, groups, size, free, files, db2_size, db2_free, uptime, ram, cpu))



@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("Invite Link Generation Failed, Iam Not Having Sufficient Rights")
    except Exception as e:
        return await message.reply(f'Error {e}')
    await message.reply(f'Here is your Invite Link {link.invite_link}')

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    # https://t.me/GetTGLink/4185
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure I have met him before.")
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")


    
@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("Thismight be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"Successfully unbanned {k.mention}")


    
@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    raju = await message.reply('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")

@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('Getting List Of chats')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    async for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += '( Disabled Chat )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="List Of Chats")
