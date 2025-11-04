# 🔍 Troubleshooting Guide

Panduan lengkap mengatasi masalah pada YouTube Music Bot.

---

## 🚨 Common Issues

### 1. Bot Tidak Merespon `/start`

**Symptoms:**

- Bot tidak membalas saat kirim `/start`
- No response dari bot

**Solutions:**

✅ **Check if bot is running:**

```bash
ps aux | grep ytmusic_interactive_bot.py
```

✅ **Check logs:**

```bash
# If using systemd
sudo journalctl -u ytmusic-bot -n 50

# If running manually
# Check terminal output
```

✅ **Verify token:**

```bash
# Edit bot
nano ytmusic_interactive_bot.py

# Make sure TOKEN is correct (from @BotFather)
# Format: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

✅ **Restart bot:**

```bash
# If systemd
sudo systemctl restart ytmusic-bot

# If manual
# Ctrl+C and run again
python3 ytmusic_interactive_bot.py
```

✅ **Check internet:**

```bash
ping telegram.org
curl https://api.telegram.org
```

---

### 2. Error: "Token is invalid"

**Symptoms:**

```
telegram.error.InvalidToken: Invalid token
```

**Solutions:**

✅ **Get new token:**

1. Open [@BotFather](https://t.me/botfather)
2. Send `/mybots`
3. Select your bot
4. Select "API Token"
5. Copy token

✅ **Check format:**

```python
# CORRECT:
TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# WRONG:
TOKEN = "1234567890: ABCdefGHIjklMNOpqrsTUVwxyz"  # Space after :
TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz "  # Space at end
TOKEN = """1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"""  # Triple quotes
```

✅ **Regenerate token:**

```
@BotFather → /mybots → Your Bot → API Token → Revoke & Get New
```

---

### 3. Error: "Access denied"

**Symptoms:**

- Bot says "❌ You don't have access to this bot"
- Can't use bot commands

**Solutions:**

✅ **Check whitelist:**

```python
# Open bot file
nano ytmusic_interactive_bot.py

# Find this line
ALLOWED_USERS = [123456789]  # Your user ID must be here

# To allow everyone:
ALLOWED_USERS = []  # Empty list
```

✅ **Get your user ID:**

1. Open [@userinfobot](https://t.me/userinfobot)
2. Send `/start`
3. Copy your "Id:" number
4. Add to ALLOWED_USERS

---

### 4. Error: "mpv not found"

**Symptoms:**

```
FileNotFoundError: [Errno 2] No such file or directory: 'mpv'
```

**Solutions:**

✅ **Install mpv:**

```bash
sudo apt update
sudo apt install mpv -y
```

✅ **Verify installation:**

```bash
which mpv
# Should output: /usr/bin/mpv

mpv --version
# Should show version info
```

✅ **Test mpv:**

```bash
mpv --no-video "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
# Should play audio (Ctrl+C to stop)
```

✅ **Fix path (if mpv in different location):**

```python
# In start_mpv() function
cmd = [
    '/usr/bin/mpv',  # Full path
    # ... rest of options
]
```

---

### 5. Error: "yt-dlp extraction failed"

**Symptoms:**

```
ERROR: Unable to extract video data
ERROR: Video unavailable
```

**Solutions:**

✅ **Update yt-dlp:**

```bash
pip3 install --upgrade yt-dlp
```

✅ **Test extraction manually:**

```bash
yt-dlp --flat-playlist "YOUR_PLAYLIST_URL"
yt-dlp -f bestaudio "YOUR_VIDEO_URL"
```

✅ **Check YouTube URL:**

```
✅ VALID:
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
https://www.youtube.com/playlist?list=PLxxxxxxxx

