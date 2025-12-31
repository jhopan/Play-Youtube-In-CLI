"""
Advanced Features Callbacks
Handlers for queue management, favorites, history, timer, and resolution settings
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..core import player, storage
from ..utils.keyboards import Keyboards
from ..utils.formatters import format_duration
from ..utils.access_control import restricted

logger = logging.getLogger(__name__)

# ============================================================================
# QUEUE MANAGEMENT CALLBACKS
# ============================================================================

@restricted
async def queue_management_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show queue management menu"""
    query = update.callback_query
    await query.answer()
    
    text = "🎵 <b>Queue Management</b>\n\n"
    text += f"Total songs in queue: {len(player.playlist)}\n"
    text += f"Current position: {player.current_index + 1}/{len(player.playlist)}"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.queue_management_menu(),
        parse_mode='HTML'
    )

@restricted
async def queue_remove_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show song selection for removal"""
    query = update.callback_query
    await query.answer()
    
    if len(player.playlist) <= 1:
        await query.answer("⚠️ Queue is empty or has only current song!", show_alert=True)
        return
    
    text = "🗑️ <b>Remove Song from Queue</b>\n\n"
    text += "Select a song to remove:\n"
    text += "<i>(Current song cannot be removed)</i>"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.queue_remove_menu(page=0),
        parse_mode='HTML'
    )

@restricted
async def remove_queue_song_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove specific song from queue"""
    query = update.callback_query
    song_index = int(query.data.split('_')[2])
    
    if player.remove_song_from_queue(song_index):
        await query.answer("✅ Song removed from queue!")
        
        # Refresh the remove menu
        text = "🗑️ <b>Remove Song from Queue</b>\n\n"
        text += "Select a song to remove:\n"
        text += "<i>(Current song cannot be removed)</i>"
        
        await query.edit_message_text(
            text=text,
            reply_markup=Keyboards.queue_remove_menu(page=0),
            parse_mode='HTML'
        )
    else:
        await query.answer("❌ Cannot remove this song!", show_alert=True)

@restricted
async def clear_queue_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all songs from queue"""
    query = update.callback_query
    
    # Clear but keep current song
    player.clear_queue(keep_current=True)
    
    await query.answer("✅ Queue cleared (kept current song)")
    
    # Return to main menu
    from .callbacks import show_main_menu
    await show_main_menu(update, context)

# ============================================================================
# FAVORITES CALLBACKS
# ============================================================================

@restricted
async def show_favorites_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show favorites menu"""
    query = update.callback_query
    await query.answer()
    
    fav_count = len(storage.get_favorites())
    
    text = "⭐ <b>Favorites</b>\n\n"
    text += f"You have {fav_count} favorite song{'s' if fav_count != 1 else ''}.\n\n"
    
    if player.current_song:
        is_fav = storage.is_favorite(player.current_song.url)
        status = "❤️ Already in favorites" if is_fav else "🤍 Not in favorites yet"
        text += f"Current song: {status}"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.favorites_menu(),
        parse_mode='HTML'
    )

@restricted
async def toggle_favorite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle current song in favorites"""
    query = update.callback_query
    
    if not player.current_song:
        await query.answer("⚠️ No song is currently playing!", show_alert=True)
        return
    
    song_data = {
        'url': player.current_song.url,
        'title': player.current_song.title,
        'duration': player.current_song.duration
    }
    
    is_fav = storage.is_favorite(player.current_song.url)
    
    if is_fav:
        # Remove from favorites
        storage.remove_favorite(player.current_song.url)
        await query.answer("💔 Removed from favorites")
    else:
        # Add to favorites
        storage.add_favorite(song_data)
        await query.answer("❤️ Added to favorites!")
    
    # Refresh favorites menu
    await show_favorites_callback(update, context)

@restricted
async def view_favorites_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View list of favorite songs"""
    query = update.callback_query
    await query.answer()
    
    favorites = storage.get_favorites()
    
    if not favorites:
        await query.answer("⚠️ No favorites yet!", show_alert=True)
        return
    
    text = "⭐ <b>Your Favorite Songs</b>\n\n"
    text += f"Total: {len(favorites)} songs\n\n"
    text += "<i>Tap a song to play it, or tap 🗑️ to remove</i>"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.favorites_list_menu(favorites, page=0),
        parse_mode='HTML'
    )

