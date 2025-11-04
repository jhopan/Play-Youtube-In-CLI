#!/bin/bash

# YouTube Music Bot - Quick Setup Script
# For Ubuntu Server

set -e

echo "🎵 YouTube Music Bot - Quick Setup"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "❌ Please don't run as root. Use a normal user account."
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv mpv ffmpeg

# Create directory
echo "📁 Creating bot directory..."
mkdir -p ~/ytmusic-bot
cd ~/ytmusic-bot

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install python-telegram-bot==20.7 yt-dlp

# Check if bot file exists
if [ ! -f "ytmusic_interactive_bot.py" ]; then
    echo "⚠️  ytmusic_interactive_bot.py not found!"
    echo "Please upload the bot file to ~/ytmusic-bot/"
    exit 1
fi

# Make executable
chmod +x ytmusic_interactive_bot.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit bot configuration:"
echo "   nano ~/ytmusic-bot/ytmusic_interactive_bot.py"
echo "   (Change TOKEN to your bot token)"
echo ""
echo "2. Test the bot:"
echo "   cd ~/ytmusic-bot"
echo "   source venv/bin/activate"
echo "   python3 ytmusic_interactive_bot.py"
echo ""
echo "3. Setup as service (optional):"
echo "   sudo ./setup_service.sh"
echo ""
