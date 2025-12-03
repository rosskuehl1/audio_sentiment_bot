# Audio Sentiment Bot – AI Guide
## Architecture
- Core logic lives in `analysis.py`, exposing `transcribe_audio_bytes`, `classify_sentiment`, and `analyze_audio_file`; everything else delegates here.
- `transcribe_audio_bytes` wraps `speech_recognition` with Google Web Speech API, defaulting to `en-US` and returning `""` for unknown speech while raising `RuntimeError` on API failures.
- Sentiment classification returns `{"label": <POSITIVE|NEGATIVE|NEUTRAL>, "score": float}` with 4-decimal rounding and `None` when transcripts are empty; keep this contract.
- `app.py` provides Flask `POST /analyze` that expects multipart field `audio`, normalizes errors into JSON, renders `templates/index.html` for the web UI, and keeps `debug=True` on port 6142 for local development.
- `stream_live.py` handles microphone capture via `Recognizer.listen(..., phrase_time_limit=5)`; it prints transcripts and formatted confidence to stdout and relies on `KeyboardInterrupt` for shutdown.
- `ui_overlay.py` implements the Tkinter `SentimentOverlay` class; background threads push result dictionaries into `_results` queue and `_poll_results` drains it on the UI thread every 100 ms.
- `aifc.py` is a shim replacing the removed stdlib module in Python 3.13+ so `speech_recognition` imports succeed; do not remove or bypass it.
## Workflows
- Use Python 3.13+; create a venv with `python -m venv .venv && source .venv/bin/activate` before installing packages.
- Install dependencies via `pip install -r requirements.txt`; add `pip install pyaudio` manually if you need live microphone streaming on macOS.
- Run the Flask web app with `python app.py`; the server binds to `0.0.0.0:6142`, serves the browser UI at `/`, and logs requests because debug mode stays on.
- Launch the desktop overlay with `python ui_overlay.py`; the UI spawns worker threads for file analysis and microphone capture based on button state.
- Real-time CLI streaming uses `python stream_live.py`; audio is chunked into 5 second windows, then `classify_sentiment` formats console output.
## Patterns & Conventions
- API requests must provide multipart field `audio`; missing or empty uploads return 400, while transcription failures return HTTP 200 with `"transcript": ""` and `"sentiment": null`.
- Keep error responses as simple JSON payloads following the current keys (`error`, `transcript`, `sentiment`) so UI clients remain compatible.
- Reuse helpers in `analysis.py` for any new features instead of calling speech or sentiment libraries directly; update helpers to change system-wide behavior.
- Threaded or async tasks should queue dictionaries containing `type`, `transcript`, `sentiment`, and metadata to align with overlay consumers.
- UI sentiment styling expects uppercase labels `POSITIVE`/`NEGATIVE`/`NEUTRAL`; ensure new sentiment sources reuse these tags for consistent coloring.
- Sentiment `score` values should stay within `[0, 1]` after rounding; guard against raw VADER compound values leaking to callers.
## External Services & Limits
- Google Web Speech API is invoked through `speech_recognition`; catch `RuntimeError` from helpers when the network is unavailable and expose actionable messages.
- VADER analyzer (`SentimentIntensityAnalyzer`) is initialized once at import time; avoid constructing new analyzers inside loops or hot paths.
- `audioop-lts` in `requirements.txt` restores the removed `audioop` module for Python 3.13; do not downgrade Python or remove this dependency.
- Google transcription handles clips under ~60 seconds; consider chunking audio before calling `transcribe_audio_bytes` if you extend the API to longer files.
