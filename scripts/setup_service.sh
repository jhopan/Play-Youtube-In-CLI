#!/bin/bash

# Setup systemd service for YouTube Music Bot
# Interactive service creation script

set -e

echo "🔧 Systemd Service Setup"
echo "================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Please run this script as normal user (not root)"
   echo "The script will ask for sudo when needed."
   exit 1
fi

# Get current user and home directory
CURRENT_USER=$(whoami)
HOME_DIR="$HOME"

echo "👤 Current user: $CURRENT_USER"
echo "🏠 Home directory: $HOME_DIR"
echo ""

# Ask what service to create
echo "📋 What service do you want to create?"
echo "-----------------------------------"
echo "1. YouTube Music Telegram Bot"
echo "2. Custom Python Script Service"
echo "3. Custom Application Service"
echo "0. Cancel"
echo ""
read -p "Select option [1-3]: " SERVICE_TYPE

case $SERVICE_TYPE in
    1)
        echo ""
        echo "🎵 Setting up YouTube Music Bot Service"
        echo ""
        
        # Find bot directory
        DEFAULT_BOT_DIR="$HOME_DIR/Play-Youtube-In-CLI"
        
        if [ -d "$DEFAULT_BOT_DIR" ]; then
            echo "✅ Found bot directory: $DEFAULT_BOT_DIR"
            BOT_DIR="$DEFAULT_BOT_DIR"
        else
            echo "⚠️  Default directory not found"
            read -p "Enter bot directory path:" BOT_DIR
            BOT_DIR="${BOT_DIR/#\~/$HOME_DIR}"
        fi
        
        # Check if main.py exists
        if [ ! -f "$BOT_DIR/main.py" ]; then
            echo "❌ main.py not found in $BOT_DIR"
            exit 1
        fi
        
        # Check if start.sh exists
        if [ ! -f "$BOT_DIR/scripts/start.sh" ]; then
            echo "❌ scripts/start.sh not found in $BOT_DIR"
            exit 1
        fi
        
        # Make scripts executable
        chmod +x "$BOT_DIR/scripts/start.sh" 2>/dev/null || true
        chmod +x "$BOT_DIR/scripts/stop.sh" 2>/dev/null || true
        
        SERVICE_NAME="ytmusic-bot"
        DESCRIPTION="YouTube Music Telegram Bot"
        EXEC_START="$BOT_DIR/scripts/start.sh"
        EXEC_STOP="$BOT_DIR/scripts/stop.sh"
        WORKING_DIR="$BOT_DIR"
        USE_CUSTOM_SCRIPTS=true
        ;;
        
    2)
        echo ""
        echo "🐍 Setting up Custom Python Script Service"
        echo ""
        
        read -p "Enter service name: " SERVICE_NAME
        read -p "Enter description: " DESCRIPTION
        read -p "Enter Python script path: " SCRIPT_PATH
        SCRIPT_PATH="${SCRIPT_PATH/#\~/$HOME_DIR}"
        
        if [ ! -f "$SCRIPT_PATH" ]; then
            echo "❌ Script not found: $SCRIPT_PATH"
            exit 1
        fi
        
        WORKING_DIR=$(dirname "$SCRIPT_PATH")
        
        # Check for venv in script directory
        if [ -d "$WORKING_DIR/venv" ]; then
            PYTHON_EXEC="$WORKING_DIR/venv/bin/python"
            echo "✅ Using virtual environment"
        else
            read -p "Python executable path (default: /usr/bin/python3): " PYTHON_EXEC
            PYTHON_EXEC="${PYTHON_EXEC:-/usr/bin/python3}"
        fi
        
        EXEC_START="$PYTHON_EXEC $SCRIPT_PATH"
        ;;
        
    3)
        echo ""
        echo "⚙️  Setting up Custom Application Service"
        echo ""
        
        read -p "Enter service name: " SERVICE_NAME
        read -p "Enter description: " DESCRIPTION
        read -p "Enter command to execute: " EXEC_START
        read -p "Enter working directory: " WORKING_DIR
        WORKING_DIR="${WORKING_DIR/#\~/$HOME_DIR}"
        ;;
        
    0)
        echo "❌ Cancelled"
        exit 0
        ;;
        
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

