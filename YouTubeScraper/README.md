# YouTube Channel Scraper

A Python script to download all videos, audio, and thumbnails from any YouTube channel.

## Features

- Download all videos from any YouTube channel
- Support for both video and audio-only downloads
- Automatic thumbnail downloads in highest available quality
- Metadata extraction and storage
- Progress tracking with progress bars
- Resume capability (skips already downloaded files)
- Robust error handling and logging
- PO token support for enhanced YouTube access

## Installation

1. Clone or download this folder
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install youtube-po-token-generator (optional but recommended):
```bash
npm install -g youtube-po-token-generator
```

## Usage

### Basic Usage

Download audio from a channel:
```bash
python scraper.py "https://www.youtube.com/@ChannelName"
```

Download videos from a channel:
```bash
python scraper.py "https://www.youtube.com/@ChannelName" --format video
```

### Advanced Options

```bash
python scraper.py "https://www.youtube.com/@ChannelName" \
    --format audio \
    --output-dir my_downloads \
    --no-thumbnails
```

### Command Line Arguments

- `channel_url` (required): YouTube channel URL
- `--format`: Download format - `audio` (default) or `video`
- `--output-dir`: Output directory (default: `downloads`)
- `--no-thumbnails`: Skip downloading thumbnails

## Output Structure

The script creates the following directory structure:

```
output_dir/
├── videos/          # Video files (.mp4)
├── audio/           # Audio files (.m4a)
├── thumbnails/      # Thumbnail images (.jpg)
├── metadata/        # Video metadata (.json)
└── scraper.log      # Logging output
```

## Examples

### Download all audio from a channel
```bash
python scraper.py "https://www.youtube.com/@KElmerTinkersAcademy"
```

### Download all videos with custom output directory
```bash
python scraper.py "https://www.youtube.com/@SomeChannel" --format video --output-dir "/path/to/downloads"
```

### Download only audio, skip thumbnails
```bash
python scraper.py "https://www.youtube.com/@SomeChannel" --no-thumbnails
```

## Features in Detail

### Resume Capability
The script automatically skips files that have already been downloaded, making it safe to run multiple times or resume interrupted downloads.

### Thumbnail Quality
Thumbnails are downloaded in the highest available quality:
1. `maxresdefault.jpg` (1920x1080)
2. `hqdefault.jpg` (480x360) 
3. `mqdefault.jpg` (320x180)
4. `default.jpg` (120x90)

### Metadata Storage
Each video's metadata is saved as JSON including:
- Title and description
- Duration, views, and rating
- Publish date
- Video ID and URL
- Author and keywords

### Error Handling
- Robust error handling for network issues
- Detailed logging to file and console
- Graceful handling of restricted or unavailable videos
- Continues processing even if individual videos fail

## Requirements

- Python 3.7+
- pytubefix (for YouTube access)
- requests (for thumbnail downloads)
- tqdm (for progress bars)
- youtube-po-token-generator (optional, for enhanced access)

## Troubleshooting

### "No suitable stream found" errors
Some videos may be restricted or unavailable. The script will log these and continue with other videos.

### Rate limiting
If you encounter rate limiting, the script will attempt to continue. Consider adding delays between downloads if needed.

### PO Token issues
If youtube-po-token-generator is not installed, the script will still work but may have reduced reliability for some channels.

## Legal Notice

This tool is for educational and personal use only. Users are responsible for complying with YouTube's Terms of Service and applicable copyright laws. Only download content you have permission to download.