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
                    f"{play_pause_emoji} {play_pause_text}",
                    callback_data="play_pause"
                ),
                InlineKeyboardButton(
                    f"{EMOJI['next']} Next",
                    callback_data="next"
                ),
                InlineKeyboardButton(
                    f"{EMOJI['prev']} Prev",
                    callback_data="prev"
                ),
            ],
            # Row 3: Modes and stop
            [
                InlineKeyboardButton(
                    f"{loop_emoji} Loop",
                    callback_data="toggle_loop"
                ),
                InlineKeyboardButton(
                    f"{shuffle_emoji} Shuffle",
                    callback_data="toggle_shuffle"
                ),
                InlineKeyboardButton(
                    f"{EMOJI['stop']} Stop",
                    callback_data="stop"
                ),
            ],
            # Row 4: Settings and info
            [
                InlineKeyboardButton(
                    f"{EMOJI['volume']} Volume",
                    callback_data="volume"
                ),
                InlineKeyboardButton(
                    f"{EMOJI['queue']} Queue",
                    callback_data="show_queue"
                ),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def volume_menu() -> InlineKeyboardMarkup:
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
                InlineKeyboardButton("« Back to Menu", callback_data="back_to_main"),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_button() -> InlineKeyboardMarkup:
        """Simple back button"""
        keyboard = [
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_to_main"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