@restricted
async def play_favorite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Play a specific favorite song"""
    query = update.callback_query
    fav_index = int(query.data.split('_')[2])
    
    favorites = storage.get_favorites()
    
    if 0 <= fav_index < len(favorites):
        fav = favorites[fav_index]
        
        # Add to queue and play
        from ..core import Song
        song = Song(
            url=fav['url'],
            title=fav['title'],
            duration=fav.get('duration', 'Unknown')
        )
        
        player.playlist.append(song)
        
        # If not playing, start
        if not player.is_playing:
            player.current_index = len(player.playlist) - 1
            from ..core import PlaybackManager
            playback_mgr = PlaybackManager()
            await playback_mgr.play_song(update, context)
        
        await query.answer(f"✅ Added: {fav['title']}")
    else:
        await query.answer("❌ Favorite not found!", show_alert=True)

@restricted
async def remove_favorite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a favorite song"""
    query = update.callback_query
    fav_index = int(query.data.split('_')[2])
    
    favorites = storage.get_favorites()
    
    if 0 <= fav_index < len(favorites):
        fav = favorites[fav_index]
        storage.remove_favorite(fav['url'])
        await query.answer("💔 Removed from favorites")
        
        # Refresh list
        await view_favorites_callback(update, context)
    else:
        await query.answer("❌ Favorite not found!", show_alert=True)

@restricted
async def play_all_favorites_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Play all favorite songs"""
    query = update.callback_query
    
    favorites = storage.get_favorites()
    
    if not favorites:
        await query.answer("⚠️ No favorites to play!", show_alert=True)
        return
    
    # Clear current queue and add all favorites
    from ..core import Song
    player.playlist.clear()
    
    for fav in favorites:
        song = Song(
            url=fav['url'],
            title=fav['title'],
            duration=fav.get('duration', 'Unknown')
        )
        player.playlist.append(song)
    
    player.current_index = 0
    
    # Start playback
    from ..core import PlaybackManager
    playback_mgr = PlaybackManager()
    await playback_mgr.play_song(update, context)
    
    await query.answer(f"✅ Playing {len(favorites)} favorites!")

# ============================================================================
# HISTORY CALLBACKS
# ============================================================================

@restricted
async def show_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show history menu"""
    query = update.callback_query
    await query.answer()
    
    history_count = len(storage.get_history())
    analytics = storage.get_analytics()
    total_plays = analytics.get('total_plays', 0)
    
    text = "📊 <b>Playback History & Analytics</b>\n\n"
    text += f"📜 History entries: {history_count}\n"
    text += f"🎵 Total plays: {total_plays}\n"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.history_menu(),
        parse_mode='HTML'
    )

@restricted
async def view_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View playback history"""
    query = update.callback_query
    await query.answer()
    
    history = storage.get_history(limit=50)
    
    if not history:
        await query.answer("⚠️ No history yet!", show_alert=True)
        return
    
    text = "📜 <b>Recent Playback History</b>\n\n"
    text += f"Showing last {len(history)} songs\n\n"
    text += "<i>Tap a song to play it again</i>"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.history_list_menu(history, page=0),
        parse_mode='HTML'
    )

@restricted
async def play_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Play a song from history"""
    query = update.callback_query
    history_index = int(query.data.split('_')[2])
    
    history = storage.get_history()
    
    if 0 <= history_index < len(history):
        item = history[history_index]
        
        from ..core import Song
        song = Song(
            url=item['url'],
            title=item['title'],
            duration=item.get('duration', 'Unknown')
        )
        
        player.playlist.append(song)
        
        if not player.is_playing:
            player.current_index = len(player.playlist) - 1
            from ..core import PlaybackManager
            playback_mgr = PlaybackManager()
            await playback_mgr.play_song(update, context)
        
        await query.answer(f"✅ Added: {item['title']}")
    else:
        await query.answer("❌ History item not found!", show_alert=True)

