import os
import re
import requests
import logging
from urllib.parse import urlparse, parse_qs

class YouTubeService:
    def __init__(self):
        self.api_key = os.environ.get('YOUTUBE_API_KEY', 'your-youtube-api-key')
        self.base_url = 'https://www.googleapis.com/youtube/v3'
        self.demo_mode = not self.api_key or self.api_key == 'your-youtube-api-key' or not self.api_key.startswith('AIza')
    
    def extract_channel_id(self, channel_input):
        """Extract channel ID from URL or return if it's already an ID"""
        if self.demo_mode:
            return self._get_demo_channel_id(channel_input)
            
        try:
            # Clean input
            channel_input = channel_input.strip()
            
            # Remove @ prefix if present
            if channel_input.startswith('@'):
                channel_input = channel_input[1:]
            
            # If it's already a channel ID (starts with UC and 24 chars total)
            if re.match(r'^UC[\w-]{22}$', channel_input):
                return channel_input
            
            # Handle different YouTube URL formats
            if 'youtube.com' in channel_input or 'youtu.be' in channel_input:
                # Channel URL with ID
                if '/channel/' in channel_input:
                    match = re.search(r'/channel/([^/?&]+)', channel_input)
                    if match:
                        return match.group(1)
                
                # Channel URL with username
                elif '/@' in channel_input:
                    username = re.search(r'/@([^/?&]+)', channel_input)
                    if username:
                        return self.get_channel_id_by_username(username.group(1))
                
                # Legacy username format
                elif '/user/' in channel_input:
                    username = re.search(r'/user/([^/?&]+)', channel_input)
                    if username:
                        return self.get_channel_id_by_username(username.group(1))
                
                # Custom URL format
                elif '/c/' in channel_input:
                    custom_name = re.search(r'/c/([^/?&]+)', channel_input)
                    if custom_name:
                        return self.get_channel_id_by_username(custom_name.group(1))
            
            # Try to use it as a username directly
            return self.get_channel_id_by_username(channel_input)
            
        except Exception as e:
            logging.error(f"Error extracting channel ID: {str(e)}")
            return None
    
    def get_channel_id_by_username(self, username):
        """Get channel ID from username or custom URL"""
        try:
            # Try with forUsername parameter
            url = f"{self.base_url}/channels"
            params = {
                'part': 'id',
                'forUsername': username,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('items'):
                return data['items'][0]['id']
            
            # If not found, try searching
            return self.search_channel_by_name(username)
            
        except Exception as e:
            logging.error(f"Error getting channel ID by username: {str(e)}")
            return None
    
    def search_channel_by_name(self, name):
        """Search for channel by name"""
        try:
            url = f"{self.base_url}/search"
            params = {
                'part': 'snippet',
                'q': name,
                'type': 'channel',
                'maxResults': 1,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('items'):
                return data['items'][0]['snippet']['channelId']
            
            return None
            
        except Exception as e:
            logging.error(f"Error searching channel by name: {str(e)}")
            return None
    
    def get_channel_info(self, channel_id):
        """Get comprehensive channel information"""
        if self.demo_mode:
            return self._get_demo_channel_info(channel_id)
            
        try:
            url = f"{self.base_url}/channels"
            params = {
                'part': 'snippet,statistics,brandingSettings',
                'id': channel_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if not data.get('items'):
                return None
            
            channel = data['items'][0]
            snippet = channel['snippet']
            statistics = channel.get('statistics', {})
            branding = channel.get('brandingSettings', {})
            
            return {
                'id': channel_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'custom_url': snippet.get('customUrl', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'banner_url': branding.get('image', {}).get('bannerExternalUrl', ''),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
                'country': snippet.get('country', ''),
                'keywords': branding.get('channel', {}).get('keywords', ''),
                'default_language': snippet.get('defaultLanguage', '')
            }
            
        except Exception as e:
            logging.error(f"Error getting channel info: {str(e)}")
            return None
    
    def get_channel_videos(self, channel_id, max_results=20):
        """Get recent videos from channel"""
        if self.demo_mode:
            return self._get_demo_videos(channel_id, max_results)
            
        try:
            # First get the uploads playlist ID
            channel_info = self.get_uploads_playlist_id(channel_id)
            if not channel_info:
                return []
            
            uploads_playlist_id = channel_info['uploads_playlist_id']
            
            # Get videos from uploads playlist
            url = f"{self.base_url}/playlistItems"
            params = {
                'part': 'snippet',
                'playlistId': uploads_playlist_id,
                'maxResults': max_results,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            videos = []
            if data.get('items'):
                video_ids = [item['snippet']['resourceId']['videoId'] for item in data['items']]
                
                # Get video statistics
                video_stats = self.get_video_statistics(video_ids)
                
                for i, item in enumerate(data['items']):
                    snippet = item['snippet']
                    video_id = snippet['resourceId']['videoId']
                    
                    video_info = {
                        'id': video_id,
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                        'view_count': video_stats.get(video_id, {}).get('viewCount', 0),
                        'like_count': video_stats.get(video_id, {}).get('likeCount', 0),
                        'comment_count': video_stats.get(video_id, {}).get('commentCount', 0)
                    }
                    videos.append(video_info)
            
            return videos
            
        except Exception as e:
            logging.error(f"Error getting channel videos: {str(e)}")
            return []
    
    def get_uploads_playlist_id(self, channel_id):
        """Get the uploads playlist ID for a channel"""
        try:
            url = f"{self.base_url}/channels"
            params = {
                'part': 'contentDetails',
                'id': channel_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('items'):
                uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                return {'uploads_playlist_id': uploads_playlist_id}
            
            return None
            
        except Exception as e:
            logging.error(f"Error getting uploads playlist ID: {str(e)}")
            return None
    
    def get_video_statistics(self, video_ids):
        """Get statistics for multiple videos"""
        try:
            if not video_ids:
                return {}
            
            url = f"{self.base_url}/videos"
            params = {
                'part': 'statistics',
                'id': ','.join(video_ids),
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            stats = {}
            if data.get('items'):
                for item in data['items']:
                    video_id = item['id']
                    statistics = item.get('statistics', {})
                    stats[video_id] = {
                        'viewCount': int(statistics.get('viewCount', 0)),
                        'likeCount': int(statistics.get('likeCount', 0)),
                        'commentCount': int(statistics.get('commentCount', 0))
                    }
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting video statistics: {str(e)}")
            return {}
    
    def _get_demo_channel_id(self, channel_input):
        """Return demo channel ID for testing"""
        # Clean input
        channel_input = channel_input.strip().lower()
        
        # Remove @ prefix and URLs
        if channel_input.startswith('@'):
            channel_input = channel_input[1:]
        
        # Extract username from URLs
        if 'youtube.com' in channel_input:
            if '/@' in channel_input:
                match = re.search(r'/@([^/?&]+)', channel_input)
                if match:
                    channel_input = match.group(1).lower()
            elif '/channel/' in channel_input:
                match = re.search(r'/channel/([^/?&]+)', channel_input)
                if match:
                    return match.group(1)
        
        # Return a demo channel ID based on input
        return f"UC{channel_input.upper()[:10].ljust(10, 'X')}{'0' * 12}"
    
    def _get_demo_channel_info(self, channel_id):
        """Return demo channel information"""
        # Extract base name from channel ID for demo
        base_name = channel_id.replace('UC', '').replace('X', '').replace('0', '')[:10]
        
        demo_channels = {
            'MRBEAST': {
                'title': 'MrBeast',
                'description': 'I want to make the world a better place before I die. Subscribe to be a part of the journey!',
                'subscriber_count': 234000000,
                'video_count': 741,
                'view_count': 51200000000,
                'thumbnail_url': 'https://via.placeholder.com/240x240/FF6B6B/FFFFFF?text=MrBeast',
            },
            'BANDERITAX': {
                'title': 'BanderitaX',
                'description': 'Canal de entretenimiento y gaming. ¡Suscríbete para más contenido!',
                'subscriber_count': 5420000,
                'video_count': 2341,
                'view_count': 1200000000,
                'thumbnail_url': 'https://via.placeholder.com/240x240/4ECDC4/FFFFFF?text=BanderitaX',
            }
        }
        
        # Default demo channel
        default_info = {
            'id': channel_id,
            'title': f'قناة تجريبية {base_name}',
            'description': 'قناة تجريبية لأغراض التطوير والاختبار',
            'custom_url': f'@{base_name.lower()}',
            'published_at': '2020-01-01T00:00:00Z',
            'thumbnail_url': f'https://via.placeholder.com/240x240/FF9F43/FFFFFF?text={base_name}',
            'banner_url': f'https://via.placeholder.com/2560x1440/FF9F43/FFFFFF?text={base_name}',
            'subscriber_count': 125000,
            'video_count': 158,
            'view_count': 2500000,
            'country': 'SA',
            'keywords': 'تعليم, ترفيه, تقنية',
            'default_language': 'ar'
        }
        
        # Use specific demo data if available
        if base_name.upper() in demo_channels:
            demo_info = demo_channels[base_name.upper()]
            default_info.update(demo_info)
        
        return default_info
    
    def _get_demo_videos(self, channel_id, max_results):
        """Return demo videos for testing"""
        demo_videos = []
        
        for i in range(min(max_results, 10)):
            video = {
                'id': f'demo_video_{i+1}',
                'title': f'فيديو تجريبي رقم {i+1} - محتوى مفيد وممتع',
                'description': f'هذا فيديو تجريبي يحتوي على محتوى تعليمي مفيد في مجال التقنية والبرمجة...',
                'published_at': f'2024-01-{str(i+1).zfill(2)}T10:00:00Z',
                'thumbnail_url': f'https://via.placeholder.com/320x180/3498DB/FFFFFF?text=Video+{i+1}',
                'view_count': (10000 - i * 500),
                'like_count': (500 - i * 25),
                'comment_count': (50 - i * 5)
            }
            demo_videos.append(video)
        
        return demo_videos
