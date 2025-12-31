#!/bin/bash

# YT Music Bot Service Manager
# Script untuk cek, list, dan hapus systemd service beserta aliasnya

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root or with sudo${NC}"
    exit 1
fi

CURRENT_USER=${SUDO_USER:-$USER}
SERVICE_NAME="ytmusic_bot"

# Function to show menu
show_menu() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   🎵 YT Music Bot Service Manager     ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}1.${NC}  Check Service Status"
    echo -e "${GREEN}2.${NC}  List All YT Music Services"
    echo -e "${GREEN}3.${NC}  Check Service Aliases"
    echo -e "${GREEN}4.${NC}  Delete Service"
    echo -e "${GREEN}5.${NC}  Delete Service + Aliases"
    echo -e "${GREEN}6.${NC}  Show Service Logs (Live)"
    echo -e "${GREEN}7.${NC}  Show Service Logs (Last 100 lines)"
    echo -e "${GREEN}8.${NC}  Restart Service"
    echo -e "${GREEN}9.${NC}  Start Service"
    echo -e "${GREEN}10.${NC} Stop Service"
    echo -e "${GREEN}11.${NC} Enable Service (Auto-start)"
    echo -e "${GREEN}12.${NC} Disable Service (No Auto-start)"
    echo -e "${GREEN}13.${NC} Delete All YT Music Services"
    echo -e "${GREEN}14.${NC} Show Service Configuration"
    echo -e "${RED}0.${NC}  Exit"
    echo ""
}

# Function to check service status
check_service() {
    echo -e "\n${YELLOW}🔍 Checking service status...${NC}\n"
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Service is RUNNING${NC}"
    else
        echo -e "${RED}❌ Service is NOT RUNNING${NC}"
    fi
    
    echo ""
    systemctl status "$SERVICE_NAME" --no-pager -l
    
    echo ""
    echo -e "${YELLOW}📊 Service Information:${NC}"
    echo -e "   Status: $(systemctl is-active $SERVICE_NAME 2>/dev/null || echo 'inactive')"
    echo -e "   Enabled: $(systemctl is-enabled $SERVICE_NAME 2>/dev/null || echo 'disabled')"
    echo -e "   Main PID: $(systemctl show -p MainPID --value $SERVICE_NAME 2>/dev/null || echo 'N/A')"
    echo -e "   Memory: $(systemctl show -p MemoryCurrent --value $SERVICE_NAME 2>/dev/null | numfmt --to=iec 2>/dev/null || echo 'N/A')"
    echo -e "   CPU: $(systemctl show -p CPUUsageNSec --value $SERVICE_NAME 2>/dev/null || echo 'N/A')"
    
    # Show uptime if running
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        start_time=$(systemctl show -p ActiveEnterTimestamp --value $SERVICE_NAME 2>/dev/null)
        if [ ! -z "$start_time" ]; then
            echo -e "   Uptime: $(systemctl show -p ActiveEnterTimestamp --value $SERVICE_NAME)"
        fi
    fi
}

