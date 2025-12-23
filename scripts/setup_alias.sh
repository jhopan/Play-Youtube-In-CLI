#!/bin/bash

# Setup Alias for Systemctl Services
# This script helps create convenient aliases for managing systemd services

set -e

echo "🔧 Setup Service Alias"
echo "================================"
echo ""

# Get all user services (non-system services)
echo "📋 Scanning available services..."
echo ""

# Get list of enabled services that are likely user-created
SERVICES=$(systemctl list-unit-files --type=service --state=enabled,disabled,static | grep -v "^UNIT" | grep -v "^[0-9]" | awk '{print $1}' | sort)

# Filter to likely user services (exclude common system services)
USER_SERVICES=()
while IFS= read -r service; do
    # Skip common system services
    if [[ ! "$service" =~ ^(getty|systemd|dbus|network|bluetooth|cups|avahi|polkit|udisks|accounts|rtkit|upower|gdm|lightdm|sshd) ]]; then
        USER_SERVICES+=("$service")
    fi
done <<< "$SERVICES"

# If no user services found, show all services
if [ ${#USER_SERVICES[@]} -eq 0 ]; then
    echo "⚠️  No user services found. Showing all services..."
    echo ""
    USER_SERVICES=($(systemctl list-unit-files --type=service | grep -v "^UNIT" | grep -v "^[0-9]" | awk '{print $1}' | head -20))
fi

# Display services with numbers
echo "Available Services:"
echo "-------------------"
for i in "${!USER_SERVICES[@]}"; do
    SERVICE="${USER_SERVICES[$i]}"
    STATUS=$(systemctl is-active "$SERVICE" 2>/dev/null || echo "inactive")
    if [ "$STATUS" = "active" ]; then
        STATUS_ICON="🟢"
    else
        STATUS_ICON="🔴"
    fi
    printf "%2d. %s %-40s [%s]\n" $((i+1)) "$STATUS_ICON" "$SERVICE" "$STATUS"
done

echo ""
echo "0. Cancel"
echo ""

# Ask user to select a service
read -p "Select service number: " SERVICE_NUM

# Validate input
if [ "$SERVICE_NUM" = "0" ]; then
    echo "❌ Cancelled"
    exit 0
fi

if ! [[ "$SERVICE_NUM" =~ ^[0-9]+$ ]] || [ "$SERVICE_NUM" -lt 1 ] || [ "$SERVICE_NUM" -gt "${#USER_SERVICES[@]}" ]; then
    echo "❌ Invalid selection"
    exit 1
fi

# Get selected service
SELECTED_SERVICE="${USER_SERVICES[$((SERVICE_NUM-1))]}"
SERVICE_NAME="${SELECTED_SERVICE%.service}"

echo ""
echo "Selected: $SELECTED_SERVICE"
echo ""

# Ask for alias name
read -p "Enter alias name (default: $SERVICE_NAME): " ALIAS_NAME

if [ -z "$ALIAS_NAME" ]; then
    ALIAS_NAME="$SERVICE_NAME"
fi

# Validate alias name (alphanumeric and underscore/hyphen only)
if ! [[ "$ALIAS_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "❌ Invalid alias name. Use only letters, numbers, underscore, and hyphen."
    exit 1
fi

echo ""
echo "📝 Creating aliases for: $ALIAS_NAME"
echo ""

# Determine shell config file
SHELL_CONFIG=""
if [ -n "$BASH_VERSION" ]; then
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_CONFIG="$HOME/.bash_profile"
    fi
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
fi

if [ -z "$SHELL_CONFIG" ]; then
    # Try to detect from $SHELL variable
    case "$SHELL" in
        */bash)
            SHELL_CONFIG="$HOME/.bashrc"
            ;;
        */zsh)
            SHELL_CONFIG="$HOME/.zshrc"
            ;;
        *)
            SHELL_CONFIG="$HOME/.bashrc"
            ;;
    esac
fi

# Create aliases
ALIASES="
# Aliases for $SELECTED_SERVICE (created by setup_alias.sh)
alias ${ALIAS_NAME}-start='sudo systemctl start $SELECTED_SERVICE'
alias ${ALIAS_NAME}-stop='sudo systemctl stop $SELECTED_SERVICE'
alias ${ALIAS_NAME}-restart='sudo systemctl restart $SELECTED_SERVICE'
alias ${ALIAS_NAME}-status='sudo systemctl status $SELECTED_SERVICE'
alias ${ALIAS_NAME}-logs='sudo journalctl -u $SELECTED_SERVICE -f'
alias ${ALIAS_NAME}-enable='sudo systemctl enable $SELECTED_SERVICE'
alias ${ALIAS_NAME}-disable='sudo systemctl disable $SELECTED_SERVICE'
"

# Check if aliases already exist
if grep -q "# Aliases for $SELECTED_SERVICE" "$SHELL_CONFIG" 2>/dev/null; then
    echo "⚠️  Aliases for $SELECTED_SERVICE already exist in $SHELL_CONFIG"
    read -p "Do you want to replace them? (y/n): " REPLACE
    if [ "$REPLACE" != "y" ] && [ "$REPLACE" != "Y" ]; then
        echo "❌ Cancelled"
        exit 0
    fi
    
    # Remove old aliases
    sed -i "/# Aliases for $SELECTED_SERVICE/,/^$/d" "$SHELL_CONFIG"
fi

# Add aliases to shell config
echo "$ALIASES" >> "$SHELL_CONFIG"

echo "✅ Aliases created successfully!"
echo ""
echo "📝 Added to: $SHELL_CONFIG"
echo ""
echo "Available aliases:"
echo "  ${ALIAS_NAME}-start     - Start the service"
echo "  ${ALIAS_NAME}-stop      - Stop the service"
echo "  ${ALIAS_NAME}-restart   - Restart the service"
echo "  ${ALIAS_NAME}-status    - Check service status"
echo "  ${ALIAS_NAME}-logs      - View live logs"
echo "  ${ALIAS_NAME}-enable    - Enable service on boot"
echo "  ${ALIAS_NAME}-disable   - Disable service on boot"
echo ""
echo "🔄 To use the aliases now, run:"
echo "   source $SHELL_CONFIG"
echo ""
echo "Or restart your terminal."
echo ""

# Ask if user wants to test
read -p "Do you want to test the aliases now? (y/n): " TEST_ALIASES

if [ "$TEST_ALIASES" = "y" ] || [ "$TEST_ALIASES" = "Y" ]; then
    echo ""
    echo "🧪 Testing alias: ${ALIAS_NAME}-status"
    echo ""
    
    # Source the config and run status
    source "$SHELL_CONFIG"
    eval "${ALIAS_NAME}-status"
fi

echo ""
echo "✅ Done!"
