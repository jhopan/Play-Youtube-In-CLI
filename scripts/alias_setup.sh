#!/bin/bash

SHELL_RC=""

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    echo "❌ Unsupported shell"
    exit 1
fi

echo "🔍 Alias Setup - Project Directory Finder"
echo "═══════════════════════════════════════════"
echo ""
echo "Scanning system for Telegram Bot projects..."
echo ""

# Scan common directories for projects
DIRS=()
DIR_PATHS=()

# Search in home directory
if [ -d "$HOME" ]; then
    while IFS= read -r -d '' dir; do
        DIRS+=("$(basename "$dir")")
        DIR_PATHS+=("$dir")
    done < <(find "$HOME" -maxdepth 3 -type d \( -name "*Youtube*" -o -name "*YT*Music*" -o -name "*Play*Youtube*" -o -name "*Bot*Telegram*" -o -name "*telegram*bot*" \) -print0 2>/dev/null | head -z -n 20)
fi

# Add current directory if it looks like a project
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
if [ -f "$PROJECT_DIR/main.py" ] || [ -f "$PROJECT_DIR/run_telegram_bot.py" ]; then
    # Check if not already in list
    if [[ ! " ${DIR_PATHS[@]} " =~ " ${PROJECT_DIR} " ]]; then
        DIRS+=("$(basename "$PROJECT_DIR") [CURRENT]")
        DIR_PATHS+=("$PROJECT_DIR")
    fi
fi

