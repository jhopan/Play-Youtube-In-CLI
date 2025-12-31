"""
Keyboard Layouts Module
All inline keyboard layouts for the bot
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ..core.player_state import player
from ..config import EMOJI


class Keyboards:
    """Keyboard layout generator"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Get the main control keyboard"""
        # Dynamic emojis based on state
        loop_emoji = EMOJI['loop_active'] if player.loop_enabled else EMOJI['loop']
        loop_text = "Loop "
        if player.loop_enabled:
            loop_text += f"({'🔂Song' if player.loop_mode == 'song' else '🔁Queue'})"
        shuffle_emoji = EMOJI['shuffle_active'] if player.shuffle_enabled else EMOJI['shuffle']
        
        if player.is_playing and not player.is_paused:
            play_pause_emoji = EMOJI['pause']
            play_pause_text = "Pause"
        else:
            play_pause_emoji = EMOJI['play']
            play_pause_text = "Play"
        
        keyboard = [
            # Row 1: Load Playlist and Clear Queue
            [
                InlineKeyboardButton(
                    f"{EMOJI['playlist']} Load Playlist",
                    callback_data="load_playlist"
                ),
                InlineKeyboardButton(
                    "🗑️ Clear Queue",
                    callback_data="clear_queue"
                ),
            ],
            # Row 1.5: Save & My Playlists
            [
                InlineKeyboardButton(
                    "💾 Save Playlist",
                    callback_data="save_playlist"
                ),
                InlineKeyboardButton(
                    "📂 My Playlists",
                    callback_data="my_playlists"
                ),
            ],
            # Row 2: Main playback controls
            [
                InlineKeyboardButton(
                    f"{EMOJI['prev']} Prev",
                    callback_data="prev"
                ),
                InlineKeyboardButton(
                    f"{play_pause_emoji} {play_pause_text}",
                    callback_data="play_pause"
                ),
                InlineKeyboardButton(
                    f"{EMOJI['next']} Next",
                    callback_data="next"
                ),
            ],
            # Row 3: Stop
            [
                InlineKeyboardButton(
                    f"{EMOJI['stop']} Stop",
                    callback_data="stop"
                ),
            ],
            # Row 4: Modes with status
            [
                InlineKeyboardButton(
                    f"{loop_emoji} {loop_text}",
                    callback_data="toggle_loop"
                ),
                InlineKeyboardButton(
                    f"{shuffle_emoji} Shuffle {'✅' if player.shuffle_enabled else ''}",
                    callback_data="toggle_shuffle"
                ),
            ],
            # Row 5: Volume and Queue
            [
                InlineKeyboardButton(
                    f"{EMOJI['volume']} Volume",
                    callback_data="volume"
                ),
                InlineKeyboardButton(
                    f"{EMOJI['queue']} Queue ({len(player.playlist)})",
                    callback_data="show_queue"
                ),
            ],
            # Row 6: Info and Settings
            [
                InlineKeyboardButton(
                    f"{EMOJI['info']} Info",
                    callback_data="show_info"
                ),
                InlineKeyboardButton(
                    "⚙️ Settings",
                    callback_data="show_settings"
                ),
            ],
            # Row 7: New Features
            [
                InlineKeyboardButton(
                    "⭐ Favorites",
                    callback_data="show_favorites"
                ),
                InlineKeyboardButton(
                    "📊 History",
                    callback_data="show_history"
                ),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def volume_menu() -> InlineKeyboardMarkup:
        """Get the volume control keyboard with fine adjustments"""
        keyboard = [
            # Row 1: Volume adjustments
            [
                InlineKeyboardButton("🔻 -10%", callback_data="vol_down"),
                InlineKeyboardButton("🔺 +10%", callback_data="vol_up"),
            ],
            # Row 2: Preset levels
            [
                InlineKeyboardButton("🔈 25%", callback_data="vol_25"),
                InlineKeyboardButton("🔉 50%", callback_data="vol_50"),
            ],
            [
                InlineKeyboardButton("🔊 75%", callback_data="vol_75"),
                InlineKeyboardButton("📢 100%", callback_data="vol_100"),
            ],
            # Row 3: Mute and back
            [
                InlineKeyboardButton("🔇 Mute/Unmute", callback_data="vol_mute"),
                InlineKeyboardButton("« Back to Menu", callback_data="back_to_main"),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def loop_confirmation_dialog() -> InlineKeyboardMarkup:
        """Keyboard for loop confirmation dialog"""
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔄 Replay Playlist",
                    callback_data="loop_continue"
                ),
                InlineKeyboardButton(
                    "⏹️ Stop",
                    callback_data="loop_stop"
                ),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def auto_next_dialog() -> InlineKeyboardMarkup:
        """Get the auto-next confirmation keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(
                    "▶️ Play Next",
                    callback_data="auto_next_continue"
                ),
                InlineKeyboardButton(
                    "⏹️ Stop",
                    callback_data="auto_next_stop"
                ),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def suggestion_dialog() -> InlineKeyboardMarkup:
        """Keyboard for YouTube suggestion dialog"""
        keyboard = [
            [
                InlineKeyboardButton(
                    "▶️ Play This",
                    callback_data="suggestion_play"
                ),
                InlineKeyboardButton(
                    "⏭️ Next Suggestion",
                    callback_data="suggestion_next"
                ),
            ],
            [
                InlineKeyboardButton(
                    "⏹️ Stop",
                    callback_data="suggestion_stop"
                ),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_button() -> InlineKeyboardMarkup:
        """Simple back button"""
        keyboard = [
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_to_main"),
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu(yt_suggestions_enabled: bool = True) -> InlineKeyboardMarkup:
        """Settings menu keyboard (redirects to extended version)"""
        return Keyboards.settings_menu_extended()
    
    @staticmethod
    def cancel_save_playlist() -> InlineKeyboardMarkup:
        """Keyboard for canceling save playlist"""
        keyboard = [
            [
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_save_playlist"),
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def saved_playlists_menu(playlists: dict) -> InlineKeyboardMarkup:
        """Menu showing saved playlists"""
        keyboard = []
        
        # Add playlist buttons (max 8 playlists to avoid too many buttons)
        for i, (name, playlist) in enumerate(list(playlists.items())[:8]):
            keyboard.append([
                InlineKeyboardButton(
                    f"📋 {name} ({len(playlist.songs)} songs)",
                    callback_data=f"load_saved_{name}"
                )
            ])
        
        # Back button
        keyboard.append([
            InlineKeyboardButton("« Back to Menu", callback_data="back_to_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def song_selection_menu(selected_indices: list) -> InlineKeyboardMarkup:
        """Menu for selecting songs to save in playlist"""
        keyboard = []
        
        # Show up to 10 songs for selection
        max_songs = min(10, len(player.playlist))
        for i in range(max_songs):
            song = player.playlist[i]
            is_selected = i in selected_indices
            checkbox = "✅" if is_selected else "⬜"
            
            # Truncate song title if too long
            title = song.title[:30] + "..." if len(song.title) > 30 else song.title
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{checkbox} {title}",
                    callback_data=f"toggle_song_{i}"
                )
            ])
        
        if len(player.playlist) > 10:
            keyboard.append([
                InlineKeyboardButton(
                    f"⚠️ Showing 10 of {len(player.playlist)} songs",
                    callback_data="dummy"
                )
            ])
        
        # Action buttons
        keyboard.append([
            InlineKeyboardButton("💾 Save All", callback_data="save_all_songs"),
            InlineKeyboardButton("✅ Save Selected", callback_data="save_selected_songs"),
        ])
        
        keyboard.append([
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_save_playlist")
        ])
        
        return InlineKeyboardMarkup(keyboard)    
    # ============================================================================
    # NEW FEATURE KEYBOARDS
    # ============================================================================
    
    @staticmethod
    def queue_management_menu() -> InlineKeyboardMarkup:
        """Queue management keyboard"""
        from ..core.storage import storage
        
        keyboard = [
            [
                InlineKeyboardButton(
                    "🗑️ Remove Song",
                    callback_data="queue_remove"
                ),
                InlineKeyboardButton(
                    "🔄 Move Song",
                    callback_data="queue_move"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🧹 Clear Queue",
                    callback_data="clear_queue"
                ),
                InlineKeyboardButton(
                    "📜 Full Queue",
                    callback_data="show_queue"
                ),
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_to_main"),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def favorites_menu() -> InlineKeyboardMarkup:
        """Favorites management keyboard"""
        from ..core.storage import storage
        
        # Check if current song is favorite
        is_fav = False
        if player.current_song:
            is_fav = storage.is_favorite(player.current_song.url)
        
        fav_count = len(storage.get_favorites())
        like_text = "💔 Unlike Current" if is_fav else "❤️ Like Current"
        
        keyboard = [
            [
                InlineKeyboardButton(
                    like_text,
                    callback_data="toggle_favorite"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"📜 View Favorites ({fav_count})",
                    callback_data="view_favorites"
                ),
                InlineKeyboardButton(
                    "▶️ Play All",
                    callback_data="play_all_favorites"
                ),
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_to_main"),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def favorites_list_menu(favorites: list, page: int = 0) -> InlineKeyboardMarkup:
        """Display list of favorite songs"""
        keyboard = []
        items_per_page = 8
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        
        page_favorites = favorites[start_idx:end_idx]
        
        for i, fav in enumerate(page_favorites):
            idx = start_idx + i
            title = fav['title'][:35] + "..." if len(fav['title']) > 35 else fav['title']
            keyboard.append([
                InlineKeyboardButton(
                    f"🎵 {title}",
                    callback_data=f"play_fav_{idx}"
                ),
                InlineKeyboardButton(
                    "🗑️",
                    callback_data=f"remove_fav_{idx}"
                ),
            ])
        
        # Pagination
        nav_buttons = []
        total_pages = (len(favorites) + items_per_page - 1) // items_per_page
        
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton("◀️ Prev", callback_data=f"fav_page_{page-1}")
            )
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton("Next ▶️", callback_data=f"fav_page_{page+1}")
            )
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([
            InlineKeyboardButton("« Back", callback_data="show_favorites")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def history_menu() -> InlineKeyboardMarkup:
        """History and analytics keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(
                    "📜 Recent History",
                    callback_data="view_history"
                ),
                InlineKeyboardButton(
                    "📈 Top Played",
                    callback_data="view_top_songs"
                ),
            ],
            [
                InlineKeyboardButton(
                    "📊 Analytics",
                    callback_data="view_analytics"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🗑️ Clear History",
                    callback_data="clear_history"
                ),
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_to_main"),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def history_list_menu(history: list, page: int = 0) -> InlineKeyboardMarkup:
        """Display playback history"""
        keyboard = []
        items_per_page = 8
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        
        page_history = history[start_idx:end_idx]
        
        for i, item in enumerate(page_history):
            idx = start_idx + i
            title = item['title'][:35] + "..." if len(item['title']) > 35 else item['title']
            keyboard.append([
                InlineKeyboardButton(
                    f"🎵 {title}",
                    callback_data=f"play_history_{idx}"
                )
            ])
        
        # Pagination
        nav_buttons = []
        total_pages = (len(history) + items_per_page - 1) // items_per_page
        
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton("◀️ Prev", callback_data=f"history_page_{page-1}")
            )
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton("Next ▶️", callback_data=f"history_page_{page+1}")
            )
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([
            InlineKeyboardButton("« Back", callback_data="show_history")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu_extended() -> InlineKeyboardMarkup:
        """Extended settings menu with new features"""
        # Get current settings
        resolution_text = player.preferred_resolution.upper() if player.preferred_resolution != "audio" else "Audio Only"
        fallback_status = "ON ✅" if player.resolution_fallback else "OFF ❌"
        
        # Sleep timer status
        timer_remaining = player.get_sleep_timer_remaining()
        if timer_remaining and timer_remaining > 0:
            timer_text = f"⏰ Timer: {timer_remaining}min"
        else:
            timer_text = "⏰ Sleep Timer"
        
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🎬 Resolution: {resolution_text}",
                    callback_data="change_resolution"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🔄 Fallback: {fallback_status}",
                    callback_data="toggle_fallback"
                ),
            ],
            [
                InlineKeyboardButton(
                    timer_text,
                    callback_data="sleep_timer_menu"
                ),
            ],
            [
                InlineKeyboardButton(
                    "⏲️ Alarms",
                    callback_data="alarms_menu"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"📺 YT Suggestions: {'ON ✅' if player.yt_suggestions_enabled else 'OFF ❌'}",
                    callback_data="toggle_yt_suggestions"
                ),
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_to_main"),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def resolution_selector_menu() -> InlineKeyboardMarkup:
        """Resolution selection keyboard"""
        current = player.preferred_resolution
        
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅ ' if current == 'audio' else ''}🎵 Audio Only",
                    callback_data="res_audio"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"{'✅ ' if current == '144p' else ''}📱 144p (Low)",
                    callback_data="res_144p"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"{'✅ ' if current == '360p' else ''}💻 360p (Standard)",
                    callback_data="res_360p"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"{'✅ ' if current == '720p' else ''}📺 720p (HD)",
                    callback_data="res_720p"
                ),
            ],
            [
                InlineKeyboardButton("« Back to Settings", callback_data="show_settings"),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def sleep_timer_menu() -> InlineKeyboardMarkup:
        """Sleep timer selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("⏰ 15 min", callback_data="timer_15"),
                InlineKeyboardButton("⏰ 30 min", callback_data="timer_30"),
            ],
            [
                InlineKeyboardButton("⏰ 45 min", callback_data="timer_45"),
                InlineKeyboardButton("⏰ 60 min", callback_data="timer_60"),
            ],
            [
                InlineKeyboardButton("⏰ 90 min", callback_data="timer_90"),
                InlineKeyboardButton("⏰ 120 min", callback_data="timer_120"),
            ],
            [
                InlineKeyboardButton("❌ Cancel Timer", callback_data="timer_cancel"),
            ],
            [
                InlineKeyboardButton("« Back to Settings", callback_data="show_settings"),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def alarms_menu() -> InlineKeyboardMarkup:
        """Alarms management keyboard"""
        from ..core.storage import storage
        
        alarms = storage.get_alarms()
        alarm_count = len(alarms)
        enabled_count = sum(1 for a in alarms if a['enabled'])
        
        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ Add Alarm",
                    callback_data="add_alarm"
                ),
            ],
        ]
        
        # Show individual alarms if any exist
        if alarms:
            keyboard.append([
                InlineKeyboardButton(
                    f"📋 View All ({alarm_count})",
                    callback_data="view_alarms"
                ),
            ])
            
            # Show first 3 alarms
            for alarm in alarms[:3]:
                status = "✅" if alarm['enabled'] else "❌"
                time_str = alarm['time']
                keyboard.append([
                    InlineKeyboardButton(
                        f"{status} {time_str}",
                        callback_data=f"toggle_alarm_{alarm['id']}"
                    ),
                    InlineKeyboardButton(
                        "🗑️",
                        callback_data=f"delete_alarm_{alarm['id']}"
                    ),
                ])
        
        keyboard.append([
            InlineKeyboardButton("« Back to Settings", callback_data="show_settings"),
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def queue_remove_menu(page: int = 0) -> InlineKeyboardMarkup:
        """Select song to remove from queue"""
        keyboard = []
        items_per_page = 8
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(player.playlist))
        
        for i in range(start_idx, end_idx):
            if i == player.current_index:
                continue  # Skip current song
            
            song = player.playlist[i]
            title = song.title[:30] + "..." if len(song.title) > 30 else song.title
            marker = "🔊" if i == player.current_index else "  "
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{marker}{i+1}. {title}",
                    callback_data=f"remove_queue_{i}"
                )
            ])
        
        # Pagination
        nav_buttons = []
        total_pages = (len(player.playlist) + items_per_page - 1) // items_per_page
        
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton("◀️ Prev", callback_data=f"queue_rm_page_{page-1}")
            )
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton("Next ▶️", callback_data=f"queue_rm_page_{page+1}")
            )
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([
            InlineKeyboardButton("« Back", callback_data="queue_management")
        ])
        
        return InlineKeyboardMarkup(keyboard)