"""
MPV Player Control Module
Handles all MPV process management
"""

import os
import signal
import subprocess
import logging
from typing import Optional

from .player_state import player
from ..config import MPV_OPTIONS

logger = logging.getLogger(__name__)


class MPVPlayer:
    """MPV player controller"""
    
    @staticmethod
    def start(url: str, volume: int = 50) -> Optional[subprocess.Popen]:
        """
        Start mpv process for streaming
        
        Args:
            url: YouTube video URL
            volume: Volume level (0-100)
        
        Returns:
            subprocess.Popen object or None if failed
        """
        try:
            # Build command
            cmd = ['mpv']
            
            # Add boolean flags
            if MPV_OPTIONS.get('no_video', True):
                cmd.append('--no-video')
            if MPV_OPTIONS.get('no_terminal', True):
                cmd.append('--no-terminal')
            if MPV_OPTIONS.get('quiet', True):
                cmd.append('--quiet')
            
            # Add volume
            cmd.append(f'--volume={volume}')
            
            # Add optional parameters
            if MPV_OPTIONS.get('demuxer_max_bytes'):
                cmd.append(f'--demuxer-max-bytes={MPV_OPTIONS["demuxer_max_bytes"]}')
            if MPV_OPTIONS.get('demuxer_max_back_bytes'):
                cmd.append(f'--demuxer-max-back-bytes={MPV_OPTIONS["demuxer_max_back_bytes"]}')
            
            # Add URL (must be last)
            cmd.append(url)
            
            logger.debug(f"MPV command: {' '.join(cmd)}")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
            
            logger.info(f"Started mpv process with PID: {process.pid}")
            return process
            
        except FileNotFoundError:
            logger.error("MPV not found! Please install: sudo apt install mpv")
            raise
        except Exception as e:
            logger.error(f"Error starting mpv: {e}")
            raise
    
    @staticmethod
    def stop():
        """Stop the current mpv process"""
        if player.mpv_process:
            try:
                player.mpv_process.terminate()
                player.mpv_process.wait(timeout=3)
                logger.info("MPV process stopped")
            except subprocess.TimeoutExpired:
                player.mpv_process.kill()
                logger.warning("MPV process killed (timeout)")
            except Exception as e:
                logger.error(f"Error stopping mpv: {e}")
            finally:
                player.mpv_process = None
    
    @staticmethod
    def pause():
        """Pause the mpv process using SIGSTOP"""
        if player.mpv_process and player.is_playing and not player.is_paused:
            try:
                os.kill(player.mpv_process.pid, signal.SIGSTOP)
                player.is_paused = True
                logger.info("MPV paused")
                return True
            except Exception as e:
                logger.error(f"Error pausing mpv: {e}")
                return False
        return False
    
    @staticmethod
    def resume():
        """Resume the mpv process using SIGCONT"""
        if player.mpv_process and player.is_paused:
            try:
                os.kill(player.mpv_process.pid, signal.SIGCONT)
                player.is_paused = False
                logger.info("MPV resumed")
                return True
            except Exception as e:
                logger.error(f"Error resuming mpv: {e}")
                return False
        return False
    
    @staticmethod
    def is_running() -> bool:
        """Check if mpv process is running"""
        if player.mpv_process:
            return player.mpv_process.poll() is None
        return False
    
    @staticmethod
    def get_status() -> str:
        """Get current player status"""
        if not player.is_playing:
            return "Stopped"
        elif player.is_paused:
            return "Paused"
        else:
            return "Playing"
