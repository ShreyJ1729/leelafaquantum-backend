# YouTube Channel Scraper

A Python script to download all videos, audio, and thumbnails from any YouTube channel.

## Features

- Download all videos from any YouTube channel
- Support for both video and audio-only downloads
- **Channel releases/albums support** - Automatically organizes music releases into separate folders
- Automatic thumbnail downloads in highest available quality
- Metadata extraction and storage
- Progress tracking with progress bars
- Resume capability (skips already downloaded files)
- Robust error handling and logging
- PO token support for enhanced YouTube access
- Proxy support for bypassing regional restrictions

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

4. Configure proxy (optional):
```bash
cp proxy_config.json.example proxy_config.json
# Edit proxy_config.json with your proxy settings
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
    --no-thumbnails \
    --proxy-config my_proxy.json
```

### Command Line Arguments

- `channel_url` (required): YouTube channel URL
- `--format`: Download format - `audio` (default) or `video`
- `--output-dir`: Output directory (default: `downloads`)
- `--no-thumbnails`: Skip downloading thumbnails
- `--proxy-config`: Path to proxy configuration JSON file (default: `proxy_config.json`)
- `--no-releases`: Skip downloading channel releases/albums
- `--releases-only`: Download only releases, skip regular channel videos

## Output Structure

The script creates the following directory structure:

```
output_dir/
├── videos/              # Regular channel videos (.mp4)
├── audio/               # Regular channel audio (.m4a)
├── thumbnails/          # Regular thumbnails (.jpg)
├── metadata/            # Regular metadata (.json)
├── releases/            # Channel releases/albums
│   ├── Album Name 1/    # Each release in separate folder
│   │   ├── videos/      # Release videos
│   │   ├── audio/       # Release audio files
│   │   ├── thumbnails/  # Release thumbnails
│   │   └── metadata/    # Release metadata
│   └── Album Name 2/
│       ├── videos/
│       ├── audio/
│       ├── thumbnails/
│       └── metadata/
└── scraper.log          # Logging output
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

### Download with proxy
```bash
python scraper.py "https://www.youtube.com/@SomeChannel" --proxy-config proxy_config.json
```

### Download only releases/albums (skip regular videos)
```bash
python scraper.py "https://www.youtube.com/@MusicArtist" --releases-only
```

### Download regular videos without releases
```bash
python scraper.py "https://www.youtube.com/@SomeChannel" --no-releases
```

### Download everything (videos + releases)
```bash
python scraper.py "https://www.youtube.com/@MusicArtist"
```

## Proxy Configuration

The scraper supports HTTP and SOCKS5 proxies for bypassing regional restrictions or routing traffic through specific servers.

### Setting up Proxy

1. **Copy the example configuration:**
```bash
cp proxy_config.json.example proxy_config.json
```

2. **Edit the configuration file:**
```json
{
  "enabled": true,
  "proxies": {
    "http": "socks5://127.0.0.1:1080",
    "https": "socks5://127.0.0.1:1080"
  }
}
```

### Proxy Configuration Options

- **SOCKS5 Proxy:**
```json
{
  "enabled": true,
  "proxies": {
    "http": "socks5://proxy_address:port",
    "https": "socks5://proxy_address:port"
  }
}
```

- **HTTP Proxy:**
```json
{
  "enabled": true,
  "proxies": {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080"
  }
}
```

- **Authenticated Proxy:**
```json
{
  "enabled": true,
  "proxies": {
    "http": "socks5://username:password@proxy.example.com:1080",
    "https": "socks5://username:password@proxy.example.com:1080"
  }
}
```

### Proxy Notes

- The proxy configuration file is automatically excluded from git commits
- If no proxy configuration is found, the scraper will proceed without proxy
- Set `"enabled": false` to temporarily disable proxy without changing settings
- Both thumbnail downloads and video/audio downloads will use the configured proxy

## Channel Releases Support

The scraper now supports downloading YouTube channel releases (albums, EPs, singles) which are automatically organized into separate folders.

### What are Channel Releases?

Channel releases correspond to YouTube's **Releases tab** which is available on Official Artist Channels and music-focused channels. These releases represent curated music collections like:

- Albums
- EPs (Extended Plays)
- Singles
- Compilations
- Other music releases

### How Releases are Organized

Each release is downloaded into its own folder structure:

```
releases/
├── Album Name/
│   ├── audio/       # All tracks from this album
│   ├── videos/      # Music videos from this album
│   ├── thumbnails/  # Thumbnails for each track
│   └── metadata/    # Metadata for each track (includes release info)
```

### Release Features

- **Automatic Discovery**: Finds all releases from the channel's releases tab
- **Organized Storage**: Each release gets its own folder with the release name
- **Complete Metadata**: Includes release name in each track's metadata
- **Progress Tracking**: Shows progress for each release separately
- **Resume Support**: Skips already downloaded tracks, just like regular videos
- **Error Handling**: Continues with other releases if one fails

### Usage Examples

```bash
# Download everything (regular videos + releases)
python scraper.py "https://www.youtube.com/@ArtistChannel"

# Download only the releases/albums
python scraper.py "https://www.youtube.com/@ArtistChannel" --releases-only

# Skip releases, download only regular videos
python scraper.py "https://www.youtube.com/@ArtistChannel" --no-releases

# Download releases with video format
python scraper.py "https://www.youtube.com/@ArtistChannel" --releases-only --format video
```

### Best For

- **Music Artists**: Official artist channels with organized discographies
- **Record Labels**: Channels with multiple album releases
- **Music Archival**: Systematically organizing music collections
- **Podcast Channels**: Some podcast channels organize content as releases

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