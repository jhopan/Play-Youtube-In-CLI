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

- **🔁 Loop Mode** - 3 modes: Off → Song Loop → Queue Loop (cycle terus)
- **🔀 Shuffle Mode** - Random playback order
- **🔊 Volume Control** - Fine-tune dengan +10/-10, preset levels, instant mute
- **📋 Queue Display** - Lihat playlist current state
- **💾 Song Selection** - Pilih lagu spesifik saat save playlist (up to 10 songs)
- **ℹ️ Info Display** - Comprehensive bot status & current song details

### 🛡️ Security & Stability

- **User Whitelist** - Access control via Telegram User ID
- **Owner-Only Controls** - Hanya bot owner yang bisa kontrol playback
- **Auto-Restart** - MPV process monitoring & auto-recovery
- **Graceful Error Handling** - Comprehensive error management
- **24/7 Operation** - Systemd service support untuk continuous operation

### 💫 User Experience

- **Interactive Buttons** - Full UI dengan inline keyboards
- **Real-time Notifications** - Instant updates saat song changes (edit-in-place, no spam)
- **HTML Formatting** - Clean UI dengan emoji & formatting
- **Async Operations** - Non-blocking dengan asyncio
- **📊 Enhanced Logging** - Detailed terminal logs dengan emoji, user tracking, event monitoring
- **🔄 Auto-Retry** - MPV error recovery dengan fresh URL extraction
- **⚡ Smart Queue** - Add to queue tanpa interrupt current song

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
│   ├── install_service.sh      # Systemd service installer
│   ├── alias_setup.sh          # Create aliases for project & service
│   ├── start.sh                # Bot starter (simple)
│   ├── stop.sh                 # Bot stopper
│   └── manage_service.sh       # Service management tool
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

YouTube memerlukan cookies untuk menghindari bot detection.

**📍 Install Chrome Extension:**

[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) - Cari di Chrome Web Store: `Get cookies.txt LOCALLY`

> ⚠️ Gunakan yang "LOCALLY" bukan yang "Export" biasa (lebih aman, tidak upload ke server)

**📍 Export Cookies:**

1. **Login** ke YouTube di Chrome (youtube.com)
2. **Klik extension** "Get cookies.txt LOCALLY" di toolbar
3. **Klik "Export"** - file `cookies.txt` akan terdownload
4. **Copy file** ke folder project (sejajar dengan `main.py`)
5. **Rename** menjadi `cookies.txt` jika berbeda

```
Project/
├── main.py
├── cookies.txt    ← Simpan di sini!
├── .env
└── bot/
```

**📍 Troubleshooting:**

- **Error: "No such file"** → Pastikan `cookies.txt` di root folder
- **Error: "403 Forbidden"** → Cookies expired, export ulang
- **Error: "Sign in to confirm"** → Logout YouTube, login ulang, export baru
- **Cookies expired?** → Update setiap 6-12 bulan

**📍 Keamanan:**

- ❌ JANGAN upload `cookies.txt` ke GitHub (sudah di `.gitignore`)
- ❌ JANGAN share cookies ke orang lain
- ✅ Simpan hanya di local server

#### 7. Run Bot

**Easy Way (Recommended):**

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start bot
./scripts/start.sh

# Stop bot (in another terminal)
./scripts/stop.sh
```

**Manual Way:**

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

## 🎮 Quick Start Scripts

### Start Bot

```bash
./scripts/start.sh
```

**Features:**

- Auto-detects if systemd service is installed
- Option to start as service or foreground
- Checks virtual environment
- Auto-installs dependencies if missing
- Validates .env configuration

**Choose Start Method:**

```
Choose start method:
1. Start as systemd service (recommended)
2. Start in foreground (manual)
```

### Stop Bot

```bash
./scripts/stop.sh
```

**Features:**

- Stops systemd service if running
- Finds and kills Python processes
- Option to kill MPV player processes
- Graceful shutdown with SIGTERM, force kill if needed

### Manage Service

```bash
sudo ./scripts/manage_service.sh
```

**Features:**

- Check service status
- View logs (live or recent)
- Start/Stop/Restart service
- Enable/Disable auto-start
- Delete service and aliases
- Show service configuration

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
3. **Pilih mode:**
   - `Save All` - Simpan semua lagu
   - `Select Songs` - Pilih lagu tertentu (max 10)
4. Beri nama playlist
5. Playlist tersimpan untuk diputar nanti

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

**🔁 Loop Mode (3 States):**

- **OFF**: Play playlist sekali saja
- **Song Loop**: Repeat lagu saat ini terus-menerus
- **Queue Loop**: Ulangi semua playlist dari awal otomatis

Klik `🔁 Loop` untuk cycle: OFF → Song → Queue → OFF

**🔀 Shuffle Mode:**

- OFF: Play in order
- ON: Random song selection

### Auto-Next Feature

When a song finishes, bot automatically plays next song with smooth transition.

**Queue Loop Mode:**
- Saat playlist habis → Otomatis restart dari awal
- Tidak ada dialog countdown (seamless loop)
- Update via "Now Playing" message yang sama (no spam)

**Normal Mode:**
- Playlist habis → Bot stops dengan notifikasi "Playlist Finished"
- Edit message yang ada (tidak kirim pesan baru)

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
🔁 Loop: OFF / Song / Queue
🔀 Shuffle: OFF
```

