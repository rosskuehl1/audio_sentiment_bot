# Audio Sentiment Bot

Audio Sentiment Bot transcribes short audio clips with Google Web Speech and scores the transcript with VADER sentiment analysis. It now ships with a responsive, mobile-first web experience plus the existing API and desktop tools.

## Features

- **Responsive Web UI**: Mobile-first interface with analysis history and keyboard-friendly workflow
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

### Web App (mobile-friendly)

Fire up the Flask dev server and open `http://localhost:6142` in your browser:
```bash
python app.py
```

![Audio Sentiment Bot UI](docs/assets/ui-preview.png)

Highlights:
- Upload a clip, pick a language, and review the transcript and sentiment history without leaving the page
- Works great on phones, tablets, and desktops
- Keeps results client-side; only the audio file you upload leaves the device

### Interactive UI Overlay

Launch the Tkinter desktop overlay to analyze local audio files or live microphone input:
```bash
python ui_overlay.py
```

Features:
- Quick file picker for WAV/MP3/FLAC/AIFF audio
- Start/stop microphone capture with real-time sentiment updates
- Language selector for the Google Web Speech API
- Color-coded transcript log for quick scanning

### Running the API Server only

If you prefer to integrate with the REST API directly, start the Flask server:
```bash
python app.py
```

The server will run on `http://0.0.0.0:6142` by default.

### API Endpoint

**POST /analyze**

Upload an audio file for transcription and sentiment analysis.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Fields:
  - `audio`: audio file (WAV, MP3, M4A, FLAC, etc.)
  - `language` (optional): BCP-47 language code such as `en-US` or `fr-FR`

**Response:**
```json
{
  "transcript": "This is a great day!",
  "sentiment": {
    "label": "POSITIVE",
    "score": 0.7845
  },
  "language": "en-US",
  "fileName": "positive.wav"
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

## Testing

Install the dependencies (including `pytest`) and run the suite:
```bash
pip install -r requirements.txt
pytest
```

The Flask app exposes a `create_app` factory, so tests can inject fake transcription and sentiment helpers without hitting external services.

## License

This project is open source and available for personal or educational use.
