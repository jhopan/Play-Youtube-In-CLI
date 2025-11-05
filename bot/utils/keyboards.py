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
        shuffle_emoji = EMOJI['shuffle_active'] if player.shuffle_enabled else EMOJI['shuffle']
        
        if player.is_playing and not player.is_paused:
            play_pause_emoji = EMOJI['pause']
            play_pause_text = "Pause"
        else:
            play_pause_emoji = EMOJI['play']
            play_pause_text = "Play"
        
        keyboard = [
            # Row 1: Load options
            [
                InlineKeyboardButton(
                    f"{EMOJI['playlist']} Load Playlist",
                    callback_data="load_playlist"
                ),
                InlineKeyboardButton(
                    f"{EMOJI['video']} Load Video",
                    callback_data="load_video"
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
            # Row 4: Modes
            [
                InlineKeyboardButton(
                    f"{loop_emoji} Loop",
                    callback_data="toggle_loop"
                ),
                InlineKeyboardButton(
                    f"{shuffle_emoji} Shuffle",
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
        """Settings menu keyboard"""
        # Dynamic emoji based on state
        yt_status = "✅ ON" if yt_suggestions_enabled else "❌ OFF"
        
        keyboard = [
            [
                InlineKeyboardButton(
                    f"📺 YouTube Suggestions: {yt_status}",
                    callback_data="toggle_yt_suggestions"
                ),
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_to_main"),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)

