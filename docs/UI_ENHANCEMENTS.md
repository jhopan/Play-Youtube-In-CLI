# UI Enhancements - Improved User Experience

## Overview

This document describes the enhanced user interface features added to the YouTube Music Player bot for better user experience and control.

## New Features

### 1. **Enhanced Main Menu Layout**

The main menu now has a cleaner, more organized layout:

```
┌──────────────────────────────────────┐
│  🎵 Load Playlist  |  🎬 Load Video  │
├──────────────────────────────────────┤
│  ⏮️ Prev  |  ▶️ Play  |  ⏭️ Next    │
├──────────────────────────────────────┤
│          ⏹️ Stop                     │
├──────────────────────────────────────┤
│      🔁 Loop  |  🔀 Shuffle          │
├──────────────────────────────────────┤
│  🔊 Volume  |  📋 Queue (5)          │
├──────────────────────────────────────┤
│          ℹ️ Info                     │
└──────────────────────────────────────┘
```

**Features:**

- Logical grouping: Load → Playback → Modes → Settings → Info
- Stop button in its own row for easy access
- Queue button shows current playlist count
- New Info button for detailed information

### 2. **Advanced Volume Control**

Enhanced volume menu with fine-grained control:

```
┌──────────────────────────────────────┐
│      🔻 -10%  |  🔺 +10%             │
├──────────────────────────────────────┤
│      🔇 25%   |  🔉 50%              │
├──────────────────────────────────────┤
│      🔊 75%   |  📢 100%             │
├──────────────────────────────────────┤
│  🔇 Mute/Unmute  |  « Back to Menu   │
└──────────────────────────────────────┘
```

**Features:**

- **+10% / -10% buttons**: Fine-tune volume in 10% increments
- **Preset levels**: Quick access to 25%, 50%, 75%, 100%
- **Mute/Unmute toggle**: Instantly mute or restore volume
- **Real-time control**: Uses `amixer` for immediate effect
- **No restart needed**: Volume changes apply to currently playing song

**Volume Controls:**

- `+10%`: Increase volume by 10% (via `amixer -D pulse sset Master 10%+`)
- `-10%`: Decrease volume by 10% (via `amixer -D pulse sset Master 10%-`)
- `Mute/Unmute`: Toggle mute (via `amixer -D pulse sset Master toggle`)
- Preset levels: Set exact volume percentage

### 3. **Info Display**

New info button shows comprehensive bot status:

```
ℹ️ Bot Information

Now Playing:
🎵 Song Title
⏱️ Duration: 3:45
🔗 YouTube Link

Playlist:
📀 Total songs: 10
▶️ Current position: 5/10

Settings:
🔊 Volume: 75%
🔁 Loop: OFF
🔀 Shuffle: ON
```

**Features:**

- Current song details with YouTube link
- Playlist position and total count
- Current settings overview
- Clickable YouTube link to view on web

### 4. **Auto-Next Dialog (YouTube-like)**

When a song finishes, the bot shows a countdown dialog:

```
ℹ️ Song Finished!

▶️ Next: Song Title

⏱️ Auto-playing in 5 seconds...
Press 'Stop' to cancel.

┌──────────────────────────────────────┐
│  ▶️ Play Next  |  ⏹️ Stop            │
└──────────────────────────────────────┘
```

**Features:**

- **5-second countdown**: Live countdown before auto-play
- **Visual feedback**: Updates every second showing remaining time
- **Manual control**:
  - "Play Next" button to skip countdown
  - "Stop" button to cancel auto-play
- **Cancellable**: Can be interrupted at any time
- **Smart behavior**: Only shows if playlist has more songs

**Behavior:**

