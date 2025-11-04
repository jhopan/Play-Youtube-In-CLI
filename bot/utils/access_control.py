"""
Access Control Utilities
User authentication and authorization
"""

import logging
from typing import Optional

from ..config import ALLOWED_USERS
from ..core.player_state import player

logger = logging.getLogger(__name__)


class AccessControl:
    """Handle user access control"""
    
    @staticmethod
    def check_access(user_id: int) -> bool:
        """
        Check if user has access to the bot
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            True if user has access
        """
        # If ALLOWED_USERS is empty, allow all
        if not ALLOWED_USERS:
            return True
        
        has_access = user_id in ALLOWED_USERS
        
        if not has_access:
            logger.warning(f"Access denied for user {user_id}")
        
        return has_access
    
    @staticmethod
    def is_owner(user_id: int) -> bool:
        """
        Check if user is the current owner
        Sets ownership on first interaction
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            True if user is the owner
        """
        # Set owner if not set
        if player.owner_id is None:
            player.owner_id = user_id
            logger.info(f"Owner set to user {user_id}")
            return True
        
        is_owner = user_id == player.owner_id
        
        if not is_owner:
            logger.warning(f"User {user_id} is not the owner (owner: {player.owner_id})")
        
        return is_owner
    
    @staticmethod
    def reset_owner():
        """Reset owner (useful for testing or admin override)"""
        old_owner = player.owner_id
        player.owner_id = None
        logger.info(f"Owner reset (was: {old_owner})")
