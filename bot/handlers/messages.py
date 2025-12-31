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
    """Handle URL messages and menu button"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    message_text = update.message.text.strip()
    
    # Check access
    if not AccessControl.check_access(user_id):
        logger.warning(f"🚫 @{username} (ID: {user_id}) tried to send message but access denied")
        return
    
    # Handle menu button
    if message_text == "🎵 Menu":
        logger.info(f"🎯 @{username} clicked Menu button")
        await update.message.reply_text(
            "Select an action:",
            reply_markup=Keyboards.main_menu(),
            parse_mode="HTML"
        )
        return
    
    # Check if we're waiting for input
    waiting_for = context.user_data.get('waiting_for')
    if not waiting_for:
        return
    
    # Handle playlist name input
    if waiting_for in ['playlist_name', 'playlist_name_all', 'playlist_name_selected']:
        await handle_playlist_name_input(update, context, message_text)
        return
    
    url = message_text
    logger.info(f"🔗 @{username} sent URL: {url}")
    
    # Validate YouTube URL
    if not YouTubeExtractor.validate_url(url):
        logger.warning(f"⚠️ Invalid YouTube URL from @{username}: {url}")
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
        logger.error(f"❌ Error processing URL from @{username}: {e}")
        await update.message.reply_text(
            MessageFormatter.error_message(f"Error loading: {str(e)}\n\nPlease try again."),
            reply_markup=Keyboards.main_menu()
        )
    finally:
        context.user_data['waiting_for'] = None


async def handle_playlist_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    """Handle playlist URL"""
    username = update.effective_user.username or update.effective_user.first_name
    
    # Show loading message
    loading_msg = await update.message.reply_text(
        MessageFormatter.loading_message("Loading playlist")
    )
    
    logger.info(f"📋 @{username} loading playlist from: {url}")
    
    # Extract playlist
    songs = YouTubeExtractor.extract_playlist(url)
    
    # Check if currently playing
    was_playing = player.is_playing
    start_index = len(player.playlist)  # Remember where new songs start
    
    # Add songs to queue
    player.playlist.extend(songs)
    
    # Update message
    if was_playing:
        await loading_msg.edit_text(
            f"{EMOJI['success']} <b>Playlist Added to Queue!</b>\n\n"
            f"📋 Added {len(songs)} songs to queue\n"
            f"📊 Total in queue: {len(player.playlist)}\n\n"
            f"Songs will play after current queue finishes.",
            parse_mode="HTML"
        )
        logger.info(f"✅ Added {len(songs)} songs to queue for @{username} (Total: {len(player.playlist)})")
    else:
        await loading_msg.edit_text(
            MessageFormatter.playlist_loaded(len(songs), len(player.playlist)),
            parse_mode="HTML"
        )
        logger.info(f"✅ Loaded {len(songs)} songs from playlist for @{username} (Total: {len(player.playlist)})")
        
        # Auto-start playback ONLY if nothing is playing
        if not player.is_playing and not player.is_paused:
            player.is_playing = True
            player.current_index = start_index
            asyncio.create_task(PlaybackManager.play_current_song(context.application))
            logger.info(f"▶️ Auto-started playback for @{username}")
    
    # Show main menu
    await update.message.reply_text(
        f"{EMOJI['success']} <b>Control Panel</b>",
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )


async def handle_video_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    """Handle single video URL"""
    username = update.effective_user.username or update.effective_user.first_name
    
    # Show loading message
    loading_msg = await update.message.reply_text(
        MessageFormatter.loading_message("Loading video")
    )
    
    logger.info(f"🎥 @{username} loading video from: {url}")
    
    # Get video info
    song = YouTubeExtractor.get_video_info(url)
    player.playlist.append(song)
    
    # Update message
    await loading_msg.edit_text(
        MessageFormatter.video_added(song, len(player.playlist)),
        parse_mode="HTML"
    )
    
    logger.info(f"✅ Added video for @{username}: '{song.title}' (Position: {len(player.playlist)})")
    
    # Auto-start playback ONLY if nothing is playing
    if not player.is_playing and not player.is_paused:
        player.is_playing = True
        player.current_index = len(player.playlist) - 1
        asyncio.create_task(PlaybackManager.play_current_song(context.application))
        logger.info(f"▶️ Auto-started playback for @{username}")
    
    # Show/update main menu
    if player.control_menu_message_id:
        try:
            await loading_msg.edit_text(
                f"{EMOJI['success']} <b>Control Panel</b>",
                reply_markup=Keyboards.main_menu(),
                parse_mode="HTML"
            )
            player.control_menu_message_id = loading_msg.message_id
        except Exception:
            msg = await update.message.reply_text(
                f"{EMOJI['success']} <b>Control Panel</b>",
                reply_markup=Keyboards.main_menu(),
                parse_mode="HTML"
            )
            player.control_menu_message_id = msg.message_id
    else:
        await loading_msg.edit_text(
            f"{EMOJI['success']} <b>Control Panel</b>",
            reply_markup=Keyboards.main_menu(),
            parse_mode="HTML"
        )
        player.control_menu_message_id = loading_msg.message_id


async def handle_playlist_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str):
    """Handle playlist name input for saving"""
    username = update.effective_user.username or update.effective_user.first_name
    waiting_for = context.user_data.get('waiting_for')
    
    # Validate name
    if len(name) < 1 or len(name) > 50:
        await update.message.reply_text(
            MessageFormatter.error_message("Playlist name must be 1-50 characters"),
            reply_markup=Keyboards.main_menu()
        )
        context.user_data['waiting_for'] = None
        return
    
    # Save playlist based on mode
    success = False
    song_count = 0
    
    if waiting_for == 'playlist_name_all' or context.user_data.get('selected_songs') is None:
        # Save all songs
        success = player.save_current_playlist(name)
        song_count = len(player.playlist)
    elif waiting_for == 'playlist_name_selected':
        # Save selected songs
        selected_songs = context.user_data.get('selected_songs', [])
        success = player.save_selected_songs(name, selected_songs)
        song_count = len(selected_songs)
    else:
        # Old behavior - save all
        success = player.save_current_playlist(name)
        song_count = len(player.playlist)
    
    if success:
        await update.message.reply_text(
            f"✅ <b>Playlist Saved!</b>\n\n"
            f"📋 Name: {name}\n"
            f"🎵 Songs: {song_count}\n\n"
            f"You can load it anytime from 'My Playlists'",
            reply_markup=Keyboards.main_menu(),
            parse_mode="HTML"
        )
        logger.info(f"✅ @{username} saved playlist '{name}' ({song_count} songs)")
    else:
        await update.message.reply_text(
            MessageFormatter.error_message("Failed to save playlist"),
            reply_markup=Keyboards.main_menu()
        )
        logger.error(f"❌ Failed to save playlist for @{username}")
    
    context.user_data['waiting_for'] = None
    context.user_data['selected_songs'] = []
