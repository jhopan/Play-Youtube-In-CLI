#!/bin/bash

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root or with sudo"
    exit 1
fi

# Get current user
CURRENT_USER=${SUDO_USER:-$USER}

echo "🚀 Systemd Service Installer"
echo "═══════════════════════════════════"
echo ""
echo "Project Directory: $PROJECT_DIR"
echo "User: $CURRENT_USER"
echo ""

# Ask for service name
read -p "Enter service name (default: ytmusic-bot): " INPUT_NAME
SERVICE_NAME=${INPUT_NAME:-ytmusic-bot}
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo ""
echo "📦 Installing service: $SERVICE_NAME..."

# Create service file
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=YouTube Music Telegram Bot
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=$PROJECT_DIR/scripts/start.sh
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

# Make start.sh executable
chmod +x "$PROJECT_DIR/scripts/start.sh"

# Reload systemd
systemctl daemon-reload

echo "✅ Service installed successfully!"
echo ""

# Ask to enable auto-start
read -p "Enable auto-start on boot? (Y/n): " ENABLE_BOOT
ENABLE_BOOT=${ENABLE_BOOT:-Y}

if [[ $ENABLE_BOOT =~ ^[Yy]$ ]]; then
    systemctl enable "$SERVICE_NAME"
    echo "✅ Auto-start enabled!"
fi

# Ask to start now
read -p "Start service now? (Y/n): " START_NOW
START_NOW=${START_NOW:-Y}

if [[ $START_NOW =~ ^[Yy]$ ]]; then
    systemctl start "$SERVICE_NAME"
    echo "✅ Service started!"
    echo ""
    systemctl status "$SERVICE_NAME" --no-pager
fi

echo ""
echo "═══════════════════════════════════"
echo "📋 Service Management Commands:"
echo "═══════════════════════════════════"
echo "  sudo systemctl start $SERVICE_NAME"
echo "  sudo systemctl stop $SERVICE_NAME"
echo "  sudo systemctl restart $SERVICE_NAME"
echo "  sudo systemctl status $SERVICE_NAME"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
