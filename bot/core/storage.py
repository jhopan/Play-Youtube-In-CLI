"""
Storage Manager
Handles persistent storage for favorites, history, analytics, and queue state
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class StorageManager:
    """Manages all persistent storage for the bot"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Storage files
        self.favorites_file = self.data_dir / "favorites.json"
        self.history_file = self.data_dir / "history.json"
        self.analytics_file = self.data_dir / "analytics.json"
        self.queue_state_file = self.data_dir / "queue_state.json"
        self.alarms_file = self.data_dir / "alarms.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Create storage files with default structure if they don't exist"""
        defaults = {
            self.favorites_file: [],
            self.history_file: [],
            self.analytics_file: {
                "total_plays": 0,
                "total_listening_time": 0,
                "most_played": {},
                "daily_stats": {}
            },
            self.queue_state_file: None,
            self.alarms_file: []
        }
        
        for file, default_content in defaults.items():
            if not file.exists():
                self._write_json(file, default_content)
    
    def _read_json(self, file: Path) -> any:
        """Read JSON file"""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _write_json(self, file: Path, data: any):
        """Write JSON file"""
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ============================================================================
    # FAVORITES
    # ============================================================================
    
    def add_favorite(self, song_data: Dict) -> bool:
        """Add song to favorites"""
        favorites = self._read_json(self.favorites_file) or []
        
        # Check if already in favorites
        for fav in favorites:
            if fav.get('url') == song_data.get('url'):
                return False  # Already exists
        
        song_data['added_at'] = datetime.now().isoformat()
        favorites.append(song_data)
        self._write_json(self.favorites_file, favorites)
        return True
    
    def remove_favorite(self, song_url: str) -> bool:
        """Remove song from favorites"""
        favorites = self._read_json(self.favorites_file) or []
        initial_len = len(favorites)
        favorites = [f for f in favorites if f.get('url') != song_url]
        
        if len(favorites) < initial_len:
            self._write_json(self.favorites_file, favorites)
            return True
        return False
    
    def get_favorites(self) -> List[Dict]:
        """Get all favorites"""
        return self._read_json(self.favorites_file) or []
    
    def is_favorite(self, song_url: str) -> bool:
        """Check if song is in favorites"""
        favorites = self.get_favorites()
        return any(f.get('url') == song_url for f in favorites)
    
    # ============================================================================
    # HISTORY
    # ============================================================================
    
    def add_to_history(self, song_data: Dict):
        """Add song to playback history"""
        history = self._read_json(self.history_file) or []
        
        song_data['played_at'] = datetime.now().isoformat()
        history.insert(0, song_data)  # Add to beginning
        
        # Keep only last 100 entries
        history = history[:100]
        
        self._write_json(self.history_file, history)
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get playback history"""
        history = self._read_json(self.history_file) or []
        return history[:limit]
    
    def clear_history(self):
        """Clear all history"""
        self._write_json(self.history_file, [])
    
    # ============================================================================
    # ANALYTICS
    # ============================================================================
    
    def update_analytics(self, song_data: Dict, duration_seconds: int = 0):
        """Update analytics data"""
        analytics = self._read_json(self.analytics_file)
        
        # Update total plays
        analytics['total_plays'] += 1
        analytics['total_listening_time'] += duration_seconds
        
        # Update most played
        song_title = song_data.get('title', 'Unknown')
        if song_title in analytics['most_played']:
            analytics['most_played'][song_title] += 1
        else:
            analytics['most_played'][song_title] = 1
        
        # Update daily stats
        today = datetime.now().date().isoformat()
        if today not in analytics['daily_stats']:
            analytics['daily_stats'][today] = {'plays': 0, 'time': 0}
        
        analytics['daily_stats'][today]['plays'] += 1
        analytics['daily_stats'][today]['time'] += duration_seconds
        
        self._write_json(self.analytics_file, analytics)
    
    def get_analytics(self) -> Dict:
        """Get analytics data"""
        return self._read_json(self.analytics_file)
    
    def get_top_songs(self, limit: int = 10) -> List[tuple]:
        """Get most played songs"""
        analytics = self.get_analytics()
        most_played = analytics.get('most_played', {})
        
        # Sort by play count
        sorted_songs = sorted(most_played.items(), key=lambda x: x[1], reverse=True)
        return sorted_songs[:limit]
    
    # ============================================================================
    # QUEUE PERSISTENCE
    # ============================================================================
    
    def save_queue_state(self, state_data: Dict):
        """Save current queue state"""
        state_data['saved_at'] = datetime.now().isoformat()
        self._write_json(self.queue_state_file, state_data)
    
    def load_queue_state(self) -> Optional[Dict]:
        """Load saved queue state"""
        return self._read_json(self.queue_state_file)
    
    def clear_queue_state(self):
        """Clear saved queue state"""
        self._write_json(self.queue_state_file, None)
    
    # ============================================================================
    # ALARMS
    # ============================================================================
    
    def add_alarm(self, alarm_data: Dict) -> str:
        """Add scheduled alarm"""
        alarms = self._read_json(self.alarms_file) or []
        
        alarm_id = f"alarm_{len(alarms)}_{int(datetime.now().timestamp())}"
        alarm_data['id'] = alarm_id
        alarm_data['created_at'] = datetime.now().isoformat()
        
        alarms.append(alarm_data)
        self._write_json(self.alarms_file, alarms)
        
        return alarm_id
    
    def remove_alarm(self, alarm_id: str) -> bool:
        """Remove alarm"""
        alarms = self._read_json(self.alarms_file) or []
        initial_len = len(alarms)
        alarms = [a for a in alarms if a.get('id') != alarm_id]
        
        if len(alarms) < initial_len:
            self._write_json(self.alarms_file, alarms)
            return True
        return False
    
    def get_alarms(self) -> List[Dict]:
        """Get all alarms"""
        return self._read_json(self.alarms_file) or []
    
    def get_active_alarms(self) -> List[Dict]:
        """Get active (enabled) alarms"""
        alarms = self.get_alarms()
        return [a for a in alarms if a.get('enabled', True)]


# Global storage manager instance
storage = StorageManager()
