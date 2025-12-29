# 🎵 YouTube Music Telegram Bot

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-Play--Youtube--In--CLI-blue?logo=github)](https://github.com/jhopan/Play-Youtube-In-CLI)

Bot Telegram headless untuk streaming musik YouTube di Ubuntu Server tanpa GUI. Kontrol penuh playback music melalui interface Telegram yang interaktif.

> 🚀 **Dokumentasi lengkap ada di bawah** - scroll untuk melihat semua fitur, instalasi, dan troubleshooting!

---

## ✨ Features

### 🎮 Playback Control

- **📋 Load Playlist** - Import seluruh YouTube playlist (otomatis masuk queue jika sedang memutar)
- **🎥 Load Video** - Tambah single video ke queue
- **▶️ Play/Pause** - Kontrol pemutaran real-time
- **⏭️ Next/Previous** - Navigasi antar lagu
- **⏹️ Stop** - Hentikan pemutaran
- **💾 Save Playlist** - Simpan playlist favorit untuk diputar kapan saja
- **📂 Saved Playlists** - Akses dan putar playlist yang sudah disimpan

### 🎚️ Advanced Features

- **🔁 Loop Mode** - Repeat satu lagu terus-menerus
- **🔀 Shuffle Mode** - Random playback order
- **🔊 Volume Control** - Fine-tune dengan +10/-10, preset levels, instant mute
- **📋 Queue Display** - Lihat playlist current state
- **⏱️ Auto-Next Dialog** - YouTube-style countdown (5 detik) sebelum next song
- **ℹ️ Info Display** - Comprehensive bot status & current song details

### 🛡️ Security & Stability

- **User Whitelist** - Access control via Telegram User ID
- **Owner-Only Controls** - Hanya bot owner yang bisa kontrol playback
- **Auto-Restart** - MPV process monitoring & auto-recovery
- **Graceful Error Handling** - Comprehensive error management
- **24/7 Operation** - Systemd service support untuk continuous operation

### 💫 User Experience

- **Interactive Buttons** - Full UI dengan inline keyboards
- **Real-time Notifications** - Instant updates saat song changes
- **HTML Formatting** - Clean UI dengan emoji & formatting
- **Async Operations** - Non-blocking dengan asyncio
- **📊 Enhanced Logging** - Detailed terminal logs dengan emoji, user tracking, event monitoring

---

## 🏗️ Architecture

### Technology Stack

| Component              | Technology                | Purpose                         |
| ---------------------- | ------------------------- | ------------------------------- |
| **Bot Framework**      | python-telegram-bot 22.5+ | Telegram Bot API integration    |
| **YouTube Extraction** | yt-dlp                    | Video URL & metadata extraction |
| **Audio Player**       | MPV                       | Headless audio streaming        |
| **Audio Processing**   | ffmpeg                    | Audio codec support             |
| **Volume Control**     | amixer / pactl            | System-level volume management  |
| **Environment**        | python-dotenv             | Configuration management        |

### Project Structure

```
Play-Youtube-In-CLI/
├── main.py                 # Bot entry point
├── .env                    # Configuration (BOT_TOKEN, ALLOWED_USER_IDS)
├── requirements.txt        # Python dependencies
├── ytmusic_bot.service     # Systemd service file
│
├── bot/
│   ├── config.py          # Configuration & emoji mappings
│   ├── core/              # Core functionality
│   │   ├── player_state.py     # Singleton player state
│   │   ├── mpv_player.py       # MPV process control
│   │   ├── youtube.py          # yt-dlp integration
│   │   └── playback.py         # Playback orchestration
│   ├── handlers/          # Telegram handlers
│   │   ├── commands.py         # /start command
│   │   ├── callbacks.py        # Button interactions
│   │   └── messages.py         # URL message processing
│   └── utils/             # Utilities
│       ├── keyboards.py        # Inline keyboard layouts
│       ├── formatters.py       # Message formatting
│       └── access_control.py   # User authentication
│
├── docs/                  # Documentation
│   ├── INDEX.md                # Documentation navigator
│   ├── QUICKSTART.md           # 5-minute setup guide
│   ├── INSTALLATION.md         # Detailed installation
│   ├── ENV_SETUP.md            # Environment configuration
│   ├── ENHANCED_LOGGING.md     # Logging system guide
│   ├── VOLUME_CONTROL.md       # Volume control technical docs
│   ├── UI_ENHANCEMENTS.md      # UI features documentation
│   ├── TROUBLESHOOTING.md      # Common issues & fixes
│   └── CHANGELOG.md            # Version history
│
├── scripts/               # Utility scripts
│   ├── setup.sh                # Auto-setup script
│   ├── setup_service.sh        # Interactive systemd service creator
│   ├── setup_alias.sh          # Create aliases for systemctl commands
│   └── healthcheck.sh          # System health checker
│
└── backup/                # Legacy monolithic version
    └── ytmusic_interactive_bot.py
```

---

## 🚀 Quick Installation

### Prerequisites

- **Ubuntu Server 20.04+** / **Debian 11+**
- **Python 3.8+**
- **Internet connection**
- **Telegram Bot Token** dari [@BotFather](https://t.me/botfather)

### One-Liner Installation

```bash
git clone https://github.com/jhopan/Play-Youtube-In-CLI.git && \
cd Play-Youtube-In-CLI && \
sudo apt update && sudo apt install -y python3 python3-pip python3-venv mpv ffmpeg alsa-utils && \
python3 -m venv venv && source venv/bin/activate && \
pip install -r requirements.txt && \
cp .env.example .env && \
echo "Setup complete! Edit .env with your bot token, then run: python3 main.py"
```

### Manual Installation

#### 1. Clone Repository

```bash
cd ~
git clone https://github.com/jhopan/Play-Youtube-In-CLI.git
cd Play-Youtube-In-CLI
```

#### 2. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv mpv ffmpeg alsa-utils
```

#### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Configure Environment

```bash
cp .env.example .env
nano .env
```

Add your configuration:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USER_IDS=123456789,987654321
DEFAULT_VOLUME=75

# YouTube Cookies (PENTING!)
YOUTUBE_COOKIES_FILE=cookies.txt
COOKIES_FROM_BROWSER=
```

**Get Your User ID:** [@userinfobot](https://t.me/userinfobot) → Send `/start` → Copy "Id"

#### 6. Setup YouTube Cookies (WAJIB!)

YouTube memerlukan cookies untuk menghindari bot detection. **Ikuti panduan lengkap:**

📖 **Baca:** [CARA_EXPORT_COOKIES.md](CARA_EXPORT_COOKIES.md)

**Quick Steps:**

1. **Install Chrome Extension:** [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. **Login** ke YouTube di Chrome
3. **Export** cookies menggunakan extension
4. **Save** file sebagai `cookies.txt` di folder project
5. File `cookies.txt` harus sejajar dengan `main.py`

```
Project/
├── main.py
├── cookies.txt    ← Simpan di sini!
└── .env
```

#### 7. Run Bot

```bash
python3 main.py
```

You should see:

```
🎵 YouTube Music Telegram Bot - Starting...
✅ Configuration validated successfully
🚀 Bot is now running! Press Ctrl+C to stop.
```

---

## 📱 Usage Guide

### Getting Started

1. Open your bot in Telegram
2. Send `/start`
3. You'll see the main menu with interactive buttons

### Main Menu Layout

```
ℹ️ Info     🔊 Volume

📋 Playlist   🎥 Video

▶️ Play    ⏭️ Next
⏮️ Prev    ⏸️ Pause

🔁 Loop    🔀 Shuffle
📋 Queue   ⏹️ Stop
```

### Loading Music

**Load Playlist:**

1. Click `📋 Load Playlist`
2. Send YouTube playlist URL
3. Bot extracts all videos
4. Jika sedang memutar musik → masuk queue (tidak langsung diputar)
5. Jika queue kosong → langsung diputar otomatis

**Load Single Video:**

1. Click `🎥 Video`
2. Send YouTube video URL
3. Video added to queue
4. Starts playing if queue was empty

**Save Playlist:**

1. Load playlist seperti biasa
2. Click `💾 Save Playlist`
3. Beri nama playlist
4. Playlist tersimpan untuk diputar nanti

**Play Saved Playlist:**

1. Click `📂 My Playlists`
2. Pilih playlist yang ingin diputar
3. Playlist langsung dimuat dan diputar

### Playback Control

| Button   | Action                      |
| -------- | --------------------------- |
| ▶️ Play  | Start/Resume playback       |
| ⏸️ Pause | Pause current song          |
| ⏭️ Next  | Skip to next song           |
| ⏮️ Prev  | Go to previous song         |
| ⏹️ Stop  | Stop playback & clear state |

### Volume Control

Click `🔊 Volume` to open volume menu:

```
Current volume: 50%

🔉 -10    🔊 +10    🔇 Mute

25%    50%    75%    100%

↩️ Back
```

- **+10/-10** - Fine-tune in 10% increments
- **Presets** - Quick jump to 25/50/75/100%
- **Mute** - Instant mute toggle

### Special Modes

**🔁 Loop Mode:**

- OFF: Play playlist sequentially
- ON: Repeat current song infinitely

**🔀 Shuffle Mode:**

- OFF: Play in order
- ON: Random song selection

### Auto-Next Feature

When a song finishes:

```
🎵 Song Finished!

▶️ Next: [Song Title]

⏱️ Auto-playing in 5 seconds...
Press 'Stop' to cancel.

[⏩ Play Next]  [⏹️ Stop]
```

- **5-second countdown** with real-time updates
- **Manual override** - Click to skip countdown
- **Cancellable** - Stop to cancel auto-play

### Info Display

Click `ℹ️ Info` to view:

```
ℹ️ Bot Information

Now Playing:
🎵 Song Title Here
⏱️ Duration: 3:45
🔗 YouTube Link

Playlist:
📀 Total songs: 15
▶️ Current position: 3/15

Settings:
🔊 Volume: 75%
🔁 Loop: OFF
🔀 Shuffle: OFF
```

---

## 🔧 Advanced Setup

### 24/7 Operation with Systemd

#### Method 1: Interactive Setup (Recommended)

Use the interactive setup script:

```bash
cd ~/Play-Youtube-In-CLI
chmod +x scripts/setup_service.sh
./scripts/setup_service.sh
```

The script will guide you through:

- Selecting service type (YouTube Music Bot, Custom Python, or Custom App)
- Auto-detecting bot directory and Python environment
- Configuring service settings
- Enabling and starting the service

#### Method 2: Manual Setup

Edit the service file:

```bash
nano ytmusic_bot.service
```

Update `User` and paths if your username is not `ubuntu`:

```ini
[Service]
User=your_username
WorkingDirectory=/home/your_username/Play-Youtube-In-CLI
ExecStart=/home/your_username/Play-Youtube-In-CLI/venv/bin/python /home/your_username/Play-Youtube-In-CLI/main.py
```

Install the service:

```bash
sudo cp ytmusic_bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ytmusic_bot
sudo systemctl start ytmusic_bot
```

#### 3. Create Convenient Aliases

Use the alias setup script to create shortcuts:

```bash
chmod +x scripts/setup_alias.sh
./scripts/setup_alias.sh
```

The script will:

- Show available systemd services
- Let you choose which service to create aliases for
- Create convenient aliases like:
  - `ytmusic-start` - Start the bot
  - `ytmusic-stop` - Stop the bot
  - `ytmusic-restart` - Restart the bot
  - `ytmusic-status` - Check status
  - `ytmusic-logs` - View live logs

After setup, you can use short commands instead of full systemctl commands!

#### 4. Manage Service

```bash
# Using full commands
sudo systemctl status ytmusic_bot
sudo journalctl -u ytmusic_bot -f
sudo systemctl restart ytmusic_bot
sudo systemctl stop ytmusic_bot

# Or using aliases (if you ran setup_alias.sh)
ytmusic-status
ytmusic-logs
ytmusic-restart
ytmusic-stop
```

### Update Bot

```bash
cd ~/Play-Youtube-In-CLI
sudo systemctl stop ytmusic_bot

git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade

sudo systemctl start ytmusic_bot
```

---

## 📊 Logging & Monitoring

### Enhanced Logging System

Bot logs detailed activity with emoji markers:

```
🚀 Bot is now running!
📞 /start command received from @username (ID: 123456789)
🎯 Button clicked by @username: 'play_pause'
▶️ @username started playback
🎵 Now playing: 'Song Title' [1/10]
🔊 @username increased volume: 50% → 60%
✅ Song finished: 'Song Title'
⏱️ Showing auto-next dialog (5 second countdown)
```

### Log Categories

| Emoji | Category | Description           |
| ----- | -------- | --------------------- |
| 🚀    | Startup  | Bot initialization    |
| 📞    | Commands | Command execution     |
| 🎯    | Buttons  | Button interactions   |
| 🎵    | Playback | Song playback events  |
| 🔊    | Volume   | Volume changes        |
| 🔗    | URLs     | URL processing        |
| ⚠️    | Warnings | Non-critical issues   |
| ❌    | Errors   | Error conditions      |
| ✅    | Success  | Successful operations |

### View Logs

```bash
# Real-time logs
sudo journalctl -u ytmusic_bot -f

# Last 100 lines
sudo journalctl -u ytmusic_bot -n 100

# Errors only
sudo journalctl -u ytmusic_bot -p err

# Specific time range
sudo journalctl -u ytmusic_bot --since "1 hour ago"
```

See [docs/ENHANCED_LOGGING.md](docs/ENHANCED_LOGGING.md) for complete logging guide.

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>Bot tidak merespon</b></summary>

```bash
# Check if bot is running
sudo systemctl status ytmusic_bot

# Check logs
sudo journalctl -u ytmusic_bot -n 50

# Restart bot
sudo systemctl restart ytmusic_bot
```

</details>

<details>
<summary><b>PEP 668 Error</b></summary>

```
error: externally-managed-environment
```

**Solution:** Use virtual environment (always recommended)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

See [docs/FIX_PYTHON_313.md](docs/FIX_PYTHON_313.md)

</details>

<details>
<summary><b>Module Not Found Error</b></summary>

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep telegram
```

See [docs/FIX_MODULE_NOT_FOUND.md](docs/FIX_MODULE_NOT_FOUND.md)

</details>

<details>
<summary><b>No Audio on Headless Server</b></summary>

**Normal behavior!** Headless servers don't have audio output hardware.

Music streams through MPV but you won't hear it locally. Control playback via Telegram.

See [docs/FIX_NO_AUDIO.md](docs/FIX_NO_AUDIO.md) for PulseAudio setup if needed.

</details>

<details>
<summary><b>Volume Control Not Working</b></summary>

```bash
# Test amixer
amixer set Master 50%

# Test pactl
pactl set-sink-volume @DEFAULT_SINK@ 50%

# Check MPV IPC socket
ls -l /tmp/mpvsocket
```

See [docs/VOLUME_CONTROL.md](docs/VOLUME_CONTROL.md)

</details>

<details>
<summary><b>MPV Error</b></summary>

```bash
# Test MPV
mpv --no-video "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Reinstall MPV
sudo apt remove mpv -y
sudo apt install mpv -y
```

</details>

<details>
<summary><b>yt-dlp Extraction Failed</b></summary>

```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Test manually
yt-dlp -f bestaudio "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

</details>

**Complete troubleshooting guide ada di atas** - lihat section 🐛 Troubleshooting

---

## 🔐 Security

### Access Control

Bot implements multi-layer access control:

1. **User Whitelist** - Only users in `ALLOWED_USER_IDS` can interact
2. **Owner Lock** - First user becomes owner, only owner can control playback
3. **Secure Token** - Bot token stored in `.env` (not in code)

### Best Practices

✅ **Keep token secret** - Never commit `.env` to git  
✅ **Use whitelist** - Limit access to trusted users only  
✅ **Run as non-root** - Use regular user account  
✅ **Update regularly** - Keep dependencies up-to-date  
✅ **Monitor logs** - Watch for unauthorized access attempts

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Need Help?

1. **Check documentation** - [docs/INDEX.md](docs/INDEX.md) has everything
2. **Read troubleshooting** - [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) covers common issues
3. **View logs** - `sudo journalctl -u ytmusic_bot -f` shows what's happening
4. **Test manually** - Run `python3 main.py` to see direct output
5. **Verify dependencies** - `mpv --version`, `python3 --version`, `yt-dlp --version`

### Reporting Issues

Please include:

- Bot logs (`sudo journalctl -u ytmusic_bot -n 100`)
- Python version (`python3 --version`)
- OS version (`cat /etc/os-release`)
- Error messages
- Steps to reproduce

---

## ⭐ Star History

If you find this project useful, please give it a star! ⭐

---

## 📧 Contact

- **Repository:** https://github.com/jhopan/Play-Youtube-In-CLI
- **Issues:** https://github.com/jhopan/Play-Youtube-In-CLI/issues

---

**Made with ❤️ for music lovers who love automation**

_Bot Telegram untuk streaming YouTube Music di Ubuntu Server - Full control via Telegram, no GUI needed!_
