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
            
            # Check sleep timer before starting new song
            if player.check_sleep_timer():
                logger.info("⏲️ Sleep timer expired, stopping playback")
                player.is_playing = False
                if player.owner_id:
                    try:
                        await application.bot.send_message(
                            chat_id=player.owner_id,
                            text=f"{EMOJI['sleep']} Sleep timer expired. Playback stopped.",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.error(f"Error sending sleep timer notification: {e}")
                return False
            
            logger.info(f"🎵 Now playing: '{current_song.title}' [{player.current_index + 1}/{len(player.playlist)}]")
            
            # Get fresh URL from yt-dlp (prevents expiration issues)
            from .youtube import YouTubeExtractor
            try:
                logger.debug(f"🔄 Refreshing URL for: {current_song.url}")
                fresh_song = YouTubeExtractor.get_video_info(
                    current_song.url,
                    preferred_resolution=player.preferred_resolution
                )
                current_song.url = fresh_song.url
                current_song.audio_quality = fresh_song.audio_quality
                logger.debug(f"✅ URL refreshed successfully ({player.preferred_resolution})")
            except Exception as url_error:
                logger.warning(f"⚠️ Could not refresh URL with {player.preferred_resolution}, using cached: {url_error}")
                
                # Try fallback to audio only if enabled and not already audio
                if player.resolution_fallback and player.preferred_resolution != "audio":
                    try:
                        logger.info(f"🔄 Trying fallback to audio only...")
                        fresh_song = YouTubeExtractor.get_video_info(current_song.url, preferred_resolution="audio")
                        current_song.url = fresh_song.url
                        current_song.audio_quality = fresh_song.audio_quality
                        logger.info(f"✅ Fallback successful")
                    except Exception as fallback_error:
                        logger.warning(f"⚠️ Fallback also failed: {fallback_error}")
            
            # Start new playback
            player.mpv_process = MPVPlayer.start(current_song.url, player.volume)
            player.is_playing = True
            player.is_paused = False
            
            # Track in history and analytics
            try:
                from .storage import Storage
                storage = Storage()
                storage.add_to_history(current_song)
                storage.update_analytics(current_song)
                logger.debug(f"📊 Added to history and analytics: {current_song.title}")
            except Exception as track_error:
                logger.warning(f"⚠️ Could not track song: {track_error}")
            
            # Notify user
            if player.owner_id:
                try:
                    # Create visual progress bar
                    total = len(player.playlist)
                    current = player.current_index + 1
                    progress = "▰" * current + "▱" * (total - current) if total <= 20 else f"{current}/{total}"
                    
                    # Format duration (convert seconds to MM:SS)
                    duration_str = current_song.duration
                    try:
                        duration_sec = int(current_song.duration) if current_song.duration.isdigit() else 0
                        if duration_sec > 0:
                            minutes = duration_sec // 60
                            seconds = duration_sec % 60
                            duration_str = f"{minutes}:{seconds:02d}"
                    except:
                        duration_str = current_song.duration
                    
                    now_playing_text = (
                        f"{EMOJI['now_playing']} <b>Now Playing:</b>\n\n"
                        f"🎵 <b>{current_song.title}</b>\n"
                        f"⏱️ Duration: {duration_str}\n"
                        f"🎧 Quality: {current_song.audio_quality}\n\n"
                        f"📊 Position: {current}/{total}\n"
                        f"▰▱ {progress}"
                    )
                    
                    # Edit existing message or send new one
                    if player.now_playing_message_id:
                        try:
                            await application.bot.edit_message_text(
                                chat_id=player.owner_id,
                                message_id=player.now_playing_message_id,
                                text=now_playing_text,
                                parse_mode="HTML"
                            )
                        except Exception as edit_error:
                            logger.warning(f"Could not edit message, sending new: {edit_error}")
                            msg = await application.bot.send_message(
                                chat_id=player.owner_id,
                                text=now_playing_text,
                                parse_mode="HTML"
                            )
                            player.now_playing_message_id = msg.message_id
                    else:
                        msg = await application.bot.send_message(
                            chat_id=player.owner_id,
                            text=now_playing_text,
                            parse_mode="HTML"
                        )
                        player.now_playing_message_id = msg.message_id
                        
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
                
                # Try to recover from MPV error
                if process_result == 2 and player.is_playing:
                    logger.info(f"🔄 Attempting recovery from MPV error code 2...")
                    await asyncio.sleep(2)  # Wait before retry
                    
                    # Retry playback once
                    try:
                        logger.info(f"🔄 Retrying playback: '{current_song.title}'")
                        await PlaybackManager.play_current_song(application)
                    except Exception as retry_error:
                        logger.error(f"❌ Retry failed: {retry_error}")
                        player.is_playing = False
                        
                        # Edit now playing message to show error
                        if player.owner_id and player.now_playing_message_id:
                            try:
                                await application.bot.edit_message_text(
                                    chat_id=player.owner_id,
                                    message_id=player.now_playing_message_id,
                                    text=f"❌ <b>Playback Error</b>\n\nCould not play: {current_song.title}\n\nSkipping to next song...",
                                    parse_mode="HTML"
                                )
                            except:
                                pass
                        
                        # Skip to next song
                        await PlaybackManager.handle_song_finished(application)
                else:
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
        Auto-plays next song immediately
        Shows YouTube suggestions if enabled, otherwise loops playlist
        
        Args:
            application: Telegram application instance
        """
        from ..config import ENABLE_YOUTUBE_SUGGESTIONS
        
        # Prevent rapid consecutive calls
        if not player.is_playing:
            return
            
        if player.loop_enabled and player.loop_mode == 'song':
            # Replay the same song
            logger.info("🔁 Loop enabled (song mode) - replaying current song")
            await asyncio.sleep(0.5)
            await PlaybackManager.play_current_song(application)
        else:
            # Check if there's a next song in queue
            next_index = player.current_index + 1
            
            if next_index < len(player.playlist):
                # Has next song - auto-play immediately
                logger.info(f"⏩ Auto-playing next song ({next_index + 1}/{len(player.playlist)})")
                await asyncio.sleep(0.5)
                await PlaybackManager.play_next(application)
            else:
                # Queue finished - check YouTube suggestions setting
                use_suggestions = ENABLE_YOUTUBE_SUGGESTIONS and player.yt_suggestions_enabled
                
                if use_suggestions:
                    # Show YouTube suggestions
                    logger.info("📺 Queue finished - fetching YouTube suggestions")
                    await PlaybackManager.show_suggestions_dialog(application)
                else:
                    # Ask user if want to loop playlist
                    logger.info("🔄 Queue finished - asking user")
                    await PlaybackManager.show_loop_confirmation(application)
        """
        Handle when a song finishes playing
        Auto-plays next song immediately (no countdown dialog)
        Auto-loops playlist when queue finishes
        Optionally shows YouTube suggestions if enabled
        
        Args:
            application: Telegram application instance
        """
        from ..config import ENABLE_YOUTUBE_SUGGESTIONS
        
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
                # Has next song in queue - auto-play immediately
                logger.info(f"⏩ Auto-playing next song ({next_index + 1}/{len(player.playlist)})")
                await asyncio.sleep(0.5)  # Small delay for smooth transition
                await PlaybackManager.play_next(application)
            else:
                # Queue finished - check loop mode
                if player.loop_enabled and player.loop_mode == 'queue':
                    # Loop queue - restart from beginning
                    logger.info("🔁 Loop enabled (queue mode) - restarting playlist from beginning")
                    player.current_index = 0
                    
                    logger.info("🔁 Loop enabled (queue mode) - restarting playlist from beginning")
                    await asyncio.sleep(1)
                    await PlaybackManager.play_current_song(application)
                else:
                    # No loop - stop playback
                    logger.info("⏹️ Queue finished - stopping playback")
                    player.is_playing = False
                    
                    # Edit now playing message to show finished status
                    if player.owner_id and player.now_playing_message_id:
                        try:
                            await application.bot.edit_message_text(
                                chat_id=player.owner_id,
                                message_id=player.now_playing_message_id,
                                text=(
                                    f"✅ <b>Playlist Finished!</b>\n\n"
                                    f"📀 Played all {len(player.playlist)} songs\n\n"
                                    f"Use Menu to load more music! 🎶"
                                ),
                                parse_mode="HTML"
                            )
                        except Exception as e:
                            logger.warning(f"Could not edit message: {e}")

                
                # Optional: Show YouTube suggestions if enabled
                if ENABLE_YOUTUBE_SUGGESTIONS:
                    logger.info("📺 YouTube suggestions enabled - will show after this loop")
                    # Note: Suggestions disabled by default for stability
    
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
    async def show_loop_confirmation(application: Application, countdown_seconds: int = 10):
        """
        Show loop confirmation dialog when playlist finishes
        Ask user if they want to replay playlist
        
        Args:
            application: Telegram application instance
            countdown_seconds: Seconds before auto-looping (default 10)
        """
        from ..utils.keyboards import Keyboards
        
        if not player.owner_id or not player.playlist:
            return
        
        try:
            # Send message with countdown
            message_text = (
                f"🎵 <b>Playlist Finished!</b>\n\n"
                f"📀 Total songs: {len(player.playlist)}\n"
                f"🔄 Replay from beginning?\n\n"
                f"⏱️ Auto-replay in <b>{countdown_seconds}</b> seconds..."
            )
            
            message = await application.bot.send_message(
                chat_id=player.owner_id,
                text=message_text,
                reply_markup=Keyboards.loop_confirmation_dialog(),
                parse_mode="HTML"
            )
            
            logger.info(f"📢 Loop confirmation dialog shown ({countdown_seconds}s countdown)")
            
            # Create countdown task
            async def countdown_task():
                for remaining in range(countdown_seconds - 1, 0, -1):
                    await asyncio.sleep(1)
                    try:
                        new_text = message_text.replace(str(countdown_seconds), str(remaining))
                        await message.edit_text(
                            new_text,
                            reply_markup=Keyboards.loop_confirmation_dialog(),
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                
                # Final countdown - loop playlist
                await asyncio.sleep(1)
                if player.is_playing:  # Check if not stopped
                    logger.info("⏩ Auto-loop countdown finished - restarting playlist")
                    player.current_index = 0
                    await PlaybackManager.play_current_song(application)
                    
                    # Clean up
                    application.bot_data.pop('loop_task', None)
            
            # Store task so it can be cancelled
            task = asyncio.create_task(countdown_task())
            application.bot_data['loop_task'] = task
            
        except Exception as e:
            logger.error(f"❌ Error showing loop confirmation: {e}")
            # Fallback - just loop
            await asyncio.sleep(1)
            player.current_index = 0
            await PlaybackManager.play_current_song(application)
    
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
        from ..config import ENABLE_YOUTUBE_SUGGESTIONS
        
        if not ENABLE_YOUTUBE_SUGGESTIONS:
            logger.info("⚠️ YouTube suggestions disabled - use auto-loop instead")
            return
        
        if not player.owner_id:
            logger.warning("⚠️ Cannot show suggestions - no owner")
            return
        
        # Get last played song for suggestions
        if not player.playlist:
            logger.warning("⚠️ No playlist available for suggestions")
            return
        
        # Use last song in playlist for suggestions
        last_song = player.playlist[-1]
        logger.info(f"🎬 Using last song for suggestions: {last_song.title}")
        
        # Send "Searching..." notification to user
        search_message = None
        try:
            search_message = await application.bot.send_message(
                chat_id=player.owner_id,
                text=(
                    f"🔍 <b>Searching for suggestions...</b>\n\n"
                    f"📺 Finding related videos on YouTube...\n"
                    f"⏱️ Please wait up to 30 seconds..."
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error sending search notification: {e}")
        
        try:
            # Get related videos from YouTube with timeout
            logger.info(f"🔍 Fetching suggestions for: {last_song.title}")
            
            # Run in executor with timeout to prevent blocking
            import concurrent.futures
            suggestions = []
            
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    logger.info("🔄 Submitting fetch task to executor...")
                    future = executor.submit(
                        YouTubeExtractor.get_related_videos,
                        last_song.url,
                        3  # Get top 3 suggestions
                    )
                    
                    logger.info("⏱️ Waiting for results (timeout: 30s)...")
                    # Wait max 30 seconds for suggestions
                    suggestions = future.result(timeout=30)
                    logger.info(f"✅ Received {len(suggestions)} suggestions")
                    
            except concurrent.futures.TimeoutError:
                logger.error("⏱️ Timeout fetching suggestions (30s) - skipping")
                suggestions = []
            except Exception as e:
                logger.error(f"❌ Error in suggestion fetch: {e}")
                import traceback
                logger.error(traceback.format_exc())
                suggestions = []
            
            # Delete "Searching..." message
            if search_message:
                try:
                    await search_message.delete()
                except:
                    pass
            
            if not suggestions:
                # No suggestions found - stop playback
                logger.warning("⚠️ No suggestions found - stopping playback")
                player.is_playing = False
                if player.owner_id:
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
            application.bot_data['suggestion_index'] = 0
            
            # Send suggestion message with countdown
            message_text = (
                f"🎵 <b>Queue Finished!</b>\n\n"
                f"📺 <b>Suggested Video:</b>\n"
                f"🎵 {next_song.title}\n\n"
                f"⏱️ Auto-play in <b>10</b> seconds..."
            )
            
            message = await application.bot.send_message(
                chat_id=player.owner_id,
                text=message_text,
                reply_markup=Keyboards.suggestion_dialog(),
                parse_mode="HTML"
            )
            logger.info("✅ Suggestion message sent successfully")
            
            # Create auto-play countdown task
            async def countdown_task():
                for remaining in range(9, 0, -1):
                    await asyncio.sleep(1)
                    try:
                        new_text = message_text.replace("10", str(remaining))
                        await message.edit_text(
                            new_text,
                            reply_markup=Keyboards.suggestion_dialog(),
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                
                # Final countdown - auto-play suggestion
                await asyncio.sleep(1)
                if player.is_playing:  # Check if not manually stopped
                    logger.info("⏩ Auto-playing YouTube suggestion")
                    # Add suggestion to playlist and play
                    player.add_song(next_song)
                    await PlaybackManager.play_current_song(application)
                    
                    # Clean up
                    application.bot_data.pop('suggestions', None)
                    application.bot_data.pop('suggestion_index', None)
                    application.bot_data.pop('suggestion_task', None)
            
            # Store task in bot_data so it can be cancelled
            task = asyncio.create_task(countdown_task())
            application.bot_data['suggestion_task'] = task
            logger.info("✅ Countdown task started")
            
        except Exception as e:
            logger.error(f"❌ CRITICAL Error showing suggestions: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Fallback - just stop
            player.is_playing = False
            if player.owner_id:
                try:
                    await application.bot.send_message(
                        chat_id=player.owner_id,
                        text="🎵 Queue finished! Use Menu to load more music. 🎶",
                        parse_mode="HTML"
                    )
                except Exception as e2:
                    logger.error(f"Failed to send fallback message: {e2}")
