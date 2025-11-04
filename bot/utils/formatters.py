"""
Message Formatter Utilities
Format messages for Telegram with HTML
"""

from typing import Optional

from ..core.player_state import player, Song
from ..core.mpv_player import MPVPlayer
from ..config import EMOJI


class MessageFormatter:
    """Format messages for Telegram"""
    
    @staticmethod
    def welcome_message() -> str:
        """Format welcome message"""
        return (
            f"🎧 <b>YouTube Music Player Bot</b>\n\n"
            f"Welcome! Use the buttons below to control the player.\n"
            f"Start by loading a playlist or a single video.\n\n"
            f"{MessageFormatter.status_info()}"
        )
    
    @staticmethod
    def status_info() -> str:
        """Format status information"""
        status = MPVPlayer.get_status()
        
        return (
            f"📊 <b>Status:</b>\n"
            f"• Songs in queue: {len(player.playlist)}\n"
            f"• Playing: {status}\n"
            f"• Volume: {player.volume}%\n"
            f"• Loop: {'ON' if player.loop_enabled else 'OFF'}\n"
            f"• Shuffle: {'ON' if player.shuffle_enabled else 'OFF'}"
        )
    
    @staticmethod
    def now_playing(song: Song, index: int, total: int) -> str:
        """Format now playing message"""
        return (
            f"{EMOJI['now_playing']} <b>Now Playing:</b>\n"
            f"{song.title}\n\n"
            f"⏱ Duration: {song.duration}s\n"
            f"📊 Position: {index + 1}/{total}"
        )
    
    @staticmethod
    def playlist_loaded(count: int, total: int) -> str:
        """Format playlist loaded message"""
        return (
            f"{EMOJI['success']} <b>Loaded {count} song{'s' if count != 1 else ''}</b>\n\n"
            f"Total in queue: {total}\n"
            f"Starting playback..."
        )
    
    @staticmethod
    def video_added(song: Song, total: int) -> str:
        """Format video added message"""
        return (
            f"{EMOJI['success']} <b>Added to queue:</b>\n"
            f"{song.title}\n\n"
            f"Total in queue: {total}"
        )
    
    @staticmethod
    def queue_display(limit: int = 10) -> str:
        """Format queue display"""
        if not player.playlist:
            return (
                f"{EMOJI['queue']} <b>Queue is empty</b>\n\n"
                f"Load some music first!"
            )
        
        text = f"{EMOJI['queue']} <b>Queue ({len(player.playlist)} songs)</b>\n\n"
        
        # Show first N songs
        display_count = min(limit, len(player.playlist))
        for i in range(display_count):
            marker = "🔊" if i == player.current_index else "  "
            song = player.playlist[i]
            text += f"{marker} {i+1}. {song.title}\n"
        
        if len(player.playlist) > limit:
            remaining = len(player.playlist) - limit
            text += f"\n... and {remaining} more song{'s' if remaining > 1 else ''}"
        
        return text
    
    @staticmethod
    def error_message(message: str) -> str:
        """Format error message"""
        return f"{EMOJI['error']} {message}"
    
    @staticmethod
    def loading_message(action: str) -> str:
        """Format loading message"""
        return f"{EMOJI['loading']} {action}..."
    
    @staticmethod
    def volume_changed(volume: int) -> str:
        """Format volume changed message"""
        emoji = {25: "🔇", 50: "🔉", 75: "🔊", 100: "📢"}.get(volume, "🔊")
        return f"{emoji} Volume set to {volume}%"
