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
    creating_alarm = context.user_data.get('creating_alarm', False)
    
    if not waiting_for and not creating_alarm:
        return
    
    # Handle alarm time input
    if creating_alarm:
        await handle_alarm_time_input(update, context, message_text)
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
    
    # Show loading message (will be edited to control panel)
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
    
    # Update message to show result
    result_text = ""
    if was_playing:
        result_text = (
            f"{EMOJI['success']} <b>Playlist Added to Queue!</b>\n\n"
            f"📋 Added {len(songs)} songs to queue\n"
            f"📊 Total in queue: {len(player.playlist)}\n\n"
            f"Songs will play after current queue finishes."
        )
        logger.info(f"✅ Added {len(songs)} songs to queue for @{username} (Total: {len(player.playlist)})")
    else:
        result_text = MessageFormatter.playlist_loaded(len(songs), len(player.playlist))
        logger.info(f"✅ Loaded {len(songs)} songs from playlist for @{username} (Total: {len(player.playlist)})")
        
        # Auto-start playback ONLY if nothing is playing
        if not player.is_playing and not player.is_paused:
            player.is_playing = True
            player.current_index = start_index
            asyncio.create_task(PlaybackManager.play_current_song(context.application))
            logger.info(f"▶️ Auto-started playback for @{username}")
    
    # Edit loading message to show control panel
    try:
        await loading_msg.edit_text(
            f"{EMOJI['success']} <b>Control Panel</b>\n\n{result_text}",
            reply_markup=Keyboards.main_menu(),
            parse_mode="HTML"
        )
        player.control_menu_message_id = loading_msg.message_id
    except Exception as e:
        logger.warning(f"Could not edit message: {e}")
        # Just update to control panel without result
        await loading_msg.edit_text(
            f"{EMOJI['success']} <b>Control Panel</b>",
            reply_markup=Keyboards.main_menu(),
            parse_mode="HTML"
        )
        player.control_menu_message_id = loading_msg.message_id



async def handle_video_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    """Handle single video URL"""
    username = update.effective_user.username or update.effective_user.first_name
    
    # Show loading message (will be edited to control panel)
    loading_msg = await update.message.reply_text(
        MessageFormatter.loading_message("Loading video")
    )
    
    logger.info(f"🎥 @{username} loading video from: {url}")
    
    # Get video info
    song = YouTubeExtractor.get_video_info(url)
    player.playlist.append(song)
    
    logger.info(f"✅ Added video for @{username}: '{song.title}' (Position: {len(player.playlist)})")
    
    # Auto-start playback ONLY if nothing is playing
    if not player.is_playing and not player.is_paused:
        player.is_playing = True
        player.current_index = len(player.playlist) - 1
        asyncio.create_task(PlaybackManager.play_current_song(context.application))
        logger.info(f"▶️ Auto-started playback for @{username}")
    
    # Edit loading message to control panel
    result_text = MessageFormatter.video_added(song, len(player.playlist))
    try:
        await loading_msg.edit_text(
            f"{EMOJI['success']} <b>Control Panel</b>\n\n{result_text}",
            reply_markup=Keyboards.main_menu(),
            parse_mode="HTML"
        )
        player.control_menu_message_id = loading_msg.message_id
    except Exception as e:
        logger.warning(f"Could not edit message: {e}")
        # Just update to control panel without result
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


async def handle_alarm_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE, time_text: str):
    """Handle alarm time input from user - edit message, delete user input"""
    username = update.effective_user.username or update.effective_user.first_name
    chat_id = update.effective_chat.id
    alarm_message_id = context.user_data.get('alarm_message_id')
    
    # Try to delete user's message immediately
    try:
        await update.message.delete()
    except Exception as e:
        logger.debug(f"Could not delete user message: {e}")
    
    # Check for cancel command
    if time_text.lower() == '/cancel':
        context.user_data['creating_alarm'] = False
        context.user_data['alarm_step'] = None
        context.user_data['alarm_time'] = None
        
        if alarm_message_id:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=alarm_message_id,
                    text="❌ Alarm creation cancelled",
                    reply_markup=Keyboards.main_menu()
                )
            except:
                pass
        return
    
    # Validate time format (HH:MM)
    import re
    time_pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$'
    match = re.match(time_pattern, time_text)
    
    if not match:
        # Edit existing message to show error
        if alarm_message_id:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=alarm_message_id,
                    text="❌ <b>Invalid time format!</b>\n\n"
                         f"You sent: <code>{time_text}</code>\n\n"
                         "Please use <b>HH:MM</b> format (24-hour)\n"
                         "Examples: 07:00, 14:30, 22:00\n\n"
                         "<i>Type /cancel to cancel</i>",
                    parse_mode='HTML'
                )
            except:
                pass
        return
    
    # Format time properly (pad with zero)
    hour, minute = match.groups()
    formatted_time = f"{int(hour):02d}:{int(minute):02d}"
    
    # Store time and move to step 2 (ringtone selection)
    context.user_data['alarm_time'] = formatted_time
    context.user_data['alarm_step'] = 'ringtone'
    
    # Import ringtones
    from .advanced import ALARM_RINGTONES
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    # Build ringtone keyboard
    keyboard = []
    for key, ringtone in ALARM_RINGTONES.items():
        keyboard.append([InlineKeyboardButton(
            ringtone['name'],
            callback_data=f"set_ringtone_{key}"
        )])
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="alarms_menu")])
    
    # Edit existing message to show ringtone selection
    if alarm_message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=alarm_message_id,
                text=f"⏰ <b>Add New Alarm</b>\n\n"
                     f"<b>Time:</b> {formatted_time} ✅\n\n"
                     f"<b>Step 2/2:</b> Select alarm sound\n\n"
                     f"Choose what to play when alarm triggers:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to edit alarm message: {e}")
    
    logger.info(f"⏰ @{username} set alarm time: {formatted_time}, selecting ringtone")