@restricted
async def view_top_songs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View most played songs"""
    query = update.callback_query
    await query.answer()
    
    top_songs = storage.get_top_songs(limit=10)
    
    if not top_songs:
        await query.answer("⚠️ No play data yet!", show_alert=True)
        return
    
    text = "📈 <b>Top Played Songs</b>\n\n"
    
    for i, (title, count) in enumerate(top_songs, 1):
        text += f"{i}. <b>{title}</b>\n"
        text += f"   🔁 Played {count} time{'s' if count > 1 else ''}\n\n"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.back_button(),
        parse_mode='HTML'
    )

@restricted
async def view_analytics_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View analytics dashboard"""
    query = update.callback_query
    await query.answer()
    
    analytics = storage.get_analytics()
    
    total_plays = analytics.get('total_plays', 0)
    total_time = analytics.get('total_listening_time', 0)
    
    # Convert seconds to hours:minutes
    hours = total_time // 3600
    minutes = (total_time % 3600) // 60
    
    text = "📊 <b>Analytics Dashboard</b>\n\n"
    text += f"🎵 Total plays: <b>{total_plays}</b>\n"
    text += f"⏱️ Listening time: <b>{hours}h {minutes}m</b>\n\n"
    
    # Top 3 songs
    top_songs = storage.get_top_songs(limit=3)
    if top_songs:
        text += "🏆 <b>Top 3 Songs:</b>\n"
        for i, (title, count) in enumerate(top_songs, 1):
            text += f"{i}. {title[:30]}... ({count}×)\n"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.back_button(),
        parse_mode='HTML'
    )

@restricted
async def clear_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear playback history"""
    query = update.callback_query
    
    storage.clear_history()
    await query.answer("✅ History cleared!")
    
    # Refresh history menu
    await show_history_callback(update, context)

# ============================================================================
# SLEEP TIMER CALLBACKS
# ============================================================================

@restricted
async def sleep_timer_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show sleep timer menu"""
    query = update.callback_query
    await query.answer()
    
    remaining = player.get_sleep_timer_remaining()
    
    text = "⏰ <b>Sleep Timer</b>\n\n"
    
    if remaining and remaining > 0:
        text += f"⏱️ Timer active: <b>{remaining} minutes</b> remaining\n\n"
        text += "Music will stop automatically when timer expires."
    else:
        text += "No active timer.\n\n"
        text += "Select duration to auto-stop playback:"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.sleep_timer_menu(),
        parse_mode='HTML'
    )

@restricted
async def set_sleep_timer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set sleep timer"""
    query = update.callback_query
    minutes = int(query.data.split('_')[1])
    
    player.set_sleep_timer(minutes)
    
    await query.answer(f"⏰ Sleep timer set for {minutes} minutes")
    
    # Refresh menu
    await sleep_timer_menu_callback(update, context)

@restricted
async def cancel_sleep_timer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel sleep timer"""
    query = update.callback_query
    
    player.cancel_sleep_timer()
    
    await query.answer("✅ Sleep timer cancelled")
    
    # Refresh menu
    await sleep_timer_menu_callback(update, context)

# ============================================================================
# RESOLUTION CALLBACKS
# ============================================================================

@restricted
async def change_resolution_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show resolution selector"""
    query = update.callback_query
    await query.answer()
    
    current = player.preferred_resolution
    resolution_names = {
        'audio': 'Audio Only',
        '144p': '144p (Low Quality)',
        '360p': '360p (Standard)',
        '720p': '720p (HD)'
    }
    
    text = "🎬 <b>Resolution Settings</b>\n\n"
    text += f"Current: <b>{resolution_names.get(current, current)}</b>\n\n"
    text += "Select preferred quality:\n"
    text += "• Audio Only - No video, saves bandwidth\n"
    text += "• 144p - Minimum quality, very light\n"
    text += "• 360p - Standard quality\n"
    text += "• 720p - HD quality\n\n"
    
    if player.resolution_fallback:
        text += "✅ <i>Auto-fallback enabled</i>"
    else:
        text += "❌ <i>Auto-fallback disabled</i>"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.resolution_selector_menu(),
        parse_mode='HTML'
    )

@restricted
async def set_resolution_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set resolution"""
    query = update.callback_query
    resolution = query.data.split('_')[1]
    
    player.set_resolution(resolution)
    player._auto_save_queue()
    
    resolution_names = {
        'audio': 'Audio Only',
        '144p': '144p',
        '360p': '360p',
        '720p': '720p'
    }
    
    await query.answer(f"✅ Resolution set to {resolution_names.get(resolution, resolution)}")
    
    # Refresh menu
    await change_resolution_callback(update, context)

