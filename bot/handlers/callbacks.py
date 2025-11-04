"""
Callback Handlers Module
Handles all button callback queries
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..core import player, PlaybackManager
from ..utils.access_control import AccessControl
from ..utils.formatters import MessageFormatter
from ..utils.keyboards import Keyboards
from ..config import EMOJI

logger = logging.getLogger(__name__)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback query router"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Check access
    if not AccessControl.check_access(user_id):
        await query.answer(
            MessageFormatter.error_message("Access denied"),
            show_alert=True
        )
        return
    
    # Check ownership for control commands
    control_commands = ["play_pause", "next", "prev", "stop", "toggle_loop", "toggle_shuffle"]
    if query.data in control_commands and not AccessControl.is_owner(user_id):
        await query.answer(
            MessageFormatter.error_message("Only the owner can control playback"),
            show_alert=True
        )
        return
    
    await query.answer()
    
    # Route to appropriate handler
    handlers = {
        "load_playlist": handle_load_playlist,
        "load_video": handle_load_video,
        "play_pause": handle_play_pause,
        "next": handle_next,
        "prev": handle_prev,
        "stop": handle_stop,
        "toggle_loop": handle_toggle_loop,
        "toggle_shuffle": handle_toggle_shuffle,
        "volume": handle_volume_menu,
        "show_queue": handle_show_queue,
        "back_to_main": handle_back_to_main,
    }
    
    # Handle volume changes
    if query.data.startswith("vol_"):
        await handle_volume_change(query, context)
        return
    
    # Execute handler
    handler = handlers.get(query.data)
    if handler:
        await handler(query, context)
    else:
        logger.warning(f"Unknown callback data: {query.data}")


async def handle_load_playlist(query, context):
    """Handle load playlist request"""
    context.user_data['waiting_for'] = 'playlist'
    await query.edit_message_text(
        f"{EMOJI['playlist']} <b>Load Playlist</b>\n\n"
        f"Please send me a YouTube playlist URL:",
        parse_mode="HTML"
    )
    logger.info("Waiting for playlist URL")


async def handle_load_video(query, context):
    """Handle load video request"""
    context.user_data['waiting_for'] = 'video'
    await query.edit_message_text(
        f"{EMOJI['video']} <b>Load Video</b>\n\n"
        f"Please send me a YouTube video URL:",
        parse_mode="HTML"
    )
    logger.info("Waiting for video URL")


async def handle_play_pause(query, context):
    """Handle play/pause toggle"""
    if not player.playlist:
        await query.edit_message_text(
            MessageFormatter.error_message("No songs in playlist. Load some music first!"),
            reply_markup=Keyboards.main_menu()
        )
        return
    
    if not player.is_playing:
        # Start playing
        player.is_playing = True
        asyncio.create_task(PlaybackManager.play_current_song(context.application))
        await query.edit_message_text(
            f"{EMOJI['play']} Starting playback...",
            reply_markup=Keyboards.main_menu()
        )
        logger.info("Started playback")
    else:
        # Toggle pause/resume
        is_paused = PlaybackManager.toggle_pause()
        status = "Paused" if is_paused else "Resumed"
        emoji = EMOJI['pause'] if is_paused else EMOJI['play']
        
        await query.edit_message_text(
            f"{emoji} {status} playback",
            reply_markup=Keyboards.main_menu()
        )
        logger.info(f"Playback {status.lower()}")


async def handle_next(query, context):
    """Handle next song"""
    if not player.playlist:
        await query.answer("No songs in playlist", show_alert=True)
        return
    
    asyncio.create_task(PlaybackManager.play_next(context.application))
    
    await query.edit_message_text(
        f"{EMOJI['next']} Skipping to next song...",
        reply_markup=Keyboards.main_menu()
    )
    logger.info("Playing next song")


async def handle_prev(query, context):
    """Handle previous song"""
    if not player.playlist:
        await query.answer("No songs in playlist", show_alert=True)
        return
    
    asyncio.create_task(PlaybackManager.play_previous(context.application))
    
    await query.edit_message_text(
        f"{EMOJI['prev']} Playing previous song...",
        reply_markup=Keyboards.main_menu()
    )
    logger.info("Playing previous song")


async def handle_stop(query, context):
    """Handle stop playback"""
    PlaybackManager.stop()
    
    await query.edit_message_text(
        f"{EMOJI['stop']} Playback stopped",
        reply_markup=Keyboards.main_menu()
    )
    logger.info("Playback stopped")


async def handle_toggle_loop(query, context):
    """Handle loop toggle"""
    loop_enabled = PlaybackManager.toggle_loop()
    status = "enabled" if loop_enabled else "disabled"
    emoji = EMOJI['loop_active'] if loop_enabled else EMOJI['loop']
    
    await query.edit_message_text(
        f"{emoji} Loop {status}",
        reply_markup=Keyboards.main_menu()
    )
    logger.info(f"Loop {status}")


async def handle_toggle_shuffle(query, context):
    """Handle shuffle toggle"""
    shuffle_enabled = PlaybackManager.toggle_shuffle()
    status = "enabled" if shuffle_enabled else "disabled"
    emoji = EMOJI['shuffle_active'] if shuffle_enabled else EMOJI['shuffle']
    
    await query.edit_message_text(
        f"{emoji} Shuffle {status}",
        reply_markup=Keyboards.main_menu()
    )
    logger.info(f"Shuffle {status}")


async def handle_volume_menu(query, context):
    """Show volume menu"""
    await query.edit_message_text(
        f"{EMOJI['volume']} <b>Volume Control</b>\n\n"
        f"Current volume: {player.volume}%\n"
        f"Select a volume level:",
        reply_markup=Keyboards.volume_menu(),
        parse_mode="HTML"
    )


async def handle_volume_change(query, context):
    """Handle volume change"""
    volume = int(query.data.split('_')[1])
    
    if PlaybackManager.set_volume(volume):
        # If currently playing, restart to apply volume
        if player.is_playing and player.mpv_process:
            PlaybackManager.stop()
            asyncio.create_task(PlaybackManager.play_current_song(context.application))
        
        await query.edit_message_text(
            MessageFormatter.volume_changed(volume),
            reply_markup=Keyboards.main_menu()
        )
        logger.info(f"Volume changed to {volume}%")


async def handle_show_queue(query, context):
    """Show current queue"""
    queue_text = MessageFormatter.queue_display()
    
    await query.edit_message_text(
        queue_text,
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )


async def handle_back_to_main(query, context):
    """Go back to main menu"""
    await query.edit_message_text(
        MessageFormatter.status_info(),
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )
