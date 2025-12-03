# Audio Sentiment Bot

A Flask-based API that transcribes audio files and analyzes the sentiment of the transcribed text using speech recognition and VADER sentiment analysis.

## Features

- **Audio Transcription**: Converts WAV/MP3 audio files to text using Google Web Speech API
- **Sentiment Analysis**: Analyzes sentiment (POSITIVE, NEGATIVE, or NEUTRAL) using VADER sentiment analyzer
- **REST API**: Simple Flask endpoint for audio file uploads
- **Live Streaming**: Optional microphone streaming for real-time sentiment analysis

## Requirements

- Python 3.13+
- See `requirements.txt` for Python dependencies

## Installation

1. Clone or download this repository

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) For live microphone streaming, install PyAudio manually:
```bash
pip install pyaudio
```

## Usage

### Running the API Server

Start the Flask server:
```bash
python app.py
```

The server will run on `http://0.0.0.0:6142`

### API Endpoint

**POST /analyze**

Upload an audio file for transcription and sentiment analysis.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Audio file with field name `audio` (WAV or MP3 format)

**Response:**
```json
{
  "transcript": "This is a great day!",
  "sentiment": {
    "label": "POSITIVE",
    "score": 0.7845
  }
}
```

**Example using curl:**
```bash
curl -X POST -F "audio=@positive.wav" http://localhost:6142/analyze
```

### Live Microphone Streaming

For real-time sentiment analysis from your microphone:
```bash
python stream_live.py
```

Speak into your microphone, and the script will display transcribed text with sentiment analysis in 5-second windows. Press `Ctrl+C` to stop.

## Project Structure

- `app.py` - Flask API server with audio transcription and sentiment analysis
- `stream_live.py` - Real-time microphone streaming with sentiment analysis
- `requirements.txt` - Python dependencies
- `positive.wav` - Sample audio file for testing

## How It Works

1. **Transcription**: Audio files are processed using the `speech_recognition` library with Google's Web Speech API (free tier, ~60 seconds per request)
2. **Sentiment Analysis**: Text is analyzed using VADER (Valence Aware Dictionary and sEntiment Reasoner), which provides a compound score:
   - Score ≥ 0.05: POSITIVE
   - Score ≤ -0.05: NEGATIVE
   - Between -0.05 and 0.05: NEUTRAL

## License

This project is open source and available for personal or educational use.
