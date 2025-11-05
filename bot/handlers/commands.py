"""
Command Handlers Module
Handles all command interactions (/start, etc.)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..utils.access_control import AccessControl
from ..utils.formatters import MessageFormatter
from ..utils.keyboards import Keyboards

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command
    Shows welcome message and main menu
    """
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # Check access
    if not AccessControl.check_access(user_id):
        logger.warning(f"❌ Access denied for user @{username} (ID: {user_id})")
        await update.message.reply_text(
            MessageFormatter.error_message("You don't have access to this bot.")
        )
        return
    
    # Set owner if not set
    is_owner = AccessControl.is_owner(user_id)
    
    logger.info("=" * 60)
    logger.info(f"🎵 /start command from @{username} (ID: {user_id})")
    logger.info(f"   Owner: {'Yes ⭐' if is_owner else 'No'}")
    logger.info("=" * 60)
    
    # Send welcome message
    await update.message.reply_text(
        MessageFormatter.welcome_message(),
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )
    
    logger.info(f"✅ Welcome message sent to @{username}")
