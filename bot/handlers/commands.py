"""
Command Handlers Module
Handles all command interactions (/start, etc.)
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
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
    
    # Create persistent menu button
    menu_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("🎵 Menu")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    from ..core.player_state import player
    
    # Send welcome message
    await update.message.reply_text(
        MessageFormatter.welcome_message(),
        reply_markup=menu_keyboard,
        parse_mode="HTML"
    )
    
    # Send inline menu buttons and save message_id
    msg = await update.message.reply_text(
        "Select an action:",
        reply_markup=Keyboards.main_menu(),
        parse_mode="HTML"
    )
    player.control_menu_message_id = msg.message_id
    
    logger.info(f"✅ Welcome message sent to @{username}")
