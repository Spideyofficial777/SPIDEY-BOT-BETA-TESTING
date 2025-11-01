"""
send.py - Advanced File Store Master for Spidey Bot
Enhanced with debugging, monitoring, and better error handling

Env vars required:
  - MAIN_CHANNEL: Telegram channel ID (e.g., -1001234567890)
  - FILE_BASE_URL: Base URL for downloads (e.g., https://example.com)
  - LOG_LEVEL: Debug level (INFO, DEBUG, ERROR)

Features:
  - Comprehensive logging
  - File type validation
  - Size limits
  - Progress tracking
  - Backup storage
  - User notifications
"""

import os
import math
import mimetypes
import asyncio
import logging
from uuid import uuid4
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from pyrogram import Client, filters
from pyrogram.enums import ParseMode, MessageMediaType
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    Message,
    User
)

from info import PROTECT_CONTENT
from database.file_storage_manager import file_storage_manager

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MAIN_CHANNEL = int(os.getenv("MAIN_CHANNEL", "-1002453024937") or 0)
FILE_BASE_URL = os.getenv("FILE_BASE_URL", os.getenv("FQDN", "http://localhost:5000/"))
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_MIME_TYPES = {
    'video/', 'audio/', 'image/', 'text/', 'application/pdf',
    'application/msword', 'application/vnd.openxmlformats-officedocument.'
}

@dataclass
class FileInfo:
    """Enhanced file information container"""
    file_name: str
    file_size: int
    mime_type: str
    file_type: str
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumb: Optional[str] = None

class FileStorageBot:
    """Advanced file storage bot handler"""
    
    def __init__(self):
        self.supported_media = [
            MessageMediaType.DOCUMENT,
            MessageMediaType.VIDEO, 
            MessageMediaType.AUDIO,
            MessageMediaType.PHOTO,
            MessageMediaType.ANIMATION,
            MessageMediaType.VOICE,
            MessageMediaType.VIDEO_NOTE
        ]
        self.stats = {
            "files_processed": 0,
            "total_size": 0,
            "errors": 0
        }
    
    def _bytes_to_human(self, size: int) -> str:
        """Convert bytes to human readable format"""
        if not size or size == 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB", "TB"]
        p = int(math.floor(math.log(size, 1024)))
        p = min(p, len(units) - 1)
        return f"{size / (1024 ** p):.2f} {units[p]}"
    
    def _guess_mime_type(self, file_name: str, telegram_mime: Optional[str]) -> str:
        """Enhanced MIME type detection"""
        if telegram_mime:
            return telegram_mime
        
        guessed_type, _ = mimetypes.guess_type(file_name or "")
        if guessed_type:
            return guessed_type
        
        # Fallback based on file extension
        ext = os.path.splitext(file_name or "")[1].lower()
        mime_map = {
            '.mkv': 'video/x-matroska',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.webm': 'video/webm',
            '.flv': 'video/x-flv',
        }
        return mime_map.get(ext, 'application/octet-stream')
    
    def _extract_file_info(self, message: Message) -> Optional[FileInfo]:
        """Extract comprehensive file information from message"""
        try:
            if message.document:
                return FileInfo(
                    file_name=message.document.file_name or "document",
                    file_size=message.document.file_size,
                    mime_type=message.document.mime_type or "application/octet-stream",
                    file_type="document"
                )
            elif message.video:
                return FileInfo(
                    file_name=message.video.file_name or "video",
                    file_size=message.video.file_size,
                    mime_type=message.video.mime_type or "video/mp4",
                    file_type="video",
                    duration=message.video.duration,
                    width=message.video.width,
                    height=message.video.height
                )
            elif message.audio:
                return FileInfo(
                    file_name=message.audio.file_name or "audio",
                    file_size=message.audio.file_size,
                    mime_type=message.audio.mime_type or "audio/mpeg",
                    file_type="audio",
                    duration=message.audio.duration
                )
            elif message.photo:
                return FileInfo(
                    file_name="photo.jpg",
                    file_size=message.photo.file_size,
                    mime_type="image/jpeg",
                    file_type="photo"
                )
            elif message.animation:
                return FileInfo(
                    file_name="animation.gif",
                    file_size=message.animation.file_size,
                    mime_type="image/gif",
                    file_type="animation"
                )
            elif message.voice:
                return FileInfo(
                    file_name="voice.ogg",
                    file_size=message.voice.file_size,
                    mime_type="audio/ogg",
                    file_type="voice",
                    duration=message.voice.duration
                )
            elif message.video_note:
                return FileInfo(
                    file_name="video_note.mp4",
                    file_size=message.video_note.file_size,
                    mime_type="video/mp4",
                    file_type="video_note",
                    duration=message.video_note.duration
                )
        except Exception as e:
            logger.error(f"Error extracting file info: {e}")
            return None
        
        return None
    
    def _validate_file(self, file_info: FileInfo) -> tuple[bool, str]:
        """Validate file before processing"""
        if file_info.file_size > MAX_FILE_SIZE:
            return False, f"File too large ({self._bytes_to_human(file_info.file_size)} > {self._bytes_to_human(MAX_FILE_SIZE)})"
        
        # Check MIME type
        if not any(file_info.mime_type.startswith(allowed) for allowed in ALLOWED_MIME_TYPES):
            return False, f"File type not allowed: {file_info.mime_type}"
        
        return True, "Valid"
    
    def _build_metadata(self, file_info: FileInfo, user: User) -> Dict[str, Any]:
        """Build comprehensive metadata for storage"""
        return {
            "secure_id": uuid4().hex,
            "uploader_id": user.id,
            "uploader_username": user.username,
            "uploader_first_name": user.first_name,
            "uploader_mention": user.mention(),
            "mime_type": file_info.mime_type,
            "file_type": file_info.file_type,
            "file_size": file_info.file_size,
            "duration": file_info.duration,
            "width": file_info.width,
            "height": file_info.height,
            "spidey_tag": "SpideyBot",
            "created_at": datetime.utcnow().isoformat(),
            "bot_version": "2.0.0"
        }
    
    def _build_channel_message(self, file_info: FileInfo, metadata: Dict[str, Any], download_url: str) -> tuple[str, InlineKeyboardMarkup]:
        """Build enhanced channel message with file details"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        file_size_str = self._bytes_to_human(file_info.file_size)
        
        # File type emoji
        type_emojis = {
            "video": "🎥",
            "audio": "🎵", 
            "photo": "🖼️",
            "document": "📄",
            "animation": "🎬",
            "voice": "🎤",
            "video_note": "📹"
        }
        file_emoji = type_emojis.get(file_info.file_type, "📁")
        
        # Duration info if available
        duration_info = ""
        if file_info.duration:
            minutes, seconds = divmod(file_info.duration, 60)
            duration_info = f"\n⏱️ **Duration:** {minutes:02d}:{seconds:02d}"
        
        # Resolution info if available
        resolution_info = ""
        if file_info.width and file_info.height:
            resolution_info = f"\n📐 **Resolution:** {file_info.width}x{file_info.height}"
        
        text = f"""
{file_emoji} **New File Added to Database**

