"""
Configuration module for the bot
All settings and constants are defined here
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# BOT CONFIGURATION
# ============================================================================

# Telegram Bot Token (Get from @BotFather)
TOKEN = os.getenv('BOT_TOKEN', '')

# User Access Control
# Empty list = allow all users
# Parse comma-separated user IDs from environment variable
_user_ids = os.getenv('ALLOWED_USER_IDS', '')
ALLOWED_USERS = [int(uid.strip()) for uid in _user_ids.split(',') if uid.strip()]

# YouTube Suggestions Feature
# Enable/disable YouTube suggestions when queue finishes
ENABLE_YOUTUBE_SUGGESTIONS = os.getenv('ENABLE_YOUTUBE_SUGGESTIONS', 'true').lower() == 'true'

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Enable debug mode from environment
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ============================================================================
# PLAYER SETTINGS
# ============================================================================

# Default volume (25, 50, 75, or 100)
DEFAULT_VOLUME = int(os.getenv('DEFAULT_VOLUME', '75'))

# MPV player options
MPV_OPTIONS = {
    'no_video': True,
    'no_terminal': True,
    'quiet': True,
    'demuxer_max_bytes': '50M',  # Limit buffer to save RAM
    'demuxer_max_back_bytes': '25M',
}

# ============================================================================
# YOUTUBE-DL OPTIONS
# ============================================================================

# YouTube Cookies Configuration
# Method 1: Use cookies file (RECOMMENDED - more reliable)
COOKIES_FILE = os.getenv('YOUTUBE_COOKIES_FILE', 'cookies.txt')

# Method 2: Extract from browser automatically (chrome, firefox, edge, safari, etc.)
# Set to empty string to disable
COOKIES_FROM_BROWSER = os.getenv('COOKIES_FROM_BROWSER', '')

# Build YTDL options
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': False,  # Allow playlists
    'extract_flat': False,  # Extract full info
    'quiet': True,
    'no_warnings': True,
    'geo_bypass': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],  # Use multiple clients for better compatibility
            'player_skip': ['webpage', 'configs'],  # Skip unnecessary requests
        }
    },
}

# Add cookies configuration (prioritize file over browser)
if COOKIES_FILE and os.path.exists(COOKIES_FILE):
    YTDL_OPTIONS['cookiefile'] = COOKIES_FILE
    # Cookies file found and will be used
elif COOKIES_FROM_BROWSER:
    YTDL_OPTIONS['cookiesfrombrowser'] = (COOKIES_FROM_BROWSER,)
    # Browser cookies will be extracted
# If neither is configured, YouTube may block requests

# ============================================================================
# UI CONFIGURATION
# ============================================================================

# Emoji mappings for UI
EMOJI = {
    'play': '▶️',
    'pause': '⏸️',
    'stop': '⏹️',
    'next': '⏭️',
    'prev': '⏮️',
    'loop': '🔁',
    'loop_active': '🔁',
    'loop_off': '🔂',
    'shuffle': '🔀',
    'shuffle_active': '🔀',
    'shuffle_off': '🔢',
    'volume': '🔊',
    'queue': '📜',
    'playlist': '📋',
    'video': '🎬',
    'music': '🎵',
    'now_playing': '🎵',
    'loading': '⏳',
    'success': '✅',
    'error': '❌',
    'info': 'ℹ️',
    'warning': '⚠️',
    'menu': '📱',
}

# Button texts
BUTTON_TEXT = {
    'play': 'Play',
    'pause': 'Pause',
    'stop': 'Stop',
    'next': 'Next',
    'prev': 'Previous',
    'loop': 'Loop',
    'shuffle': 'Shuffle',
    'volume': 'Volume',
    'queue': 'Queue',
    'back': '« Back',
}

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """
    Validate configuration settings
    Raises ValueError if configuration is invalid
    """
    errors = []
    
    # Check TOKEN
    if not TOKEN or TOKEN == '':
        errors.append("BOT_TOKEN is not set in .env file")
    
    # Check volume
    if DEFAULT_VOLUME not in [25, 50, 75, 100]:
        errors.append(f"DEFAULT_VOLUME must be 25, 50, 75, or 100 (got {DEFAULT_VOLUME})")
    
    # Report errors
    if errors:
        error_msg = "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)
    
    return True


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        format=LOG_FORMAT,
        level=LOG_LEVEL
    )
    
    # Reduce noise from other libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured")
    logger.info(f"Log level: {logging.getLevelName(LOG_LEVEL)}")
    
    return logger
