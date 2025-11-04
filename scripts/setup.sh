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
sudo apt install -y python3 python3-pip python3-venv python3-full mpv ffmpeg

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 Using project directory: $PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your BOT_TOKEN and ALLOWED_USER_IDS"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Configure environment variables:"
echo "   nano .env"
echo "   (Add BOT_TOKEN and ALLOWED_USER_IDS)"
echo ""
echo "2. Test the bot:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. Setup as service (optional):"
echo "   sudo ./scripts/setup_service.sh"
echo ""
