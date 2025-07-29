# Leela FAQuantum Backend

A backend system for processing and searching YouTube video transcriptions using ChromaDB and OpenAI embeddings.

## Features

- YouTube video downloading and transcription processing
- Vector database storage with ChromaDB
- Semantic search across video transcriptions
- FastAPI endpoint for querying transcriptions
- YouTube channel scraper for bulk downloads

## Project Structure

```
├── main.py                 # Main FastAPI application with RAG endpoint
├── create_chromadb.py      # Script to create ChromaDB from transcriptions
├── download.py             # YouTube video downloader
├── transcribe.py           # Video transcription processor
├── process_transcriptions.py # Transcription processing utilities
├── convert.py              # Video conversion utilities
├── remove_timestamps.py    # Timestamp removal from transcriptions
├── YouTubeScraper/         # Standalone YouTube channel scraper
│   ├── scraper.py          # Main scraper script
│   ├── requirements.txt    # Scraper dependencies
│   └── README.md           # Scraper documentation
├── transcriptions/         # Original transcription files
├── transcriptions_new/     # Processed transcription files
└── title_url_map.json      # Mapping of titles to YouTube URLs
```

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Install youtube-po-token-generator (optional but recommended):**
```bash
npm install -g youtube-po-token-generator
```

## Usage

### Running the FastAPI Application

Deploy to Modal:
```bash
modal deploy main.py
```

The application provides a `/rag` endpoint that accepts:
- `question`: The search query
- `n_results`: Number of results to return

### Using the YouTube Scraper

Navigate to the YouTubeScraper directory and follow the instructions in its README.md.

### Processing New Videos

1. **Download videos:**
```bash
python download.py
```

2. **Create ChromaDB:**
```bash
python create_chromadb.py
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for embeddings and completions

## Dependencies

- **modal**: For serverless deployment
- **chromadb**: Vector database for semantic search
- **openai**: OpenAI API client
- **fastapi**: Web framework
- **pytubefix**: YouTube video downloading
- **tqdm**: Progress bars
- **requests**: HTTP client

## License

This project is for educational and personal use only. Users are responsible for complying with YouTube's Terms of Service and applicable copyright laws.