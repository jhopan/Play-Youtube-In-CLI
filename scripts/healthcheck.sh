#!/bin/bash

# YouTube Music Bot - Health Check Script
# Run this to diagnose issues

echo "🏥 YouTube Music Bot - Health Check"
echo "===================================="
echo ""

# Check Python
echo "🐍 Python Version:"
python3 --version || echo "❌ Python3 not installed"
echo ""

# Check pip
echo "📦 pip Version:"
pip3 --version || echo "❌ pip3 not installed"
echo ""

# Check mpv
echo "🎵 mpv Version:"
mpv --version | head -n 1 || echo "❌ mpv not installed"
echo ""

# Check ffmpeg
echo "🎬 ffmpeg Version:"
ffmpeg -version | head -n 1 || echo "❌ ffmpeg not installed"
echo ""

# Check Python packages
echo "📚 Python Packages:"
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Using virtual environment"
fi

python3 -c "import telegram; print(f'✅ python-telegram-bot: {telegram.__version__}')" 2>/dev/null || echo "❌ python-telegram-bot not installed"
python3 -c "import yt_dlp; print(f'✅ yt-dlp: {yt_dlp.version.__version__}')" 2>/dev/null || echo "❌ yt-dlp not installed"
echo ""

# Check bot file
echo "📄 Bot File:"
if [ -f "ytmusic_interactive_bot.py" ]; then
    echo "✅ ytmusic_interactive_bot.py exists"
    
    # Check if TOKEN is configured
    if grep -q "YOUR_BOT_TOKEN_HERE" ytmusic_interactive_bot.py; then
        echo "⚠️  TOKEN not configured (still using placeholder)"
    else
        echo "✅ TOKEN appears to be configured"
    fi
else
    echo "❌ ytmusic_interactive_bot.py not found"
fi
echo ""

# Check if bot is running
echo "🤖 Bot Status:"
if pgrep -f "ytmusic_interactive_bot.py" > /dev/null; then
    echo "✅ Bot is running"
    ps aux | grep ytmusic_interactive_bot.py | grep -v grep
else
    echo "❌ Bot is not running"
fi
echo ""

# Check systemd service
echo "⚙️  Systemd Service:"
if systemctl list-unit-files | grep -q "ytmusic-bot.service"; then
    echo "✅ Service exists"
    sudo systemctl status ytmusic-bot --no-pager | head -n 5
else
    echo "❌ Service not installed"
fi
echo ""

# Check network
echo "🌐 Network:"
if ping -c 1 google.com &> /dev/null; then
    echo "✅ Internet connection OK"
else
    echo "❌ No internet connection"
fi
echo ""

# Test mpv with YouTube
echo "🧪 Testing mpv with YouTube..."
if timeout 5 mpv --no-video --really-quiet "https://www.youtube.com/watch?v=dQw4w9WgXcQ" &> /dev/null; then
    echo "✅ mpv can play YouTube videos"
else
    echo "⚠️  mpv test inconclusive (this is normal if network is slow)"
fi
echo ""

# System resources
echo "💻 System Resources:"
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'
echo "Memory Usage:"
free -h | awk '/^Mem:/ {print $3 " / " $2}'
echo "Disk Usage:"
df -h / | awk 'NR==2 {print $3 " / " $2 " (" $5 " used)"}'
echo ""

# Recent logs (if service exists)
if systemctl list-unit-files | grep -q "ytmusic-bot.service"; then
    echo "📋 Recent Logs (last 10 lines):"
    sudo journalctl -u ytmusic-bot -n 10 --no-pager
fi

echo ""
echo "✅ Health check complete!"
echo ""
