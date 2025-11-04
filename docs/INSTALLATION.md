# 🎵 YouTube Music Telegram Bot - Installation Guide

Bot Telegram headless untuk streaming musik YouTube di Ubuntu Server tanpa GUI.

## 📋 Prerequisites

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python & Dependencies

```bash
# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install mpv (music player)
sudo apt install mpv -y

# Install ffmpeg
sudo apt install ffmpeg -y
```

### 3. Verify Installation

```bash
python3 --version
mpv --version
ffmpeg -version
```

## 🚀 Bot Installation

### 1. Create Working Directory

```bash
mkdir -p ~/ytmusic-bot
cd ~/ytmusic-bot
```

### 2. Upload Files

Upload these files to `~/ytmusic-bot/`:

- `ytmusic_interactive_bot.py`
- `requirements.txt`

```bash
# Jika menggunakan scp dari komputer lokal:
# scp ytmusic_interactive_bot.py user@server:~/ytmusic-bot/
# scp requirements.txt user@server:~/ytmusic-bot/
```

### 3. Create Virtual Environment (Recommended)

```bash
cd ~/ytmusic-bot
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Bot Token

Edit file `ytmusic_interactive_bot.py`:

```bash
nano ytmusic_interactive_bot.py
```

Ganti baris:

```python
TOKEN = "YOUR_BOT_TOKEN_HERE"
```

Dengan token bot Anda dari [@BotFather](https://t.me/botfather):

```python
TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

Optional - Tambahkan whitelist user:

```python
ALLOWED_USERS = [123456789, 987654321]  # User ID Telegram Anda
```

Simpan dengan `Ctrl+O`, `Enter`, lalu `Ctrl+X`

## 🧪 Test Run Bot

### 1. Manual Test

```bash
cd ~/ytmusic-bot
source venv/bin/activate  # jika menggunakan venv
python3 ytmusic_interactive_bot.py
```

### 2. Test di Telegram

- Buka bot Anda di Telegram
- Kirim `/start`
- Harus muncul menu dengan tombol-tombol kontrol

### 3. Stop Test

Tekan `Ctrl+C` untuk stop bot

## 🔧 Setup as Systemd Service (Auto-Start 24/7)

### 1. Create Service File

```bash
sudo nano /etc/systemd/system/ytmusic-bot.service
```

### 2. Paste Configuration

**Jika TANPA Virtual Environment:**

```ini
[Unit]
Description=YouTube Music Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ytmusic-bot
ExecStart=/usr/bin/python3 /home/ubuntu/ytmusic-bot/ytmusic_interactive_bot.py
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ytmusic-bot

[Install]
WantedBy=multi-user.target
```

**Jika DENGAN Virtual Environment:**

```ini
[Unit]
Description=YouTube Music Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ytmusic-bot
ExecStart=/home/ubuntu/ytmusic-bot/venv/bin/python /home/ubuntu/ytmusic-bot/ytmusic_interactive_bot.py
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ytmusic-bot

[Install]
WantedBy=multi-user.target
```

⚠️ **Penting:** Ganti `ubuntu` dengan username Linux Anda!

### 3. Enable & Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable ytmusic-bot

# Start service
sudo systemctl start ytmusic-bot

# Check status
sudo systemctl status ytmusic-bot
```

### 4. Service Management Commands

```bash
# Start bot
sudo systemctl start ytmusic-bot

# Stop bot
sudo systemctl stop ytmusic-bot

# Restart bot
sudo systemctl restart ytmusic-bot

# View logs (real-time)
sudo journalctl -u ytmusic-bot -f

# View last 100 lines
sudo journalctl -u ytmusic-bot -n 100

# Disable auto-start
sudo systemctl disable ytmusic-bot
```

## 🎮 Alternative: Run with Screen (Simple Method)

Jika tidak mau pakai systemd, bisa pakai `screen`:

### 1. Install Screen

```bash
sudo apt install screen -y
```

### 2. Run Bot in Screen

```bash
cd ~/ytmusic-bot
screen -S ytmusic
source venv/bin/activate  # jika pakai venv
python3 ytmusic_interactive_bot.py
```

### 3. Detach Screen

Tekan `Ctrl+A` lalu `D`

### 4. Screen Commands

```bash
# List sessions
screen -ls

# Reattach to session
screen -r ytmusic

# Kill session
screen -X -S ytmusic quit
```

## 🛠️ Troubleshooting

### Bot tidak merespon

```bash
# Check if bot is running
sudo systemctl status ytmusic-bot

# Check logs
sudo journalctl -u ytmusic-bot -n 50
```

### MPV error

```bash
# Test mpv manual
mpv --no-video "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Reinstall mpv
sudo apt remove mpv -y
sudo apt install mpv -y
```

### yt-dlp error

```bash
# Update yt-dlp
pip install --upgrade yt-dlp
```

### Permission denied

```bash
# Fix file permissions
chmod +x ~/ytmusic-bot/ytmusic_interactive_bot.py

# Fix ownership
sudo chown -R $USER:$USER ~/ytmusic-bot
```

### Token invalid

- Pastikan token dari @BotFather benar
- Token format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- Tidak ada spasi atau karakter tambahan

## 📊 Check System Resources

```bash
# CPU & Memory usage
htop

# Disk space
df -h

# Process list
ps aux | grep python
```

## 🔄 Update Bot

```bash
# Stop service
sudo systemctl stop ytmusic-bot

# Backup old version
cp ytmusic_interactive_bot.py ytmusic_interactive_bot.py.backup

# Update file (upload new version)
# ...

# Restart service
sudo systemctl start ytmusic-bot

# Check status
sudo systemctl status ytmusic-bot
```

## 📝 Get Your Telegram User ID

Untuk setup ALLOWED_USERS, Anda perlu User ID:

1. Buka bot: [@userinfobot](https://t.me/userinfobot)
2. Kirim `/start`
3. Copy angka "Id:" (contoh: 123456789)
4. Masukkan ke `ALLOWED_USERS = [123456789]`

## 🔥 Firewall (Optional)

Jika ada firewall aktif:

```bash
# Allow SSH (important!)
sudo ufw allow ssh

# Enable firewall
sudo ufw enable
```

Bot tidak perlu port khusus karena menggunakan Telegram Bot API (outgoing only).

## ✅ Success Checklist

- [ ] Python 3 terinstall
- [ ] mpv terinstall
- [ ] ffmpeg terinstall
- [ ] Dependencies Python terinstall
- [ ] Token bot sudah dikonfigurasi
- [ ] Bot merespon `/start` di Telegram
- [ ] Bisa load playlist YouTube
- [ ] Musik bisa diputar
- [ ] Service systemd aktif (optional)
- [ ] Bot auto-restart jika crash

## 🎉 Usage

1. Kirim `/start` ke bot Anda
2. Klik **🎶 Load Playlist** atau **🎵 Load Video**
3. Kirim link YouTube
4. Musik akan otomatis diputar
5. Kontrol dengan tombol-tombol yang tersedia

## 🆘 Support

Jika ada masalah:

1. Check logs: `sudo journalctl -u ytmusic-bot -f`
2. Test manual: `python3 ytmusic_interactive_bot.py`
3. Verify dependencies: `mpv --version`, `python3 --version`

---

**Happy Streaming! 🎵🎧**
