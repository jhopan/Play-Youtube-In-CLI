#!/bin/bash

# Setup Alias for YT Music Bot Service
# Creates convenient shortcuts for managing the bot

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

# Default service configuration for YT Music Bot
SERVICE_NAME="ytmusic-bot"
SELECTED_SERVICE="${SERVICE_NAME}.service"

echo "🔧 YT Music Bot - Setup Alias"
echo "================================"
echo ""
echo "What do you want to do?"
echo ""
echo "1. Create/Update aliases"
echo "2. Check existing aliases"
echo "3. Delete aliases"
echo "0. Cancel"
echo ""
read -p "Select option: " OPTION

case "$OPTION" in
    1)
        # Create/Update aliases - continue to main script
        ;;
    2)
        # Check existing aliases
        echo ""
        echo "📋 YT Music Bot aliases in $SHELL_CONFIG:"
        echo ""
        if grep -q "# YT Music Bot aliases" "$SHELL_CONFIG" 2>/dev/null; then
            grep "^alias.*ytmusic" "$SHELL_CONFIG" | sed 's/alias /  /' || echo "  No aliases found"
        else
            echo "  No aliases found"
            echo ""
            echo "💡 Run option 1 to create aliases"
        fi
        echo ""
        exit 0
        ;;
    3)
        # Delete aliases
        echo ""
        if grep -q "# YT Music Bot aliases" "$SHELL_CONFIG" 2>/dev/null; then
            sed -i "/# YT Music Bot aliases/,/^$/d" "$SHELL_CONFIG"
            echo "✅ YT Music Bot aliases deleted"
            echo ""
            echo "🔄 Run: source $SHELL_CONFIG"
        else
            echo "⚠️  No YT Music Bot aliases found"
        fi
        echo ""
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

# Continue with create/update aliases
echo ""
echo "🎵 Setting up aliases for YT Music Bot"
echo ""

# Check if service exists
if ! systemctl list-unit-files | grep -q "^${SELECTED_SERVICE}"; then
    echo "⚠️  Service ${SELECTED_SERVICE} not found"
    echo ""
    read -p "Do you want to create the service first? (y/n): " CREATE_SERVICE
    
    if [ "$CREATE_SERVICE" = "y" ] || [ "$CREATE_SERVICE" = "Y" ]; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        "$SCRIPT_DIR/setup_service.sh"
        exit 0
    else
        echo "❌ Cancelled - Service must exist before creating aliases"
        exit 1
    fi
fi

# Ask for alias prefix
read -p "Enter alias prefix (default: ytmusic): " ALIAS_PREFIX

if [ -z "$ALIAS_PREFIX" ]; then
    ALIAS_PREFIX="ytmusic"
fi

# Validate alias prefix
if ! [[ "$ALIAS_PREFIX" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "❌ Invalid prefix. Use only letters, numbers, underscore, and hyphen."
    exit 1
fi

echo ""
echo "📝 Creating aliases for: $ALIAS_PREFIX"
echo ""

# Create aliases
ALIASES="
# YT Music Bot aliases (created by setup_alias.sh)
alias start${ALIAS_PREFIX}='sudo systemctl start $SELECTED_SERVICE'
alias stop${ALIAS_PREFIX}='sudo systemctl stop $SELECTED_SERVICE'
alias restart${ALIAS_PREFIX}='sudo systemctl restart $SELECTED_SERVICE'
alias status${ALIAS_PREFIX}='sudo systemctl status $SELECTED_SERVICE'
alias logs${ALIAS_PREFIX}='sudo journalctl -u $SELECTED_SERVICE -f'
alias enable${ALIAS_PREFIX}='sudo systemctl enable $SELECTED_SERVICE'
alias disable${ALIAS_PREFIX}='sudo systemctl disable $SELECTED_SERVICE'
"

# Check if aliases already exist
if grep -q "# YT Music Bot aliases" "$SHELL_CONFIG" 2>/dev/null; then
    echo "⚠️  YT Music Bot aliases already exist in $SHELL_CONFIG"
    read -p "Do you want to replace them? (y/n): " REPLACE
    if [ "$REPLACE" != "y" ] && [ "$REPLACE" != "Y" ]; then
        echo "❌ Cancelled"
        exit 0
    fi
    
    # Remove old aliases
    sed -i "/# YT Music Bot aliases/,/^$/d" "$SHELL_CONFIG"
fi

# Add aliases to shell config
echo "$ALIASES" >> "$SHELL_CONFIG"

echo "✅ Aliases created successfully!"
echo ""
echo "📝 Added to: $SHELL_CONFIG"
echo ""
echo "Available aliases:"
echo "  start${ALIAS_PREFIX}      - Start the bot"
echo "  stop${ALIAS_PREFIX}       - Stop the bot"
echo "  restart${ALIAS_PREFIX}    - Restart the bot"
echo "  status${ALIAS_PREFIX}     - Check bot status"
echo "  logs${ALIAS_PREFIX}       - View live logs"
echo "  enable${ALIAS_PREFIX}     - Enable bot on boot"
echo "  disable${ALIAS_PREFIX}    - Disable bot on boot"
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