# Validate service name
if ! [[ "$SERVICE_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "❌ Invalid service name. Use only letters, numbers, underscore, and hyphen."
    exit 1
fi

echo ""
echo "📝 Service Configuration:"
echo "------------------------"
echo "Name: $SERVICE_NAME"
echo "Description: $DESCRIPTION"
echo "User: $CURRENT_USER"
echo "Working Directory: $WORKING_DIR"
echo "Exec: $EXEC_START"
echo ""

read -p "Create this service? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ Cancelled"
    exit 0
fi

# Create service file
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo ""
echo "🔨 Creating service file..."

if [ "${USE_CUSTOM_SCRIPTS:-false}" = "true" ]; then
    # For services using custom start/stop scripts (like ytmusic-bot)
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=$DESCRIPTION
After=network.target

[Service]
Type=forking
User=$CURRENT_USER
WorkingDirectory=$WORKING_DIR
ExecStart=$EXEC_START
ExecStop=$EXEC_STOP
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF
else
    # For standard services
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=$DESCRIPTION
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$WORKING_DIR
ExecStart=$EXEC_START
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF
fi

echo "✅ Service file created: $SERVICE_FILE"

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Ask if user wants to enable service
read -p "Enable service on boot? (y/n): " ENABLE_SERVICE

if [ "$ENABLE_SERVICE" = "y" ] || [ "$ENABLE_SERVICE" = "Y" ]; then
    echo "⚙️  Enabling service..."
    sudo systemctl enable $SERVICE_NAME
    echo "✅ Service enabled"
fi

# Ask if user wants to start service now
read -p "Start service now? (y/n): " START_SERVICE

if [ "$START_SERVICE" = "y" ] || [ "$START_SERVICE" = "Y" ]; then
    echo "▶️  Starting service..."
    sudo systemctl start $SERVICE_NAME
    
    # Wait a moment
    sleep 2
    
    # Check status
    echo ""
    echo "📊 Service Status:"
    echo "-------------------"
    sudo systemctl status $SERVICE_NAME --no-pager || true
fi

echo ""
echo "✅ Service setup complete!"
echo ""

if [ "${USE_CUSTOM_SCRIPTS:-false}" = "true" ]; then
    echo "📝 Quick commands:"
    echo "  ./scripts/start.sh                      - Start bot (easy way)"
    echo "  ./scripts/stop.sh                       - Stop bot (easy way)"
    echo "  sudo ./scripts/manage_service.sh        - Manage service"
    echo ""
    echo "📝 Systemctl commands:"
    echo "  sudo systemctl start $SERVICE_NAME      - Start service"
    echo "  sudo systemctl stop $SERVICE_NAME       - Stop service"
    echo "  sudo systemctl restart $SERVICE_NAME    - Restart service"
    echo "  sudo systemctl status $SERVICE_NAME     - Check status"
    echo "  sudo journalctl -u $SERVICE_NAME -f     - View live logs"
else
    echo "📝 Useful commands:"
    echo "  sudo systemctl start $SERVICE_NAME      - Start service"
    echo "  sudo systemctl stop $SERVICE_NAME       - Stop service"
    echo "  sudo systemctl restart $SERVICE_NAME    - Restart service"
    echo "  sudo systemctl status $SERVICE_NAME     - Check status"
    echo "  sudo systemctl enable $SERVICE_NAME     - Enable on boot"
    echo "  sudo systemctl disable $SERVICE_NAME    - Disable on boot"
    echo "  sudo journalctl -u $SERVICE_NAME -f     - View live logs"
fi
echo ""
echo "💡 Tip: Use scripts/setup_alias.sh to create convenient aliases!"
echo ""