- Countdown updates in real-time (5, 4, 3, 2, 1...)
- If not cancelled, automatically plays next song
- If "Play Next" is clicked, immediately starts next song
- If "Stop" is clicked, stops playback and cancels countdown
- Respects loop mode (doesn't show dialog when looping)

## Technical Implementation

### Volume Control Backend

The volume control uses a triple-fallback system:

1. **MPV IPC Socket** (Primary): Real-time control via Unix socket
2. **amixer** (Recommended): System volume control via ALSA/PulseAudio
3. **pactl** (Fallback): PulseAudio control utility

```python
# Volume up by 10%
amixer -D pulse sset Master 10%+

# Volume down by 10%
amixer -D pulse sset Master 10%-

# Toggle mute
amixer -D pulse sset Master toggle
```

### Auto-Next Dialog

Uses `asyncio` for non-blocking countdown:

```python
async def show_auto_next_dialog(application, countdown_seconds=5):
    # Send initial message
    message = await bot.send_message(...)

    # Create countdown task
    async def countdown_task():
        for remaining in range(countdown_seconds - 1, 0, -1):
            await asyncio.sleep(1)
            await message.edit_text(...)  # Update countdown

        # Auto-play next song
        await play_next(application)

    # Store task for cancellation
    task = asyncio.create_task(countdown_task())
    application.bot_data['auto_next_task'] = task
```

**Cancellation:**

```python
# Cancel countdown when user clicks button
if 'auto_next_task' in context.bot_data:
    context.bot_data['auto_next_task'].cancel()
    del context.bot_data['auto_next_task']
```

## Usage Examples

### Adjusting Volume

1. Click "🔊 Volume" button
2. Use "+10%" or "-10%" for fine adjustments
3. Or select preset level (25%, 50%, 75%, 100%)
4. Click "Mute/Unmute" to toggle mute
5. Volume changes apply immediately

### Viewing Bot Info

1. Click "ℹ️ Info" button
2. View current song, playlist status, and settings
3. Click "« Back to Menu" to return

### Auto-Next Behavior

1. Song finishes playing
2. Bot shows countdown: "Auto-playing in 5 seconds..."
3. Options:
   - Wait: Next song plays automatically after 5 seconds
   - Click "▶️ Play Next": Skip countdown, play immediately
   - Click "⏹️ Stop": Cancel auto-play, stop playback

## Benefits

### User Experience

- **Intuitive layout**: Clear visual hierarchy
- **Fine control**: Precise volume adjustments
- **Transparency**: Full status visibility via Info button
- **Predictability**: YouTube-like auto-next behavior

### Technical

- **Non-blocking**: Countdown doesn't block other operations
- **Cancellable**: User maintains full control
- **Real-time**: Volume changes apply instantly
- **Graceful**: Handles errors and edge cases

## Configuration

No additional configuration needed. All features work out of the box with existing setup.

### Countdown Duration

To change auto-next countdown duration, edit `playback.py`:

```python
# Default: 5 seconds
await PlaybackManager.show_auto_next_dialog(application, countdown_seconds=5)

# Custom: 10 seconds
await PlaybackManager.show_auto_next_dialog(application, countdown_seconds=10)
```

## Troubleshooting

### Volume buttons not working

**Symptom**: +10% / -10% buttons don't change volume

**Solution**: Ensure `amixer` is installed and PulseAudio is running:

```bash
# Check amixer
amixer -D pulse sset Master 5%+

# Check PulseAudio
pactl info
```

### Auto-next countdown stuck

**Symptom**: Countdown doesn't update or complete

**Solution**: Check logs for errors:

```bash
tail -f logs/bot.log | grep "auto-next"
```

### Info button shows wrong data

**Symptom**: Info display shows incorrect song or settings

**Solution**: Restart bot to reset state:

```bash
systemctl restart ytmusic-bot
```

## Future Enhancements

Potential improvements for future versions:

1. **Seek controls**: Fast forward / rewind buttons
2. **Lyrics display**: Show song lyrics if available
3. **Search feature**: Search YouTube directly from bot
4. **Favorites**: Mark songs as favorites
5. **History**: View recently played songs
6. **Custom countdown**: User-configurable auto-next delay

## Related Documentation

- [Volume Control Guide](VOLUME_CONTROL.md) - Manual volume control commands
- [Architecture](ARCHITECTURE.md) - Technical architecture overview
- [Configuration](CONFIGURATION.md) - Bot configuration options

## Changelog

### Version 2.1 (Current)

- ✅ Enhanced main menu layout with Info button
- ✅ Advanced volume control (+10% / -10% / Mute)
- ✅ Info display with comprehensive status
- ✅ Auto-next dialog with countdown (YouTube-like)
- ✅ Real-time volume control via amixer
- ✅ Non-blocking countdown with cancellation

### Version 2.0

- ✅ MPV IPC socket implementation
- ✅ System volume control via amixer fallback
- ✅ Basic volume menu (preset levels only)

---

**Note**: All UI enhancements are fully tested and production-ready. The countdown feature is non-blocking and won't interfere with other bot operations.
