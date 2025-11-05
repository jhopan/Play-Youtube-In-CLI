#!/usr/bin/env python3
"""
YouTube Music Telegram Bot - Main Entry Point
Modular architecture for better maintainability

Author: JHOSUA
Version: 1.0.0
Date: 2024-11-05
"""

import logging
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
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
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
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("⏸️ Bot stopped by user (Ctrl+C)")
        logger.info("=" * 60)
    finally:
        # Cleanup
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
