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
    username = update.effective_user.username or update.effective_user.first_name
    
    logger.info(f"🎯 Button clicked by @{username} (ID: {user_id}): '{query.data}'")
    
    # Check access
    if not AccessControl.check_access(user_id):
        logger.warning(f"🚫 Access denied for @{username} (ID: {user_id})")
        await query.answer(
            MessageFormatter.error_message("Access denied"),
            show_alert=True
        )
        return
    
    # Check ownership for control commands
    control_commands = ["play_pause", "next", "prev", "stop", "toggle_loop", "toggle_shuffle"]
    if query.data in control_commands and not AccessControl.is_owner(user_id):
        logger.warning(f"🚫 Non-owner @{username} tried to use control: '{query.data}'")
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
        "show_info": handle_show_info,
        "show_settings": handle_show_settings,
        "toggle_yt_suggestions": handle_toggle_yt_suggestions,
        "back_to_main": handle_back_to_main,
        "auto_next_continue": handle_auto_next_continue,
        "auto_next_stop": handle_auto_next_stop,
        "suggestion_play": handle_suggestion_play,
        "suggestion_next": handle_suggestion_next,
        "suggestion_stop": handle_suggestion_stop,
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
    username = query.from_user.username or query.from_user.first_name
    context.user_data['waiting_for'] = 'playlist'
    await query.edit_message_text(
        f"{EMOJI['playlist']} <b>Load Playlist</b>\n\n"
        f"Please send me a YouTube playlist URL:",
        parse_mode="HTML"
    )
    logger.info(f"📋 @{username} requested to load playlist - waiting for URL")


async def handle_load_video(query, context):
    """Handle load video request"""
    username = query.from_user.username or query.from_user.first_name
    context.user_data['waiting_for'] = 'video'
    await query.edit_message_text(
        f"{EMOJI['video']} <b>Load Video</b>\n\n"
        f"Please send me a YouTube video URL:",
        parse_mode="HTML"
    )
    logger.info(f"🎥 @{username} requested to load video - waiting for URL")


async def handle_play_pause(query, context):
    """Handle play/pause toggle"""
    username = query.from_user.username or query.from_user.first_name
    
    if not player.playlist:
        logger.warning(f"⚠️ @{username} tried to play but playlist is empty")
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
        logger.info(f"▶️ @{username} started playback")
    else:
        # Toggle pause/resume
        is_paused = PlaybackManager.toggle_pause()
        status = "Paused" if is_paused else "Resumed"
        emoji = EMOJI['pause'] if is_paused else EMOJI['play']
        
        await query.edit_message_text(
            f"{emoji} {status} playback",
            reply_markup=Keyboards.main_menu()
        )
        logger.info(f"{'⏸️' if is_paused else '▶️'} @{username} {status.lower()} playback")


async def handle_next(query, context):
    """Handle next song"""
    username = query.from_user.username or query.from_user.first_name
    
    if not player.playlist:
        await query.answer("No songs in playlist", show_alert=True)
        logger.warning(f"⚠️ @{username} tried to skip but playlist is empty")
        return
    
    # Keep playing state active for auto-play
    player.is_playing = True
    asyncio.create_task(PlaybackManager.play_next(context.application))
    
    await query.edit_message_text(
        f"{EMOJI['next']} Skipping to next song...",
        reply_markup=Keyboards.main_menu()
    )
    logger.info(f"⏭️ @{username} skipped to next song")


async def handle_prev(query, context):
    """Handle previous song"""
    username = query.from_user.username or query.from_user.first_name
    
    if not player.playlist:
        await query.answer("No songs in playlist", show_alert=True)
        logger.warning(f"⚠️ @{username} tried to go back but playlist is empty")
        return
    
    # Keep playing state active for auto-play
    player.is_playing = True
    asyncio.create_task(PlaybackManager.play_previous(context.application))
    
    await query.edit_message_text(
        f"{EMOJI['prev']} Playing previous song...",
        reply_markup=Keyboards.main_menu()
    )
    logger.info(f"⏮️ @{username} went to previous song")


async def handle_stop(query, context):
    """Handle stop playback"""
    username = query.from_user.username or query.from_user.first_name
    PlaybackManager.stop()
    
    await query.edit_message_text(
        f"{EMOJI['stop']} Playback stopped",
        reply_markup=Keyboards.main_menu()
    )
    logger.info(f"⏹️ @{username} stopped playback")


