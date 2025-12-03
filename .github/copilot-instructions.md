# Audio Sentiment Bot – AI Agent Guide

## Architecture Overview

Always prioritize improvements to the Audio Sentiment Bot experience above ancillary tooling. Keep the Flask backend and GitHub Pages frontend in lockstep before touching other artifacts.

Audio Sentiment Bot is a Flask-based web app that transcribes audio clips with Google Web Speech API and analyzes sentiment using VADER. The architecture provides three interfaces: a responsive web UI (`app.py` + `templates/index.html`), a Tkinter desktop overlay (`ui_overlay.py`), and CLI microphone streaming (`stream_live.py`).

### Core Components

**`analysis.py`** – Single source of truth for transcription and sentiment logic:
- `transcribe_audio_bytes(audio_bytes, language="en-US")`: Wraps `speech_recognition` library; returns empty string `""` on unknown speech, raises `RuntimeError` on API failures
- `classify_sentiment(transcript)`: Returns `{"label": "POSITIVE|NEGATIVE|NEUTRAL", "score": float}` with 4-decimal rounding, or `None` for empty transcripts
- `analyze_audio_file(file_path, language)`: Convenience wrapper that reads file and chains the above two functions
- `analyze_audio_bytes(audio_bytes, *, language="en-US", transcribe_fn, classify_fn)`: In-memory equivalent used by `app.py` and tests for dependency injection

**`app.py`** – Flask server with dependency injection pattern:
- Uses factory function `create_app(transcribe_fn, classify_fn)` to enable test doubles without hitting external APIs
- `POST /analyze` accepts multipart field `audio` and optional `language` (defaults to `en-US`, validates against `LANGUAGE_CHOICES` tuple)
- Error handling is deliberate: 400 for missing/empty files, 500 for transcription `RuntimeError`, HTTP 200 with `"error"` field when speech unrecognized
- Runs on `0.0.0.0:6142` with `debug=True` by default

**`ui_overlay.py`** – Tkinter desktop app with threaded workers:
- `SentimentOverlay` class uses `threading.Event` to manage microphone state and `queue.Queue` for cross-thread result passing
- `_poll_results()` drains queue on UI thread every 100ms to update transcript text box with color-coded sentiment tags
- Microphone capture uses `Recognizer.listen(microphone, timeout=1, phrase_time_limit=5)` for 5-second chunks

**`stream_live.py`** – CLI tool for real-time microphone streaming:
- Calibrates ambient noise on startup with `adjust_for_ambient_noise(microphone)`
- Continuously listens in 5-second windows, transcribes via `transcribe_audio_bytes(audio.get_wav_data())`, and prints formatted results
- Exits cleanly on `KeyboardInterrupt`

**`aifc.py`** – Python 3.13+ compatibility shim:
- Minimal stub for removed `aifc` stdlib module required by `speech_recognition`
- Raises informative `Error` if AIFF files are opened; WAV/MP3 only

### Data Flows

1. **Web UI**: Browser uploads audio → Flask `/analyze` → inline transcription/classification → JSON response → JavaScript renders result card
2. **Desktop Overlay**: File picker or mic button → background thread calls `analyze_audio_file` → result dict queued → UI thread renders
3. **CLI Streaming**: Microphone audio → 5-second chunks → `transcribe_audio_bytes` → `classify_sentiment` → stdout

## Development Workflows

### Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Optional for live mic: pip install pyaudio
```

**Python version**: 3.13+ required (`audioop-lts` restores removed `audioop` module). PyAudio not yet compatible with 3.14+.

### Running the App
- **Web interface**: `python app.py` → visit `http://localhost:6142`
- **Desktop overlay**: `python ui_overlay.py`
- **CLI streaming**: `python stream_live.py`

### Testing
```bash
pytest  # Runs all tests in tests/
pytest tests/test_app.py  # Specific module
pytest -k test_transcription_empty  # Single test by name
```

Test strategy:
- `test_app.py` uses `create_app(fake_transcribe, fake_classify)` to inject test doubles
- `test_analysis.py` uses `monkeypatch` to replace `speech_recognition` internals with dummy classes
- `pytest.ini` suppresses VADER deprecation warnings about `codecs.open()`
- No integration tests call external APIs; `test_integration.py` still uses fakes

### Testing the API
```bash
curl -X POST -F "audio=@positive.wav" http://localhost:6142/analyze
curl -X POST -F "audio=@clip.wav" -F "language=fr-FR" http://localhost:6142/analyze
```

### GitHub Pages Frontend Sync
- Static site lives in sibling repo `rosskuehl1.github.io`; update it immediately after touching `templates/index.html`, `static/app.js`, or `static/styles.css`.
- Replace Flask templating with static paths when copying markup and ensure waveform preview + endpoint selector remain functional.
- The Pages script persists an API base URL in `localStorage` and always calls `<api-base>/analyze`; keep API contracts aligned.
- Preview the Pages repo locally with `python -m http.server` before committing so GitHub Pages redeploys a tested build.
- Validate releases by spinning up a temporary `make_server` instance (see README) that serves the Flask app, posting `positive.wav`, and verifying `Access-Control-Allow-Origin` returns your Pages URL.

