# WARP.md

This file provides quick guidance for WARP (warp.dev) when contributing to this project.

## Project overview

Audio Sentiment Bot is a static web application. It loads WebAssembly speech-recognition and sentiment models directly in the browser (via `@xenova/transformers`) and never calls a backend. Realtime streaming keeps sentiment and transcript updates on-device while you speak.

## Common tasks

- **Preview locally**
  ```bash
  cd audio_sentiment_bot
  npx serve docs
  ```
  Open the printed URL, drop a short audio clip, and wait while the models load on first use.
- **Realtime demo** – Click **Start recording** to stream microphone audio; the sentiment gauge updates every ~3 seconds. Use **Analyze latest recording** afterward to persist the session in history.

- **Performance tips**
  - Keep clips under ~90 seconds to avoid long inference times.
  - Encourage users to stay on the tab during the initial model download (roughly 80 MB total).

- **GitHub Pages deployment**
  Push the `docs/` folder to `main`. Pages is already configured to serve from that directory—no build step required.

## Architecture

- `docs/index.html` – Document shell and UI copy.
- `docs/assets/app.js` – Audio decoding, resampling, live stream analysis, waveform rendering, Whisper transcription, and DistilBERT sentiment scoring.
- `docs/assets/styles.css` – Layout and design tokens.
- External dependency: `@xenova/transformers` fetched from jsDelivr at runtime (models cached by the browser once loaded).

## Legacy note

Older Flask/Python tooling has been removed. If you need it, check out a commit before December 2025.
