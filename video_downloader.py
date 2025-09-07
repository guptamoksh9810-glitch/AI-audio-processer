import yt_dlp
import tempfile
import os
import re
from pathlib import Path
import io


class VideoDownloader:
    def __init__(self):
        self.supported_sites = [
            'youtube.com', 'youtu.be', 'soundcloud.com', 'vimeo.com',
            'dailymotion.com', 'facebook.com', 'instagram.com', 'tiktok.com'
        ]
    
    def is_valid_url(self, url):
        """Check if the URL is valid and from a supported site"""
        if not url or not url.strip():
            return False
            
        # Basic URL pattern check
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url.strip()):
            return False
        
        # Check if it's from a supported site
        for site in self.supported_sites:
            if site in url.lower():
                return True
        
        return True  # Allow other sites but warn user
    
    def get_video_info(self, url):
        """Get basic information about the video without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', ''),
                    'view_count': info.get('view_count', 0),
                    'webpage_url': info.get('webpage_url', url)
                }
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")
    
    def download_audio(self, url, output_dir=None):
        """Download audio from video URL and return the file path"""
        try:
            # Create temporary directory if none provided
            if output_dir is None:
                output_dir = tempfile.mkdtemp()
            
            # Configure yt-dlp options for audio extraction
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'extractaudio': True,
                'audioformat': 'wav',  # Use WAV for better compatibility with librosa
                'audioquality': '0',  # Best quality
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
            }
            
            # Download the audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Find the downloaded file
                title = info.get('title', 'audio')
                # Clean filename for filesystem compatibility
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
                
                # Look for the downloaded file
                for ext in ['.wav', '.mp3', '.m4a', '.webm']:
                    potential_file = os.path.join(output_dir, f"{safe_title}{ext}")
                    if os.path.exists(potential_file):
                        return potential_file
                
                # If exact match not found, look for any audio file in the directory
                for file in os.listdir(output_dir):
                    if file.endswith(('.wav', '.mp3', '.m4a', '.webm', '.ogg')):
                        return os.path.join(output_dir, file)
                
                raise Exception("Downloaded audio file not found")
                
        except Exception as e:
            raise Exception(f"Failed to download audio: {str(e)}")
    
    def download_audio_to_buffer(self, url):
        """Download audio directly to memory buffer"""
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Download to temporary file
                audio_file_path = self.download_audio(url, temp_dir)
                
                # Read file into buffer
                with open(audio_file_path, 'rb') as f:
                    audio_buffer = io.BytesIO(f.read())
                
                # Clean up temporary files
                self.cleanup_temp_files(temp_dir)
                
                return audio_buffer
                
            except Exception as e:
                # Clean up on error
                self.cleanup_temp_files(temp_dir)
                raise e
                
        except Exception as e:
            raise Exception(f"Failed to download audio to buffer: {str(e)}")
    
    def cleanup_temp_files(self, directory):
        """Clean up temporary files and directory"""
        try:
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    file_path = os.path.join(directory, file)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                os.rmdir(directory)
        except Exception as e:
            # Silent cleanup failure - not critical
            pass
    
    def format_duration(self, seconds):
        """Format duration in seconds to readable format"""
        if not seconds:
            return "Unknown"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def get_supported_sites_info(self):
        """Get information about supported sites"""
        return {
            'primary_sites': [
                'YouTube (youtube.com, youtu.be)',
                'SoundCloud (soundcloud.com)',
                'Vimeo (vimeo.com)',
                'TikTok (tiktok.com)'
            ],
            'additional_sites': [
                'Facebook Videos',
                'Instagram',
                'Dailymotion',
                'Twitter/X Videos'
            ],
            'note': 'Many other video platforms are also supported!'
        }