#!/usr/bin/env python3
"""
YouTube Music Telegram Bot - Main Entry Point
Modular architecture for better maintainability

Author: JHOSUA
Version: 1.0.0
Date: 2024-11-05
"""

import logging
import signal
import sys
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from bot.config import TOKEN, LOG_LEVEL, LOG_FORMAT, validate_config
from bot.handlers import start_command, button_callback, handle_url_message
from bot.core import player, MPVPlayer

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    format=LOG_FORMAT,
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

# Disable noisy third-party loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# ============================================================================
# SIGNAL HANDLERS
# ============================================================================

_app_instance = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    sig_name = signal.Signals(signum).name
    logger.info(f"📨 Received signal: {sig_name}")
    
    # Don't exit immediately, let the application handle shutdown
    if _app_instance:
        logger.info("🛑 Initiating graceful shutdown...")
    else:
        logger.warning("⚠️ No application instance to shut down")

# ============================================================================
# ERROR HANDLER
# ============================================================================

async def error_handler(update: Update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Start the bot"""
    global _app_instance
    
    try:
        # Validate configuration
        validate_config()
        logger.info("✅ Configuration validated successfully")
        
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}\n")
        return
    
    logger.info("=" * 60)
    logger.info("🎵 YouTube Music Telegram Bot - Starting...")
    logger.info("=" * 60)
    logger.info(f"🔑 Token configured: {'Yes' if TOKEN != 'YOUR_BOT_TOKEN_HERE' else 'No'}")
    logger.info(f"📝 Log level: {logging.getLevelName(LOG_LEVEL)}")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    logger.info("✓ Signal handlers registered (SIGTERM, SIGINT)")
    
    # Create application with network error handling
    application = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .get_updates_connect_timeout(30)
        .get_updates_read_timeout(30)
        .get_updates_pool_timeout(30)
        .build()
    )
    _app_instance = application
    
    # Add handlers
    logger.info("📋 Registering handlers...")
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    logger.info("✓ Command handlers registered")
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(button_callback))
    logger.info("✓ Callback handlers registered")
    
    # Message handlers
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_url_message
    ))
    logger.info("✓ Message handlers registered")
    
    # Error handler
    application.add_error_handler(error_handler)
    logger.info("✓ Error handler registered")
    
    # Start bot
    logger.info("=" * 60)
    logger.info("🚀 Bot is now running! Press Ctrl+C to stop.")
    logger.info("=" * 60)
    
    # Infinite retry loop for network resilience
    while True:
        try:
            # Run bot with proper signal handling and network error recovery
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,  # Ignore old messages on startup
                close_loop=False  # Don't close event loop on error
            )
            # If we get here, it means clean shutdown
            break
            
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("⏸️ Bot stopped by user (Ctrl+C)")
            logger.info("=" * 60)
            break
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's a network error
            if any(keyword in error_msg for keyword in [
                'connection', 'network', 'timeout', 'unreachable',
                'refused', 'reset', 'broken pipe', 'temporarily unavailable'
            ]):
                logger.warning(f"⚠️ Network error: {e}")
                logger.info("🔄 Waiting 10 seconds before reconnecting...")
                import time
                time.sleep(10)
                logger.info("🔌 Attempting to reconnect...")
                continue  # Retry connection
            else:
                # Unknown error, log and retry anyway
                logger.error(f"❌ Unexpected error: {e}", exc_info=True)
                logger.info("🔄 Waiting 15 seconds before restarting...")
                import time
                time.sleep(15)
                logger.info("🔌 Attempting to restart...")
                continue  # Retry anyway
    
    # Cleanup (only if clean exit)
    logger.info("🧹 Cleaning up...")
    MPVPlayer.stop()
    logger.info("✅ Cleanup complete. Goodbye! 👋")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal Error: {e}\n")
        MPVPlayer.stop()
