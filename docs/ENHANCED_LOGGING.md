# Enhanced Logging System

## Overview

Bot now features comprehensive terminal logging that shows meaningful activity instead of generic HTTP requests. All important events are logged with emojis for easy visual scanning.

## What's Logged

### 🚀 Bot Startup

```
🎵 YouTube Music Telegram Bot - Starting...
✅ Configuration validated successfully
🔑 Token configured: Yes
📝 Log level: INFO
📋 Registering handlers...
✓ Command handlers registered
✓ Callback handlers registered
✓ Message handlers registered
✓ Error handler registered
🚀 Bot is now running! Press Ctrl+C to stop.
```

### 👤 User Interactions

**Commands:**

```
📞 /start command received from @username (ID: 123456789, Name: John)
💬 Welcome message sent to @username
```

**Button Clicks:**

```
🎯 Button clicked by @username (ID: 123456789): 'play_pause'
▶️ @username started playback
⏸️ @username paused playback
⏭️ @username skipped to next song
⏮️ @username went to previous song
⏹️ @username stopped playback
```

**Access Control:**

```
🚫 Access denied for @unauthorized (ID: 987654321)
🚫 Non-owner @guest tried to use control: 'next'
```

### 🎵 Playback Events

**Song Playing:**

```
🎵 Now playing: 'Song Title Here' [3/10]
✅ Song finished: 'Song Title Here'
```

**Auto-Next Dialog:**

```
⏱️ Showing auto-next dialog (5 second countdown)
📢 Auto-next dialog: Next song is 'Next Song Title'
⏩ Auto-next countdown finished - playing next song
⏩ @username manually continued to next song via auto-next dialog
⏹️ @username stopped playback via auto-next dialog
```

**Loop & Shuffle:**

```
🔁 Loop enabled - replaying current song
🔁 @username enabled loop mode
🔀 Shuffle mode: Selected random song at index 5
🔀 @username enabled shuffle mode
```

### 🔊 Volume Control

**Volume Menu:**

```
🔊 @username opened volume menu (current: 50%)
```

**Volume Changes:**

```
🔊 @username increased volume: 50% → 60%
🔉 @username decreased volume: 60% → 50%
🔊 @username set volume: 50% → 75%
🔇 @username toggled mute
```

**Volume Errors:**

```
❌ Volume increase failed for @username
❌ Volume decrease failed for @username
❌ Mute toggle failed for @username
```

### 🔗 URL Processing

**Video/Playlist Loading:**

```
🔗 @username sent URL: https://youtube.com/watch?v=...
📋 @username loading playlist from: https://youtube.com/playlist?list=...
✅ Loaded 25 songs from playlist for @username (Total: 25)
▶️ Auto-started playback for @username

🎥 @username loading video from: https://youtube.com/watch?v=...
✅ Added video for @username: 'Video Title' (Position: 1)
▶️ Auto-started playback for @username
```

**URL Errors:**

```
⚠️ Invalid YouTube URL from @username: https://invalid-url.com
❌ Error processing URL from @username: Connection timeout
```

### 📋 Navigation

**Menu Actions:**

```
📋 @username viewed queue (10 songs)
ℹ️ @username viewed bot info
↩️ @username returned to main menu
📋 @username requested to load playlist - waiting for URL
🎥 @username requested to load video - waiting for URL
```

### ⚠️ Warnings & Errors

**Warnings:**

```
⚠️ @username tried to play but playlist is empty
⚠️ @username tried to skip but playlist is empty
⚠️ No songs in playlist
⚠️ MPV exited with code 1
```

**Errors:**

```
❌ Error playing song: MPV process failed
❌ Error sending notification: User blocked bot
❌ Error updating countdown: Message was deleted
❌ Configuration error: BOT_TOKEN not set
```

## Configuration

### Disable Noisy Logs

The following third-party loggers are automatically set to WARNING level to reduce noise:

```python
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
```

### Log Format

All logs use the format:

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Example:

```
2024-11-05 10:30:45,123 - __main__ - INFO - 🎵 Now playing: 'Song Title' [1/10]
```

### Log Levels

- **INFO**: Normal operations (default)
- **WARNING**: Unusual events (empty playlist, invalid URLs)
- **ERROR**: Failures (MPV errors, API failures)

## Benefits

✅ **Easy Monitoring**: Visual emoji scanning  
✅ **User Tracking**: See who does what  
✅ **Debugging**: Detailed event timeline  
✅ **Performance**: Quick issue identification  
✅ **Audit Trail**: Complete activity history

## Example Session

```
2024-11-05 10:30:00 - __main__ - INFO - 🚀 Bot is now running!
2024-11-05 10:30:15 - bot.handlers.commands - INFO - 📞 /start command received from @john (ID: 123456789, Name: John Doe)
2024-11-05 10:30:15 - bot.handlers.commands - INFO - 💬 Welcome message sent to @john
2024-11-05 10:30:20 - bot.handlers.callbacks - INFO - 🎯 Button clicked by @john (ID: 123456789): 'load_playlist'
2024-11-05 10:30:20 - bot.handlers.callbacks - INFO - 📋 @john requested to load playlist - waiting for URL
2024-11-05 10:30:30 - bot.handlers.messages - INFO - 🔗 @john sent URL: https://youtube.com/playlist?list=PLxxxx
2024-11-05 10:30:30 - bot.handlers.messages - INFO - 📋 @john loading playlist from: https://youtube.com/playlist?list=PLxxxx
2024-11-05 10:30:35 - bot.handlers.messages - INFO - ✅ Loaded 15 songs from playlist for @john (Total: 15)
2024-11-05 10:30:35 - bot.handlers.messages - INFO - ▶️ Auto-started playback for @john
2024-11-05 10:30:35 - bot.core.playback - INFO - 🎵 Now playing: 'First Song Title' [1/15]
2024-11-05 10:33:45 - bot.core.playback - INFO - ✅ Song finished: 'First Song Title'
2024-11-05 10:33:45 - bot.core.playback - INFO - ⏱️ Showing auto-next dialog (5 second countdown)
2024-11-05 10:33:45 - bot.core.playback - INFO - 📢 Auto-next dialog: Next song is 'Second Song Title'
2024-11-05 10:33:50 - bot.core.playback - INFO - ⏩ Auto-next countdown finished - playing next song
2024-11-05 10:33:50 - bot.core.playback - INFO - 🎵 Now playing: 'Second Song Title' [2/15]
2024-11-05 10:34:00 - bot.handlers.callbacks - INFO - 🎯 Button clicked by @john (ID: 123456789): 'volume'
2024-11-05 10:34:00 - bot.handlers.callbacks - INFO - 🔊 @john opened volume menu (current: 50%)
2024-11-05 10:34:05 - bot.handlers.callbacks - INFO - 🎯 Button clicked by @john (ID: 123456789): 'vol_up'
2024-11-05 10:34:05 - bot.handlers.callbacks - INFO - 🔊 @john increased volume: 50% → 60%
```

## Troubleshooting

### Still Seeing httpx Logs?

Make sure you're using the latest version with the logger suppression code in `main.py`.

### Logs Not Showing?

Check log level in `.env`:

```bash
LOG_LEVEL=INFO
```

### Too Verbose?

Set to WARNING to only see issues:

```bash
LOG_LEVEL=WARNING
```

## Related Documentation

- [UI Enhancements](UI_ENHANCEMENTS.md) - Improved button interface
- [Volume Control](VOLUME_CONTROL.md) - Real-time volume system
- [Installation Guide](INSTALLATION.md) - Setup instructions
