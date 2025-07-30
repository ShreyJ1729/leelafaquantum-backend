#!/usr/bin/env python3
"""
YouTube Channel Scraper
Downloads all videos, audio, and thumbnails from any YouTube channel.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from pytubefix import Channel
from tqdm import tqdm


class YouTubeScraper:
    def __init__(self, channel_url, output_dir="downloads", format_type="audio", download_thumbnails=True, proxy_config_path=None, download_releases=True, releases_only=False):
        self.channel_url = channel_url
        self.output_dir = Path(output_dir)
        self.format_type = format_type.lower()
        self.download_thumbnails = download_thumbnails
        self.download_releases = download_releases
        self.releases_only = releases_only
        
        # Create output directories
        self.videos_dir = self.output_dir / "videos"
        self.audio_dir = self.output_dir / "audio"
        self.thumbnails_dir = self.output_dir / "thumbnails"
        self.metadata_dir = self.output_dir / "metadata"
        self.releases_dir = self.output_dir / "releases"
        
        # Create base directories
        base_dirs = [self.videos_dir, self.audio_dir, self.thumbnails_dir, self.metadata_dir, self.releases_dir]
        for dir_path in base_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging BEFORE loading proxy config (which uses logger)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'scraper.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load proxy configuration (after logger is initialized)
        self.proxies = self._load_proxy_config(proxy_config_path)
        
        # Initialize PO token
        self.po_token_data = self._get_po_token()
    
    def _load_proxy_config(self, proxy_config_path):
        """Load proxy configuration from JSON file"""
        if not proxy_config_path:
            proxy_config_path = Path(__file__).parent / "proxy_config.json"
        else:
            proxy_config_path = Path(proxy_config_path)
            
        if not proxy_config_path.exists():
            self.logger.info("No proxy configuration found, proceeding without proxy")
            return None
            
        try:
            with open(proxy_config_path, 'r') as f:
                config = json.load(f)
                
            if not config.get("enabled", False):
                self.logger.info("Proxy disabled in configuration")
                return None
                
            proxies = config.get("proxies", {})
            if proxies:
                self.logger.info(f"Using proxy configuration: {proxies}")
                return proxies
            else:
                self.logger.warning("Proxy enabled but no proxy addresses configured")
                return None
                
        except Exception as e:
            self.logger.warning(f"Failed to load proxy configuration: {e}")
            return None
    
    def _get_po_token(self):
        """Generate PO token for YouTube access"""
        try:
            process = subprocess.Popen(["youtube-po-token-generator"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.logger.warning(f"PO token generation failed: {stderr.decode()}")
                return None
                
            return json.loads(stdout)
        except Exception as e:
            self.logger.warning(f"Could not generate PO token: {e}")
            return None
    
    def _po_token_verifier(self):
        """PO token verifier for pytubefix"""
        if self.po_token_data:
            return (self.po_token_data["visitorData"], self.po_token_data["poToken"])
        return None
    
    def _sanitize_filename(self, filename):
        """Sanitize filename for filesystem compatibility"""
        # Replace problematic characters
        sanitized = filename.replace("/", " or ").replace("\\", " or ")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in (' ', '-', '_', '.', '(', ')'))
        return sanitized.strip()
    
    def _download_thumbnail(self, video, filename_base):
        """Download video thumbnail in highest available quality"""
        if not self.download_thumbnails:
            return
            
        thumbnail_qualities = [
            "maxresdefault.jpg",
            "hqdefault.jpg", 
            "mqdefault.jpg",
            "default.jpg"
        ]
        
        video_id = video.video_id
        
        for quality in thumbnail_qualities:
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/{quality}"
            thumbnail_path = self.thumbnails_dir / f"{filename_base}.jpg"
            
            if thumbnail_path.exists():
                self.logger.info(f"Thumbnail already exists: {thumbnail_path.name}")
                return
                
            try:
                # Use proxies if configured
                response = requests.get(thumbnail_url, timeout=30, proxies=self.proxies)
                if response.status_code == 200:
                    with open(thumbnail_path, 'wb') as f:
                        f.write(response.content)
                    self.logger.info(f"Downloaded thumbnail: {thumbnail_path.name}")
                    return
            except Exception as e:
                self.logger.warning(f"Failed to download thumbnail {quality} for {filename_base}: {e}")
                continue
        
        self.logger.warning(f"Could not download any thumbnail for {filename_base}")
    
    def _save_metadata(self, video, filename_base):
        """Save video metadata as JSON"""
        metadata = {
            "title": video.title,
            "description": video.description,
            "length": video.length,
            "views": video.views,
            "rating": getattr(video, 'rating', None),
            "publish_date": video.publish_date.isoformat() if video.publish_date else None,
            "video_id": video.video_id,
            "watch_url": video.watch_url,
            "author": video.author,
            "keywords": getattr(video, 'keywords', []),
        }
        
        metadata_path = self.metadata_dir / f"{filename_base}.json"
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved metadata: {metadata_path.name}")
        except Exception as e:
            self.logger.error(f"Failed to save metadata for {filename_base}: {e}")
    
    def _download_video(self, video, filename_base):
        """Download video file"""
        try:
            if self.format_type == "video":
                # Download highest quality video
                stream = video.streams.get_highest_resolution()
                output_path = self.videos_dir
                extension = ".mp4"
            else:  # audio
                # Download audio only
                stream = video.streams.get_audio_only()
                output_path = self.audio_dir
                extension = ".m4a"
            
            if not stream:
                self.logger.error(f"No suitable stream found for {filename_base}")
                return False
                
            filename = f"{filename_base}{extension}"
            full_path = output_path / filename
            
            if full_path.exists():
                self.logger.info(f"File already exists, skipping: {filename}")
                return True
                
            stream.download(output_path=output_path, filename=filename)
            self.logger.info(f"Downloaded {self.format_type}: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download {self.format_type} for {filename_base}: {e}")
            return False
    
    def _create_release_directories(self, release_name):
        """Create directory structure for a specific release"""
        sanitized_name = self._sanitize_filename(release_name)
        release_base_dir = self.releases_dir / sanitized_name
        
        release_videos_dir = release_base_dir / "videos"
        release_audio_dir = release_base_dir / "audio"
        release_thumbnails_dir = release_base_dir / "thumbnails"
        release_metadata_dir = release_base_dir / "metadata"
        
        for dir_path in [release_videos_dir, release_audio_dir, release_thumbnails_dir, release_metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        return {
            'videos': release_videos_dir,
            'audio': release_audio_dir,
            'thumbnails': release_thumbnails_dir,
            'metadata': release_metadata_dir
        }
    
    def _download_release_video(self, video, release_name, filename_base):
        """Download video file for a specific release"""
        try:
            release_dirs = self._create_release_directories(release_name)
            
            if self.format_type == "video":
                stream = video.streams.get_highest_resolution()
                output_path = release_dirs['videos']
                extension = ".mp4"
            else:  # audio
                stream = video.streams.get_audio_only()
                output_path = release_dirs['audio']
                extension = ".m4a"
            
            if not stream:
                self.logger.error(f"No suitable stream found for {filename_base} in release {release_name}")
                return False
                
            filename = f"{filename_base}{extension}"
            full_path = output_path / filename
            
            if full_path.exists():
                self.logger.info(f"File already exists, skipping: {release_name}/{filename}")
                return True
                
            stream.download(output_path=output_path, filename=filename)
            self.logger.info(f"Downloaded {self.format_type}: {release_name}/{filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download {self.format_type} for {filename_base} in release {release_name}: {e}")
            return False
    
    def _download_release_thumbnail(self, video, release_name, filename_base):
        """Download video thumbnail for a specific release"""
        if not self.download_thumbnails:
            return
            
        release_dirs = self._create_release_directories(release_name)
        thumbnail_qualities = [
            "maxresdefault.jpg",
            "hqdefault.jpg", 
            "mqdefault.jpg",
            "default.jpg"
        ]
        
        video_id = video.video_id
        
        for quality in thumbnail_qualities:
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/{quality}"
            thumbnail_path = release_dirs['thumbnails'] / f"{filename_base}.jpg"
            
            if thumbnail_path.exists():
                self.logger.info(f"Thumbnail already exists: {release_name}/{thumbnail_path.name}")
                return
                
            try:
                response = requests.get(thumbnail_url, timeout=30, proxies=self.proxies)
                if response.status_code == 200:
                    with open(thumbnail_path, 'wb') as f:
                        f.write(response.content)
                    self.logger.info(f"Downloaded thumbnail: {release_name}/{thumbnail_path.name}")
                    return
            except Exception as e:
                self.logger.warning(f"Failed to download thumbnail {quality} for {filename_base} in release {release_name}: {e}")
                continue
        
        self.logger.warning(f"Could not download any thumbnail for {filename_base} in release {release_name}")
    
    def _save_release_metadata(self, video, release_name, filename_base):
        """Save video metadata for a specific release"""
        release_dirs = self._create_release_directories(release_name)
        
        metadata = {
            "title": video.title,
            "description": video.description,
            "length": video.length,
            "views": video.views,
            "rating": getattr(video, 'rating', None),
            "publish_date": video.publish_date.isoformat() if video.publish_date else None,
            "video_id": video.video_id,
            "watch_url": video.watch_url,
            "author": video.author,
            "keywords": getattr(video, 'keywords', []),
            "release_name": release_name,
        }
        
        metadata_path = release_dirs['metadata'] / f"{filename_base}.json"
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved metadata: {release_name}/{metadata_path.name}")
        except Exception as e:
            self.logger.error(f"Failed to save metadata for {filename_base} in release {release_name}: {e}")
    
    def _process_release(self, release):
        """Process individual release (album/EP)"""
        try:
            release_name = getattr(release, 'owner', 'Unknown Release')
            if not release_name or release_name == 'Unknown Release':
                # Try alternative properties
                release_name = getattr(release, 'title', f"Release_{release.playlist_id}")
            
            self.logger.info(f"Processing release: {release_name}")
            
            # Get videos in this release
            try:
                videos = list(release.videos)
                if not videos:
                    self.logger.warning(f"No videos found in release: {release_name}")
                    return 0, 0
            except Exception as e:
                self.logger.error(f"Failed to get videos for release {release_name}: {e}")
                return 0, 1
            
            self.logger.info(f"Found {len(videos)} tracks in release: {release_name}")
            
            successful_downloads = 0
            failed_downloads = 0
            
            # Process each video in the release
            for video in tqdm(videos, desc=f"Downloading {release_name}", leave=False):
                try:
                    filename_base = self._sanitize_filename(video.title)
                    
                    # Save metadata
                    self._save_release_metadata(video, release_name, filename_base)
                    
                    # Download thumbnail
                    self._download_release_thumbnail(video, release_name, filename_base)
                    
                    # Download video/audio
                    if self._download_release_video(video, release_name, filename_base):
                        successful_downloads += 1
                    else:
                        failed_downloads += 1
                        
                except Exception as e:
                    self.logger.error(f"Error processing video '{video.title}' in release '{release_name}': {e}")
                    failed_downloads += 1
                    continue
            
            self.logger.info(f"Release '{release_name}' complete: {successful_downloads} successful, {failed_downloads} failed")
            return successful_downloads, failed_downloads
            
        except Exception as e:
            self.logger.error(f"Failed to process release: {e}")
            return 0, 1
    
    def _scrape_releases(self, channel):
        """Main method to scrape all releases from channel"""
        try:
            releases = list(channel.releases)
            if not releases:
                self.logger.info("No releases found for this channel")
                return 0, 0
                
            self.logger.info(f"Found {len(releases)} releases to process")
            
            total_successful = 0
            total_failed = 0
            
            for release in tqdm(releases, desc="Processing releases"):
                successful, failed = self._process_release(release)
                total_successful += successful
                total_failed += failed
                
            return total_successful, total_failed
            
        except Exception as e:
            self.logger.error(f"Failed to access channel releases: {e}")
            return 0, 0
    
    def scrape_channel(self):
        """Main method to scrape entire channel"""
        try:
            # Initialize channel with proxy support
            channel_kwargs = {}
            if self.proxies:
                channel_kwargs['proxies'] = self.proxies
                
            if self.po_token_data:
                channel = Channel(
                    self.channel_url,
                    use_po_token=True,
                    po_token_verifier=self._po_token_verifier,
                    **channel_kwargs
                )
            else:
                channel = Channel(self.channel_url, **channel_kwargs)
            
            self.logger.info(f"Starting scrape of channel: {channel.channel_name}")
            self.logger.info(f"Channel URL: {self.channel_url}")
            self.logger.info(f"Output directory: {self.output_dir}")
            self.logger.info(f"Format: {self.format_type}")
            self.logger.info(f"Download thumbnails: {self.download_thumbnails}")
            self.logger.info(f"Using proxy: {bool(self.proxies)}")
            self.logger.info(f"Download releases: {self.download_releases}")
            self.logger.info(f"Releases only: {self.releases_only}")
            
            # Initialize counters
            total_successful_videos = 0
            total_failed_videos = 0
            total_successful_releases = 0
            total_failed_releases = 0
            
            # Process regular videos (unless releases_only is True)
            if not self.releases_only:
                # Get all videos
                videos = list(channel.videos)
                self.logger.info(f"Found {len(videos)} regular videos to process")
                
                # Process each video
                for video in tqdm(videos, desc=f"Downloading regular {self.format_type}"):
                    try:
                        filename_base = self._sanitize_filename(video.title)
                        
                        # Save metadata
                        self._save_metadata(video, filename_base)
                        
                        # Download thumbnail
                        self._download_thumbnail(video, filename_base)
                        
                        # Download video/audio
                        if self._download_video(video, filename_base):
                            total_successful_videos += 1
                        else:
                            total_failed_videos += 1
                            
                    except Exception as e:
                        self.logger.error(f"Error processing video '{video.title}': {e}")
                        total_failed_videos += 1
                        continue
            else:
                self.logger.info("Skipping regular videos (releases-only mode)")
            
            # Process releases (if enabled)
            if self.download_releases:
                self.logger.info("Starting releases processing...")
                releases_successful, releases_failed = self._scrape_releases(channel)
                total_successful_releases += releases_successful
                total_failed_releases += releases_failed
            else:
                self.logger.info("Skipping releases (disabled)")
            
            # Summary
            self.logger.info("=" * 50)
            self.logger.info("SCRAPING COMPLETE")
            if not self.releases_only:
                self.logger.info(f"Regular videos - Successful: {total_successful_videos}, Failed: {total_failed_videos}")
            if self.download_releases:
                self.logger.info(f"Release tracks - Successful: {total_successful_releases}, Failed: {total_failed_releases}")
            self.logger.info(f"Total successful downloads: {total_successful_videos + total_successful_releases}")
            self.logger.info(f"Total failed downloads: {total_failed_videos + total_failed_releases}")
            self.logger.info(f"Output directory: {self.output_dir}")
            self.logger.info("=" * 50)
            
        except Exception as e:
            self.logger.error(f"Fatal error during channel scraping: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Download all videos from a YouTube channel")
    parser.add_argument("channel_url", help="YouTube channel URL")
    parser.add_argument(
        "--format", 
        choices=["video", "audio"], 
        default="audio",
        help="Download format (default: audio)"
    )
    parser.add_argument(
        "--output-dir", 
        default="downloads",
        help="Output directory (default: downloads)"
    )
    parser.add_argument(
        "--no-thumbnails",
        action="store_true",
        help="Skip downloading thumbnails"
    )
    parser.add_argument(
        "--proxy-config",
        help="Path to proxy configuration JSON file (default: proxy_config.json)"
    )
    parser.add_argument(
        "--download-releases",
        action="store_true",
        default=True,
        help="Download channel releases/albums (default: True)"
    )
    parser.add_argument(
        "--no-releases",
        action="store_true",
        help="Skip downloading releases/albums"
    )
    parser.add_argument(
        "--releases-only",
        action="store_true",
        help="Download only releases, skip regular channel videos"
    )
    
    args = parser.parse_args()
    
    # Validate URL
    parsed_url = urlparse(args.channel_url)
    if not parsed_url.netloc or "youtube.com" not in parsed_url.netloc:
        print("Error: Please provide a valid YouTube channel URL")
        sys.exit(1)
    
    # Create scraper and run
    scraper = YouTubeScraper(
        channel_url=args.channel_url,
        output_dir=args.output_dir,
        format_type=args.format,
        download_thumbnails=not args.no_thumbnails,
        proxy_config_path=args.proxy_config,
        download_releases=not args.no_releases,
        releases_only=args.releases_only
    )
    
    scraper.scrape_channel()


if __name__ == "__main__":
    main()