❌ INVALID:
youtube.com/watch (no https://)
https://music.youtube.com/... (YouTube Music different API)
```

✅ **Install latest YouTube fixes:**

```bash
pip3 install --upgrade yt-dlp
# Or specific version:
pip3 install yt-dlp==2024.01.01
```

---

### 6. Music Not Playing (No Audio)

**Symptoms:**

- Bot says "Now Playing" but no sound
- MPV process running but silent

**Solutions:**

⚠️ **Expected behavior:**

```
Bot is HEADLESS = No audio output!
Bot runs mpv on server (not your computer)
You control via Telegram, but music plays on server (silent)
```

✅ **Verify playback:**

```bash
# Check if mpv is running
ps aux | grep mpv

# Check mpv logs
sudo journalctl -u ytmusic-bot -f
```

✅ **If you want audio output:**

```python
# Remove --no-video flag in start_mpv()
cmd = [
    'mpv',
    # '--no-video',  # Comment this out
    f'--volume={player.volume}',
    url
]
```

Then configure ALSA/PulseAudio on server.

---

### 7. High CPU/Memory Usage

**Symptoms:**

- Server slow
- `htop` shows high usage
- Out of memory errors

**Solutions:**

✅ **Limit mpv buffer:**

```python
def start_mpv(url: str) -> subprocess.Popen:
    cmd = [
        'mpv',
        '--no-video',
        '--quiet',
        f'--volume={player.volume}',
        '--demuxer-max-bytes=50M',  # Add this
        '--cache-secs=10',           # Add this
        url
    ]
```

✅ **Monitor resources:**

```bash
# Real-time monitoring
htop

# Memory usage
free -h

# Process list
ps aux --sort=-%mem | head
```

✅ **Kill zombie processes:**

```bash
# Find zombie mpv
ps aux | grep mpv | grep -v grep

# Kill by PID
kill -9 <PID>

# Or kill all mpv
pkill -9 mpv
```

✅ **Restart bot:**

```bash
sudo systemctl restart ytmusic-bot
```

---

### 8. Bot Crashes After Some Time

**Symptoms:**

- Bot stops responding after hours/days
- Systemd shows "failed" status

**Solutions:**

✅ **Enable auto-restart:**

```ini
# In ytmusic-bot.service
[Service]
Restart=always
RestartSec=10
```

✅ **Check logs for errors:**

```bash
sudo journalctl -u ytmusic-bot -n 100
```

✅ **Add memory limits (optional):**

```ini
# In ytmusic-bot.service
[Service]
MemoryLimit=512M
```

✅ **Update dependencies:**

```bash
pip3 install --upgrade python-telegram-bot yt-dlp
sudo apt update && sudo apt upgrade -y
```

---

### 9. Systemd Service Won't Start

**Symptoms:**

```
Failed to start ytmusic-bot.service
```

**Solutions:**

✅ **Check service status:**

```bash
sudo systemctl status ytmusic-bot
```

✅ **Check service file syntax:**

```bash
sudo systemctl daemon-reload
sudo systemctl start ytmusic-bot
sudo journalctl -u ytmusic-bot -n 50
```

✅ **Verify paths:**

```bash
# Check if files exist
ls -la /home/ubuntu/ytmusic-bot/ytmusic_interactive_bot.py
ls -la /usr/bin/python3

# Check permissions
ls -la /home/ubuntu/ytmusic-bot/
```

✅ **Test manual run:**

```bash
cd /home/ubuntu/ytmusic-bot
python3 ytmusic_interactive_bot.py
# If works manually, check service user/permissions
```

✅ **Fix permissions:**

```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/ytmusic-bot
chmod +x /home/ubuntu/ytmusic-bot/ytmusic_interactive_bot.py
```

---

### 10. Buttons Not Working

**Symptoms:**

- Clicking buttons shows loading but nothing happens
- Callback query timeout

**Solutions:**

✅ **Check logs:**

```bash
sudo journalctl -u ytmusic-bot -f
# Click button and watch for errors
```

✅ **Verify callback handlers:**

```python
# Make sure this is in main():
application.add_handler(CallbackQueryHandler(button_callback))
```

✅ **Check ownership:**

```python
# Only owner can control playback
# Make sure you're the first user to use bot
# Or remove ownership check (not recommended)
```

✅ **Restart bot:**

```bash
sudo systemctl restart ytmusic-bot
```

---

## 🔧 Diagnostic Commands

### System Health Check

```bash
# Run health check script
chmod +x healthcheck.sh
./healthcheck.sh
```

### Manual Testing

```bash
# 1. Test Python
python3 --version

# 2. Test imports
python3 -c "import telegram; print('✅ telegram OK')"
python3 -c "import yt_dlp; print('✅ yt-dlp OK')"

# 3. Test mpv
mpv --version

# 4. Test ffmpeg
ffmpeg -version

# 5. Test network
ping -c 3 telegram.org
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# 6. Test YouTube access
yt-dlp --flat-playlist "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
```

### Log Analysis

```bash
# View all logs
sudo journalctl -u ytmusic-bot --no-pager

# View recent errors
sudo journalctl -u ytmusic-bot -p err

# Follow logs real-time
sudo journalctl -u ytmusic-bot -f

# Export logs to file
sudo journalctl -u ytmusic-bot > bot_logs.txt
```

---

## 🐛 Debug Mode

Enable debug logging:

```python
# At top of ytmusic_interactive_bot.py
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Change from INFO to DEBUG
)

