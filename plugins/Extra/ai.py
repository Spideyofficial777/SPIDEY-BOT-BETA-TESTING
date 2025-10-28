import random
import time
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto
from pyrogram.enums import ChatAction, ParseMode
from pyrogram.errors import MediaCaptionTooLong

# API Endpoints
API_URL_GPT = "https://nandha-api.onrender.com/ai/gpt"
API_URL_BARD = "https://nandha-api.onrender.com/ai/bard"

# Helper function for API requests
def fetch_data(api_url: str, query: str) -> tuple:
    try:
        response = requests.get(f"{api_url}/{query}")
        response.raise_for_status()
        data = response.json()
        return data.get("content", "No response available."), data.get("images", [])
    except requests.exceptions.RequestException as e:
        return None, f"API request error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"

@Client.on_message(filters.command(["openai", "ai", "chatgpt", "gpt", "solve"]))
async def chatgpt_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("**Please provide a query.**")

    query = " ".join(message.command[1:])
    txt = await message.reply_text("**Processing your query...**")
    
    response, error = fetch_data(API_URL_GPT, query)
    await txt.edit(response or error)

@Client.on_message(filters.command(["bard", "gemini"]))
async def bard_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a query.")
    
    query = " ".join(message.command[1:])
    txt = await message.reply_text("**Querying Bard API...**")
    
    response, images = fetch_data(API_URL_BARD, query)
    if not images:
        return await txt.edit(response)

    medias = [InputMediaPhoto(media=url) for url in images[:-1]]
    medias.append(InputMediaPhoto(media=images[-1], caption=response))
    
    try:
        await client.send_media_group(chat_id=message.chat.id, media=medias)
        await txt.delete()
    except MediaCaptionTooLong:
        await txt.edit("Caption too long; displaying text only.\n" + response)
    except Exception as e:
        await txt.edit(f"Error: {str(e)}")
