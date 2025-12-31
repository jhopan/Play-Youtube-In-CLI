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

echo "🚀 YT Music Bot - Alias Setup"
echo "═══════════════════════════════════════════"
echo ""

# Get current project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME=$(basename "$PROJECT_DIR")

# Verify this is the correct project
if [ ! -f "$PROJECT_DIR/main.py" ]; then
    echo "❌ Error: main.py not found!"
    echo "This script must be run from Play-Youtube-In-CLI/scripts directory"
    exit 1
fi

echo "Project: $PROJECT_NAME"
echo "Path: $PROJECT_DIR"
echo ""

# Ask for alias name
DEFAULT_ALIAS="ytmusic"
read -p "Enter alias name (default: $DEFAULT_ALIAS): " ALIAS_NAME
ALIAS_NAME=${ALIAS_NAME:-$DEFAULT_ALIAS}

echo ""
echo "🔍 Scanning systemd services for ytmusic..."
echo ""

# Scan only ytmusic-related services
SERVICES=()
SERVICE_UNITS=()

# Get system services matching ytmusic pattern
while IFS= read -r line; do
    service=$(echo "$line" | awk '{print $1}')
    if [[ $service =~ \.service$ ]]; then
        name=$(basename "$service" .service)
        SERVICE_UNITS+=("$service")
        SERVICES+=("$name")
    fi
done < <(systemctl list-unit-files --type=service 2>/dev/null | grep -i ytmusic)

# Check running system services
while IFS= read -r line; do
    service=$(echo "$line" | awk '{print $1}')
    if [[ $service =~ \.service$ ]]; then
        name=$(basename "$service" .service)
        # Check if not already in list
        if [[ ! " ${SERVICE_UNITS[@]} " =~ " ${service} " ]]; then
            SERVICE_UNITS+=("$service")
            SERVICES+=("$name")
        fi
    fi
done < <(systemctl list-units --all --type=service 2>/dev/null | grep -i ytmusic)

if [ ${#SERVICES[@]} -eq 0 ]; then
    echo "⚠️  No ytmusic systemd services found!"
    echo ""
    read -p "Enter service name manually (or press Enter to skip): " SERVICE_NAME
    
    if [ -z "$SERVICE_NAME" ]; then
        echo ""
        echo "🔧 Creating alias without systemctl commands..."
        
        # Remove old aliases if exist
        sed -i "/# YT Music Bot Aliases/,/^$/d" "$SHELL_RC" 2>/dev/null
        
        # Add simple cd alias only
        cat >> "$SHELL_RC" <<EOF

# YT Music Bot Aliases
alias $ALIAS_NAME='cd $PROJECT_DIR'
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
elif [ ${#SERVICES[@]} -eq 1 ]; then
    # Auto-select if only one service found
    SERVICE_NAME="${SERVICES[0]}"
    echo "✅ Found service: $SERVICE_NAME"
else
    echo "Found ${#SERVICES[@]} ytmusic service(s):"
    echo ""
    for i in "${!SERVICES[@]}"; do
        echo "  [$((i+1))] ${SERVICES[$i]}"
    done
    echo ""
    
    echo "═══════════════════════════════════════════"
    read -p "Select service number (1-${#SERVICES[@]}): " SERVICE_SELECTION
    
    SERVICE_INDEX=$((SERVICE_SELECTION-1))
    
    if [ $SERVICE_INDEX -lt 0 ] || [ $SERVICE_INDEX -ge ${#SERVICES[@]} ]; then
        echo "❌ Invalid selection"
        exit 1
    fi
    
    SERVICE_NAME="${SERVICES[$SERVICE_INDEX]}"
fi

echo ""
echo "✅ Selected service: $SERVICE_NAME"
echo "   Type: System service (requires sudo)"
echo ""
echo "🔧 Setting up aliases..."

# Remove old aliases if exist
sed -i "/# YT Music Bot Aliases/,/^$/d" "$SHELL_RC" 2>/dev/null

# Add new aliases (system service with sudo)
cat >> "$SHELL_RC" <<EOF

# YT Music Bot Aliases
alias $ALIAS_NAME='cd $PROJECT_DIR'
alias ${ALIAS_NAME}-start='sudo systemctl start $SERVICE_NAME.service'
alias ${ALIAS_NAME}-stop='sudo systemctl stop $SERVICE_NAME.service'
alias ${ALIAS_NAME}-restart='sudo systemctl restart $SERVICE_NAME.service'
alias ${ALIAS_NAME}-status='sudo systemctl status $SERVICE_NAME.service'
alias ${ALIAS_NAME}-logs='sudo journalctl -u $SERVICE_NAME.service -f'
alias ${ALIAS_NAME}-enable='sudo systemctl enable $SERVICE_NAME.service'
alias ${ALIAS_NAME}-disable='sudo systemctl disable $SERVICE_NAME.service'
EOF

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
