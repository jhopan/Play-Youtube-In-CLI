"""
Playback Management Module
Handles all playback logic (play, next, previous, auto-next)
"""

import asyncio
import random
import logging
from typing import Optional

from telegram.ext import Application

from .player_state import player
from .mpv_player import MPVPlayer
from ..config import EMOJI

logger = logging.getLogger(__name__)


class PlaybackManager:
    """Manages music playback operations"""
    
    @staticmethod
    async def play_current_song(application: Application) -> bool:
        """
        Play the current song in the playlist
        
        Args:
            application: Telegram application instance
        
        Returns:
            True if successful, False otherwise
        """
        if not player.playlist:
            logger.warning("⚠️ No songs in playlist")
            return False
        
        if player.current_index >= len(player.playlist):
            player.current_index = 0
        
        current_song = player.current_song
        if not current_song:
            return False
        
        try:
            # Stop any existing playback
            MPVPlayer.stop()
            
            logger.info(f"🎵 Now playing: '{current_song.title}' [{player.current_index + 1}/{len(player.playlist)}]")
            
            # Start new playback
            player.mpv_process = MPVPlayer.start(current_song.url, player.volume)
            player.is_playing = True
            player.is_paused = False
            
            # Notify user
            if player.owner_id:
                try:
                    await application.bot.send_message(
                        chat_id=player.owner_id,
                        text=(
                            f"{EMOJI['now_playing']} <b>Now Playing:</b>\n"
                            f"{current_song.title}\n\n"
                            f"📊 {player.current_index + 1}/{len(player.playlist)}"
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"❌ Error sending notification: {e}")
            
            # Wait for playback to finish
            process_result = await asyncio.get_event_loop().run_in_executor(
                None, player.mpv_process.wait
            )
            
            # Add small delay to prevent rapid restarts
            await asyncio.sleep(1)
            
            # Check if playback finished naturally (not stopped manually)
            if player.is_playing and process_result == 0:
                logger.info(f"✅ Song finished: '{current_song.title}'")
                await PlaybackManager.handle_song_finished(application)
            elif process_result != 0:
                logger.warning(f"⚠️ MPV exited with code {process_result}")
                player.is_playing = False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error playing song: {e}")
            player.is_playing = False
            return False
    
    @staticmethod
    async def handle_song_finished(application: Application):
        """
        Handle when a song finishes playing
        Decides whether to loop, go to next, or get YouTube suggestions
        Shows auto-next dialog with countdown
        
        Args:
            application: Telegram application instance
        """
        # Prevent rapid consecutive calls
        if not player.is_playing:
            return
            
        if player.loop_enabled:
            # Replay the same song
            logger.info("🔁 Loop enabled - replaying current song")
            await asyncio.sleep(0.5)  # Small delay before replay
            await PlaybackManager.play_current_song(application)
        else:
            # Check if there's a next song in queue
            next_index = player.current_index + 1
            
            if next_index < len(player.playlist):
                # Has next song in queue - show normal auto-next dialog
                logger.info("⏱️ Showing auto-next dialog (5 second countdown)")
                await PlaybackManager.show_auto_next_dialog(application)
            else:
                # Queue finished - get YouTube suggestions
                logger.info("📺 Queue finished - fetching YouTube suggestions")
                await PlaybackManager.show_suggestions_dialog(application)
    
    @staticmethod
    async def show_auto_next_dialog(application: Application, countdown_seconds: int = 5):
        """
        Show auto-next dialog with countdown
        
        Args:
            application: Telegram application instance
            countdown_seconds: Seconds before auto-playing next song
        """
        from ..utils.keyboards import Keyboards
        
        if not player.owner_id or not player.playlist:
            return
        
        # Check if there's a next song
        next_index = player.current_index + 1
        if next_index >= len(player.playlist):
            next_index = 0
        
        next_song = player.playlist[next_index]
        
        logger.info(f"📢 Auto-next dialog: Next song is '{next_song.title}'")
        
        try:
            # Send initial message with countdown
            message = await application.bot.send_message(
                chat_id=player.owner_id,
                text=(
                    f"{EMOJI['info']} <b>Song Finished!</b>\n\n"
                    f"▶️ <b>Next:</b> {next_song.title}\n\n"
                    f"⏱️ Auto-playing in {countdown_seconds} seconds...\n"
                    f"Press 'Stop' to cancel."
                ),
                reply_markup=Keyboards.auto_next_dialog(),
                parse_mode="HTML"
            )
            
            # Create countdown task
            async def countdown_task():
                for remaining in range(countdown_seconds - 1, 0, -1):
                    await asyncio.sleep(1)
                    try:
                        await message.edit_text(
                            (
                                f"{EMOJI['info']} <b>Song Finished!</b>\n\n"
                                f"▶️ <b>Next:</b> {next_song.title}\n\n"
                                f"⏱️ Auto-playing in {remaining} seconds...\n"
                                f"Press 'Stop' to cancel."
                            ),
                            reply_markup=Keyboards.auto_next_dialog(),
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.error(f"❌ Error updating countdown: {e}")
                        break
                
                # Final countdown - play next
                await asyncio.sleep(1)
                if player.is_playing:  # Check if not manually stopped
                    logger.info("⏩ Auto-next countdown finished - playing next song")
                    await PlaybackManager.play_next(application)
            
            # Store task in bot_data so it can be cancelled
            task = asyncio.create_task(countdown_task())
            application.bot_data['auto_next_task'] = task
            
        except Exception as e:
            logger.error(f"❌ Error showing auto-next dialog: {e}")
            # Fallback - just play next
            await asyncio.sleep(1)
            await PlaybackManager.play_next(application)
    
    @staticmethod
    async def play_next(application: Application) -> bool:
        """
        Play the next song in the playlist
        
        Args:
            application: Telegram application instance
        
        Returns:
            True if successful, False otherwise
        """
        if not player.playlist:
            return False
        
        if player.shuffle_enabled:
            # Random song
            player.current_index = random.randint(0, len(player.playlist) - 1)
            logger.info(f"🔀 Shuffle mode: Selected random song at index {player.current_index}")
        else:
            # Next song
            player.current_index += 1
            if player.current_index >= len(player.playlist):
                player.current_index = 0
                logger.info("Reached end of playlist, starting from beginning")
        
        return await PlaybackManager.play_current_song(application)
    
    @staticmethod
    async def play_previous(application: Application) -> bool:
        """
        Play the previous song in the playlist
        
        Args:
            application: Telegram application instance
        
        Returns:
            True if successful, False otherwise
        """
        if not player.playlist:
            return False
        
        if player.shuffle_enabled:
            # Random song (for shuffle mode)
            player.current_index = random.randint(0, len(player.playlist) - 1)
            logger.info(f"Shuffle: Selected random song at index {player.current_index}")
        else:
            # Previous song
            player.current_index -= 1
            if player.current_index < 0:
                player.current_index = len(player.playlist) - 1
                logger.info("Reached start of playlist, jumping to end")
        
        return await PlaybackManager.play_current_song(application)
    
    @staticmethod
    def toggle_pause() -> bool:
        """
        Toggle pause/resume
        
        Returns:
            True if paused, False if resumed/failed
        """
        if player.is_paused:
            return not MPVPlayer.resume()
        else:
            return MPVPlayer.pause()
    
    @staticmethod
    def stop():
        """Stop playback completely"""
        MPVPlayer.stop()
        player.is_playing = False
        player.is_paused = False
        logger.info("Playback stopped")
    
    @staticmethod
    def toggle_loop() -> bool:
        """
        Toggle loop mode
        
        Returns:
            New loop state
        """
        player.loop_enabled = not player.loop_enabled
        logger.info(f"Loop mode: {player.loop_enabled}")
        return player.loop_enabled
    
    @staticmethod
    def toggle_shuffle() -> bool:
        """
        Toggle shuffle mode
        
        Returns:
            New shuffle state
        """
        player.shuffle_enabled = not player.shuffle_enabled
        logger.info(f"Shuffle mode: {player.shuffle_enabled}")
        return player.shuffle_enabled
    
    @staticmethod
    def set_volume(volume: int) -> bool:
        """
        Set volume level
        
        Args:
            volume: Volume level (25, 50, 75, or 100)
        
        Returns:
            True if successful
        """
        if volume not in [25, 50, 75, 100]:
            logger.warning(f"Invalid volume: {volume}")
            return False
        
        player.volume = volume
        logger.info(f"Volume set to {volume}%")
        
        # If MPV is running, update volume via IPC
        if player.is_playing and MPVPlayer.is_running():
            success = MPVPlayer.set_volume(volume)
            if success:
                logger.info(f"Updated MPV volume to {volume}% via IPC")
            else:
                logger.warning("Failed to update MPV volume via IPC, will apply on next song")
        
        return True
    
    @staticmethod
    async def show_suggestions_dialog(application: Application):
        """
        Show YouTube suggestions dialog when queue is empty
        Gets related videos and asks user if they want to continue
        
        Args:
            application: Telegram application instance
        """
        from ..utils.keyboards import Keyboards
        from .youtube import YouTubeExtractor
        
        if not player.owner_id or not player.current_song:
            return
        
        try:
            # Get related videos from YouTube
            logger.info(f"🔍 Fetching suggestions for: {player.current_song.title}")
            suggestions = YouTubeExtractor.get_related_videos(
                player.current_song.url,
                count=3  # Get top 3 suggestions
            )
            
            if not suggestions:
                # No suggestions found - stop playback
                logger.warning("⚠️ No suggestions found - stopping playback")
                player.is_playing = False
                await application.bot.send_message(
                    chat_id=player.owner_id,
                    text=(
                        f"🎵 <b>Queue Finished!</b>\n\n"
                        f"No more songs to play.\n"
                        f"Use Menu button to load more music! 🎶"
                    ),
                    parse_mode="HTML"
                )
                return
            
            # Show first suggestion with options
            next_song = suggestions[0]
            logger.info(f"📺 Suggesting: {next_song.title}")
            
            # Store suggestions in bot_data for callback
            application.bot_data['suggestions'] = suggestions
            application.bot_data['current_suggestion_index'] = 0
            
            # Send suggestion message
            await application.bot.send_message(
                chat_id=player.owner_id,
                text=(
                    f"🎵 <b>Queue Finished!</b>\n\n"
                    f"🎬 <b>Suggested Video:</b>\n"
                    f"{next_song.title}\n\n"
                    f"⏱️ Continue playing?\n"
                    f"Auto-play in 10 seconds..."
                ),
                reply_markup=Keyboards.suggestion_dialog(),
                parse_mode="HTML"
            )
            
            # Create auto-play countdown task
            async def countdown_task():
                for remaining in range(9, 0, -1):
                    await asyncio.sleep(1)
                
                # Final countdown - auto-play suggestion
                await asyncio.sleep(1)
                if player.is_playing:  # Check if not manually stopped
                    logger.info("⏩ Auto-playing YouTube suggestion")
                    # Add suggestion to playlist and play
                    player.playlist.append(next_song)
                    player.current_index = len(player.playlist) - 1
                    await PlaybackManager.play_current_song(application)
            
            # Store task in bot_data so it can be cancelled
            task = asyncio.create_task(countdown_task())
            application.bot_data['suggestion_task'] = task
            
        except Exception as e:
            logger.error(f"❌ Error showing suggestions: {e}")
            # Fallback - just stop
            player.is_playing = False
            if player.owner_id:
                await application.bot.send_message(
                    chat_id=player.owner_id,
                    text="🎵 Queue finished! Use Menu to load more music. 🎶",
                    parse_mode="HTML"
                )
