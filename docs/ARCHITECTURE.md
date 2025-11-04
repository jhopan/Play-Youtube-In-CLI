# 🏗️ Project Architecture - Modular Structure

## 📁 New Project Structure

```
Project Root/
│
├── main.py                          ⭐ Entry point (run this!)
│
├── bot/                             📦 Main bot package
│   ├── __init__.py                  Package initialization
│   ├── config.py                    ⚙️  Configuration & settings
│   │
│   ├── core/                        🎵 Core functionality
│   │   ├── __init__.py
│   │   ├── player_state.py          State management
│   │   ├── mpv_player.py            MPV control
│   │   ├── youtube.py               YouTube extraction
│   │   └── playback.py              Playback logic (play/next/stop)
│   │
│   ├── handlers/                    📨 Telegram handlers
│   │   ├── __init__.py
│   │   ├── commands.py              Command handlers (/start)
│   │   ├── callbacks.py             Button callbacks
│   │   └── messages.py              Message handlers (URLs)
│   │
│   └── utils/                       🛠️ Utilities
│       ├── __init__.py
│       ├── keyboards.py             Keyboard layouts
│       ├── access_control.py        User authentication
│       └── formatters.py            Message formatting
│
├── requirements.txt                 📦 Dependencies
├── ytmusic_bot.service             ⚙️  Systemd service
│
└── [Old Files]
    └── ytmusic_interactive_bot.py   📜 Old monolithic version (backup)
```

---

## 🎯 Module Responsibilities

### 🌟 `main.py` - Entry Point

**Purpose:** Application initialization and startup

- Validates configuration
- Creates Telegram application
- Registers all handlers
- Starts bot polling
- Handles cleanup on exit

**Run with:**

```bash
python3 main.py
```

---

### ⚙️ `bot/config.py` - Configuration

**Purpose:** All settings and constants

- Bot token and user whitelist
- Logging configuration
- Player default settings
- MPV and yt-dlp options
- UI emojis and texts
- Configuration validation

**Key Settings:**

```python
TOKEN = "YOUR_BOT_TOKEN_HERE"
ALLOWED_USERS = []
DEFAULT_VOLUME = 50
QUEUE_DISPLAY_LIMIT = 10
```

---

### 🎵 `bot/core/` - Core Functionality

#### `player_state.py` - State Management

**Purpose:** Global player state

- Singleton pattern for state management
- Playlist storage
- Current song tracking
- Player modes (loop, shuffle)
- Process management
- Queue information

**Key Classes:**

- `Song` - Dataclass for song info
- `PlayerState` - Singleton state manager
- `player` - Global instance

#### `mpv_player.py` - MPV Control

**Purpose:** MPV process management

- Start/stop MPV process
- Pause/resume with signals
- Process status checking
- Volume control
- Error handling

**Key Methods:**

```python
MPVPlayer.start(url, volume)
MPVPlayer.stop()
MPVPlayer.pause()
MPVPlayer.resume()
MPVPlayer.is_running()
```

#### `youtube.py` - YouTube Integration

**Purpose:** YouTube data extraction

- Extract playlist information
- Get single video info
- URL validation
- Error handling for yt-dlp

**Key Methods:**

```python
YouTubeExtractor.extract_playlist(url)
YouTubeExtractor.get_video_info(url)
YouTubeExtractor.validate_url(url)
```

#### `playback.py` - Playback Logic

**Purpose:** Playback orchestration

- Play current song
- Auto-next functionality
- Previous/next navigation
- Loop mode handling
- Shuffle mode handling
- Volume management

**Key Methods:**

```python
PlaybackManager.play_current_song(app)
PlaybackManager.play_next(app)
PlaybackManager.play_previous(app)
PlaybackManager.toggle_pause()
PlaybackManager.stop()
PlaybackManager.toggle_loop()
PlaybackManager.toggle_shuffle()
```

---

### 📨 `bot/handlers/` - Telegram Handlers

#### `commands.py` - Command Handlers

**Purpose:** Handle slash commands

- `/start` command
- Access control check
- Welcome message
- Owner assignment

#### `callbacks.py` - Button Callbacks

**Purpose:** Handle button clicks

- Main callback router
- Load playlist/video
- Play/pause/next/prev
- Loop/shuffle toggle
- Volume control
- Queue display
- Access control for controls

**Handlers:**

```python
handle_load_playlist()
handle_load_video()
handle_play_pause()
handle_next()
handle_prev()
handle_stop()
handle_toggle_loop()
handle_toggle_shuffle()
handle_volume_menu()
handle_volume_change()
handle_show_queue()
handle_back_to_main()
```

#### `messages.py` - Message Handlers

**Purpose:** Handle text messages

- URL message processing
- Playlist URL handling
- Video URL handling
- URL validation
- Auto-start playback

---

### 🛠️ `bot/utils/` - Utilities

#### `keyboards.py` - Keyboard Layouts

**Purpose:** Generate inline keyboards

- Main menu keyboard
- Volume control keyboard
- Dynamic emoji updates
- Back button

**Key Methods:**

```python
Keyboards.main_menu()
Keyboards.volume_menu()
Keyboards.back_button()
```

#### `access_control.py` - Access Control

**Purpose:** User authentication/authorization

- Check user access
- Owner identification
- Owner assignment
- Access logging

**Key Methods:**

```python
AccessControl.check_access(user_id)
AccessControl.is_owner(user_id)
AccessControl.reset_owner()
```