# Function to list all ytmusic services
list_services() {
    echo -e "\n${YELLOW}📋 All YT Music Bot Services:${NC}\n"
    
    services=$(systemctl list-units --type=service --all | grep -i "ytmusic\|pemutar" || echo "")
    
    if [ -z "$services" ]; then
        echo -e "${RED}No YT Music Bot services found${NC}"
    else
        echo "$services"
    fi
    
    echo ""
    echo -e "${YELLOW}📋 Service Files in /etc/systemd/system/:${NC}\n"
    service_files=$(ls -lh /etc/systemd/system/*ytmusic* /etc/systemd/system/*pemutar* 2>/dev/null)
    
    if [ -z "$service_files" ]; then
        echo -e "${RED}No service files found${NC}"
    else
        echo "$service_files"
    fi
}

# Function to check aliases
check_aliases() {
    echo -e "\n${YELLOW}🔗 Checking shell aliases...${NC}\n"
    
    # Check common shell config files
    declare -a config_files=(
        "/home/$CURRENT_USER/.bashrc"
        "/home/$CURRENT_USER/.bash_aliases"
        "/home/$CURRENT_USER/.zshrc"
        "/root/.bashrc"
        "/root/.zshrc"
    )
    
    found_aliases=false
    
    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            aliases=$(grep -n "ytmusic\|pemutar\|ytbot\|music-bot" "$config_file" 2>/dev/null || echo "")
            if [ ! -z "$aliases" ]; then
                echo -e "${GREEN}Found in: $config_file${NC}"
                echo "$aliases"
                echo ""
                found_aliases=true
            fi
        fi
    done
    
    if [ "$found_aliases" = false ]; then
        echo -e "${YELLOW}No aliases found${NC}"
    fi
}

# Function to delete service
delete_service() {
    echo -e "\n${RED}⚠️  WARNING: This will delete the systemd service${NC}\n"
    read -p "Service name to delete (default: $SERVICE_NAME): " input_service
    target_service=${input_service:-$SERVICE_NAME}
    
    # Remove .service suffix if exists (avoid double .service.service)
    target_service=${target_service%.service}
    
    echo -e "\n${YELLOW}Deleting service: $target_service${NC}\n"
    
    # Get PID and kill if needed
    pid=$(systemctl show -p MainPID --value "$target_service" 2>/dev/null)
    
    # Stop service
    echo "Stopping service..."
    systemctl stop "$target_service" 2>/dev/null
    
    # Force kill if still running
    if [ ! -z "$pid" ] && [ "$pid" != "0" ]; then
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "Force killing process $pid..."
            kill -9 "$pid" 2>/dev/null
            sleep 1
        fi
    fi
    
    # Disable service
    echo "Disabling service..."
    systemctl disable "$target_service" 2>/dev/null
    
    # Remove service file
    service_file="/etc/systemd/system/${target_service}.service"
    if [ -f "$service_file" ]; then
        echo "Removing service file: $service_file"
        rm -f "$service_file"
    fi
    
    # Reload daemon
    echo "Reloading systemd daemon..."
    systemctl daemon-reload
    systemctl reset-failed 2>/dev/null
    
    echo -e "\n${GREEN}✅ Service deleted successfully!${NC}"
}

# Function to delete service and aliases
delete_service_and_aliases() {
    delete_service
    
    echo -e "\n${YELLOW}🗑️  Removing aliases...${NC}\n"
    
    declare -a config_files=(
        "/home/$CURRENT_USER/.bashrc"
        "/home/$CURRENT_USER/.bash_aliases"
        "/home/$CURRENT_USER/.zshrc"
        "/root/.bashrc"
    )
    
    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            # Backup original
            cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
            
            # Remove lines containing ytmusic/pemutar/ytbot/music-bot aliases
            sed -i '/alias.*ytmusic/d' "$config_file" 2>/dev/null
            sed -i '/alias.*pemutar/d' "$config_file" 2>/dev/null
            sed -i '/alias.*ytbot/d' "$config_file" 2>/dev/null
            sed -i '/alias.*music-bot/d' "$config_file" 2>/dev/null
            
            echo "✅ Cleaned: $config_file"
        fi
    done
    
    echo -e "\n${GREEN}✅ Service and aliases deleted!${NC}"
    echo -e "${YELLOW}💡 Run 'source ~/.bashrc' to apply changes${NC}"
}

# Function to show live logs
show_live_logs() {
    echo -e "\n${YELLOW}📜 Live logs (Press Ctrl+C to exit):${NC}\n"
    journalctl -u "$SERVICE_NAME" -f --no-pager
}

# Function to show recent logs
show_recent_logs() {
    echo -e "\n${YELLOW}📜 Last 100 log lines:${NC}\n"
    journalctl -u "$SERVICE_NAME" -n 100 --no-pager
    
    echo ""
    echo -e "${CYAN}💡 Tips:${NC}"
    echo -e "   - View more: journalctl -u $SERVICE_NAME -n 500"
    echo -e "   - Follow live: journalctl -u $SERVICE_NAME -f"
    echo -e "   - Filter errors: journalctl -u $SERVICE_NAME -p err"
    echo -e "   - Today's logs: journalctl -u $SERVICE_NAME --since today"
}

# Function to restart service
restart_service() {
    echo -e "\n${YELLOW}🔄 Restarting service: $SERVICE_NAME${NC}\n"
    
    systemctl restart "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Service restarted successfully!${NC}"
        sleep 2
        echo ""
        systemctl status "$SERVICE_NAME" --no-pager -l
    else
        echo -e "${RED}❌ Failed to restart service${NC}"
        echo ""
        echo -e "${YELLOW}Showing error logs:${NC}"
        journalctl -u "$SERVICE_NAME" -n 20 --no-pager
    fi
}

# Function to start service
start_service() {
    echo -e "\n${YELLOW}▶️  Starting service: $SERVICE_NAME${NC}\n"
    
    systemctl start "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Service started successfully!${NC}"
        sleep 2
        echo ""
        systemctl status "$SERVICE_NAME" --no-pager -l
    else
        echo -e "${RED}❌ Failed to start service${NC}"
        echo ""
        echo -e "${YELLOW}Showing error logs:${NC}"
        journalctl -u "$SERVICE_NAME" -n 20 --no-pager
    fi
}

# Function to stop service
stop_service() {
    echo -e "\n${YELLOW}⏹️  Stopping service: $SERVICE_NAME${NC}\n"
    
    systemctl stop "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Service stopped successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to stop service${NC}"
    fi
}

# Function to enable service
enable_service() {
    echo -e "\n${YELLOW}🔧 Enabling service: $SERVICE_NAME${NC}\n"
    echo -e "${CYAN}This will make the service start automatically on boot${NC}\n"
    
    systemctl enable "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Service enabled successfully!${NC}"
        echo -e "${CYAN}Service will now start automatically on system boot${NC}"
    else
        echo -e "${RED}❌ Failed to enable service${NC}"
    fi
}

# Function to disable service
disable_service() {
    echo -e "\n${YELLOW}🔧 Disabling service: $SERVICE_NAME${NC}\n"
    echo -e "${CYAN}This will prevent the service from starting automatically on boot${NC}\n"
    
    systemctl disable "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Service disabled successfully!${NC}"
        echo -e "${CYAN}Service will NOT start automatically on system boot${NC}"
    else
        echo -e "${RED}❌ Failed to disable service${NC}"
    fi
}

# Function to show service configuration
show_service_config() {
    echo -e "\n${YELLOW}⚙️  Service Configuration:${NC}\n"
    
    service_file="/etc/systemd/system/${SERVICE_NAME}.service"
    
    if [ -f "$service_file" ]; then
        echo -e "${CYAN}Service file: $service_file${NC}\n"
        cat "$service_file"
        
        echo ""
        echo -e "${YELLOW}File permissions:${NC}"
        ls -lh "$service_file"
    else
        echo -e "${RED}❌ Service file not found: $service_file${NC}"
    fi
}

# Function to delete ALL ytmusic services
delete_all_services() {
    echo -e "\n${RED}⚠️  WARNING: This will delete ALL YT Music Bot services!${NC}\n"
    
    # Find all service files
    service_files=$(ls /etc/systemd/system/*ytmusic*.service /etc/systemd/system/*pemutar*.service 2>/dev/null)
    
    if [ -z "$service_files" ]; then
        echo -e "${YELLOW}No YT Music Bot services found${NC}"
        return
    fi
    
    echo -e "${YELLOW}Found services:${NC}"
    for file in $service_files; do
        basename "$file"
    done
    
    echo ""
    read -p "Delete ALL these services? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo -e "${YELLOW}Cancelled${NC}"
        return
    fi
    
    echo -e "\n${YELLOW}Deleting all services...${NC}\n"
    
    for file in $service_files; do
        service_name=$(basename "$file" .service)
        echo -e "${BLUE}Processing: $service_name${NC}"
        
        # Get PID
        pid=$(systemctl show -p MainPID --value "$service_name" 2>/dev/null)
        
        # Stop
        systemctl stop "$service_name" 2>/dev/null
        
        # Force kill if needed
        if [ ! -z "$pid" ] && [ "$pid" != "0" ]; then
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "  Force killing PID $pid..."
                kill -9 "$pid" 2>/dev/null
            fi
        fi
        
        # Disable
        systemctl disable "$service_name" 2>/dev/null
        
        # Remove file
        echo "  Removing: $file"
        rm -f "$file"
    done
    
    # Reload daemon
    echo ""
    echo "Reloading systemd daemon..."
    systemctl daemon-reload
    systemctl reset-failed 2>/dev/null
    
    echo -e "\n${GREEN}✅ All services deleted successfully!${NC}"
    
    # Ask to delete aliases
    echo ""
    read -p "Delete aliases too? (Y/n): " delete_aliases
    delete_aliases=${delete_aliases:-Y}
    
    if [[ $delete_aliases =~ ^[Yy]$ ]]; then
        echo -e "\n${YELLOW}🗑️  Removing aliases...${NC}\n"
        
        declare -a config_files=(
            "/home/$CURRENT_USER/.bashrc"
            "/home/$CURRENT_USER/.bash_aliases"
            "/home/$CURRENT_USER/.zshrc"
            "/root/.bashrc"
        )
        
        for config_file in "${config_files[@]}"; do
            if [ -f "$config_file" ]; then
                # Backup original
                cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
                
                # Remove lines containing ytmusic/pemutar/ytbot/music-bot aliases
                sed -i '/alias.*ytmusic/d' "$config_file" 2>/dev/null
                sed -i '/alias.*pemutar/d' "$config_file" 2>/dev/null
                sed -i '/alias.*ytbot/d' "$config_file" 2>/dev/null
                sed -i '/alias.*music-bot/d' "$config_file" 2>/dev/null
                
                echo "✅ Cleaned: $config_file"
            fi
        done
        
        echo -e "\n${GREEN}✅ Aliases deleted!${NC}"
        echo -e "${YELLOW}💡 Run 'source ~/.bashrc' to apply changes${NC}"
    fi
}

# Main loop
while true; do
    show_menu
    read -p "Choose an option (0-14): " choice
    
    case $choice in
        1)
            check_service
            ;;
        2)
            list_services
            ;;
        3)
            check_aliases
            ;;
        4)
            delete_service
            ;;
        5)
            delete_service_and_aliases
            ;;
        6)
            show_live_logs
            ;;
        7)
            show_recent_logs
            ;;
        8)
            restart_service
            ;;
        9)
            start_service
            ;;
        10)
            stop_service
            ;;
        11)
            enable_service
            ;;
        12)
            disable_service
            ;;
        13)
            delete_all_services
            ;;
        14)
            show_service_config
            ;;
        0)
            echo -e "\n${GREEN}👋 Goodbye!${NC}\n"
            exit 0
            ;;
        *)
            echo -e "\n${RED}❌ Invalid option!${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