async def handle_toggle_loop(query, context):
    """Handle loop toggle"""
    username = query.from_user.username or query.from_user.first_name
    loop_enabled = PlaybackManager.toggle_loop()
    status = "enabled" if loop_enabled else "disabled"
    emoji = EMOJI['loop_active'] if loop_enabled else EMOJI['loop']
    
    await query.edit_message_text(
        f"{emoji} Loop {status}",
        reply_markup=Keyboards.main_menu()
    )
    logger.info(f"🔁 @{username} {status} loop mode")


async def handle_toggle_shuffle(query, context):
    """Handle shuffle toggle"""
    username = query.from_user.username or query.from_user.first_name
    shuffle_enabled = PlaybackManager.toggle_shuffle()
    status = "enabled" if shuffle_enabled else "disabled"
    emoji = EMOJI['shuffle_active'] if shuffle_enabled else EMOJI['shuffle']
    
    await query.edit_message_text(
        f"{emoji} Shuffle {status}",
        reply_markup=Keyboards.main_menu()
    )
    logger.info(f"🔀 @{username} {status} shuffle mode")


async def handle_volume_menu(query, context):
    """Show volume menu"""
    username = query.from_user.username or query.from_user.first_name
    await query.edit_message_text(
        f"{EMOJI['volume']} <b>Volume Control</b>\n\n"
        f"Current volume: {player.volume}%\n"
        f"Select a volume level:",
        reply_markup=Keyboards.volume_menu(),
        parse_mode="HTML"
    )
    logger.info(f"🔊 @{username} opened volume menu (current: {player.volume}%)")


