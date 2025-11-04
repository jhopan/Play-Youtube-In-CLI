#!/bin/bash

# Setup systemd service for YouTube Music Bot

set -e

echo "🔧 Setting up systemd service..."
echo ""

# Check if running as root for systemd
if [ "$EUID" -ne 0 ]; then 
   echo "This script needs sudo to setup systemd service."
   echo "It will ask for your password."
   echo ""
fi

# Get current user and home directory
CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)
BOT_DIR="$HOME_DIR/ytmusic-bot"

# Check if bot file exists
if [ ! -f "$BOT_DIR/ytmusic_interactive_bot.py" ]; then
    echo "❌ Bot file not found at $BOT_DIR/ytmusic_interactive_bot.py"
    exit 1
fi

# Check if venv exists
if [ -d "$BOT_DIR/venv" ]; then
    PYTHON_EXEC="$BOT_DIR/venv/bin/python"
    echo "✅ Using virtual environment"
else
    PYTHON_EXEC="/usr/bin/python3"
    echo "✅ Using system Python"
fi

# Create service file
SERVICE_FILE="/etc/systemd/system/ytmusic-bot.service"

echo "Creating service file..."
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=YouTube Music Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$BOT_DIR
ExecStart=$PYTHON_EXEC $BOT_DIR/ytmusic_interactive_bot.py
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ytmusic-bot

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable service
echo "Enabling service..."
sudo systemctl enable ytmusic-bot

# Start service
echo "Starting service..."
sudo systemctl start ytmusic-bot

# Wait a moment
sleep 2

# Check status
echo ""
echo "✅ Service setup complete!"
echo ""
echo "📊 Status:"
sudo systemctl status ytmusic-bot --no-pager

echo ""
echo "📝 Useful commands:"
echo "  sudo systemctl start ytmusic-bot    - Start bot"
echo "  sudo systemctl stop ytmusic-bot     - Stop bot"
echo "  sudo systemctl restart ytmusic-bot  - Restart bot"
echo "  sudo systemctl status ytmusic-bot   - Check status"
echo "  sudo journalctl -u ytmusic-bot -f   - View logs"
echo ""
