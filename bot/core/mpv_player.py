"""
MPV Player Control Module
Handles all MPV process management
"""

import os
import signal
import subprocess
import logging
import json
import socket
from typing import Optional
from pathlib import Path

from .player_state import player
from ..config import MPV_OPTIONS

logger = logging.getLogger(__name__)

# IPC socket path
IPC_SOCKET = "/tmp/mpvsocket"


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
            # Remove old socket if exists
            if os.path.exists(IPC_SOCKET):
                os.remove(IPC_SOCKET)
            
            # Build command
            cmd = ['mpv']
            
            # Add IPC socket for control
            cmd.append(f'--input-ipc-server={IPC_SOCKET}')
            
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
    def send_command(command: dict) -> bool:
        """
        Send command to MPV via IPC socket
        
        Args:
            command: Dictionary with MPV command
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(IPC_SOCKET):
                logger.warning("MPV IPC socket not found")
                return False
            
            # Connect to socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(IPC_SOCKET)
            
            # Send command
            command_str = json.dumps(command) + '\n'
            sock.send(command_str.encode('utf-8'))
            
            # Get response
            response = sock.recv(4096).decode('utf-8')
            sock.close()
            
            logger.debug(f"MPV response: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending command to MPV: {e}")
            return False
    
    @staticmethod
    def set_volume(volume: int) -> bool:
        """
        Set volume via IPC or system amixer
        
        Args:
            volume: Volume level (0-100)
            
        Returns:
            True if successful
        """
        try:
            # Try IPC first (if MPV supports it)
            if os.path.exists(IPC_SOCKET):
                command = {
                    "command": ["set_property", "volume", volume]
                }
                success = MPVPlayer.send_command(command)
                if success:
                    logger.info(f"Set volume to {volume}% via IPC")
                    return True
            
            # Fallback to system volume control using amixer
            try:
                # Set volume using amixer
                cmd = ['amixer', '-D', 'pulse', 'sset', 'Master', f'{volume}%']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                
                if result.returncode == 0:
                    logger.info(f"Set system volume to {volume}% via amixer")
                    return True
                else:
                    logger.warning(f"amixer failed: {result.stderr}")
            except FileNotFoundError:
                logger.warning("amixer not found, trying pactl...")
                # Alternative: use pactl
                cmd = ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume}%']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                
                if result.returncode == 0:
                    logger.info(f"Set system volume to {volume}% via pactl")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False
    
    @staticmethod
    def get_volume() -> Optional[int]:
        """Get current volume from MPV"""
        try:
            command = {"command": ["get_property", "volume"]}
            # This needs more complex implementation to get return value
            # For now, return stored volume from player state
            return player.volume
        except Exception as e:
            logger.error(f"Error getting volume: {e}")
            return None
    
    @staticmethod
    def volume_up(step: int = 5) -> bool:
        """
        Increase system volume
        
        Args:
            step: Percentage to increase (default 5%)
            
        Returns:
            True if successful
        """
        try:
            # Try with PulseAudio first
            cmd = ['amixer', '-D', 'pulse', 'sset', 'Master', f'{step}%+']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                logger.info(f"✅ Increased volume by {step}% (PulseAudio)")
                return True
            
            # Fallback to direct ALSA if PulseAudio fails
            logger.warning(f"PulseAudio failed, trying ALSA directly. Error: {result.stderr}")
            cmd = ['amixer', 'sset', 'Master', f'{step}%+']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                logger.info(f"✅ Increased volume by {step}% (ALSA)")
                return True
            
            logger.error(f"❌ Both methods failed. ALSA error: {result.stderr}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Exception increasing volume: {e}")
            return False
    
    @staticmethod
    def volume_down(step: int = 5) -> bool:
        """
        Decrease system volume
        
        Args:
            step: Percentage to decrease (default 5%)
            
        Returns:
            True if successful
        """
        try:
            # Try with PulseAudio first
            cmd = ['amixer', '-D', 'pulse', 'sset', 'Master', f'{step}%-']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                logger.info(f"✅ Decreased volume by {step}% (PulseAudio)")
                return True
            
            # Fallback to direct ALSA if PulseAudio fails
            logger.warning(f"PulseAudio failed, trying ALSA directly. Error: {result.stderr}")
            cmd = ['amixer', 'sset', 'Master', f'{step}%-']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                logger.info(f"✅ Decreased volume by {step}% (ALSA)")
                return True
            
            logger.error(f"❌ Both methods failed. ALSA error: {result.stderr}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Exception decreasing volume: {e}")
            return False
    
    @staticmethod
    def toggle_mute() -> bool:
        """
        Toggle mute on/off
        
        Returns:
            True if successful
        """
        try:
            # Try with PulseAudio first
            cmd = ['amixer', '-D', 'pulse', 'sset', 'Master', 'toggle']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                logger.info("✅ Toggled mute (PulseAudio)")
                return True
            
            # Fallback to direct ALSA if PulseAudio fails
            logger.warning(f"PulseAudio failed, trying ALSA directly. Error: {result.stderr}")
            cmd = ['amixer', 'sset', 'Master', 'toggle']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                logger.info("✅ Toggled mute (ALSA)")
                return True
            
            logger.error(f"❌ Both methods failed. ALSA error: {result.stderr}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Exception toggling mute: {e}")
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