📁 **File Name:** `{file_info.file_name}`
💾 **Size:** `{file_size_str}`
📊 **Type:** `{file_info.mime_type}`{duration_info}{resolution_info}
👤 **Uploaded By:** {metadata['uploader_mention']}
🆔 **User ID:** `{metadata['uploader_id']}`
🕒 **Time:** `{timestamp}`

👇 **Click below to download**
        """.strip()

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬇️ Download File", url=download_url)],
            [InlineKeyboardButton("🔗 Direct Link", url=download_url)]
        ])
        
        return text, keyboard
    
    async def _download_file(self, message: Message, file_info: FileInfo) -> Optional[bytes]:
        """Download file with progress tracking"""
        try:
            logger.info(f"Downloading file: {file_info.file_name} ({self._bytes_to_human(file_info.file_size)})")
            
            # Download in chunks for large files
            file_bytes = await message.download(in_memory=True)
            
            if hasattr(file_bytes, 'getvalue'):
                content = file_bytes.getvalue()
            else:
                content = file_bytes.read()
            
            logger.info(f"Download completed: {len(content)} bytes")
            return content
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None
    
    async def process_file(self, client: Client, message: Message) -> Optional[Dict[str, Any]]:
        """Main file processing pipeline"""
        logger.info("🚀 Starting file processing pipeline")
        
        # Validate environment
        if not MAIN_CHANNEL:
            logger.error("MAIN_CHANNEL not configured")
            return None
        
        if not FILE_BASE_URL:
            logger.warning("FILE_BASE_URL not configured, download URLs will not work")
        
        # Extract user info
        user = message.from_user
        if not user:
            logger.error("No user information found")
            return None
        
        logger.info(f"Processing file from user: {user.id} (@{user.username})")
        
        # Extract file information
        file_info = self._extract_file_info(message)
        if not file_info:
            logger.error("Could not extract file information")
            return None
        
        logger.info(f"File info: {file_info.file_name} ({file_info.mime_type}) - {self._bytes_to_human(file_info.file_size)}")
        
        # Validate file
        is_valid, validation_msg = self._validate_file(file_info)
        if not is_valid:
            logger.warning(f"File validation failed: {validation_msg}")
            await message.reply_text(f"❌ {validation_msg}")
            return None
        
        # Download file
        file_content = await self._download_file(message, file_info)
        if not file_content:
            logger.error("File download failed")
            await message.reply_text("❌ Failed to download file")
            return None
        
        # Prepare metadata
        metadata = self._build_metadata(file_info, user)
        secure_id = metadata["secure_id"]
        
        logger.info(f"Storing file with secure_id: {secure_id}")
        
        # Store in database
        try:
            file_id = await file_storage_manager.store_file(
                file_name=file_info.file_name,
                file_content=file_content,
                file_type=file_info.file_type,
                metadata=metadata
            )
            
            logger.info(f"File stored successfully with ID: {file_id}")
            
        except Exception as e:
            logger.error(f"Storage failed: {e}")
            await message.reply_text("❌ Failed to store file in database")
            return None
        
        # Build download URL
        download_url = f"{FILE_BASE_URL.rstrip('/')}/file?id={secure_id}" if FILE_BASE_URL else ""
        
        # Update statistics
        self.stats["files_processed"] += 1
        self.stats["total_size"] += file_info.file_size
        
        result = {
            "file_id": file_id,
            "secure_id": secure_id,
            "file_info": file_info,
            "metadata": metadata,
            "download_url": download_url,
            "user": user
        }
        
        logger.info("✅ File processing completed successfully")
        return result
    
    async def notify_channel(self, client: Client, result: Dict[str, Any]) -> bool:
        """Notify main channel about new file"""
        try:
            file_info = result["file_info"]
            metadata = result["metadata"]
            download_url = result["download_url"]
            
            text, keyboard = self._build_channel_message(file_info, metadata, download_url)
            
            await client.send_message(
                chat_id=MAIN_CHANNEL,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                protect_content=bool(PROTECT_CONTENT),
                reply_markup=keyboard
            )
            
            logger.info(f"✅ Notification sent to channel {MAIN_CHANNEL}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to notify channel: {e}")
            return False
    
    async def notify_user(self, client: Client, message: Message, success: bool, result: Optional[Dict[str, Any]] = None):
        """Notify user about processing result"""
        try:
            if success and result:
                file_info = result["file_info"]
                await message.reply_text(
                    f"✅ **File stored successfully!**\n\n"
                    f"📁 **File:** `{file_info.file_name}`\n"
                    f"💾 **Size:** `{self._bytes_to_human(file_info.file_size)}`\n"
                    f"🔗 **Available in channel**",
                    parse_mode=ParseMode.HTML
                )
            else:
                await message.reply_text(
                    "❌ **Failed to process file**\n\n"
                    "Please try again later or contact support.",
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")

# Global instance
file_bot = FileStorageBot()

# Main handler
@Client.on_message(
    filters.private & (
        filters.document |
        filters.video |
        filters.audio | 
        filters.photo |
        filters.animation |
        filters.voice |
        filters.video_note
    )
)
async def handle_file_upload(client: Client, message: Message):
    """Main file upload handler"""
    logger.info(f"📥 New file received from user {message.from_user.id}")
    
    try:
        # Process the file
        result = await file_bot.process_file(client, message)
        
        if result:
            # Notify channel
            channel_success = await file_bot.notify_channel(client, result)
            
            # Notify user
            await file_bot.notify_user(client, message, True, result)
            
            logger.info("🎉 File processing pipeline completed successfully")
            
        else:
            await file_bot.notify_user(client, message, False)
            logger.error("💥 File processing pipeline failed")
    
    except Exception as e:
        logger.error(f"💥 Unhandled error in file handler: {e}")
        try:
            await message.reply_text("❌ **System error occurred**\n\nPlease try again later.")
        except:
            pass

# Statistics command
@Client.on_message(filters.private & filters.command("stats"))
async def handle_stats(client: Client, message: Message):
    """Get bot statistics"""
    stats = file_bot.stats
    text = f"""
🤖 **File Storage Bot Statistics**

📊 **Files Processed:** `{stats['files_processed']}`
💾 **Total Size:** `{file_bot._bytes_to_human(stats['total_size'])}`
❌ **Errors:** `{stats['errors']}`
🔄 **Uptime:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
    """.strip()
    
    await message.reply_text(text, parse_mode=ParseMode.HTML)

# Test command
@Client.on_message(filters.private & filters.command("test"))
async def handle_test(client: Client, message: Message):
    """Test bot responsiveness"""
    await message.reply_text(
        "✅ **Bot is operational!**\n\n"
        "Send any file (document, video, audio, etc.) to store it in the database.",
        parse_mode=ParseMode.HTML
    )

if __name__ == "__main__":
    logger.info("🚀 File Storage Bot started")
    logger.info(f"📊 Configuration: MAIN_CHANNEL={MAIN_CHANNEL}, FILE_BASE_URL={FILE_BASE_URL}")