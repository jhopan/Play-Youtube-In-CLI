"""
Alarm Scheduler Module
Background task to check and trigger alarms
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Optional
from telegram.ext import Application

from .player_state import player
from .youtube import YouTubeExtractor
from .playback import PlaybackManager
from .storage import storage

logger = logging.getLogger(__name__)


class AlarmScheduler:
    """Manages alarm scheduling and execution"""
    
    _instance: Optional['AlarmScheduler'] = None
    _task: Optional[asyncio.Task] = None
    _running: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def start(cls, application: Application):
        """Start the alarm scheduler background task"""
        if cls._task is not None and not cls._task.done():
            logger.warning("Alarm scheduler already running")
            return
        
        cls._running = True
        cls._task = asyncio.create_task(cls._run_scheduler(application))
        logger.info("⏰ Alarm scheduler started")
    
    @classmethod
    def stop(cls):
        """Stop the alarm scheduler"""
        cls._running = False
        if cls._task is not None:
            cls._task.cancel()
            logger.info("⏰ Alarm scheduler stopped")
    
    @classmethod
    async def _run_scheduler(cls, application: Application):
        """Main scheduler loop - checks every minute"""
        last_checked_minute = None
        
        while cls._running:
            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                current_day = now.strftime("%A")
                
                # Only check once per minute
                if current_time == last_checked_minute:
                    await asyncio.sleep(10)  # Check every 10 seconds
                    continue
                
                last_checked_minute = current_time
                
                # Check all alarms
                alarms = storage.get_alarms()
                for alarm in alarms:
                    if not alarm.get('enabled', False):
                        continue
                    
                    # Check if alarm time matches
                    if alarm['time'] != current_time:
                        continue
                    
                    # Check if alarm should trigger today
                    alarm_days = alarm.get('days', [])
                    if alarm_days and current_day not in alarm_days:
                        continue
                    
                    # Trigger alarm
                    logger.info(f"⏰ Triggering alarm: {alarm['time']}")
                    await cls._trigger_alarm(application, alarm)
                    
                    # If one-time alarm (no repeat days), disable it
                    if not alarm_days:
                        alarm['enabled'] = False
                        storage.save_alarms(alarms)
                        logger.info(f"⏰ One-time alarm disabled: {alarm['time']}")
                
                # Sleep for 10 seconds before next check
                await asyncio.sleep(10)
                
            except asyncio.CancelledError:
                logger.info("⏰ Scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in alarm scheduler: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait a minute on error
    
    @classmethod
    async def _trigger_alarm(cls, application: Application, alarm: dict):
        """Trigger an alarm - start playback"""
        try:
            # Notify owner
            if player.owner_id:
                try:
                    await application.bot.send_message(
                        chat_id=player.owner_id,
                        text=f"⏰ <b>Alarm!</b>\n\n"
                             f"Time: {alarm['time']}\n"
                             f"Starting playback...",
                        parse_mode='HTML'
                    )
                except Exception as e:
                    logger.error(f"Failed to send alarm notification: {e}")
            
            # If playlist URL specified, load it
            playlist_url = alarm.get('playlist_url')
            if playlist_url:
                try:
                    logger.info(f"Loading playlist from alarm: {playlist_url}")
                    songs = YouTubeExtractor.extract_playlist(playlist_url)
                    player.playlist = songs
                    player.current_index = 0
                    logger.info(f"Loaded {len(songs)} songs from alarm playlist")
                except Exception as e:
                    logger.error(f"Failed to load alarm playlist: {e}")
                    # Continue with current queue if load fails
            
            # Start playback if not already playing
            if not player.is_playing and player.playlist:
                await PlaybackManager.play_current_song(application)
                logger.info(f"⏰ Alarm playback started")
            elif player.is_playing:
                logger.info(f"⏰ Already playing, alarm notification sent")
            else:
                logger.warning(f"⏰ No songs to play for alarm")
                
                if player.owner_id:
                    try:
                        await application.bot.send_message(
                            chat_id=player.owner_id,
                            text="⚠️ Alarm triggered but no songs in queue!",
                            parse_mode='HTML'
                        )
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"❌ Failed to trigger alarm: {e}", exc_info=True)


# Create singleton instance
alarm_scheduler = AlarmScheduler()