@restricted
async def toggle_fallback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle resolution fallback"""
    query = update.callback_query
    
    player.toggle_resolution_fallback()
    player._auto_save_queue()
    
    status = "enabled" if player.resolution_fallback else "disabled"
    await query.answer(f"✅ Fallback {status}")
    
    # Return to settings
    from .callbacks import show_settings_callback
    await show_settings_callback(update, context)

# ============================================================================
# ALARMS CALLBACKS
# ============================================================================

@restricted
async def alarms_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show alarms menu"""
    query = update.callback_query
    await query.answer()
    
    alarms = storage.get_alarms()
    
    text = "⏲️ <b>Scheduled Alarms</b>\n\n"
    
    if alarms:
        text += f"Total alarms: {len(alarms)}\n\n"
        for i, alarm in enumerate(alarms, 1):
            time_str = alarm['time']
            enabled = "✅" if alarm['enabled'] else "❌"
            days = ", ".join(alarm['days']) if alarm['days'] else "Once"
            ringtone_name = alarm.get('ringtone_name', '📋 Current Queue')
            
            text += f"{i}. {enabled} <b>{time_str}</b>\n"
            text += f"   📅 {days}\n"
            text += f"   🔔 {ringtone_name}\n\n"
    else:
        text += "No alarms set.\n\n"
        text += "📌 <b>How to use:</b>\n"
        text += "1. Click 'Add Alarm'\n"
        text += "2. Send time in HH:MM format\n"
        text += "3. Choose alarm sound\n"
    
    await query.edit_message_text(
        text=text,
        reply_markup=Keyboards.alarms_menu(),
        parse_mode='HTML'
    )

# Available ringtones (YouTube URLs or local paths)
ALARM_RINGTONES = {
    'default': {'name': '🔔 Default Bell', 'url': 'https://www.youtube.com/watch?v=aR9zqepd_qA'},
    'soft': {'name': '🌊 Soft Waves', 'url': 'https://www.youtube.com/watch?v=bn9F19Hi1Lk'},
    'upbeat': {'name': '🎵 Upbeat Morning', 'url': 'https://www.youtube.com/watch?v=FTQbiNvZqaY'},
    'nature': {'name': '🌿 Nature Sounds', 'url': 'https://www.youtube.com/watch?v=eKFTSSKCzWA'},
    'classic': {'name': '🎻 Classical Wake', 'url': 'https://www.youtube.com/watch?v=NlprozGcs80'},
    'queue': {'name': '📋 Current Queue', 'url': None},
}

@restricted
async def add_alarm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start alarm creation process"""
    query = update.callback_query
    await query.answer()
    
    # Set context flag for alarm creation - step 1: time input
    context.user_data['creating_alarm'] = True
    context.user_data['alarm_step'] = 'time'
    context.user_data['alarm_message_id'] = query.message.message_id
    
    text = "⏰ <b>Add New Alarm</b>\n\n"
    text += "<b>Step 1/2:</b> Set the time\n\n"
    text += "Send time in <b>HH:MM</b> format (24-hour)\n\n"
    text += "Examples:\n"
    text += "• <code>07:00</code> - 7:00 AM\n"
    text += "• <code>14:30</code> - 2:30 PM\n"
    text += "• <code>22:00</code> - 10:00 PM\n\n"
    text += "<i>Type /cancel to cancel</i>"
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML'
    )

@restricted
async def view_alarms_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all alarms with details"""
    query = update.callback_query
    await query.answer()
    
    alarms = storage.get_alarms()
    
    text = "⏰ <b>All Alarms</b>\n\n"
    
    if alarms:
        for i, alarm in enumerate(alarms, 1):
            enabled = "✅ Enabled" if alarm['enabled'] else "❌ Disabled"
            time_str = alarm['time']
            days = ", ".join(alarm['days']) if alarm['days'] else "Once"
            playlist = alarm.get('playlist_name', 'Current Queue')
            
            text += f"<b>Alarm {i}</b> - {enabled}\n"
            text += f"🕐 Time: {time_str}\n"
            text += f"📅 Days: {days}\n"
            text += f"🎵 Playlist: {playlist}\n"
            text += f"ID: <code>{alarm['id']}</code>\n\n"
    else:
        text += "No alarms configured.\n"
    
    keyboard = [
        [{"text": "🔙 Back to Alarms", "callback_data": "alarms_menu"}]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup={"inline_keyboard": keyboard},
        parse_mode='HTML'
    )