---

## 🔧 Advanced Setup

### 24/7 Operation with Systemd

#### 1. Install Service

Use the simple installer:

```bash
cd ~/Play-Youtube-In-CLI/scripts
sudo ./install_service.sh
```

**Features:**
- Interactive service name selection (default: ytmusic-bot)
- Auto-creates service file with correct paths
- Option to enable auto-start on boot
- Option to start service immediately
- Displays management commands

**What it does:**
```
🚀 Systemd Service Installer
═══════════════════════════════════
Project Directory: /home/user/Play-Youtube-In-CLI
User: your_username

Enter service name (default: ytmusic-bot): [Enter]
📦 Installing service: ytmusic-bot...
✅ Service installed successfully!

Enable auto-start on boot? (Y/n): y
✅ Auto-start enabled!

Start service now? (Y/n): y
✅ Service started!
```

#### 2. Create Shell Aliases (Optional)

Use the smart alias setup:

```bash
cd ~/Play-Youtube-In-CLI/scripts
./alias_setup.sh
```

**Features:**
- 🔍 Auto-scans for project directories (Youtube, YT Music, Telegram Bot)
- 🔍 Auto-detects systemd services (user & system)
- 🎯 Auto-detects service type (system/user)
- 📝 Creates full management aliases

**What it creates:**

```bash
ytmusic              # Go to project directory
ytmusic-start        # Start service
ytmusic-stop         # Stop service
ytmusic-restart      # Restart service
ytmusic-status       # Check service status
ytmusic-logs         # View live logs
ytmusic-enable       # Enable service on boot
ytmusic-disable      # Disable service on boot
```

After setup, reload your shell:
```bash
source ~/.bashrc   # or ~/.zshrc for zsh
```

#### 3. Manage Service

```bash
# Using scripts (easiest)
./scripts/start.sh           # Start bot
./scripts/stop.sh            # Stop bot
./scripts/manage_service.sh  # Full management UI

# Using systemctl directly
sudo systemctl status ytmusic-bot
sudo journalctl -u ytmusic-bot -f
sudo systemctl restart ytmusic-bot
sudo systemctl stop ytmusic-bot

# Or using aliases (if you ran alias_setup.sh)
ytmusic-status
ytmusic-logs
logsytmusic
restartytmusic
stopytmusic
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

## 📋 Recent Updates

### v2.5.0 (Dec 31, 2024)
- 🔁 **3-State Loop Mode**: OFF → Song Loop → Queue Loop
- 🎯 **Song Selection**: Pilih lagu spesifik saat save playlist (max 10)
- 🚫 **No Message Spam**: Edit-in-place untuk semua notifikasi
- 🔄 **MPV Auto-Retry**: Fresh URL extraction & error recovery
- ⚡ **Smart Queue**: Add to queue tanpa interrupt current song
- 🛠️ **Simplified Setup**: setup_alias.sh focused on ytmusic-bot only
- 🐛 **Service Fix**: Changed Type=forking to Type=simple (no more stuck)

### v2.4.0 (Previous)
- 📊 Enhanced logging with emoji & user tracking
- 🔊 Advanced volume control
- 💾 Playlist save/load functionality
- 🎮 Improved playback control

See [docs/CHANGELOG.md](docs/CHANGELOG.md) for full history.

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
