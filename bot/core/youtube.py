"""
YouTube Integration Module
Handles all YouTube data extraction using yt-dlp
"""

import logging
from typing import List
import yt_dlp

from .player_state import Song
from ..config import YTDL_OPTIONS

logger = logging.getLogger(__name__)


class YouTubeExtractor:
    """YouTube data extractor using yt-dlp"""
    
    @staticmethod
    def extract_playlist(url: str) -> List[Song]:
        """
        Extract all videos from a YouTube playlist or single video
        
        Args:
            url: YouTube playlist or video URL
        
        Returns:
            List of Song objects
        
        Raises:
            Exception if extraction fails
        """
        try:
            ydl_opts = YTDL_OPTIONS.copy()
            ydl_opts['extract_flat'] = True
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    # It's a playlist
                    songs = []
                    for entry in info['entries']:
                        if entry:
                            song = Song(
                                url=f"https://www.youtube.com/watch?v={entry['id']}",
                                title=entry.get('title', 'Unknown Title'),
                                duration=str(entry.get('duration', 'Unknown'))
                            )
                            songs.append(song)
                    
                    logger.info(f"Extracted {len(songs)} songs from playlist")
                    return songs
                else:
                    # Single video
                    song = Song(
                        url=url,
                        title=info.get('title', 'Unknown Title'),
                        duration=str(info.get('duration', 'Unknown'))
                    )
                    logger.info(f"Extracted single video: {song.title}")
                    return [song]
                    
        except Exception as e:
            logger.error(f"Error extracting YouTube data: {e}")
            raise
    
    @staticmethod
    def get_video_info(url: str) -> Song:
        """
        Get info for a single video
        
        Args:
            url: YouTube video URL
        
        Returns:
            Song object
        
        Raises:
            Exception if extraction fails
        """
        try:
            ydl_opts = YTDL_OPTIONS.copy()
            ydl_opts['extract_flat'] = False
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                song = Song(
                    url=url,
                    title=info.get('title', 'Unknown Title'),
                    duration=str(info.get('duration', 'Unknown'))
                )
                logger.info(f"Got video info: {song.title}")
                return song
                
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate if URL is a valid YouTube URL
        
        Args:
            url: URL to validate
        
        Returns:
            True if valid, False otherwise
        """
        valid_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
        return any(domain in url.lower() for domain in valid_domains)
    
    @staticmethod
    def get_related_videos(video_url: str, count: int = 5) -> List[Song]:
        """
        Get related/suggested videos from YouTube
        
        Args:
            video_url: Current video URL
            count: Number of suggestions to get (default 5)
        
        Returns:
            List of Song objects (suggested videos)
        """
        try:
            ydl_opts = YTDL_OPTIONS.copy()
            ydl_opts['extract_flat'] = 'in_playlist'  # Faster extraction
            ydl_opts['socket_timeout'] = 10  # 10 second timeout
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info with timeout
                info = ydl.extract_info(video_url, download=False)
                
                related = []
                
                # Method 1: Try to get related videos from video info
                if 'related_videos' in info and info['related_videos']:
                    logger.info("Using related_videos from YouTube")
                    for vid in info['related_videos'][:count]:
                        try:
                            video_id = vid.get('id', vid.get('video_id'))
                            if not video_id:
                                continue
                            
                            song = Song(
                                url=f"https://www.youtube.com/watch?v={video_id}",
                                title=vid.get('title', 'Unknown Title'),
                                duration=str(vid.get('duration', 'Unknown'))
                            )
                            related.append(song)
                        except Exception as e:
                            logger.debug(f"Error parsing related video: {e}")
                            continue
                
                # Method 2: Fallback - Use channel's recent videos (faster with extract_flat)
                if len(related) < count and 'channel_id' in info:
                    try:
                        logger.info("Fetching channel videos as fallback")
                        channel_id = info['channel_id']
                        channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"
                        
                        # Use extract_flat for faster channel extraction
                        ydl_opts['extract_flat'] = True
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl_channel:
                            channel_info = ydl_channel.extract_info(
                                channel_url,
                                download=False,
                                process=False  # Don't process entries
                            )
                            
                            if 'entries' in channel_info:
                                for entry in channel_info['entries'][:count * 2]:  # Get extra in case of duplicates
                                    if not entry:
                                        continue
                                    
                                    # Skip current video
                                    entry_id = entry.get('id', entry.get('url', '').split('=')[-1])
                                    current_id = info.get('id', '')
                                    if entry_id == current_id:
                                        continue
                                    
                                    try:
                                        song = Song(
                                            url=f"https://www.youtube.com/watch?v={entry_id}",
                                            title=entry.get('title', 'Unknown Title'),
                                            duration=str(entry.get('duration', 'Unknown'))
                                        )
                                        related.append(song)
                                        
                                        if len(related) >= count:
                                            break
                                    except Exception as e:
                                        logger.debug(f"Error parsing channel video: {e}")
                                        continue
                    except Exception as e:
                        logger.warning(f"Could not fetch channel videos: {e}")
                
                if related:
                    logger.info(f"✅ Found {len(related)} related videos")
                else:
                    logger.warning("⚠️ No related videos found")
                
                return related[:count]
                
        except Exception as e:
            logger.error(f"❌ Error getting related videos: {e}")
            return []