## Conventions & Patterns

### API Contracts
- **Request**: Multipart `audio` field (required), optional `language` field (BCP-47 code)
- **Response fields**: Always include `transcript`, `sentiment`, `language`, `fileName`; add `error` field for failures
- **Status codes**: 400 (missing/empty file) → 500 (API failure) → 200 (success or unrecognized speech with `error` field)
- Language normalization: blank/invalid codes fall back to `en-US`

### Sentiment Output Format
- Labels are uppercase strings: `"POSITIVE"`, `"NEGATIVE"`, `"NEUTRAL"`
- Scores are floats in `[0, 1]` rounded to 4 decimals
- Classification thresholds: compound ≥ 0.05 → POSITIVE, ≤ -0.05 → NEGATIVE, else NEUTRAL
- UI styling depends on exact label strings (see `transcript_box.tag_configure` in `ui_overlay.py`, `toneFromLabel` in `static/app.js`)

### Waveform Visualization
- Waveform previews live entirely in the browser via `AudioContext` + `<canvas>`; keep `renderWaveform`, `drawWaveform`, and `clearWaveform` behaviour identical in both repositories.
- Never upload decoded PCM data—`renderWaveform` must operate on the user-selected file only.
- When adding new ingestion paths (drag-and-drop, microphone recordings, etc.), route them through the existing helpers so the preview and metadata stay accurate.
- Update CSS/HTML counterparts whenever you tweak canvas dimensions or metadata copy.

### CORS & Hosted Frontend
- Flask adds `Access-Control-Allow-*` headers for every response and handles `OPTIONS` preflight requests.
- Configure the allowed origin by setting `AUDIO_SENTIMENT_BOT_CORS_ORIGIN` (default `*`). Set this to your GitHub Pages URL when deploying.
- The GitHub Pages frontend expects the `/analyze` route to accept cross-origin form-data uploads; keep allowed headers (`Content-Type, Accept`) in sync if you add custom request headers.

### Dependency Injection Pattern
The `create_app` factory accepts `transcribe_fn` and `classify_fn` arguments stored in `app.config`. Tests inject fakes to avoid network calls:
```python
def fake_transcribe(audio_bytes, language="en-US"):
    return "test transcript"

app = create_app(transcribe_fn=fake_transcribe, classify_fn=lambda t: {"label": "NEUTRAL", "score": 0.5})
```

### Threading Conventions (Tkinter overlay)
- File/mic analysis runs in daemon threads to avoid blocking UI
- Results are dictionaries with `{"type": "file"|"mic"|"error", "transcript": str, "sentiment": dict, ...}`
- UI thread polls `_results` queue every 100ms via `root.after(100, self._poll_results)`

### Centralized Logic in `analysis.py`
Do not call `speech_recognition` or `vaderSentiment` directly from new code. Instead, modify helpers in `analysis.py` to change system-wide behavior. This ensures consistent error handling and makes testing easier.

## External Dependencies

### Google Web Speech API
- Free tier, invoked via `speech_recognition` library
- Limit: ~60 seconds per request; longer audio should be chunked before calling `transcribe_audio_bytes`
- Network failures raise `sr.RequestError`, wrapped in `RuntimeError` by `transcribe_audio_bytes`
- Unknown speech raises `sr.UnknownValueError`, caught and returned as empty string

### VADER Sentiment Analyzer
- `SentimentIntensityAnalyzer` instantiated once at module import time as `_sentiment_analyzer`
- Returns `polarity_scores(text)` dict with `compound` key in `[-1, 1]`
- Do not create new analyzer instances in hot paths

### Python 3.13+ Compatibility
- `audioop-lts` package restores `audioop` module removed from stdlib
- `aifc.py` shim prevents import errors from `speech_recognition` (stdlib `aifc` also removed)
- PyAudio not yet updated for Python 3.14+; manual install required for mic streaming

## Key Files Reference

- **`analysis.py`**: Core transcription/sentiment logic (3 functions, single analyzer instance)
- **`app.py`**: Flask factory with `/analyze` endpoint and `/` template route
- **`templates/index.html`**: Mobile-first upload form, rendered by Flask
- **`static/app.js`**: Fetch-based upload, dynamic result card rendering, empty state management
 - **`static/app.js`**: Fetch-based upload, waveform rendering via Web Audio API, dynamic result card rendering, empty state management
- **`static/styles.css`**: Responsive layout with sentiment color tokens
- **`ui_overlay.py`**: Tkinter GUI with file picker, mic toggle, threaded workers, queue-based updates
- **`stream_live.py`**: CLI mic streaming with 5-second phrase limit
- **`pytest.ini`**: Suppresses deprecation warnings from VADER
- **`requirements.txt`**: Flask 3.0.0, speechrecognition 3.10.4, audioop-lts 0.2.2, vaderSentiment 3.3.2, pytest
- **`aifc.py`**: Compatibility shim for Python 3.13+ (do not delete)