if [ ${#DIRS[@]} -eq 0 ]; then
    echo "❌ No project directories found!"
    echo ""
    echo "Manually enter project directory:"
    read -p "Path: " MANUAL_DIR
    if [ -d "$MANUAL_DIR" ]; then
        DIR_PATHS=("$MANUAL_DIR")
        SELECTED_INDEX=0
    else
        echo "❌ Directory not found: $MANUAL_DIR"
        exit 1
    fi
else
    echo "Found ${#DIRS[@]} project(s):"
    echo ""
    for i in "${!DIRS[@]}"; do
        echo "  [$((i+1))] ${DIRS[$i]}"
        echo "      ${DIR_PATHS[$i]}"
        echo ""
    done
    
    echo "═══════════════════════════════════════════"
    read -p "Select project number (1-${#DIRS[@]}): " SELECTION
    
    SELECTED_INDEX=$((SELECTION-1))
    
    if [ $SELECTED_INDEX -lt 0 ] || [ $SELECTED_INDEX -ge ${#DIRS[@]} ]; then
        echo "❌ Invalid selection"
        exit 1
    fi
fi

SELECTED_DIR="${DIR_PATHS[$SELECTED_INDEX]}"
PROJECT_NAME=$(basename "$SELECTED_DIR")

echo ""
echo "✅ Selected: $PROJECT_NAME"
echo "   Path: $SELECTED_DIR"
echo ""

# Ask for alias name
DEFAULT_ALIAS=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/^-//;s/-$//')
read -p "Enter alias name (default: $DEFAULT_ALIAS): " ALIAS_NAME
ALIAS_NAME=${ALIAS_NAME:-$DEFAULT_ALIAS}

echo ""
echo "🔍 Scanning systemd services..."
echo ""

# Scan systemd services (user and system)
SERVICES=()
SERVICE_UNITS=()
ALL_SERVICES=()
ALL_SERVICE_UNITS=()

# Get user services
while IFS= read -r line; do
    service=$(echo "$line" | awk '{print $1}')
    if [[ $service =~ \.service$ ]]; then
        name=$(basename "$service" .service)
        # Case-insensitive match
        if echo "$name" | grep -iq -E '(bot|telegram|ytmusic|youtube|music|python)'; then
            SERVICE_UNITS+=("$service")
            SERVICES+=("$name [USER]")
        fi
        ALL_SERVICE_UNITS+=("$service")
        ALL_SERVICES+=("$name [USER]")
    fi
done < <(systemctl --user list-unit-files --type=service 2>/dev/null)

# Check running user services
while IFS= read -r line; do
    service=$(echo "$line" | awk '{print $1}')
    if [[ $service =~ \.service$ ]]; then
        name=$(basename "$service" .service)
        # Check if not already in list
        if [[ ! " ${SERVICE_UNITS[@]} " =~ " ${service} " ]]; then
            if echo "$name" | grep -iq -E '(bot|telegram|ytmusic|youtube|music|python)'; then
                SERVICE_UNITS+=("$service")
                SERVICES+=("$name [USER-ACTIVE]")
            fi
        fi
        if [[ ! " ${ALL_SERVICE_UNITS[@]} " =~ " ${service} " ]]; then
            ALL_SERVICE_UNITS+=("$service")
            ALL_SERVICES+=("$name [USER-ACTIVE]")
        fi
    fi
done < <(systemctl --user list-units --all --type=service 2>/dev/null)

# Get system services
while IFS= read -r line; do
    service=$(echo "$line" | awk '{print $1}')
    if [[ $service =~ \.service$ ]]; then
        name=$(basename "$service" .service)
        # Case-insensitive match
        if echo "$name" | grep -iq -E '(bot|telegram|ytmusic|youtube|music|python)'; then
            SERVICE_UNITS+=("$service")
            SERVICES+=("$name [SYSTEM]")
        fi
        ALL_SERVICE_UNITS+=("$service")
        ALL_SERVICES+=("$name [SYSTEM]")
    fi
done < <(systemctl list-unit-files --type=service 2>/dev/null)

# Check running system services
while IFS= read -r line; do
    service=$(echo "$line" | awk '{print $1}')
    if [[ $service =~ \.service$ ]]; then
        name=$(basename "$service" .service)
        # Check if not already in list
        if [[ ! " ${SERVICE_UNITS[@]} " =~ " ${service} " ]]; then
            if echo "$name" | grep -iq -E '(bot|telegram|ytmusic|youtube|music|python)'; then
                SERVICE_UNITS+=("$service")
                SERVICES+=("$name [SYSTEM-ACTIVE]")
            fi
        fi
        if [[ ! " ${ALL_SERVICE_UNITS[@]} " =~ " ${service} " ]]; then
            ALL_SERVICE_UNITS+=("$service")
            ALL_SERVICES+=("$name [SYSTEM-ACTIVE]")
        fi
    fi
done < <(systemctl list-units --all --type=service 2>/dev/null)

if [ ${#SERVICES[@]} -eq 0 ]; then
    echo "⚠️  No matching services found with keywords: bot, telegram, ytmusic, youtube, music, python"
    echo ""
    echo "Total services found: ${#ALL_SERVICES[@]}"
    read -p "Show all ${#ALL_SERVICES[@]} services? (y/n): " SHOW_ALL
    
    if [[ $SHOW_ALL =~ ^[Yy] ]]; then
        SERVICES=("${ALL_SERVICES[@]}")
        SERVICE_UNITS=("${ALL_SERVICE_UNITS[@]}")
    fi
fi

if [ ${#SERVICES[@]} -eq 0 ]; then
    echo "⚠️  No systemd services found!"
    echo ""
    read -p "Enter service name manually (or press Enter to skip systemctl aliases): " SERVICE_NAME
    
    if [ -z "$SERVICE_NAME" ]; then
        echo ""
        echo "🔧 Creating alias without systemctl commands..."
        
        # Remove old aliases if exist
        sed -i "/# $PROJECT_NAME Aliases/,/^$/d" "$SHELL_RC" 2>/dev/null
        
        # Add simple cd alias only
        cat >> "$SHELL_RC" <<EOF

# $PROJECT_NAME Aliases
alias $ALIAS_NAME='cd $SELECTED_DIR'
EOF
        
        echo "✅ Alias added to $SHELL_RC"
        echo ""
        echo "═══════════════════════════════════════════"
        echo "📋 Available Command:"
        echo "═══════════════════════════════════════════"
        echo "  $ALIAS_NAME  - Go to project directory"
        echo ""
        echo "Run this to activate:"
        echo "  source $SHELL_RC"
        echo ""
        exit 0
    fi
    
    USE_SUDO=""
    USE_USER_FLAG=""
else
    echo "Found ${#SERVICES[@]} service(s):"
    echo ""
    for i in "${!SERVICES[@]}"; do
        echo "  [$((i+1))] ${SERVICES[$i]}"
        echo "      ${SERVICE_UNITS[$i]}"
        echo ""
    done
    
    echo "═══════════════════════════════════════════"
    echo "0. Enter service name manually"
    echo ""
    read -p "Select service number (0-${#SERVICES[@]}): " SERVICE_SELECTION
    
    if [ "$SERVICE_SELECTION" = "0" ]; then
        read -p "Enter service name: " SERVICE_NAME
        read -p "Service type - [1] System (sudo), [2] User (--user), default: 1): " SERVICE_TYPE
        SERVICE_TYPE=${SERVICE_TYPE:-1}
        
        if [ "$SERVICE_TYPE" = "2" ]; then
            USE_SUDO=""
            USE_USER_FLAG="--user "
        else
            USE_SUDO="sudo "
            USE_USER_FLAG=""
        fi
    else
        SERVICE_INDEX=$((SERVICE_SELECTION-1))
        
        if [ $SERVICE_INDEX -lt 0 ] || [ $SERVICE_INDEX -ge ${#SERVICES[@]} ]; then
            echo "❌ Invalid selection"
            exit 1
        fi
        
        SERVICE_NAME=$(basename "${SERVICE_UNITS[$SERVICE_INDEX]}" .service)
        
        # Check if system or user service
        if [[ ${SERVICES[$SERVICE_INDEX]} == *"[SYSTEM"* ]]; then
            USE_SUDO="sudo "
            USE_USER_FLAG=""
        else
            USE_SUDO=""
            USE_USER_FLAG="--user "
        fi
    fi
fi

echo ""
echo "✅ Selected service: $SERVICE_NAME"
if [ -n "$USE_SUDO" ]; then
    echo "   Type: System service (requires sudo)"
else
    echo "   Type: User service"
fi
echo ""
echo "🔧 Setting up aliases..."

# Remove old aliases if exist
sed -i "/# $PROJECT_NAME Aliases/,/^$/d" "$SHELL_RC" 2>/dev/null

# Add new aliases
if [ -n "$USE_SUDO" ]; then
    # System service - needs sudo
    cat >> "$SHELL_RC" <<EOF

# $PROJECT_NAME Aliases
alias $ALIAS_NAME='cd $SELECTED_DIR'
alias ${ALIAS_NAME}-start='sudo systemctl start $SERVICE_NAME.service'
alias ${ALIAS_NAME}-stop='sudo systemctl stop $SERVICE_NAME.service'
alias ${ALIAS_NAME}-restart='sudo systemctl restart $SERVICE_NAME.service'
alias ${ALIAS_NAME}-status='sudo systemctl status $SERVICE_NAME.service'
alias ${ALIAS_NAME}-logs='sudo journalctl -u $SERVICE_NAME.service -f'
alias ${ALIAS_NAME}-enable='sudo systemctl enable $SERVICE_NAME.service'
alias ${ALIAS_NAME}-disable='sudo systemctl disable $SERVICE_NAME.service'
EOF
else
    # User service - no sudo
    cat >> "$SHELL_RC" <<EOF

# $PROJECT_NAME Aliases
alias $ALIAS_NAME='cd $SELECTED_DIR'
alias ${ALIAS_NAME}-start='systemctl --user start $SERVICE_NAME.service'
alias ${ALIAS_NAME}-stop='systemctl --user stop $SERVICE_NAME.service'
alias ${ALIAS_NAME}-restart='systemctl --user restart $SERVICE_NAME.service'
alias ${ALIAS_NAME}-status='systemctl --user status $SERVICE_NAME.service'
alias ${ALIAS_NAME}-logs='journalctl --user -u $SERVICE_NAME.service -f'
alias ${ALIAS_NAME}-enable='systemctl --user enable $SERVICE_NAME.service'
alias ${ALIAS_NAME}-disable='systemctl --user disable $SERVICE_NAME.service'
EOF
fi

echo "✅ Aliases added to $SHELL_RC"
echo ""
echo "═══════════════════════════════════════════"
echo "📋 Available Commands:"
echo "═══════════════════════════════════════════"
echo "  $ALIAS_NAME            - Go to project directory"
echo "  ${ALIAS_NAME}-start    - Start service"
echo "  ${ALIAS_NAME}-stop     - Stop service"
echo "  ${ALIAS_NAME}-restart  - Restart service"
echo "  ${ALIAS_NAME}-status   - Check service status"
echo "  ${ALIAS_NAME}-logs     - View service logs"
echo "  ${ALIAS_NAME}-enable   - Enable service on boot"
echo "  ${ALIAS_NAME}-disable  - Disable service on boot"
echo ""
echo "Run this to activate:"
echo "  source $SHELL_RC"
echo ""
