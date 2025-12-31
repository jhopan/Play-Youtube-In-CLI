#!/bin/bash

# YT Music Bot Stop Script
# Script untuk menghentikan bot dengan mudah

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🛑 YT Music Bot Stopper              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

SERVICE_NAME="ytmusic_bot"

# Check if running as systemd service
if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
    echo -e "${YELLOW}📋 Systemd service detected${NC}\n"
    
    # Check if service is running
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${YELLOW}⏹️  Stopping systemd service...${NC}\n"
        
        if [ "$EUID" -ne 0 ]; then
            sudo systemctl stop "$SERVICE_NAME"
        else
            systemctl stop "$SERVICE_NAME"
        fi
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Service stopped successfully!${NC}\n"
            
            # Show status
            if [ "$EUID" -ne 0 ]; then
                sudo systemctl status "$SERVICE_NAME" --no-pager -l
            else
                systemctl status "$SERVICE_NAME" --no-pager -l
            fi
        else
            echo -e "${RED}❌ Failed to stop service${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Service is not running${NC}"
    fi
else
    echo -e "${YELLOW}📋 No systemd service found${NC}"
    echo -e "${YELLOW}Looking for running Python processes...${NC}\n"
fi

# Find and kill Python process running main.py
pids=$(pgrep -f "python.*main.py" 2>/dev/null)

if [ ! -z "$pids" ]; then
    echo -e "${YELLOW}Found running bot processes:${NC}"
    ps -p $pids -o pid,cmd --no-headers
    echo ""
    
    read -p "Kill these processes? (Y/n): " confirm
    confirm=${confirm:-Y}
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "\n${YELLOW}🔪 Killing processes...${NC}\n"
        
        for pid in $pids; do
            echo "Killing PID: $pid"
            kill -15 $pid 2>/dev/null
            
            # Wait a bit
            sleep 1
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo "Force killing PID: $pid"
                kill -9 $pid 2>/dev/null
            fi
        done
        
        echo -e "\n${GREEN}✅ All processes stopped${NC}"
    else
        echo -e "\n${YELLOW}Cancelled${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No running bot processes found${NC}"
fi

# Also kill any mpv processes that might be running
mpv_pids=$(pgrep -f "mpv.*youtube" 2>/dev/null)
if [ ! -z "$mpv_pids" ]; then
    echo -e "\n${YELLOW}Found MPV music player processes${NC}"
    read -p "Kill MPV processes too? (Y/n): " kill_mpv
    kill_mpv=${kill_mpv:-Y}
    
    if [[ $kill_mpv =~ ^[Yy]$ ]]; then
        for pid in $mpv_pids; do
            kill -9 $pid 2>/dev/null
        done
        echo -e "${GREEN}✅ MPV processes stopped${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Done!${NC}"
