import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import ForceReply

# Install missing dependencies if needed
try:
    from langdetect import detect
except ImportError:
    os.system("pip install langdetect edge-tts")

@Client.on_message(filters.command("tts") & filters.private)
async def tts(client, message):
    try:
        # Ask user for input text
        msg = await client.ask(
            message.chat.id,
            "<b>📢 Send me a text to convert into an audio file.</b>",
            reply_to_message_id=message.id,
            filters=filters.text,
            reply_markup=ForceReply(True)
        )

        if not msg.text:
            return await message.reply("<b>⚠️ Please send a valid text after using /tts command.</b>")

        # Show processing message
        processing_msg = await message.reply("<b>⏳ Converting to audio...</b>")

        # Clean and format text
        toConvert = msg.text.replace("\n", " ").replace("`", "").replace('"', '\\"')

        # Detect language (supports Hindi & English)
        try:
            lang = detect(toConvert)
        except:
            lang = "hi"  # Default to Hindi if detection fails

        # Select appropriate voice
        voice = "en-US-JennyNeural" if lang == 'en' else "hi-IN-SwaraNeural"

        # Optimize long text (Split if needed)
        max_length = 300  # Edge-TTS works best under 300 characters
        if len(toConvert) > max_length:
            toConvert = toConvert[:max_length]  # Trim text if too long

        # Generate TTS command
        command = f'edge-tts --voice "{voice}" --text "{toConvert}" --write-media "tts.mp3"'

        # Execute command safely
        subprocess.run(command, shell=True, check=True)

        # Send the generated audio file
        await processing_msg.delete()
        await message.reply_voice("tts.mp3", caption="🎧 Here is your audio file!")

        # Remove the file after sending
        os.remove("tts.mp3")

    except Exception as e:
        await processing_msg.edit("❌ **Something went wrong! Please try again or report the issue in our support group.**")
        print("TTS Error:", e)

        # Ensure file cleanup in case of error
        if os.path.exists("tts.mp3"):
            os.remove("tts.mp3")
            
