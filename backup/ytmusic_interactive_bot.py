#!/usr/bin/env python3
"""
YouTube Music Player Bot for Telegram
Headless music player for Ubuntu Server using mpv and yt-dlp
"""

import asyncio
import logging
import os
import signal
import subprocess
from typing import Optional, List, Dict
from dataclasses import dataclass
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import yt_dlp

# ============================================================================
# CONFIGURATION
# ============================================================================

TOKEN = "YOUR_BOT_TOKEN_HERE"  # Ganti dengan token bot Telegram Anda
ALLOWED_USERS = []  # Kosongkan untuk allow semua user, atau isi dengan [123456789, 987654321]

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Song:
    """Represents a song in the playlist"""
    url: str
    title: str
    duration: str = "Unknown"

class PlayerState:
    """Global player state"""
    def __init__(self):
        self.playlist: List[Song] = []
        self.current_index: int = 0
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.loop_enabled: bool = False
        self.shuffle_enabled: bool = False
        self.volume: int = 50
        self.mpv_process: Optional[subprocess.Popen] = None
        self.owner_id: Optional[int] = None
        self.playback_task: Optional[asyncio.Task] = None

player = PlayerState()

# ============================================================================
# YOUTUBE DLP FUNCTIONS
# ============================================================================

def extract_playlist(url: str) -> List[Song]:
    """Extract all videos from a YouTube playlist"""
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                # It's a playlist
                songs = []
                for entry in info['entries']:
                    if entry:
                        song = Song(
                            url=f"https://www.youtube.com/watch?v={entry['id']}",
                            title=entry.get('title', 'Unknown Title'),
                            duration=str(entry.get('duration', 'Unknown'))
                        )
                        songs.append(song)
                return songs
            else:
                # Single video
                song = Song(
                    url=url,
                    title=info.get('title', 'Unknown Title'),
                    duration=str(info.get('duration', 'Unknown'))
                )
                return [song]
    except Exception as e:
        logger.error(f"Error extracting playlist: {e}")
        raise

