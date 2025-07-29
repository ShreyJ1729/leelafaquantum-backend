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
    def __init__(self, channel_url, output_dir="downloads", format_type="audio", download_thumbnails=True):
        self.channel_url = channel_url
        self.output_dir = Path(output_dir)
        self.format_type = format_type.lower()
        self.download_thumbnails = download_thumbnails
        
        # Create output directories
        self.videos_dir = self.output_dir / "videos"
        self.audio_dir = self.output_dir / "audio"
        self.thumbnails_dir = self.output_dir / "thumbnails"
        self.metadata_dir = self.output_dir / "metadata"
        
        for dir_path in [self.videos_dir, self.audio_dir, self.thumbnails_dir, self.metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'scraper.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize PO token
        self.po_token_data = self._get_po_token()
    
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
                response = requests.get(thumbnail_url, timeout=30)
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
    
    def scrape_channel(self):
        """Main method to scrape entire channel"""
        try:
            # Initialize channel
            if self.po_token_data:
                channel = Channel(
                    self.channel_url,
                    use_po_token=True,
                    po_token_verifier=self._po_token_verifier,
                )
            else:
                channel = Channel(self.channel_url)
            
            self.logger.info(f"Starting scrape of channel: {channel.channel_name}")
            self.logger.info(f"Channel URL: {self.channel_url}")
            self.logger.info(f"Output directory: {self.output_dir}")
            self.logger.info(f"Format: {self.format_type}")
            self.logger.info(f"Download thumbnails: {self.download_thumbnails}")
            
            # Get all videos
            videos = list(channel.videos)
            self.logger.info(f"Found {len(videos)} videos to process")
            
            successful_downloads = 0
            failed_downloads = 0
            
            # Process each video
            for video in tqdm(videos, desc=f"Downloading {self.format_type}"):
                try:
                    filename_base = self._sanitize_filename(video.title)
                    
                    # Save metadata
                    self._save_metadata(video, filename_base)
                    
                    # Download thumbnail
                    self._download_thumbnail(video, filename_base)
                    
                    # Download video/audio
                    if self._download_video(video, filename_base):
                        successful_downloads += 1
                    else:
                        failed_downloads += 1
                        
                except Exception as e:
                    self.logger.error(f"Error processing video '{video.title}': {e}")
                    failed_downloads += 1
                    continue
            
            # Summary
            self.logger.info("=" * 50)
            self.logger.info("SCRAPING COMPLETE")
            self.logger.info(f"Total videos found: {len(videos)}")
            self.logger.info(f"Successful downloads: {successful_downloads}")
            self.logger.info(f"Failed downloads: {failed_downloads}")
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
        download_thumbnails=not args.no_thumbnails
    )
    
    scraper.scrape_channel()


if __name__ == "__main__":
    main()