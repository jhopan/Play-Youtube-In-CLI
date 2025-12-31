# 🚀 New Features Implementation Guide

## Overview

Implementasi 8 fitur baru yang powerful:

1. ✅ **Queue Management** - Remove, move, clear queue
2. ⏰ **Sleep Timer** - Auto-stop after X minutes
3. 📊 **Playback History** - Track played songs
4. ⭐ **Favorites System** - Like/unlike songs
5. 💾 **Queue Persistence** - Auto-save/restore queue
6. 📈 **Analytics Dashboard** - Listening stats
7. ⏲️ **Alarm System** - Scheduled playback
8. 🎬 **Resolution Selector** - Choose quality dengan fallback

## Implementation Status

### ✅ Completed

- [x] Storage Manager (`bot/core/storage.py`)
  - Favorites management
  - History tracking
  - Analytics data
  - Queue persistence
  - Alarm management

- [x] PlayerState Updates (`bot/core/player_state.py`)
  - Queue management methods
  - Sleep timer functionality
  - Resolution settings
  - Queue persistence methods

### 🔄 In Progress

- [ ] Keyboards Update (`bot/utils/keyboards.py`)
  - Queue management keyboard
  - Favorites keyboard
  - History keyboard
  - Analytics keyboard
  - Settings keyboard (resolution, timer, alarms)

- [ ] Callbacks Handlers (`bot/handlers/callbacks.py`)
  - Queue management callbacks
  - Favorites callbacks
  - History callbacks
  - Timer callbacks
  - Resolution callbacks
  - Alarm callbacks

- [ ] Playback Manager Updates (`bot/core/playback.py`)
  - Auto-save to history
  - Update analytics
  - Sleep timer check
  - Resolution fallback logic

### 📋 TODO

- [ ] Main menu reorganization
- [ ] Testing all features
- [ ] Documentation update
- [ ] Requirements update (if needed)

## New File Structure

```
bot/
├── core/
│   ├── storage.py          # NEW - Storage manager
│   ├── player_state.py     # UPDATED - New methods
│   ├── playback.py         # TODO - Update for history/analytics
│   └── youtube.py          # TODO - Add resolution support
├── handlers/
│   ├── callbacks.py        # TODO - Add new callbacks
│   └── queue_manager.py    # NEW - Queue management handlers
├── utils/
│   └── keyboards.py        # TODO - Add new keyboards
└── data/                   # NEW - Data directory
    ├── favorites.json
    ├── history.json
    ├── analytics.json
    ├── queue_state.json
    └── alarms.json
```

## Usage Examples

### Queue Management

```python
# Remove song from queue
player.remove_song_from_queue(index=5)

# Move song
player.move_song_in_queue(from_index=2, to_index=5)

# Clear queue (keep current)
player.clear_queue(keep_current=True)
```

### Sleep Timer

```python
# Set timer for 30 minutes
player.set_sleep_timer(minutes=30)

# Check remaining time
remaining = player.get_sleep_timer_remaining()

# Cancel timer
player.cancel_sleep_timer()
```

### Favorites

```python
from bot.core import storage

# Add to favorites
storage.add_favorite({
    'url': song.url,
    'title': song.title,
    'duration': song.duration
})

# Check if favorite
is_fav = storage.is_favorite(song.url)

# Get all favorites
favs = storage.get_favorites()
```

### History & Analytics

```python
# Add to history (auto-called on playback)
storage.add_to_history(song_data)

# Update analytics
storage.update_analytics(song_data, duration_seconds=180)

# Get stats
analytics = storage.get_analytics()
top_songs = storage.get_top_songs(limit=10)
```

### Queue Persistence

```python
# Auto-save (called automatically)
player._auto_save_queue()

# Restore on startup
if player.restore_queue_state():
    print("Queue restored!")
```

### Resolution

```python
# Set preferred resolution
player.set_resolution("144p")  # or "audio", "360p", "720p"

# Toggle fallback
player.toggle_resolution_fallback()
```

## Keyboard Layouts

### Main Menu (Updated)

```
ℹ️ Info     🔊 Volume    ⚙️ Settings

📋 Load PL   🎥 Video    ⭐ Favorites

▶️ Play    ⏭️ Next
⏮️ Prev    ⏸️ Pause

🔁 Loop    🔀 Shuffle
📋 Queue   ⏹️ Stop
```

### Queue Management Menu

```
📋 Queue Management

🗑️ Remove Song
🔄 Move Song
🧹 Clear Queue
📜 Show Full Queue

↩️ Back to Main
```

### Favorites Menu

```
⭐ Favorites

❤️ Like Current Song
📜 View Favorites
▶️ Play All Favorites
🗑️ Remove from Favorites

↩️ Back
```

### History Menu

```
📊 History

📜 View History (50)
📈 Top Played
🗑️ Clear History

↩️ Back
```

### Settings Menu

```
⚙️ Settings

🎬 Resolution: [Audio/144p/360p/720p]
🔄 Fallback: [ON/OFF]
⏰ Sleep Timer
⏲️ Alarms

↩️ Back
```

## Next Steps

1. Update keyboards.py dengan layout baru
2. Implement callback handlers
3. Update playback manager
4. Add resolution support ke youtube.py
5. Testing & debugging
6. Update README.md

## Notes

- All data stored in `data/` directory
- JSON format untuk easy backup/restore
- Auto-save queue after every change
- History limited to 100 entries
- Analytics tracks all plays dengan timestamps