#### `formatters.py` - Message Formatting

**Purpose:** Format messages for Telegram

- Welcome message
- Status information
- Now playing display
- Queue display
- Error messages
- Loading messages

**Key Methods:**

```python
MessageFormatter.welcome_message()
MessageFormatter.status_info()
MessageFormatter.now_playing(song, idx, total)
MessageFormatter.queue_display(limit)
MessageFormatter.error_message(msg)
```

---

## 🔄 Data Flow

### Startup Flow

```
main.py
  ↓
validate_config()
  ↓
Create Application
  ↓
Register Handlers
  ↓
Start Polling
```

### User Interaction Flow

```
User clicks button
  ↓
callbacks.py (button_callback)
  ↓
AccessControl.check_access()
  ↓
Route to specific handler
  ↓
Handler executes
  ↓
Update PlayerState
  ↓
Call Core functions
  ↓
Send response via Keyboards & Formatters
```

### Playback Flow

```
User loads playlist
  ↓
messages.py (handle_playlist_url)
  ↓
YouTubeExtractor.extract_playlist()
  ↓
Update player.playlist
  ↓
PlaybackManager.play_current_song()
  ↓
MPVPlayer.start()
  ↓
Wait for completion
  ↓
PlaybackManager.handle_song_finished()
  ↓
Auto-next or loop
```

---

## 📦 Module Dependencies

```
main.py
  ├── bot.config
  ├── bot.handlers (all)
  └── bot.core.MPVPlayer

bot.handlers
  ├── bot.core (all)
  ├── bot.utils (all)
  └── bot.config

bot.core
  ├── bot.config
  └── bot.core.player_state (internal)

bot.utils
  ├── bot.core.player_state
  └── bot.config
```

---

## 🎓 Benefits of Modular Structure

### ✅ **Maintainability**

- Each module has single responsibility
- Easy to locate and fix bugs
- Clear separation of concerns

### ✅ **Scalability**

- Easy to add new features
- Can extend without breaking existing code
- Modular testing

### ✅ **Readability**

- Clear structure
- Logical organization
- Self-documenting code

### ✅ **Reusability**

- Core modules can be reused
- Utils are independent
- Easy to create similar bots

### ✅ **Testability**

- Each module can be tested independently
- Mock external dependencies
- Unit testing friendly

---

## 🔧 How to Modify

### Adding a New Command

1. Add handler in `bot/handlers/commands.py`
2. Register in `main.py`
3. Update keyboards if needed

### Adding a New Button

1. Add callback in `bot/handlers/callbacks.py`
2. Add button in `bot/utils/keyboards.py`
3. Update router in `button_callback()`

### Adding a New Core Feature

1. Create function in appropriate `bot/core/` module
2. Call from handlers
3. Update state if needed

### Changing UI

1. Update emojis in `bot/config.py`
2. Update keyboards in `bot/utils/keyboards.py`
3. Update formatters in `bot/utils/formatters.py`

---

## 🚀 Running the Bot

### Development Mode

```bash
# Edit configuration
nano bot/config.py

# Run directly
python3 main.py
```

### Production Mode

```bash
# Setup as service
sudo nano /etc/systemd/system/ytmusic-bot.service

# Update ExecStart to point to main.py
ExecStart=/usr/bin/python3 /path/to/main.py

# Start service
sudo systemctl start ytmusic-bot
```

---

## 📝 Configuration Steps

1. **Edit `bot/config.py`:**

```python
TOKEN = "YOUR_TOKEN_FROM_BOTFATHER"
ALLOWED_USERS = []  # or [123456789]
DEFAULT_VOLUME = 50
```

2. **Or use environment variables:**

```bash
export TELEGRAM_BOT_TOKEN="your_token"
python3 main.py
```

3. **Customize settings:**

- Change emojis in `EMOJI` dict
- Adjust MPV options in `MPV_OPTIONS`
- Modify queue display limit

---

## ✅ Comparison: Old vs New

| Aspect              | Old (Monolithic)       | New (Modular)               |
| ------------------- | ---------------------- | --------------------------- |
| **File Count**      | 1 file (800 lines)     | 15 files (~100 lines each)  |
| **Structure**       | Everything in one file | Organized by responsibility |
| **Maintainability** | Hard to navigate       | Easy to find code           |
| **Testing**         | Difficult              | Each module testable        |
| **Collaboration**   | Merge conflicts        | Multiple people can work    |
| **Readability**     | Need to scroll         | Clear module names          |
| **Extensibility**   | Hard to add features   | Easy to extend              |

---

## 🎯 Quick Reference

### Import Structure

```python
# From handlers
from bot.core import player, PlaybackManager, MPVPlayer
from bot.utils import Keyboards, MessageFormatter, AccessControl
from bot.config import EMOJI

# From core
from bot.config import MPV_OPTIONS, YTDL_OPTIONS
from .player_state import player, Song

# From utils
from bot.core.player_state import player
from bot.config import EMOJI
```

### Key Objects

```python
player            # Global state singleton
MPVPlayer         # MPV control class
YouTubeExtractor  # YouTube extraction class
PlaybackManager   # Playback orchestration class
Keyboards         # Keyboard generation class
MessageFormatter  # Message formatting class
AccessControl     # Access control class
```

---

**🎉 Struktur baru siap digunakan!**

Lebih rapi, lebih mudah maintenance, dan lebih profesional! 🚀
