# Audio Sentiment Bot

Audio Sentiment Bot is now a zero-backend, browser-first experience. The app runs entirely on the client using WebAssembly-powered models to transcribe spoken English and predict sentiment—streamed live from your microphone or loaded from a file—without shipping audio to a server.

![Audio Sentiment Bot UI](docs/assets/ui-preview.png)

## What changed

- **All client-side** – Everything runs in your browser; no Flask server, Python runtime, or API key required.
- **Realtime streaming** – Watch the live sentiment gauge update every few seconds while you speak; recordings are optional.
- **Modern models** – Speech recognition uses Whisper Tiny (quantized) via `@xenova/transformers`. Sentiment scores come from DistilBERT, also loaded on-demand in the browser.
- **Same polished UI** – Waveform preview, accessible status messaging, and analysis history remain intact.
- **English-only focus** – Scope is intentionally narrowed to English to keep downloads reasonable and latency low.

## Quick start

1. Clone or download this repository.
2. Serve the static site in `docs/` with any HTTP server, for example:
   ```bash
   cd audio_sentiment_bot
   npx serve docs
   ```
   or open `docs/index.html` directly from disk in a modern Chromium or Firefox browser.
3. Drop a short audio clip (≤ ~90 seconds) *or* click **Start recording** to begin a live stream. The first run downloads model weights and caches them locally; subsequent runs are fast and offline-friendly.

## Live streaming tips

- Grant microphone access when prompted, then watch the live sentiment meter while you speak.
- The realtime transcript accumulates in short snippets; click **Stop** to preserve the clip for a full transcription review.
- Use **Analyze latest recording** after stopping to run full transcription on the captured audio, including a stored history entry.

> Note: The first transcription may take a minute while the WebAssembly bundles download and compile. Keep the tab open—progress is shown in the status banner.

## Deploying to GitHub Pages

The project ships ready for Pages. Point your repository settings to the `docs/` folder or copy the folder into your Pages repo (`rosskuehl1.github.io`). GitHub will deploy automatically on push—no build step necessary.

Recommended checklist before publishing:

1. `npx serve docs` (or equivalent) and open the served URL.
2. Run one or two analyses to warm the model cache and confirm transcript quality.
3. Commit changes and push to `main`. GitHub Pages will redeploy with the updated static assets.

## Project structure

- `docs/index.html` – Static HTML shell.
- `docs/assets/styles.css` – Responsive layout, live sentiment visuals, and component styling.
- `docs/assets/app.js` – Client-side waveform rendering, live stream analysis, audio resampling, speech transcription, and sentiment scoring using `@xenova/transformers`.
- `docs/assets/ui-preview.png` – Screenshot used in docs.
- `positive.wav` – Sample clip for manual testing.

## Browser requirements

- Chromium 115+, Firefox 116+, or any browser with WebAssembly SIMD + Multi-Threading support.
- Microphones are optional but required for realtime streaming; the app also works with recorded files (`.wav`, `.mp3`, `.m4a`, `.aac`, etc.).
- Expect a one-time download of roughly 80 MB for the model pair. Assets are cached by the browser after the first run.

## Legacy tooling

The previous Flask API, desktop overlay, and Python streaming helpers were removed from the main branch. If you still need them, check the git history prior to December 2025.

## License

This project remains open source for personal or educational use.
