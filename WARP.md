# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Audio Sentiment Bot is a Flask-based API that transcribes audio files and analyzes sentiment using Google's Web Speech API and VADER sentiment analysis. The project supports both REST API endpoints and real-time microphone streaming.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install PyAudio for live streaming (not yet compatible with Python 3.14+)
pip install pyaudio
```

### Running the Application
```bash
# Start Flask API server (runs on http://0.0.0.0:6142)
python app.py

# Run live microphone streaming (requires PyAudio)
python stream_live.py
```

### Testing the API
```bash
# Test with sample audio file
curl -X POST -F "audio=@positive.wav" http://localhost:6142/analyze
```

## Architecture

### Core Components

**app.py** - Flask REST API server
- Single endpoint: `POST /analyze` accepts multipart/form-data with audio file
- Transcribes audio using Google Web Speech API (free tier, ~60 seconds per request)
- Analyzes sentiment using VADER with compound scoring
- Returns JSON with transcript and sentiment (label + score)

**stream_live.py** - Real-time microphone processing
- Captures 5-second audio windows from microphone
- Uses same transcription and sentiment analysis pipeline as API
- Outputs text and sentiment to console in real-time

**aifc.py** - Python 3.13+ compatibility shim
- Provides minimal `aifc` module stub (removed from stdlib in Python 3.13+)
- Required by SpeechRecognition library dependency
- Raises informative error if AIFF files are attempted (WAV/MP3 only supported)

### Sentiment Scoring Logic

Both `app.py` and `stream_live.py` implement identical sentiment classification:
- **POSITIVE**: compound score ≥ 0.05
- **NEGATIVE**: compound score ≤ -0.05
- **NEUTRAL**: compound score between -0.05 and 0.05

The confidence score calculation differs by label:
- POSITIVE/NEGATIVE: uses absolute value of compound score
- NEUTRAL: uses `1 - abs(compound)` for inverse confidence

### Key Dependencies

- **Flask 3.0.0**: Web framework for REST API
- **SpeechRecognition 3.10.4**: Audio transcription via Google Web Speech API
- **audioop-lts 0.2.2**: Restores `audioop` module for Python 3.13+ (required by SpeechRecognition)
- **vaderSentiment 3.3.2**: Lexicon-based sentiment analysis
- **PyAudio** (optional): Microphone input for live streaming; install manually, not compatible with Python 3.14+

## Python Version Requirements

- **Minimum**: Python 3.13+
- **Note**: PyAudio not yet updated for Python 3.14+ (live streaming will not work)
- The project uses `audioop-lts` to restore functionality removed from Python 3.13+ stdlib

## API Specification

### POST /analyze

**Request:**
- Content-Type: `multipart/form-data`
- Field name: `audio`
- Supported formats: WAV, MP3

**Success Response (200):**
```json
{
  "transcript": "This is a great day!",
  "sentiment": {
    "label": "POSITIVE",
    "score": 0.7845
  }
}
```

**Error Responses:**
- 400: Missing audio file or empty filename
- 500: Speech API error
- 200 (with error field): Transcription failed but request valid

## Important Notes

- No test suite currently exists in this project
- Flask runs in debug mode by default on port 6142
- Audio transcription happens in-memory using BytesIO (no temp files written)
- Sentiment analyzer is loaded once at startup as a module-level singleton for performance
- Google Web Speech API is free but has rate limits (~60 seconds per request)
