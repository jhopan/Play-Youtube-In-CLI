"""
Message Handlers Module
Handles text messages (mainly URL inputs)
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..core import player, YouTubeExtractor, PlaybackManager
from ..utils.access_control import AccessControl
from ..utils.formatters import MessageFormatter
from ..utils.keyboards import Keyboards
from ..config import EMOJI

logger = logging.getLogger(__name__)


async def handle_url_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL messages when waiting for input"""
    user_id = update.effective_user.id
    
    # Check access
    if not AccessControl.check_access(user_id):
        return
    
    # Check if we're waiting for input
    waiting_for = context.user_data.get('waiting_for')
    if not waiting_for:
        return
    
    url = update.message.text.strip()
    
    # Validate YouTube URL
    if not YouTubeExtractor.validate_url(url):
        await update.message.reply_text(
            MessageFormatter.error_message(
                "Invalid URL. Please send a valid YouTube URL."
            ),
            reply_markup=Keyboards.main_menu()
        )
        context.user_data['waiting_for'] = None
        return
    
    try:
        if waiting_for == 'playlist':
            await handle_playlist_url(update, context, url)
        elif waiting_for == 'video':
            await handle_video_url(update, context, url)
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        await update.message.reply_text(
            MessageFormatter.error_message(f"Error loading: {str(e)}\n\nPlease try again."),
            reply_markup=Keyboards.main_menu()
        )
    finally:
        context.user_data['waiting_for'] = None


async def handle_playlist_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    """Handle playlist URL"""
    # Show loading message
    loading_msg = await update.message.reply_text(
        MessageFormatter.loading_message("Loading playlist")
    )
    
    # Extract playlist
    songs = YouTubeExtractor.extract_playlist(url)
    player.playlist.extend(songs)
    
    # Update message
    await loading_msg.edit_text(
        MessageFormatter.playlist_loaded(len(songs), len(player.playlist)),
        parse_mode="HTML"
    )
    
    logger.info(f"Loaded {len(songs)} songs from playlist")
    
    # Auto-start playback if not already playing
    if not player.is_playing:
        player.is_playing = True
        player.current_index = len(player.playlist) - len(songs)
        asyncio.create_task(PlaybackManager.play_current_song(context.application))
    
    # Show main menu
    await update.message.reply_text(
        f"{EMOJI['success']} <b>Control Panel</b>",
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )


async def handle_video_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    """Handle single video URL"""
    # Show loading message
    loading_msg = await update.message.reply_text(
        MessageFormatter.loading_message("Loading video")
    )
    
    # Get video info
    song = YouTubeExtractor.get_video_info(url)
    player.playlist.append(song)
    
    # Update message
    await loading_msg.edit_text(
        MessageFormatter.video_added(song, len(player.playlist)),
        parse_mode="HTML"
    )
    
    logger.info(f"Added video: {song.title}")
    
    # Auto-start playback if not already playing
    if not player.is_playing:
        player.is_playing = True
        player.current_index = len(player.playlist) - 1
        asyncio.create_task(PlaybackManager.play_current_song(context.application))
    
    # Show main menu
    await update.message.reply_text(
        f"{EMOJI['success']} <b>Control Panel</b>",
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )
