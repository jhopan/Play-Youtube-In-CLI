# 🎵 YouTube Music Telegram Bot

Bot Telegram headless untuk streaming musik YouTube di Ubuntu Server tanpa GUI. Bot ini memungkinkan Anda mendengarkan musik YouTube langsung melalui Telegram dengan kontrol penuh menggunakan tombol interaktif.

> 🚀 **Quick Start?** Baca **[QUICKSTART.md](QUICKSTART.md)** untuk mulai dalam 5 menit!  
> 📚 **Dokumentasi Lengkap?** Lihat **[INDEX.md](INDEX.md)** untuk navigasi semua docs.

## ✨ Features

### 🎮 Full Playback Control

- **Load Playlist** - Load seluruh playlist YouTube
- **Load Video** - Tambahkan satu video ke queue
- **Play/Pause** - Kontrol pemutaran
- **Next/Previous** - Navigasi lagu
- **Stop** - Hentikan pemutaran

### 🎚️ Advanced Features

- **🔁 Loop Mode** - Ulangi satu lagu terus-menerus
- **🔀 Shuffle Mode** - Acak urutan pemutaran
- **🔊 Volume Control** - 4 level volume (25%, 50%, 75%, 100%)
- **📜 Queue Display** - Lihat 10 lagu teratas di playlist
- **Auto-Next** - Otomatis lanjut ke lagu berikutnya

### 🛡️ Security & Stability

- **User Whitelist** - Kontrol akses dengan user ID
- **Owner-only Controls** - Hanya owner yang bisa kontrol playback
- **Auto-restart** - Jika mpv crash, otomatis lanjut
- **Error Handling** - Tangani error dengan graceful
- **24/7 Operation** - Bisa jalan terus dengan systemd

### 💫 User Experience

- **Interactive Buttons** - Semua kontrol pakai tombol (tidak perlu command text)
- **Real-time Notifications** - Notifikasi saat lagu berganti
- **HTML Formatting** - Tampilan rapi dengan emoji
- **Responsive** - Menggunakan asyncio untuk performa optimal

## 🏗️ Architecture

### Technology Stack

```
├── Python 3
├── python-telegram-bot  # Telegram Bot API
├── yt-dlp              # YouTube data extraction
├── mpv                 # Headless audio player
└── ffmpeg              # Audio processing
```

### Bot Structure

```
ytmusic_interactive_bot.py
├── Configuration        # Token, whitelist, settings
├── Data Structures      # Song class, PlayerState
├── YouTube Functions    # yt-dlp integration
│   ├── extract_playlist()
│   └── get_video_info()
├── MPV Functions        # Player control
│   ├── start_mpv()
│   ├── stop_mpv()
│   ├── pause_mpv()
│   └── resume_mpv()
├── Playback Management  # Core logic
│   ├── play_current_song()
│   ├── play_next_song()
│   ├── play_previous_song()
│   └── handle_song_finished()
├── UI Components        # Keyboards
│   ├── get_main_keyboard()
│   └── get_volume_keyboard()
├── Command Handlers     # /start
├── Callback Handlers    # Button clicks
│   ├── handle_load_playlist()
│   ├── handle_load_video()
│   ├── handle_play_pause()
│   ├── handle_next()
│   ├── handle_prev()
│   ├── handle_stop()
│   ├── handle_toggle_loop()
│   ├── handle_toggle_shuffle()
│   ├── handle_volume_change()
│   └── handle_show_queue()
├── Message Handlers     # URL processing
└── Error Handler        # Global error handling
```

## 📦 Files

```
📁 Project
├── 📄 ytmusic_interactive_bot.py  # Main bot script (800+ lines)
├── 📄 requirements.txt            # Python dependencies
├── 📄 ytmusic_bot.service         # Systemd service file
├── 📄 INSTALLATION.md            # Detailed installation guide
└── 📄 README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# System packages
sudo apt update
sudo apt install python3 python3-pip mpv ffmpeg -y

# Python packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

Add your bot token and allowed user IDs:
```env
BOT_TOKEN=your_bot_token_from_botfather
ALLOWED_USER_IDS=123456789,987654321
DEFAULT_VOLUME=75
DEBUG=false
```

📖 **See [ENV_SETUP.md](docs/ENV_SETUP.md) for detailed configuration guide**

### 3. Run Bot

Ganti `TOKEN`:

```python
TOKEN = "YOUR_BOT_TOKEN_HERE"  # Dari @BotFather
```

Optional whitelist:

```python
ALLOWED_USERS = [123456789]  # Your Telegram User ID
```

### 3. Run Bot

```bash
python3 ytmusic_interactive_bot.py
```

### 4. Test in Telegram

1. Buka bot Anda di Telegram
2. Kirim `/start`
3. Klik **🎶 Load Playlist**
4. Kirim link playlist YouTube
5. Musik otomatis diputar!

## 📱 Usage Guide

### Main Menu

```
🎧 YouTube Player Bot
Pilih tindakan:
[🎶 Load Playlist] [🎵 Load Video]
[▶️ Play] [⏸ Pause] [⏭ Next] [⏮ Prev]
[🔁 Loop] [🔀 Shuffle] [🔊 Volume] [📜 Queue]
[⏹ Stop]
```

### Loading Music

1. **Playlist**: Klik 🎶 → Kirim playlist URL → Semua video dimuat
2. **Single Video**: Klik 🎵 → Kirim video URL → Ditambahkan ke queue

### Playback Control

- **▶️ Play**: Mulai/resume pemutaran
- **⏸ Pause**: Jeda pemutaran
- **⏭ Next**: Lagu selanjutnya
- **⏮ Prev**: Lagu sebelumnya
- **⏹ Stop**: Stop dan clear playback

### Special Modes

- **🔁 Loop**: Aktif (🔂) = ulang 1 lagu terus
- **🔀 Shuffle**: Aktif (🎲) = acak urutan

### Volume Control

```
Pilih volume:
[🔇 25%] [🔉 50%]
[🔊 75%] [📢 100%]
```

### Queue Display

```
📜 Queue (15 songs)

🔊 1. Rick Astley - Never Gonna Give You Up
   2. Queen - Bohemian Rhapsody
   3. The Beatles - Hey Jude
   ...
   10. Led Zeppelin - Stairway to Heaven

... and 5 more songs
```

## 🔧 Advanced Setup

### Systemd Service (24/7 Operation)

1. **Create service file:**

```bash
sudo nano /etc/systemd/system/ytmusic-bot.service
```

2. **Paste configuration:**

```ini
[Unit]
Description=YouTube Music Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/usr/bin/python3 /home/ubuntu/ytmusic_interactive_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Enable & start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable ytmusic-bot
sudo systemctl start ytmusic-bot
sudo systemctl status ytmusic-bot
```

4. **View logs:**

```bash
sudo journalctl -u ytmusic-bot -f
```

### Using Screen (Alternative)

```bash
# Install screen
sudo apt install screen -y

# Run bot
screen -S ytmusic
python3 ytmusic_interactive_bot.py

# Detach: Ctrl+A then D
# Reattach: screen -r ytmusic
```

## 🎯 How It Works

### 1. Streaming Architecture

```
YouTube → yt-dlp (extract URL) → mpv (stream audio) → Server speakers (headless)
                                                      ↓
                                            User controls via Telegram
```

### 2. Playback Flow

```
User clicks Load Playlist
    ↓
yt-dlp extracts all video info
    ↓
Songs added to playlist[]
    ↓
Auto-start play_current_song()
    ↓
mpv streams directly (no download)
    ↓
Wait for song finish
    ↓
Auto-next or loop (based on mode)
    ↓
Repeat
```

### 3. State Management

```python
class PlayerState:
    playlist: List[Song]      # All songs
    current_index: int        # Current playing
    is_playing: bool          # Playing status
    is_paused: bool           # Paused status
    loop_enabled: bool        # Loop mode
    shuffle_enabled: bool     # Shuffle mode
    volume: int               # Volume level
    mpv_process: Popen        # MPV process
    owner_id: int             # Bot owner
```

### 4. Error Handling

- **yt-dlp error**: Invalid URL → Show error message
- **mpv crash**: Auto-skip to next song
- **Network issue**: Retry with exponential backoff
- **Empty playlist**: Show "Load music first" message
- **Unauthorized user**: Deny access with message

## 🔐 Security

### Access Control

```python
# Only specific users can use bot
ALLOWED_USERS = [123456789, 987654321]

# Only owner can control playback
def is_owner(user_id: int) -> bool:
    if player.owner_id is None:
        player.owner_id = user_id
        return True
    return user_id == player.owner_id
```

### Best Practices

- ✅ Keep TOKEN secret (use environment variable in production)
- ✅ Use whitelist for private bot
- ✅ Run as non-root user
- ✅ Regular security updates: `sudo apt update && sudo apt upgrade`

## 🐛 Troubleshooting

### Bot not responding

```bash
# Check if running
ps aux | grep python3

# Check logs
sudo journalctl -u ytmusic-bot -n 50

# Restart
sudo systemctl restart ytmusic-bot
```

### MPV not working

```bash
# Test mpv
mpv --no-video "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Reinstall
sudo apt remove mpv -y
sudo apt install mpv -y
```

### yt-dlp extraction failed

```bash
# Update yt-dlp (YouTube changes often)
pip install --upgrade yt-dlp

# Test extraction
yt-dlp --flat-playlist "PLAYLIST_URL"
```

### High CPU usage

```bash
# Check process
htop

# Limit mpv CPU (optional)
# Add to mpv command: --demuxer-max-bytes=50M
```

## 📊 System Requirements

### Minimum

- **OS**: Ubuntu 18.04+ (or any Linux with mpv)
- **RAM**: 512 MB
- **CPU**: 1 core
- **Network**: Stable internet for streaming

### Recommended

- **RAM**: 1 GB+
- **CPU**: 2 cores+
- **Storage**: 1 GB free space (for logs)
- **Network**: 5+ Mbps for smooth streaming

## 🔄 Updates & Maintenance

### Update Bot

```bash
# Backup
cp ytmusic_interactive_bot.py ytmusic_interactive_bot.py.backup

# Upload new version
# ...

# Restart
sudo systemctl restart ytmusic-bot
```

### Update Dependencies

```bash
pip install --upgrade python-telegram-bot yt-dlp
sudo apt update && sudo apt upgrade -y
```

### Clean Logs (if too big)

```bash
# Check log size
sudo journalctl --disk-usage

# Clean old logs
sudo journalctl --vacuum-time=7d
```

## 💡 Tips & Tricks

### 1. Multiple Playlists

Load beberapa playlist berturut-turut - semua akan ditambahkan ke queue.

### 2. Mix Modes

Kombinasi Loop OFF + Shuffle ON = acak playlist tanpa repeat.

### 3. Background Operation

Gunakan systemd agar bot jalan 24/7, bahkan setelah server restart.

### 4. Volume Persistence

Volume tersimpan di memory, akan reset jika bot restart.

### 5. Queue Management

Saat ini queue tidak bisa diedit. Restart bot untuk clear queue.

## 📝 Known Limitations

- ❌ Tidak bisa skip ke lagu tertentu (hanya next/prev)
- ❌ Tidak bisa hapus lagu dari queue
- ❌ Volume tidak persisten (reset saat restart)
- ❌ Tidak support Spotify/SoundCloud (YouTube only)
- ❌ Tidak ada audio output ke Telegram (player di server)

## 🛣️ Roadmap

Fitur yang mungkin ditambahkan:

- [ ] Database untuk save playlist
- [ ] Skip to specific song
- [ ] Remove song from queue
- [ ] Save/load favorite playlists
- [ ] Multi-user queue (collaborative playlist)
- [ ] Now playing with album art
- [ ] Spotify/SoundCloud support

## 📄 License

MIT License - Bebas digunakan dan dimodifikasi.

## 👨‍💻 Contributing

Feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 🙏 Credits

Built with:

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [mpv](https://mpv.io/)

## 📞 Support

Jika ada pertanyaan atau masalah, check:

1. **INSTALLATION.md** - Detailed setup guide
2. **Logs**: `sudo journalctl -u ytmusic-bot -f`
3. **Manual test**: `python3 ytmusic_interactive_bot.py`

---

**Selamat menikmati musik! 🎵🎧🎉**

Made with ❤️ for music lovers who run headless servers.
