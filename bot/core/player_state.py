"""
Player State Management
Manages the global state of the music player
"""

import asyncio
import json
import os
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
import subprocess

@dataclass
class Song:
    """Represents a song in the playlist"""
    url: str
    title: str
    duration: str = "Unknown"
    audio_quality: str = "Unknown"  # e.g., "128kbps" or "256kbps"
    
    def __repr__(self):
        return f"Song(title='{self.title}', duration={self.duration})"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'Song':
        """Create Song from dictionary"""
        return Song(**data)


@dataclass
class SavedPlaylist:
    """Represents a saved playlist"""
    name: str
    songs: List[Song]
    created_at: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'songs': [s.to_dict() for s in self.songs],
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'SavedPlaylist':
        """Create SavedPlaylist from dictionary"""
        return SavedPlaylist(
            name=data['name'],
            songs=[Song.from_dict(s) for s in data['songs']],
            created_at=data['created_at']
        )


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
        self.loop_mode: str = 'song'  # 'song' or 'queue'
        self.shuffle_enabled: bool = False
        
        # Feature toggles
        self.yt_suggestions_enabled: bool = True  # Default ON
        
        # Audio settings
        self.volume: int = 50
        
        # Process management
        self.mpv_process: Optional[subprocess.Popen] = None
        
        # User management
        self.owner_id: Optional[int] = None
        
        # Message management (untuk edit message instead of send new)
        self.now_playing_message_id: Optional[int] = None
        self.control_menu_message_id: Optional[int] = None
        
        # Async task management
        self.playback_task: Optional[asyncio.Task] = None
        
        # Saved playlists
        self.playlists_file: str = 'saved_playlists.json'
        self._saved_playlists: Dict[str, SavedPlaylist] = self._load_playlists()
        
        self._initialized = True
    
    def reset(self):
        """Reset player state to initial values"""
        self.playlist.clear()
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.loop_enabled = False
        self.loop_mode = 'song'
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
    
    def _load_playlists(self) -> Dict[str, SavedPlaylist]:
        """Load saved playlists from file"""
        if not os.path.exists(self.playlists_file):
            return {}
        
        try:
            with open(self.playlists_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {name: SavedPlaylist.from_dict(pl) for name, pl in data.items()}
        except Exception as e:
            print(f"Error loading playlists: {e}")
            return {}
    
    def _save_playlists(self):
        """Save playlists to file"""
        try:
            data = {name: pl.to_dict() for name, pl in self._saved_playlists.items()}
            with open(self.playlists_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving playlists: {e}")
    
    def save_current_playlist(self, name: str) -> bool:
        """Save current playlist with given name"""
        if not self.playlist:
            return False
        
        from datetime import datetime
        playlist = SavedPlaylist(
            name=name,
            songs=self.playlist.copy(),
            created_at=datetime.now().isoformat()
        )
        self._saved_playlists[name] = playlist
        self._save_playlists()
        return True
    
    def save_selected_songs(self, name: str, song_indices: list) -> bool:
        """Save selected songs from current playlist"""
        if not self.playlist:
            return False
        
        # Get selected songs
        selected_songs = [self.playlist[i] for i in song_indices if 0 <= i < len(self.playlist)]
        
        if not selected_songs:
            return False
        
        from datetime import datetime
        playlist = SavedPlaylist(
            name=name,
            songs=selected_songs,
            created_at=datetime.now().isoformat()
        )
        self._saved_playlists[name] = playlist
        self._save_playlists()
        return True
    
    def load_saved_playlist(self, name: str, append: bool = False) -> bool:
        """Load a saved playlist"""
        if name not in self._saved_playlists:
            return False
        
        playlist = self._saved_playlists[name]
        
        if append:
            # Append to current playlist
            self.playlist.extend(playlist.songs)
        else:
            # Replace current playlist
            self.playlist = playlist.songs.copy()
            self.current_index = 0
        
        return True
    
    def get_saved_playlists(self) -> Dict[str, SavedPlaylist]:
        """Get all saved playlists"""
        return self._saved_playlists
    
    def delete_saved_playlist(self, name: str) -> bool:
        """Delete a saved playlist"""
        if name in self._saved_playlists:
            del self._saved_playlists[name]
            self._save_playlists()
            return True
        return False


# Global player instance
player = PlayerState()