def get_video_info(url: str) -> Song:
    """Get info for a single video"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            song = Song(
                url=url,
                title=info.get('title', 'Unknown Title'),
                duration=str(info.get('duration', 'Unknown'))
            )
            return song
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        raise

# ============================================================================
# MPV PLAYER FUNCTIONS
# ============================================================================

def start_mpv(url: str) -> subprocess.Popen:
    """Start mpv process for streaming"""
    try:
        cmd = [
            'mpv',
            '--no-video',
            '--no-terminal',
            '--quiet',
            f'--volume={player.volume}',
            url
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        
        logger.info(f"Started mpv process with PID: {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Error starting mpv: {e}")
        raise

def stop_mpv():
    """Stop the current mpv process"""
    if player.mpv_process:
        try:
            player.mpv_process.terminate()
            player.mpv_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            player.mpv_process.kill()
        except Exception as e:
            logger.error(f"Error stopping mpv: {e}")
        finally:
            player.mpv_process = None

def pause_mpv():
    """Pause the mpv process"""
    if player.mpv_process and player.is_playing:
        try:
            os.kill(player.mpv_process.pid, signal.SIGSTOP)
            player.is_paused = True
            logger.info("MPV paused")
        except Exception as e:
            logger.error(f"Error pausing mpv: {e}")

def resume_mpv():
    """Resume the mpv process"""
    if player.mpv_process and player.is_paused:
        try:
            os.kill(player.mpv_process.pid, signal.SIGCONT)
            player.is_paused = False
            logger.info("MPV resumed")
        except Exception as e:
            logger.error(f"Error resuming mpv: {e}")

# ============================================================================
# PLAYBACK MANAGEMENT
# ============================================================================

async def play_current_song(application: Application):
    """Play the current song in the playlist"""
    if not player.playlist:
        logger.warning("No songs in playlist")
        return
    
    if player.current_index >= len(player.playlist):
        player.current_index = 0
    
    current_song = player.playlist[player.current_index]
    
    try:
        # Stop any existing playback
        stop_mpv()
        
        # Start new playback
        player.mpv_process = start_mpv(current_song.url)
        player.is_playing = True
        player.is_paused = False
        
        # Notify user
        if player.owner_id:
            try:
                await application.bot.send_message(
                    chat_id=player.owner_id,
                    text=f"🎵 <b>Now Playing:</b>\n{current_song.title}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
        
        # Wait for playback to finish
        await asyncio.get_event_loop().run_in_executor(
            None, player.mpv_process.wait
        )
        
        # Check if playback finished naturally (not stopped manually)
        if player.is_playing:
            await handle_song_finished(application)
            
    except Exception as e:
        logger.error(f"Error playing song: {e}")
        if player.is_playing:
            await handle_song_finished(application)

async def handle_song_finished(application: Application):
    """Handle when a song finishes playing"""
    if player.loop_enabled:
        # Replay the same song
        await play_current_song(application)
    else:
        # Move to next song
        await play_next_song(application)

async def play_next_song(application: Application):
    """Play the next song in the playlist"""
    if not player.playlist:
        return
    
    if player.shuffle_enabled:
        # Random song
        player.current_index = random.randint(0, len(player.playlist) - 1)
    else:
        # Next song
        player.current_index += 1
        if player.current_index >= len(player.playlist):
            player.current_index = 0
    
    await play_current_song(application)

async def play_previous_song(application: Application):
    """Play the previous song in the playlist"""
    if not player.playlist:
        return
    
    if player.shuffle_enabled:
        # Random song
        player.current_index = random.randint(0, len(player.playlist) - 1)
    else:
        # Previous song
        player.current_index -= 1
        if player.current_index < 0:
            player.current_index = len(player.playlist) - 1
    
    await play_current_song(application)

# ============================================================================
# KEYBOARD LAYOUTS
# ============================================================================

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Get the main control keyboard"""
    loop_emoji = "🔂" if player.loop_enabled else "🔁"
    shuffle_emoji = "🎲" if player.shuffle_enabled else "🔀"
    play_pause_emoji = "⏸" if player.is_playing and not player.is_paused else "▶️"
    
    keyboard = [
        [
            InlineKeyboardButton("🎶 Load Playlist", callback_data="load_playlist"),
            InlineKeyboardButton("🎵 Load Video", callback_data="load_video"),
        ],
        [
            InlineKeyboardButton(play_pause_emoji, callback_data="play_pause"),
            InlineKeyboardButton("⏭ Next", callback_data="next"),
            InlineKeyboardButton("⏮ Prev", callback_data="prev"),
        ],
        [
            InlineKeyboardButton(loop_emoji, callback_data="toggle_loop"),
            InlineKeyboardButton(shuffle_emoji, callback_data="toggle_shuffle"),
            InlineKeyboardButton("⏹ Stop", callback_data="stop"),
        ],
        [
            InlineKeyboardButton("🔊 Volume", callback_data="volume"),
            InlineKeyboardButton("📜 Queue", callback_data="show_queue"),
        ],
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_volume_keyboard() -> InlineKeyboardMarkup:
    """Get the volume control keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🔇 25%", callback_data="vol_25"),
            InlineKeyboardButton("🔉 50%", callback_data="vol_50"),
        ],
        [
            InlineKeyboardButton("🔊 75%", callback_data="vol_75"),
            InlineKeyboardButton("📢 100%", callback_data="vol_100"),
        ],
        [
            InlineKeyboardButton("« Back", callback_data="back_to_main"),
        ],
    ]
    
    return InlineKeyboardMarkup(keyboard)

# ============================================================================
# ACCESS CONTROL
# ============================================================================

def check_access(user_id: int) -> bool:
    """Check if user has access to the bot"""
    if not ALLOWED_USERS:
        return True
    return user_id in ALLOWED_USERS

def is_owner(user_id: int) -> bool:
    """Check if user is the current owner"""
    if player.owner_id is None:
        player.owner_id = user_id
        return True
    return user_id == player.owner_id

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    
    if not check_access(user_id):
        await update.message.reply_text("❌ You don't have access to this bot.")
        return
    
    # Set owner if not set
    if player.owner_id is None:
        player.owner_id = user_id
    
    welcome_text = (
        "🎧 <b>YouTube Music Player Bot</b>\n\n"
        "Welcome! Use the buttons below to control the player.\n"
        "Start by loading a playlist or a single video.\n\n"
        f"📊 <b>Status:</b>\n"
        f"• Songs in queue: {len(player.playlist)}\n"
        f"• Playing: {'Yes' if player.is_playing else 'No'}\n"
        f"• Volume: {player.volume}%"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Check access
    if not check_access(user_id):
        await query.answer("❌ Access denied", show_alert=True)
        return
    
    # Check ownership for control commands
    control_commands = ["play_pause", "next", "prev", "stop", "toggle_loop", "toggle_shuffle"]
    if query.data in control_commands and not is_owner(user_id):
        await query.answer("❌ Only the owner can control playback", show_alert=True)
        return
    
    await query.answer()
    
    # Handle different callbacks
    if query.data == "load_playlist":
        await handle_load_playlist(query, context)
    
    elif query.data == "load_video":
        await handle_load_video(query, context)
    
    elif query.data == "play_pause":
        await handle_play_pause(query, context)
    
    elif query.data == "next":
        await handle_next(query, context)
    
    elif query.data == "prev":
        await handle_prev(query, context)
    
    elif query.data == "stop":
        await handle_stop(query, context)
    
    elif query.data == "toggle_loop":
        await handle_toggle_loop(query, context)
    
    elif query.data == "toggle_shuffle":
        await handle_toggle_shuffle(query, context)
    
    elif query.data == "volume":
        await handle_volume_menu(query, context)
    
    elif query.data.startswith("vol_"):
        await handle_volume_change(query, context)
    
    elif query.data == "show_queue":
        await handle_show_queue(query, context)
    
    elif query.data == "back_to_main":
        await handle_back_to_main(query, context)

# ============================================================================
# CALLBACK IMPLEMENTATIONS
# ============================================================================

async def handle_load_playlist(query, context):
    """Handle load playlist request"""
    context.user_data['waiting_for'] = 'playlist'
    await query.edit_message_text(
        "🎶 <b>Load Playlist</b>\n\n"
        "Please send me a YouTube playlist URL:",
        parse_mode="HTML"
    )

async def handle_load_video(query, context):
    """Handle load video request"""
    context.user_data['waiting_for'] = 'video'
    await query.edit_message_text(
        "🎵 <b>Load Video</b>\n\n"
        "Please send me a YouTube video URL:",
        parse_mode="HTML"
    )

async def handle_play_pause(query, context):
    """Handle play/pause toggle"""
    if not player.playlist:
        await query.edit_message_text(
            "❌ No songs in playlist. Load some music first!",
            reply_markup=get_main_keyboard()
        )
        return
    
    if not player.is_playing:
        # Start playing
        player.is_playing = True
        asyncio.create_task(play_current_song(context.application))
        await query.edit_message_text(
            "▶️ Starting playback...",
            reply_markup=get_main_keyboard()
        )
    elif player.is_paused:
        # Resume
        resume_mpv()
        await query.edit_message_text(
            "▶️ Resumed playback",
            reply_markup=get_main_keyboard()
        )
    else:
        # Pause
        pause_mpv()
        await query.edit_message_text(
            "⏸ Paused playback",
            reply_markup=get_main_keyboard()
        )

async def handle_next(query, context):
    """Handle next song"""
    if not player.playlist:
        await query.answer("No songs in playlist", show_alert=True)
        return
    
    asyncio.create_task(play_next_song(context.application))
    await query.edit_message_text(
        "⏭ Skipping to next song...",
        reply_markup=get_main_keyboard()
    )

async def handle_prev(query, context):
    """Handle previous song"""
    if not player.playlist:
        await query.answer("No songs in playlist", show_alert=True)
        return
    
    asyncio.create_task(play_previous_song(context.application))
    await query.edit_message_text(
        "⏮ Playing previous song...",
        reply_markup=get_main_keyboard()
    )

async def handle_stop(query, context):
    """Handle stop playback"""
    stop_mpv()
    player.is_playing = False
    player.is_paused = False
    
    await query.edit_message_text(
        "⏹ Playback stopped",
        reply_markup=get_main_keyboard()
    )

async def handle_toggle_loop(query, context):
    """Handle loop toggle"""
    player.loop_enabled = not player.loop_enabled
    status = "enabled" if player.loop_enabled else "disabled"
    emoji = "🔂" if player.loop_enabled else "🔁"
    
    await query.edit_message_text(
        f"{emoji} Loop {status}",
        reply_markup=get_main_keyboard()
    )

async def handle_toggle_shuffle(query, context):
    """Handle shuffle toggle"""
    player.shuffle_enabled = not player.shuffle_enabled
    status = "enabled" if player.shuffle_enabled else "disabled"
    emoji = "🎲" if player.shuffle_enabled else "🔀"
    
    await query.edit_message_text(
        f"{emoji} Shuffle {status}",
        reply_markup=get_main_keyboard()
    )

async def handle_volume_menu(query, context):
    """Show volume menu"""
    await query.edit_message_text(
        f"🔊 <b>Volume Control</b>\n\n"
        f"Current volume: {player.volume}%\n"
        f"Select a volume level:",
        reply_markup=get_volume_keyboard(),
        parse_mode="HTML"
    )

async def handle_volume_change(query, context):
    """Handle volume change"""
    volume = int(query.data.split('_')[1])
    player.volume = volume
    
    # If currently playing, restart to apply volume
    if player.is_playing and player.mpv_process:
        stop_mpv()
        asyncio.create_task(play_current_song(context.application))
    
    await query.edit_message_text(
        f"🔊 Volume set to {volume}%",
        reply_markup=get_main_keyboard()
    )

async def handle_show_queue(query, context):
    """Show current queue"""
    if not player.playlist:
        await query.edit_message_text(
            "📜 <b>Queue is empty</b>\n\n"
            "Load some music first!",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        return
    
    queue_text = f"📜 <b>Queue ({len(player.playlist)} songs)</b>\n\n"
    
    # Show first 10 songs
    for i, song in enumerate(player.playlist[:10]):
        marker = "🔊" if i == player.current_index else "  "
        queue_text += f"{marker} {i+1}. {song.title}\n"
    
    if len(player.playlist) > 10:
        queue_text += f"\n... and {len(player.playlist) - 10} more songs"
    
    await query.edit_message_text(
        queue_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

async def handle_back_to_main(query, context):
    """Go back to main menu"""
    status_text = (
        f"🎧 <b>YouTube Music Player</b>\n\n"
        f"📊 <b>Status:</b>\n"
        f"• Songs in queue: {len(player.playlist)}\n"
        f"• Playing: {'Yes' if player.is_playing else 'No'}\n"
        f"• Volume: {player.volume}%"
    )
    
    await query.edit_message_text(
        status_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

# ============================================================================
# MESSAGE HANDLERS
# ============================================================================

async def handle_url_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL messages when waiting for input"""
    user_id = update.effective_user.id
    
    if not check_access(user_id):
        return
    
    waiting_for = context.user_data.get('waiting_for')
    
    if not waiting_for:
        return
    
    url = update.message.text.strip()
    
    # Validate YouTube URL
    if 'youtube.com' not in url and 'youtu.be' not in url:
        await update.message.reply_text(
            "❌ Invalid URL. Please send a valid YouTube URL.",
            reply_markup=get_main_keyboard()
        )
        context.user_data['waiting_for'] = None
        return
    
    try:
        if waiting_for == 'playlist':
            # Load playlist
            loading_msg = await update.message.reply_text("⏳ Loading playlist...")
            
            songs = extract_playlist(url)
            player.playlist.extend(songs)
            
            await loading_msg.edit_text(
                f"✅ <b>Loaded {len(songs)} songs</b>\n\n"
                f"Total in queue: {len(player.playlist)}\n"
                f"Starting playback...",
                parse_mode="HTML"
            )
            
            # Auto-start playback if not already playing
            if not player.is_playing:
                player.is_playing = True
                player.current_index = len(player.playlist) - len(songs)
                asyncio.create_task(play_current_song(context.application))
            
        elif waiting_for == 'video':
            # Load single video
            loading_msg = await update.message.reply_text("⏳ Loading video...")
            
            song = get_video_info(url)
            player.playlist.append(song)
            
            await loading_msg.edit_text(
                f"✅ <b>Added to queue:</b>\n{song.title}\n\n"
                f"Total in queue: {len(player.playlist)}",
                parse_mode="HTML"
            )
            
            # Auto-start playback if not already playing
            if not player.is_playing:
                player.is_playing = True
                player.current_index = len(player.playlist) - 1
                asyncio.create_task(play_current_song(context.application))
        
        # Show main menu
        await update.message.reply_text(
            "🎧 <b>Control Panel</b>",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        await update.message.reply_text(
            f"❌ Error loading: {str(e)}\n\n"
            "Please try again with a valid URL.",
            reply_markup=get_main_keyboard()
        )
    
    finally:
        context.user_data['waiting_for'] = None

# ============================================================================
# ERROR HANDLER
# ============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Start the bot"""
    logger.info("Starting YouTube Music Player Bot...")
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_url_message
    ))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        stop_mpv()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        stop_mpv()
