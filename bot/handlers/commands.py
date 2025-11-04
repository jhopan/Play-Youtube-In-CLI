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
    user_id = update.effective_user.id
    
    # Check access
    if not AccessControl.check_access(user_id):
        await update.message.reply_text(
            MessageFormatter.error_message("You don't have access to this bot.")
        )
        return
    
    # Set owner if not set
    AccessControl.is_owner(user_id)
    
    # Send welcome message
    await update.message.reply_text(
        MessageFormatter.welcome_message(),
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )
    
    logger.info(f"User {user_id} started the bot")
