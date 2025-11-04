# 🔧 Configuration Guide

Panduan lengkap konfigurasi YouTube Music Bot.

## 🎯 Basic Configuration

### 1. Bot Token

**Mendapatkan Token:**

1. Buka [@BotFather](https://t.me/botfather) di Telegram
2. Kirim `/newbot`
3. Ikuti instruksi (nama bot, username)
4. Copy token yang diberikan

**Format Token:**

```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456789
```

**Konfigurasi di script:**

```python
TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456789"
```

⚠️ **Jangan share token ke publik!**

### 2. User Whitelist

**Allow All Users (Public Bot):**

```python
ALLOWED_USERS = []  # Kosongkan = semua orang bisa akses
```

**Restrict to Specific Users (Private Bot):**

```python
ALLOWED_USERS = [123456789, 987654321]  # Hanya user ID ini yang bisa akses
```

**Cara dapat User ID:**

1. Buka [@userinfobot](https://t.me/userinfobot)
2. Kirim `/start`
3. Copy angka di "Id:"

---

## ⚙️ Advanced Configuration

### Volume Default

**Setting awal volume (25-100):**

```python
class PlayerState:
    def __init__(self):
        # ... other settings ...
        self.volume: int = 50  # Ganti dengan 25, 50, 75, atau 100
```

### MPV Options

**Customize mpv command:**

```python
def start_mpv(url: str) -> subprocess.Popen:
    cmd = [
        'mpv',
        '--no-video',              # Jangan tampilkan video
        '--no-terminal',           # Mode headless
        '--quiet',                 # Minimal output
        f'--volume={player.volume}',
        '--demuxer-max-bytes=50M', # Limit buffer (hemat RAM)
        '--cache=yes',             # Enable cache
        '--cache-secs=10',         # 10 detik buffer
        url
    ]
    # ...
```

**Options berguna:**

- `--volume=N` - Set volume (0-100)
- `--speed=N` - Playback speed (0.5 = slow, 2.0 = fast)
- `--af=equalizer=...` - Audio filters/equalizer
- `--cache-secs=N` - Cache duration
- `--demuxer-max-bytes=N` - Max buffer size

### Logging Level

**Change log verbosity:**

```python
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Ganti: DEBUG, INFO, WARNING, ERROR
)
```

**Level explanation:**

- `DEBUG` - Semua info detail (banyak log)
- `INFO` - Info normal (recommended)
- `WARNING` - Hanya warning & error
- `ERROR` - Hanya error

---

## 🔒 Security Configuration

### 1. Environment Variables (Recommended)

**Jangan hardcode token di script!**

**Cara 1: .env file**

```bash
# Buat file .env
nano .env
```

```bash
# Isi .env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USER_IDS=123456789,987654321
```

```python
# Install python-dotenv
pip install python-dotenv

# Di script:
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ALLOWED_USERS = [int(x) for x in os.getenv('ALLOWED_USER_IDS', '').split(',') if x]
```

**Cara 2: System environment**

```bash
# Di ~/.bashrc atau /etc/environment
export TELEGRAM_BOT_TOKEN="1234567890:..."
export ALLOWED_USER_IDS="123456789,987654321"
```

```python
# Di script:
import os
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ALLOWED_USERS = [int(x) for x in os.environ.get('ALLOWED_USER_IDS', '').split(',') if x]
```

### 2. File Permissions

```bash
# Script hanya bisa dibaca owner
chmod 600 ytmusic_interactive_bot.py

# Atau
chmod 700 ytmusic_interactive_bot.py
```

### 3. Firewall (Optional)

```bash
# Install ufw
sudo apt install ufw -y

# Allow SSH (PENTING!)
sudo ufw allow ssh

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

Bot tidak perlu port khusus (outgoing connection only).

---

## 🎛️ Playback Configuration

### Auto-Next Behavior

**Default: Auto-next setelah lagu selesai**

**Custom delay before next:**

```python
async def handle_song_finished(application: Application):
    """Handle when a song finishes playing"""

    # Tambahkan delay 2 detik sebelum next
    await asyncio.sleep(2)

    if player.loop_enabled:
        await play_current_song(application)
    else:
        await play_next_song(application)
```

### Shuffle Algorithm

**Default: Random**

**Custom: Weighted random (jarang yang belum diputar):**

```python
async def play_next_song(application: Application):
    if player.shuffle_enabled:
        # Implementasi custom shuffle
        # Contoh: prioritaskan lagu yang belum diputar
        unplayed = [i for i in range(len(player.playlist))
                    if i != player.current_index]
        if unplayed:
            player.current_index = random.choice(unplayed)
    else:
        player.current_index += 1
        if player.current_index >= len(player.playlist):
            player.current_index = 0

    await play_current_song(application)
```

### Error Retry

**Auto-retry jika mpv crash:**

```python
async def play_current_song(application: Application):
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # ... play logic ...
            break
        except Exception as e:
            retry_count += 1
            logger.error(f"Retry {retry_count}/{max_retries}: {e}")
            await asyncio.sleep(2)

    if retry_count >= max_retries:
        # Skip to next song
        await play_next_song(application)
```

---

## 📱 UI Customization

### Button Layout

**Custom main keyboard:**

```python
def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        # Row 1: Load options
        [
            InlineKeyboardButton("📂 Playlist", callback_data="load_playlist"),
            InlineKeyboardButton("🎵 Video", callback_data="load_video"),
        ],
        # Row 2: Main controls
        [
            InlineKeyboardButton("⏮️", callback_data="prev"),
            InlineKeyboardButton("⏯️", callback_data="play_pause"),
            InlineKeyboardButton("⏭️", callback_data="next"),
        ],
        # Row 3: Modes
        [
            InlineKeyboardButton("🔁", callback_data="toggle_loop"),
            InlineKeyboardButton("🔀", callback_data="toggle_shuffle"),
            InlineKeyboardButton("⏹️", callback_data="stop"),
        ],
        # Row 4: Settings
        [
            InlineKeyboardButton("🔊 Vol", callback_data="volume"),
            InlineKeyboardButton("📜 Queue", callback_data="show_queue"),
            InlineKeyboardButton("ℹ️ Info", callback_data="show_info"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
```

### Message Format

**Custom now playing message:**

```python
# Di play_current_song():
message = (
    f"🎵 <b>Now Playing</b>\n\n"
    f"<i>{current_song.title}</i>\n\n"
    f"⏱ Duration: {current_song.duration}s\n"
    f"📊 {player.current_index + 1}/{len(player.playlist)}\n"
    f"🔊 Volume: {player.volume}%\n"
    f"🔁 Loop: {'ON' if player.loop_enabled else 'OFF'}\n"
    f"🔀 Shuffle: {'ON' if player.shuffle_enabled else 'OFF'}"
)
```

### Emoji Customization

**Change emojis:**

```python
# Di get_main_keyboard():
loop_emoji = "♾️" if player.loop_enabled else "🔁"  # Infinity untuk loop
shuffle_emoji = "🎰" if player.shuffle_enabled else "🔀"  # Dice untuk shuffle
play_emoji = "⏸️" if (player.is_playing and not player.is_paused) else "▶️"
```

---

## 🗄️ Data Persistence (Advanced)

### Save Playlist to File

```python
import json

def save_playlist():
    """Save current playlist to file"""
    data = {
        'playlist': [{'url': s.url, 'title': s.title} for s in player.playlist],
        'current_index': player.current_index,
        'volume': player.volume,
        'loop_enabled': player.loop_enabled,
        'shuffle_enabled': player.shuffle_enabled,
    }
    with open('playlist_state.json', 'w') as f:
        json.dump(data, f)

def load_playlist():
    """Load playlist from file"""
    try:
        with open('playlist_state.json', 'r') as f:
            data = json.load(f)

        player.playlist = [Song(url=s['url'], title=s['title'])
                          for s in data['playlist']]
        player.current_index = data['current_index']
        player.volume = data['volume']
        player.loop_enabled = data['loop_enabled']
        player.shuffle_enabled = data['shuffle_enabled']
    except FileNotFoundError:
        pass

# Call on start/stop
# Di main(): load_playlist()
# Di stop handler: save_playlist()
```

---

## 🧪 Testing Configuration

### Test Mode

```python
# Add at top
DEBUG_MODE = True  # Set False in production

if DEBUG_MODE:
    # Use test token
    TOKEN = "TEST_TOKEN"
    # Allow only test user
    ALLOWED_USERS = [YOUR_TEST_USER_ID]
    # Increase logging
    logging.basicConfig(level=logging.DEBUG)
```

### Dry Run (No Audio)

```python
def start_mpv(url: str) -> subprocess.Popen:
    if DEBUG_MODE:
        # Fake process (no actual audio)
        logger.info(f"[DRY RUN] Would play: {url}")
        return None

    # Normal mpv launch
    # ...
```

---

## 📊 Monitoring Configuration

### Stats Tracking

```python
class PlayerState:
    def __init__(self):
        # ... existing ...
        self.total_songs_played: int = 0
        self.total_playback_time: int = 0
        self.start_time: float = time.time()

# Update on each song
async def play_current_song():
    # ...
    player.total_songs_played += 1
    # ...

# Show stats command
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = time.time() - player.start_time
    message = (
        f"📊 <b>Bot Statistics</b>\n\n"
        f"⏰ Uptime: {int(uptime/3600)}h {int((uptime%3600)/60)}m\n"
        f"🎵 Songs played: {player.total_songs_played}\n"
        f"📂 Queue size: {len(player.playlist)}\n"
        f"👤 Owner: {player.owner_id}\n"
    )
    await update.message.reply_text(message, parse_mode="HTML")

# Add handler
application.add_handler(CommandHandler("stats", stats_command))
```

---

## 🔄 Update Configuration

### Auto-Update yt-dlp

```python
import subprocess

def update_ytdlp():
    """Update yt-dlp to latest version"""
    try:
        subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'],
                      check=True, capture_output=True)
        logger.info("yt-dlp updated successfully")
    except Exception as e:
        logger.error(f"Failed to update yt-dlp: {e}")

# Run on bot start or daily
# In main():
# update_ytdlp()
```

---

## ✅ Configuration Checklist

- [ ] Token configured correctly
- [ ] User whitelist setup (if needed)
- [ ] Environment variables (for production)
- [ ] File permissions secured
- [ ] Logging level appropriate
- [ ] MPV options tuned
- [ ] UI customized (optional)
- [ ] Data persistence setup (optional)
- [ ] Monitoring enabled (optional)

---

## 🆘 Configuration Help

**Common issues:**

1. **"Token is invalid"**

   - Check format (no spaces/newlines)
   - Get new token from @BotFather

2. **"Access denied"**

   - Check ALLOWED_USERS array
   - Make sure your user ID is included

3. **"MPV not found"**

   - Check mpv path: `which mpv`
   - Update cmd in start_mpv()

4. **High memory usage**
   - Add `--demuxer-max-bytes=50M` to mpv
   - Reduce `--cache-secs`

---

**Configuration done! 🎉**

Lanjut ke: `QUICKSTART.md` untuk test bot!
