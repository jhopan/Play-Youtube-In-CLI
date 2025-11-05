"""
Player State Management
Manages the global state of the music player
"""

import asyncio
from typing import Optional, List
from dataclasses import dataclass
import subprocess

@dataclass
class Song:
    """Represents a song in the playlist"""
    url: str
    title: str
    duration: str = "Unknown"
    
    def __repr__(self):
        return f"Song(title='{self.title}', duration={self.duration})"


class PlayerState:
    """Global player state singleton"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlayerState, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Playlist management
        self.playlist: List[Song] = []
        self.current_index: int = 0
        
        # Playback state
        self.is_playing: bool = False
        self.is_paused: bool = False
        
        # Player modes
        self.loop_enabled: bool = False
        self.shuffle_enabled: bool = False
        
        # Feature toggles
        self.yt_suggestions_enabled: bool = True  # Default ON
        
        # Audio settings
        self.volume: int = 50
        
        # Process management
        self.mpv_process: Optional[subprocess.Popen] = None
        
        # User management
        self.owner_id: Optional[int] = None
        
        # Async task management
        self.playback_task: Optional[asyncio.Task] = None
        
        self._initialized = True
    
    def reset(self):
        """Reset player state to initial values"""
        self.playlist.clear()
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.loop_enabled = False
        self.shuffle_enabled = False
        self.mpv_process = None
        self.playback_task = None
    
    @property
    def current_song(self) -> Optional[Song]:
        """Get the current song"""
        if not self.playlist or self.current_index >= len(self.playlist):
            return None
        return self.playlist[self.current_index]
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next song"""
        return self.current_index < len(self.playlist) - 1
    
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous song"""
        return self.current_index > 0
    
    def get_queue_info(self) -> str:
        """Get formatted queue information"""
        if not self.playlist:
            return "Queue is empty"
        
        info = f"📊 Queue ({len(self.playlist)} songs)\n\n"
        
        # Show up to 10 songs
        display_count = min(10, len(self.playlist))
        for i in range(display_count):
            marker = "🔊" if i == self.current_index else "  "
            song = self.playlist[i]
            info += f"{marker} {i+1}. {song.title}\n"
        
        if len(self.playlist) > 10:
            remaining = len(self.playlist) - 10
            info += f"\n... and {remaining} more song{'s' if remaining > 1 else ''}"
        
        return info


# Global player instance
player = PlayerState()
