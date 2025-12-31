#!/bin/bash

# Setup Alias for Systemctl Services
# This script helps create convenient aliases for managing systemd services

set -e

# Determine shell config file
get_shell_config() {
    if [ -n "$BASH_VERSION" ]; then
        if [ -f "$HOME/.bashrc" ]; then
            echo "$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            echo "$HOME/.bash_profile"
        fi
    elif [ -n "$ZSH_VERSION" ]; then
        echo "$HOME/.zshrc"
    else
        case "$SHELL" in
            */bash) echo "$HOME/.bashrc" ;;
            */zsh) echo "$HOME/.zshrc" ;;
            *) echo "$HOME/.bashrc" ;;
        esac
    fi
}

SHELL_CONFIG=$(get_shell_config)

echo "🔧 Setup Service Alias"
echo "================================"
echo ""
echo "What do you want to do?"
echo ""
echo "1. Create new alias"
echo "2. Check existing aliases"
echo "3. Delete alias"
echo "0. Cancel"
echo ""
read -p "Select option: " OPTION

case "$OPTION" in
    1)
        # Create new alias - continue to main script
        ;;
    2)
        # Check existing aliases
        echo ""
        echo "📋 Service aliases in $SHELL_CONFIG:"
        echo ""
        grep "# Aliases for.*\.service" "$SHELL_CONFIG" 2>/dev/null | sed 's/# Aliases for /  - /' || echo "  No aliases found"
        echo ""
        exit 0
        ;;
    3)
        # Delete alias
        echo ""
        echo "📋 Existing service aliases:"
        echo ""
        ALIAS_SERVICES=$(grep "# Aliases for.*\.service" "$SHELL_CONFIG" 2>/dev/null | sed 's/# Aliases for \(.*\) (created.*/\1/' || echo "")
        
        if [ -z "$ALIAS_SERVICES" ]; then
            echo "  No aliases found"
            exit 0
        fi
        
        mapfile -t ALIAS_ARRAY <<< "$ALIAS_SERVICES"
        for i in "${!ALIAS_ARRAY[@]}"; do
            printf "%2d. %s\n" $((i+1)) "${ALIAS_ARRAY[$i]}"
        done
        echo ""
        echo "0. Cancel"
        echo ""
        read -p "Select alias to delete: " DEL_NUM
        
        if [ "$DEL_NUM" = "0" ]; then
            echo "❌ Cancelled"
            exit 0
        fi
        
        if [[ "$DEL_NUM" =~ ^[0-9]+$ ]] && [ "$DEL_NUM" -ge 1 ] && [ "$DEL_NUM" -le "${#ALIAS_ARRAY[@]}" ]; then
            SELECTED="${ALIAS_ARRAY[$((DEL_NUM-1))]}"
            sed -i "/# Aliases for $SELECTED/,/^$/d" "$SHELL_CONFIG"
            echo "✅ Deleted aliases for: $SELECTED"
            echo ""
            echo "🔄 Run: source $SHELL_CONFIG"
        else
            echo "❌ Invalid selection"
        fi
        exit 0
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

# Continue with create new alias
echo ""
echo "📋 Scanning active services..."
echo ""

# Get list of active services
ACTIVE_SERVICES=$(systemctl list-units --type=service --state=active | grep "\.service" | awk '{print $1}' | sort)

# Filter out system services, keep only user/custom services
USER_SERVICES=()
while IFS= read -r service; do
    # Skip common system services
    if [[ ! "$service" =~ ^(getty|systemd|dbus|network|bluetooth|cups|avahi|polkit|udisks|accounts|rtkit|upower|gdm|lightdm|user@|user-runtime) ]]; then
        USER_SERVICES+=("$service")
    fi
done <<< "$ACTIVE_SERVICES"

# If no user services found, show all active services
if [ ${#USER_SERVICES[@]} -eq 0 ]; then
    echo "⚠️  No user services found. Showing all active services..."
    echo ""
    USER_SERVICES=($(systemctl list-units --type=service --state=active | grep "\.service" | awk '{print $1}' | sort))
fi

# Display active services with numbers
echo "Active Services (${#USER_SERVICES[@]} found):"
echo "-------------------"
for i in "${!USER_SERVICES[@]}"; do
    SERVICE="${USER_SERVICES[$i]}"
    printf "%2d. 🟢 %-50s [active]\n" $((i+1)) "$SERVICE"
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

# Create aliases (all use systemctl - systemd service will handle scripts)
ALIASES="
# Aliases for $SELECTED_SERVICE (created by setup_alias.sh)
alias start${ALIAS_NAME}='sudo systemctl start $SELECTED_SERVICE'
alias stop${ALIAS_NAME}='sudo systemctl stop $SELECTED_SERVICE'
alias restart${ALIAS_NAME}='sudo systemctl restart $SELECTED_SERVICE'
alias status${ALIAS_NAME}='sudo systemctl status $SELECTED_SERVICE'
alias logs${ALIAS_NAME}='sudo journalctl -u $SELECTED_SERVICE -f'
alias enable${ALIAS_NAME}='sudo systemctl enable $SELECTED_SERVICE'
alias disable${ALIAS_NAME}='sudo systemctl disable $SELECTED_SERVICE'
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
echo "  start${ALIAS_NAME}      - Start the service"
echo "  stop${ALIAS_NAME}       - Stop the service"
echo "  restart${ALIAS_NAME}    - Restart the service"
echo "  status${ALIAS_NAME}     - Check service status"
echo "  logs${ALIAS_NAME}       - View live logs"
echo "  enable${ALIAS_NAME}     - Enable service on boot"
echo "  disable${ALIAS_NAME}    - Disable service on boot"
echo ""
echo "🔄 To use the aliases now, run:"
echo "   source $SHELL_CONFIG"
echo ""
echo "Or restart your terminal."
echo ""

# Ask if user wants to test
read -p "Do you want to test the status now? (y/n): " TEST_ALIASES

if [ "$TEST_ALIASES" = "y" ] || [ "$TEST_ALIASES" = "Y" ]; then
    echo ""
    echo "🧪 Testing service status..."
    echo ""
    
    # Run systemctl directly (alias not loaded yet in current session)
    sudo systemctl status "$SELECTED_SERVICE" --no-pager -l
fi

echo ""
echo "✅ Done!"