# Also enable httpx debug
logging.getLogger("httpx").setLevel(logging.DEBUG)
```

Run bot manually to see all debug output:

```bash
cd ~/ytmusic-bot
python3 ytmusic_interactive_bot.py
```

---

## 🛠️ Advanced Troubleshooting

### Network Issues

```bash
# Check firewall
sudo ufw status

# Test DNS
nslookup telegram.org
nslookup youtube.com

# Test connectivity
curl -I https://www.youtube.com
curl -I https://api.telegram.org

# Check proxy (if using)
echo $http_proxy
echo $https_proxy
```

### Python Environment Issues

```bash
# Check Python version (need 3.7+)
python3 --version

# Check pip
pip3 --version

# List installed packages
pip3 list | grep -E 'telegram|yt-dlp'

# Reinstall packages
pip3 uninstall python-telegram-bot yt-dlp -y
pip3 install python-telegram-bot yt-dlp
```

### Permission Issues

```bash
# Check file ownership
ls -la ~/ytmusic-bot/

# Fix ownership
sudo chown -R $USER:$USER ~/ytmusic-bot/

# Check executable permission
chmod +x ~/ytmusic-bot/ytmusic_interactive_bot.py

# Check service permissions
sudo cat /etc/systemd/system/ytmusic-bot.service
```

### Process Management

```bash
# Find all bot processes
ps aux | grep ytmusic

# Kill all bot processes
pkill -f ytmusic_interactive_bot.py

# Kill all mpv processes
pkill mpv

# Check zombie processes
ps aux | grep defunct
```

---

## 📝 Error Messages Reference

### Common Error Messages & Meanings

| Error                                        | Meaning               | Solution                           |
| -------------------------------------------- | --------------------- | ---------------------------------- |
| `InvalidToken`                               | Wrong bot token       | Get new token from @BotFather      |
| `NetworkError`                               | No internet           | Check network connection           |
| `TimedOut`                                   | Request too slow      | Check network speed                |
| `ChatNotFound`                               | Chat/user not found   | User must start bot first          |
| `FileNotFoundError: mpv`                     | mpv not installed     | `sudo apt install mpv`             |
| `ModuleNotFoundError: telegram`              | Package not installed | `pip3 install python-telegram-bot` |
| `yt_dlp.utils.DownloadError`                 | Can't download video  | Update yt-dlp, check URL           |
| `OSError: [Errno 12] Cannot allocate memory` | Out of RAM            | Restart server, reduce buffer      |

---

## 🆘 Getting Help

### Information to Provide

When asking for help, provide:

1. **Error message:**

```bash
sudo journalctl -u ytmusic-bot -n 50
```

2. **System info:**

```bash
uname -a
python3 --version
mpv --version
pip3 list | grep -E 'telegram|yt-dlp'
```

3. **Configuration:**

- TOKEN format (hide actual token)
- ALLOWED_USERS setting
- Service file content

4. **Steps to reproduce:**

- What you did
- What you expected
- What actually happened

### Health Check Output

```bash
./healthcheck.sh > health_report.txt
cat health_report.txt
```

Send this report when asking for help.

---

## ✅ Final Checklist

- [ ] Bot token is correct
- [ ] Dependencies installed (mpv, ffmpeg, Python packages)
- [ ] Internet connection working
- [ ] User ID in whitelist (if using)
- [ ] Service file configured correctly
- [ ] File permissions correct
- [ ] Logs checked for errors
- [ ] Manual test successful

---

## 🎯 Quick Fix Commands

```bash
# Nuclear option: Complete reinstall
sudo systemctl stop ytmusic-bot
pkill -f ytmusic_interactive_bot.py
pkill mpv
cd ~/ytmusic-bot
pip3 install --upgrade --force-reinstall python-telegram-bot yt-dlp
sudo systemctl start ytmusic-bot
sudo journalctl -u ytmusic-bot -f
```

---

**Still having issues?**

1. Run `./healthcheck.sh`
2. Check all outputs
3. Read error messages carefully
4. Search error message online
5. Check GitHub issues (if applicable)

**Good luck! 🍀**