async def handle_volume_change(query, context):
    """Handle volume change"""
    username = query.from_user.username or query.from_user.first_name
    vol_action = query.data.split('_')[1]
    
    # Handle relative volume changes
    if vol_action == "up":
        from ..core.mpv_player import MPVPlayer
        old_volume = player.volume
        if MPVPlayer.volume_up(10):
            player.volume = min(100, player.volume + 10)
            await query.edit_message_text(
                f"{EMOJI['volume']} Volume increased to {player.volume}%",
                reply_markup=Keyboards.volume_menu(),
                parse_mode="HTML"
            )
            logger.info(f"🔊 @{username} increased volume: {old_volume}% → {player.volume}%")
        else:
            await query.answer("Failed to increase volume", show_alert=True)
            logger.error(f"❌ Volume increase failed for @{username}")
        return
    
    elif vol_action == "down":
        from ..core.mpv_player import MPVPlayer
        old_volume = player.volume
        if MPVPlayer.volume_down(10):
            player.volume = max(0, player.volume - 10)
            await query.edit_message_text(
                f"{EMOJI['volume']} Volume decreased to {player.volume}%",
                reply_markup=Keyboards.volume_menu(),
                parse_mode="HTML"
            )
            logger.info(f"🔉 @{username} decreased volume: {old_volume}% → {player.volume}%")
        else:
            await query.answer("Failed to decrease volume", show_alert=True)
            logger.error(f"❌ Volume decrease failed for @{username}")
        return
    
    elif vol_action == "mute":
        from ..core.mpv_player import MPVPlayer
        if MPVPlayer.toggle_mute():
            # Get current mute status from amixer to show accurate state
            import subprocess
            try:
                result = subprocess.run(
                    ["amixer", "-D", "pulse", "get", "Master"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                is_muted = "[off]" in result.stdout
                status_text = "🔇 <b>Muted</b>" if is_muted else "🔊 <b>Unmuted</b>"
            except:
                status_text = "🔇/🔊 <b>Mute toggled</b>"
            
            await query.edit_message_text(
                f"{EMOJI['volume']} Volume Control\n\n{status_text}",
                reply_markup=Keyboards.volume_menu(),
                parse_mode="HTML"
            )
            logger.info(f"🔇 @{username} toggled mute")
        else:
            await query.answer("Failed to toggle mute", show_alert=True)
            logger.error(f"❌ Mute toggle failed for @{username}")
        return
    
    # Handle preset volume levels
    volume = int(vol_action)
    old_volume = player.volume
    
    if PlaybackManager.set_volume(volume):
        # If currently playing, restart to apply volume
        if player.is_playing and player.mpv_process:
            PlaybackManager.stop()
            asyncio.create_task(PlaybackManager.play_current_song(context.application))
        
        await query.edit_message_text(
            MessageFormatter.volume_changed(volume),
            reply_markup=Keyboards.main_menu()
        )
        logger.info(f"🔊 @{username} set volume: {old_volume}% → {volume}%")


async def handle_show_queue(query, context):
    """Show current queue"""
    username = query.from_user.username or query.from_user.first_name
    queue_text = MessageFormatter.queue_display()
    
    await query.edit_message_text(
        queue_text,
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )
    logger.info(f"📋 @{username} viewed queue ({len(player.playlist)} songs)")


async def handle_back_to_main(query, context):
    """Go back to main menu"""
    username = query.from_user.username or query.from_user.first_name
    await query.edit_message_text(
        MessageFormatter.status_info(),
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )
    logger.info(f"↩️ @{username} returned to main menu")


async def handle_show_info(query, context):
    """Show bot and current song information"""
    username = query.from_user.username or query.from_user.first_name
    info_text = f"{EMOJI['info']} <b>Bot Information</b>\n\n"
    
    # Current song info
    if player.current_song:
        info_text += f"<b>Now Playing:</b>\n"
        info_text += f"🎵 {player.current_song.title}\n"
        info_text += f"⏱️ Duration: {player.current_song.duration}\n"
        info_text += f"🔗 <a href='{player.current_song.url}'>YouTube Link</a>\n\n"
    else:
        info_text += "No song currently playing\n\n"
    
    # Playlist info
    info_text += f"<b>Playlist:</b>\n"
    info_text += f"📀 Total songs: {len(player.playlist)}\n"
    info_text += f"▶️ Current position: {player.current_index + 1}/{len(player.playlist)}\n\n"
    
    # Settings
    info_text += f"<b>Settings:</b>\n"
    info_text += f"🔊 Volume: {player.volume}%\n"
    info_text += f"🔁 Loop: {'ON' if player.loop_enabled else 'OFF'}\n"
    info_text += f"🔀 Shuffle: {'ON' if player.shuffle_enabled else 'OFF'}\n"
    
    await query.edit_message_text(
        info_text,
        reply_markup=Keyboards.back_button(),
        parse_mode="HTML"
    )
    logger.info(f"ℹ️ @{username} viewed bot info")


async def handle_auto_next_continue(query, context):
    """Handle auto-next continue (play next song)"""
    username = query.from_user.username or query.from_user.first_name
    # Cancel the auto-next timer if it exists
    if 'auto_next_task' in context.bot_data:
        context.bot_data['auto_next_task'].cancel()
        del context.bot_data['auto_next_task']
    
    # Play next song
    await handle_next(query, context)
    logger.info(f"⏩ @{username} manually continued to next song via auto-next dialog")


async def handle_auto_next_stop(query, context):
    """Handle auto-next stop (stop playback)"""
    username = query.from_user.username or query.from_user.first_name
    # Cancel the auto-next timer if it exists
    if 'auto_next_task' in context.bot_data:
        context.bot_data['auto_next_task'].cancel()
        del context.bot_data['auto_next_task']
    
    # Stop playback
    await handle_stop(query, context)
    logger.info(f"⏹️ @{username} stopped playback via auto-next dialog")


async def handle_suggestion_play(query, context):
    """Handle play current YouTube suggestion"""
    username = query.from_user.username or query.from_user.first_name
    
    # Cancel the countdown timer if it exists
    if 'suggestion_task' in context.bot_data:
        context.bot_data['suggestion_task'].cancel()
        del context.bot_data['suggestion_task']
    
    # Get current suggestion
    suggestions = context.bot_data.get('suggestions', [])
    current_index = context.bot_data.get('suggestion_index', 0)
    
    if not suggestions or current_index >= len(suggestions):
        await query.answer("No suggestion available", show_alert=True)
        return
    
    current_suggestion = suggestions[current_index]
    
    # Add to playlist and play
    player.add_song(current_suggestion)
    
    await query.edit_message_text(
        f"{EMOJI['play']} <b>Playing suggestion:</b>\n🎵 {current_suggestion.title}",
        parse_mode="HTML"
    )
    
    # Start playback
    asyncio.create_task(PlaybackManager.play_current_song(context.application))
    
    # Clean up suggestion data
    context.bot_data.pop('suggestions', None)
    context.bot_data.pop('suggestion_index', None)
    
    logger.info(f"▶️ @{username} played YouTube suggestion: {current_suggestion.title}")


async def handle_suggestion_next(query, context):
    """Handle show next YouTube suggestion"""
    username = query.from_user.username or query.from_user.first_name
    
    # Cancel the countdown timer if it exists
    if 'suggestion_task' in context.bot_data:
        context.bot_data['suggestion_task'].cancel()
        del context.bot_data['suggestion_task']
    
    # Get suggestions
    suggestions = context.bot_data.get('suggestions', [])
    current_index = context.bot_data.get('suggestion_index', 0)
    
    if not suggestions:
        await query.answer("No suggestions available", show_alert=True)
        return
    
    # Move to next suggestion
    next_index = (current_index + 1) % len(suggestions)
    context.bot_data['suggestion_index'] = next_index
    next_suggestion = suggestions[next_index]
    
    # Show next suggestion with new countdown
    message_text = (
        f"{EMOJI['info']} <b>YouTube Suggestion {next_index + 1}/{len(suggestions)}</b>\n\n"
        f"🎵 <b>{next_suggestion.title}</b>\n"
        f"⏱️ {next_suggestion.duration}\n\n"
        f"Auto-play in <b>10</b> seconds..."
    )
    
    await query.edit_message_text(
        message_text,
        reply_markup=Keyboards.suggestion_dialog(),
        parse_mode="HTML"
    )
    
    # Start new countdown
    async def countdown():
        for remaining in range(9, -1, -1):
            await asyncio.sleep(1)
            if remaining > 0:
                new_text = message_text.replace("10", str(remaining))
                try:
                    await query.message.edit_text(
                        new_text,
                        reply_markup=Keyboards.suggestion_dialog(),
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
        
        # Auto-play after countdown
        player.add_song(next_suggestion)
        await query.message.edit_text(
            f"{EMOJI['play']} <b>Auto-playing suggestion:</b>\n🎵 {next_suggestion.title}",
            parse_mode="HTML"
        )
        asyncio.create_task(PlaybackManager.play_current_song(context.application))
        
        # Clean up
        context.bot_data.pop('suggestions', None)
        context.bot_data.pop('suggestion_index', None)
        context.bot_data.pop('suggestion_task', None)
    
    # Create and store countdown task
    task = asyncio.create_task(countdown())
    context.bot_data['suggestion_task'] = task
    
    logger.info(f"⏭️ @{username} skipped to next suggestion: {next_suggestion.title}")


async def handle_suggestion_stop(query, context):
    """Handle stop YouTube suggestions"""
    username = query.from_user.username or query.from_user.first_name
    
    # Cancel the countdown timer if it exists
    if 'suggestion_task' in context.bot_data:
        context.bot_data['suggestion_task'].cancel()
        del context.bot_data['suggestion_task']
    
    # Clean up suggestion data
    context.bot_data.pop('suggestions', None)
    context.bot_data.pop('suggestion_index', None)
    
    # Stop playback
    PlaybackManager.stop()
    
    await query.edit_message_text(
        f"{EMOJI['stop']} <b>Playback stopped</b>\n\nSuggestions cancelled.",
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )
    
    logger.info(f"⏹️ @{username} stopped YouTube suggestions and playback")


async def handle_show_settings(query, context):
    """Show settings menu"""
    username = query.from_user.username or query.from_user.first_name
    
    settings_text = (
        f"⚙️ <b>Bot Settings</b>\n\n"
        f"<b>YouTube Suggestions:</b>\n"
        f"Status: {'✅ Enabled' if player.yt_suggestions_enabled else '❌ Disabled'}\n"
        f"When enabled, bot will suggest related videos from YouTube when playlist ends.\n"
        f"When disabled, playlist will loop from beginning.\n\n"
        f"Click button below to toggle:"
    )
    
    await query.edit_message_text(
        settings_text,
        reply_markup=Keyboards.settings_menu(player.yt_suggestions_enabled),
        parse_mode="HTML"
    )
    logger.info(f"⚙️ @{username} opened settings")


async def handle_toggle_yt_suggestions(query, context):
    """Toggle YouTube suggestions feature"""
    username = query.from_user.username or query.from_user.first_name
    
    # Toggle the setting
    player.yt_suggestions_enabled = not player.yt_suggestions_enabled
    status = "enabled" if player.yt_suggestions_enabled else "disabled"
    
    settings_text = (
        f"⚙️ <b>Bot Settings</b>\n\n"
        f"<b>YouTube Suggestions:</b>\n"
        f"Status: {'✅ Enabled' if player.yt_suggestions_enabled else '❌ Disabled'}\n"
        f"When enabled, bot will suggest related videos from YouTube when playlist ends.\n"
        f"When disabled, playlist will loop from beginning.\n\n"
        f"Click button below to toggle:"
    )
    
    await query.edit_message_text(
        settings_text,
        reply_markup=Keyboards.settings_menu(player.yt_suggestions_enabled),
        parse_mode="HTML"
    )
    
    logger.info(f"🔄 @{username} {status} YouTube suggestions")

