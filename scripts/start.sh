#!/bin/bash

# YT Music Bot Starter Script
# Script untuk memulai bot dengan mudah

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Detect if running from systemd (no interactive terminal)
if [ -t 1 ]; then
    INTERACTIVE=true
else
    INTERACTIVE=false
fi

if [ "$INTERACTIVE" = true ]; then
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   🎵 YT Music Bot Starter              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""
fi

# Check if running as systemd service
SERVICE_NAME="ytmusic_bot"

if [ "$INTERACTIVE" = true ] && systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
    echo -e "${YELLOW}📋 Systemd service detected${NC}"
    echo ""
    echo "Choose start method:"
    echo "1. Start as systemd service (recommended)"
    echo "2. Start in foreground (manual)"
    echo ""
    read -p "Choice (1-2): " choice
    
    if [ "$choice" == "1" ]; then
        echo -e "\n${YELLOW}🔄 Starting systemd service...${NC}\n"
        
        if [ "$EUID" -ne 0 ]; then
            sudo systemctl start "$SERVICE_NAME"
        else
            systemctl start "$SERVICE_NAME"
        fi
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Service started successfully!${NC}\n"
            
            # Show status
            if [ "$EUID" -ne 0 ]; then
                sudo systemctl status "$SERVICE_NAME" --no-pager -l
            else
                systemctl status "$SERVICE_NAME" --no-pager -l
            fi
            
            echo ""
            echo -e "${YELLOW}💡 Tips:${NC}"
            echo "   - View logs: sudo journalctl -u $SERVICE_NAME -f"
            echo "   - Stop service: ./scripts/stop.sh"
            echo "   - Manage service: sudo ./scripts/manage_service.sh"
        else
            echo -e "${RED}❌ Failed to start service${NC}"
            echo -e "${YELLOW}Showing error logs:${NC}\n"
            
            if [ "$EUID" -ne 0 ]; then
                sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
            else
                journalctl -u "$SERVICE_NAME" -n 20 --no-pager
            fi
        fi
        exit 0
    fi
fi

# Start in foreground (manual or called by systemd)
if [ "$INTERACTIVE" = true ]; then
    echo -e "${YELLOW}▶️  Starting YT Music Bot...${NC}\n"
fi

cd "$PROJECT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    if [ "$INTERACTIVE" = true ]; then
        echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
        echo -e "${YELLOW}Creating virtual environment...${NC}\n"
    fi
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        if [ "$INTERACTIVE" = true ]; then
            echo -e "${RED}❌ Failed to create virtual environment${NC}"
        fi
        exit 1
    fi
fi

# Activate venv
if [ "$INTERACTIVE" = true ]; then
    echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
fi
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/lib/python3.*/site-packages/telegram" ]; then
    if [ "$INTERACTIVE" = true ]; then
        echo -e "${YELLOW}📦 Installing dependencies...${NC}\n"
    fi
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        if [ "$INTERACTIVE" = true ]; then
            echo -e "${RED}❌ Failed to install dependencies${NC}"
        fi
        exit 1
    fi
fi

# Check .env file
if [ ! -f ".env" ]; then
    if [ "$INTERACTIVE" = true ]; then
        echo -e "${RED}❌ .env file not found!${NC}"
        echo -e "${YELLOW}Please create .env file with your configuration${NC}"
        echo ""
        echo "Example:"
        echo "  TELEGRAM_BOT_TOKEN=your_bot_token_here"
        echo "  TELEGRAM_USER_ID=your_user_id_here"
        echo ""
    fi
    exit 1
fi

if [ "$INTERACTIVE" = true ]; then
    echo -e "${GREEN}✅ Starting bot...${NC}\n"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

# Run the bot
python3 main.py