@restricted
async def toggle_alarm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle alarm enable/disable"""
    query = update.callback_query
    alarm_id = query.data.split('_')[2]
    
    alarms = storage.get_alarms()
    for alarm in alarms:
        if alarm['id'] == alarm_id:
            alarm['enabled'] = not alarm['enabled']
            storage.save_alarms(alarms)
            status = "enabled" if alarm['enabled'] else "disabled"
            await query.answer(f"Alarm {status}")
            break
    
    # Refresh menu
    await alarms_menu_callback(update, context)

@restricted  
async def delete_alarm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete an alarm"""
    query = update.callback_query
    alarm_id = query.data.split('_')[2]
    
    alarms = storage.get_alarms()
    alarms = [a for a in alarms if a['id'] != alarm_id]
    storage.save_alarms(alarms)
    
    await query.answer("Alarm deleted")
    
    # Refresh menu
    await alarms_menu_callback(update, context)


@restricted
async def alarm_ringtone_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show ringtone selection for alarm"""
    query = update.callback_query
    await query.answer()
    
    text = "🔔 <b>Select Alarm Sound</b>\n\n"
    text += "Choose what to play when alarm triggers:\n\n"
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = []
    for key, ringtone in ALARM_RINGTONES.items():
        keyboard.append([InlineKeyboardButton(
            ringtone['name'],
            callback_data=f"set_ringtone_{key}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="alarms_menu")])
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


@restricted
async def set_alarm_ringtone_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set ringtone for alarm being created"""
    query = update.callback_query
    ringtone_key = query.data.split('_')[2]
    
    if ringtone_key in ALARM_RINGTONES:
        ringtone = ALARM_RINGTONES[ringtone_key]
        alarm_time = context.user_data.get('alarm_time')
        
        if not alarm_time:
            await query.answer("❌ No alarm time set", show_alert=True)
            return
        
        # Create alarm with ringtone
        import uuid
        alarm_id = str(uuid.uuid4())[:8]
        alarm_data = {
            'id': alarm_id,
            'time': alarm_time,
            'enabled': True,
            'days': [],
            'ringtone': ringtone_key,
            'ringtone_name': ringtone['name'],
            'ringtone_url': ringtone['url'],
            'playlist_name': ringtone['name'] if ringtone['url'] else 'Current Queue',
            'playlist_url': ringtone['url']
        }
        
        storage.add_alarm(alarm_data)
        
        # Clear context
        context.user_data['creating_alarm'] = False
        context.user_data['alarm_step'] = None
        context.user_data['alarm_time'] = None
        
        await query.answer("✅ Alarm created!")
        
        text = f"✅ <b>Alarm Created!</b>\n\n"
        text += f"⏰ Time: {alarm_time}\n"
        text += f"🔔 Sound: {ringtone['name']}\n"
        text += f"📅 Repeat: Once\n\n"
        text += "<i>Go to Alarms menu to manage</i>"
        
        await query.edit_message_text(
            text=text,
            reply_markup=Keyboards.alarms_menu(),
            parse_mode='HTML'
        )
        
        logger.info(f"⏰ Alarm created: {alarm_time} with ringtone {ringtone_key}")
    else:
        await query.answer("❌ Invalid ringtone", show_alert=True)
