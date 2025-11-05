# ⚡ Quick Install Guide

Panduan cepat install bot dengan mengatasi PEP 668 (Python 3.11+).

## 🚀 One-Command Install

```bash
# Clone & setup dengan virtual environment
git clone https://github.com/jhopan/Play-Youtube-In-CLI.git && \
cd Play-Youtube-In-CLI && \
chmod +x scripts/setup.sh && \
./scripts/setup.sh
```

## 📋 Manual Install (Step by Step)

### 1. Clone Repository

```bash
git clone https://github.com/jhopan/Play-Youtube-In-CLI.git
cd Play-Youtube-In-CLI
```

### 2. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-full mpv ffmpeg
```

### 3. Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate
```

### 4. Install Python Packages

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

Add your bot token and user IDs:

```env
BOT_TOKEN=your_bot_token_here
ALLOWED_USER_IDS=123456789,987654321
```

### 6. Run Bot

```bash
# Make sure venv is activated
source venv/bin/activate

# Run bot
python main.py
```

## 🔄 Running Bot After Reboot

Setiap kali mau run bot, **aktifkan virtual environment dulu**:

```bash
cd Play-Youtube-In-CLI
source venv/bin/activate
python main.py
```

## 🤖 Setup as Systemd Service

Agar bot auto-start dan run 24/7:

### 1. Edit Service File

```bash
nano ytmusic_bot.service
```

Update paths (ganti `your_username`):

```ini
[Service]
User=your_username
WorkingDirectory=/home/your_username/Play-Youtube-In-CLI
ExecStart=/home/your_username/Play-Youtube-In-CLI/venv/bin/python main.py
```

### 2. Install Service

```bash
sudo cp ytmusic_bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ytmusic_bot
sudo systemctl start ytmusic_bot
```

### 3. Check Status

```bash
sudo systemctl status ytmusic_bot
```

## ❌ Troubleshooting PEP 668 Error

### Problem:

```
error: externally-managed-environment
× This environment is externally managed
```

### Solution A: Virtual Environment (Recommended ✅)

```bash
# Install venv
sudo apt install python3-venv python3-full -y

# Create and activate
python3 -m venv venv
source venv/bin/activate

# Now you can install
pip install -r requirements.txt
```

### Solution B: Break System Packages (Not Recommended ⚠️)

```bash
pip install -r requirements.txt --break-system-packages
```

**Warning:** Ini bisa break system Python!

### Solution C: System Packages Only

```bash
# Install from apt (terbatas)
sudo apt install python3-pip -y
sudo apt install python3-telegram-bot -y  # Jika tersedia

# Install sisanya
pip3 install yt-dlp python-dotenv --break-system-packages
```

## ✅ Verification

Test apakah bot sudah jalan:

```bash
# In Telegram, message your bot
/start
```

Kamu harus dapat response dengan menu buttons!

## 🔧 Common Commands

```bash
# Activate venv
source venv/bin/activate

# Deactivate venv
deactivate

# Check bot status (if using service)
sudo systemctl status ytmusic_bot

# View logs (if using service)
sudo journalctl -u ytmusic_bot -f

# Restart bot (if using service)
sudo systemctl restart ytmusic_bot

# Stop bot (if using service)
sudo systemctl stop ytmusic_bot
```

## 📚 Next Steps

- ✅ Bot jalan? Baca [CONFIGURATION.md](CONFIGURATION.md) untuk advanced config
- ✅ Ada masalah? Lihat [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- ✅ Mau customize? Lihat [ARCHITECTURE.md](ARCHITECTURE.md)

## 💡 Pro Tips

1. **Always activate venv** sebelum run commands Python
2. **Don't use sudo with pip** dalam venv
3. **Check venv active**: prompt akan show `(venv)`
4. **Use systemd service** untuk production (auto-restart, logs, dll)

## 🆘 Still Having Issues?

### Virtual Environment Not Working?

```bash
# Check Python version
python3 --version

# Should be 3.8+
# Install python3-venv
sudo apt install python3-venv python3-full -y
```

### Module Not Found?

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### Bot Won't Start?

```bash
# Check .env file
cat .env

# Verify token format (no spaces!)
# Run with debug
DEBUG=true python main.py
```

---

**Happy Streaming! 🎵🎧**
