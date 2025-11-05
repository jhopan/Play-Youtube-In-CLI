# Changelog

All notable changes to YouTube Music Telegram Bot will be documented in this file.

## [2.1.0] - 2024-12-19

### 🎨 UI Enhancements

#### ✨ New Features

- **Enhanced Main Menu Layout**
  - Reorganized button layout for better UX
  - Added dedicated Info button for bot status
  - Stop button in its own row for easy access
  - Queue button shows current count (e.g., "Queue (5)")
  - Cleaner visual hierarchy and grouping

- **Advanced Volume Control** 🔊
  - **+10% / -10% buttons** - Fine-tune volume in 10% increments
  - **Mute/Unmute toggle** - Instant mute control
  - Preset levels retained (25%, 50%, 75%, 100%)
  - Real-time control via `amixer` (no restart needed)
  - All volume changes apply immediately to playing song

- **Info Display** ℹ️
  - Comprehensive bot status overview
  - Current song details with clickable YouTube link
  - Playlist position and total count
  - Current settings (Volume, Loop, Shuffle)
  - Quick reference for all active states

- **Auto-Next Dialog** ⏱️ (YouTube-like)
  - 5-second countdown before auto-play
  - Real-time countdown updates (5, 4, 3, 2, 1...)
  - "Play Next" button to skip countdown
  - "Stop" button to cancel auto-play
  - Non-blocking countdown (doesn't freeze bot)
  - Cancellable at any time
  - Respects loop mode (no dialog when looping)

#### 🔧 Technical Improvements

- **Volume Backend Enhancement**
  - Direct `amixer` integration for volume up/down
  - Proper state tracking for volume changes
  - Triple fallback: MPV IPC → amixer → pactl
  - 10% increment/decrement support

- **Auto-Next Implementation**
  - Async countdown with `asyncio.create_task()`
  - Task storage in `bot_data` for cancellation
  - Proper cleanup on stop/cancel
  - Error handling for network issues

- **Callback Handler Updates**
  - Added `handle_show_info()` for info display
  - Added `handle_auto_next_continue()` for manual next
  - Added `handle_auto_next_stop()` for cancel
  - Enhanced `handle_volume_change()` for +/- controls

#### 📚 Documentation

- **UI_ENHANCEMENTS.md** - Complete guide to new features
- Updated **CHANGELOG.md** with version 2.1 details

### 🐛 Bug Fixes

- Fixed keyboard layout syntax errors
- Improved volume state synchronization
- Better error handling in countdown task

## [2.0.0] - 2024-12-18

### 🎵 Volume Control Enhancement

#### ✨ New Features

- **Real-Time Volume Control**
  - MPV IPC socket implementation (`/tmp/mpvsocket`)
  - Live volume changes without restart
  - JSON-based command protocol
  
- **System Volume Fallback**
  - `amixer` integration for ALSA/PulseAudio
  - `pactl` fallback for PulseAudio-only systems
  - Triple-fallback system for reliability

- **Volume Helper Functions**
  - `volume_up(step=5)` - Increase volume
  - `volume_down(step=5)` - Decrease volume
  - `toggle_mute()` - Mute/unmute toggle

#### 📚 Documentation

- **VOLUME_CONTROL.md** - Manual volume control guide
- **FIX_NO_AUDIO.md** - Headless server audio setup

## [1.2.0] - 2024-12-15

### 🔧 Deployment Fixes

#### 🐛 Bug Fixes

- **Python 3.13 Compatibility**
  - Upgraded `python-telegram-bot` to >=21.0
  - Fixed AttributeError with async context managers
  - Updated all async patterns for Python 3.13

- **Module Import Errors**
  - Fixed `ModuleNotFoundError: bot.config`
  - Force-added `config.py` to git (was in .gitignore)
  - Updated git tracking for all bot modules

- **Infinite Loop Fix**
  - Added delays in playback loop (1s between songs)
  - Added MPV exit code checks
  - Prevented rapid process restarts

- **Missing Emoji Keys**
  - Added 'now_playing', 'loop_active', 'shuffle_active'
  - Added 'playlist', 'video', 'info' emoji keys
  - Updated all handlers to use new keys

- **PEP 668 Compliance**
  - Enforced virtual environment usage
  - Updated setup scripts for venv
  - Added venv to .gitignore

#### 📚 Documentation

- **FIX_MODULE_NOT_FOUND.md** - Module import troubleshooting
- **FIX_PYTHON_313.md** - Python 3.13 compatibility guide
- Updated **TROUBLESHOOTING.md** with all fixes

## [1.1.0] - 2024-11-10

### 🏗️ Architectural Refactoring

#### ✨ Features

- **Modular Structure**
  - Separated monolithic bot into organized modules
  - Created `bot/` package with submodules
  - `core/` - Player logic (state, mpv, youtube, playback)
  - `handlers/` - Request handlers (commands, callbacks, messages)
  - `utils/` - Utilities (keyboards, formatters, access control)

- **Environment Variables**
  - `.env` file support for configuration
  - `BOT_TOKEN` - Telegram bot token
  - `ALLOWED_USER_IDS` - Comma-separated user IDs
  - `DEFAULT_VOLUME` - Default volume level
  - `DEBUG` - Debug mode flag

- **GitHub Deployment**
  - Repository: https://github.com/jhopan/Play-Youtube-In-CLI
  - Complete version control setup
  - Organized documentation structure

#### 🔧 Technical Changes

- **main.py** - Entry point with config validation
- **bot/config.py** - Environment-based configuration
- **Improved logging** - Better log formatting and levels
- **Cleaner separation** - SRP (Single Responsibility Principle)

#### 📚 Documentation

- **ARCHITECTURE.md** - System architecture guide
- **MIGRATION.md** - Migration from monolithic version
- **ENV_SETUP.md** - Environment variable setup
- Expanded all existing docs

## [1.0.0] - 2024-11-04

### 🎉 Initial Release

#### ✨ Features

- **Interactive Button Control** - All controls via Telegram buttons (no text commands)
- **YouTube Playlist Support** - Load entire playlists with one link
- **Single Video Support** - Add individual videos to queue
- **Full Playback Control** - Play, pause, next, previous, stop
- **Loop Mode** - Repeat single song continuously
- **Shuffle Mode** - Random playback order
- **Volume Control** - 4 levels (25%, 50%, 75%, 100%)
- **Queue Display** - View current playlist (10 songs preview)
- **Auto-Next** - Automatic progression to next song
- **User Whitelist** - Access control via user ID
- **Owner-Only Controls** - Only bot owner can control playback
- **Error Recovery** - Auto-restart if mpv crashes
- **Async Operations** - Non-blocking playback for bot responsiveness

#### 🔧 Technical Features

- **Headless Operation** - Works on Ubuntu Server without GUI
- **Direct Streaming** - No file downloads, streams directly from YouTube
- **MPV Integration** - Using mpv for reliable audio playback
- **yt-dlp Integration** - Robust YouTube data extraction
- **Subprocess Management** - Proper process handling with Popen
- **Signal Handling** - Graceful pause/resume with SIGSTOP/SIGCONT
- **Systemd Support** - Can run as system service for 24/7 operation
- **Comprehensive Logging** - Detailed logs for debugging

#### 📚 Documentation

- **INDEX.md** - Complete documentation navigation
- **README.md** - Full project documentation
- **QUICKSTART.md** - 5-minute quick start guide
- **INSTALLATION.md** - Detailed installation instructions
- **CONFIGURATION.md** - Configuration and customization guide
- **TROUBLESHOOTING.md** - Problem-solving reference
- **GETTING_STARTED.md** - First-time user guide
- **PROJECT_SUMMARY.md** - Project overview and file structure

#### 🛠️ Utilities

- **setup.sh** - Automated installation script
- **setup_service.sh** - Systemd service setup script
- **healthcheck.sh** - System health diagnostic tool
- **test_components.py** - Component verification script

#### 🔐 Security

- User access control via whitelist
- Owner-only playback control
- Token security guidelines in documentation
- .gitignore for sensitive files

#### 📦 Dependencies

- Python 3.7+
- python-telegram-bot 20.7+
- yt-dlp latest
- mpv (system)
- ffmpeg (system)

#### 🎯 Supported Platforms

- Ubuntu 18.04+
- Debian 10+
- Any Linux distribution with mpv support

#### 🐛 Known Limitations

- No audio output to Telegram (headless only)
- Cannot skip to specific song in queue
- Cannot remove songs from queue
- Volume not persistent across restarts
- YouTube only (no Spotify/SoundCloud support)

---

## [Future] - Planned Features

### Under Consideration

- [ ] Database integration for persistent playlists
- [ ] Skip to specific song by number
- [ ] Remove song from queue
- [ ] Save/load favorite playlists
- [ ] Multi-user collaborative queue
- [ ] Now playing with album artwork
- [ ] Spotify/SoundCloud support
- [ ] Web dashboard for monitoring
- [ ] Voice message support
- [ ] Search YouTube directly from bot
- [ ] Download queue as playlist file
- [ ] Statistics and listening history

---

## Version History

| Version | Date       | Description                           |
| ------- | ---------- | ------------------------------------- |
| 1.0.0   | 2024-11-04 | Initial release with full feature set |

---

## How to Update

### From source

```bash
# Backup current version
cp ytmusic_interactive_bot.py ytmusic_interactive_bot.py.backup

# Download new version
# (instructions will be added when updates are available)

# Restart bot
sudo systemctl restart ytmusic-bot
```

### Dependencies

```bash
# Update Python packages
pip3 install --upgrade python-telegram-bot yt-dlp

# Update system packages
sudo apt update && sudo apt upgrade -y
```

---

## Contribution Guidelines

We welcome contributions! Areas where help is needed:

- Bug fixes
- Feature implementations
- Documentation improvements
- Testing on different platforms
- Translation to other languages

---

## Credits

**Built with:**

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube data extraction
- [mpv](https://mpv.io/) - Media player
- [ffmpeg](https://ffmpeg.org/) - Multimedia framework

**Special thanks to:**

- The open-source community
- All contributors and testers
- Music lovers everywhere 🎵

---

Made with ❤️ for the headless server community.
