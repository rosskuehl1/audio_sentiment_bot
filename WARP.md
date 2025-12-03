# WARP.md

This file provides quick guidance for WARP (warp.dev) when contributing to this project.

## Project overview

Audio Sentiment Bot is a static web application. It loads WebAssembly speech-recognition and sentiment models directly in the browser (via `@xenova/transformers`) and never calls a backend. Realtime streaming keeps sentiment and transcript updates on-device while you speak (or play guitar) without leaving the tab.

## Common tasks

- **Preview locally**
  ```bash
  cd audio_sentiment_bot
  npm install
  npm run dev   # wraps npx serve docs
  ```
  Open the printed URL, drop a short audio clip, and wait while the models load on first use.
- **Realtime demo** – Click **Start recording** to stream microphone audio; the sentiment gauge updates every ~3 seconds. Use **Analyze latest recording** afterward to persist the session in history.
- **Instrument mode** – Flip the Input mode selector to **Electric guitar / line-in** when plugging in a USB interface. This disables AGC/noise suppression so riffs keep their sustain. Voice mode re-enables the filters for spoken input.
- **Smoke tests** – `npm run test` executes the Playwright suite (`tests/smoke.spec.ts`) that boots the site, toggles instrument modes, and verifies the CI badge is visible.

- **Performance tips**
  - Keep clips under ~90 seconds to avoid long inference times.
  - Encourage users to stay on the tab during the initial model download (roughly 80 MB total).

- **GitHub Pages deployment**
  Push the `docs/` folder to `main`. Pages is already configured to serve from that directory—no build step required. The GitHub Actions workflow (`.github/workflows/ci.yml`) must stay green before publishing.

## Architecture

- `docs/index.html` – Document shell and UI copy.
- `docs/assets/app.js` – Audio decoding, resampling, live stream analysis, waveform rendering, Whisper transcription, DistilBERT sentiment scoring, instrument-mode tuning, sparkline rendering, and CI status fetch.
- `docs/assets/styles.css` – Layout and design tokens.
- External dependency: `@xenova/transformers` fetched from jsDelivr at runtime (models cached by the browser once loaded).

## Tooling

- `package.json` – Houses the `dev`, `serve`, `test`, and `test:ci` scripts.
- `playwright.config.ts` – Spins up `npx serve docs` for tests and captures traces/screenshots on failure.
- `.github/workflows/ci.yml` – Installs dependencies, downloads Chromium, runs `npm run test:ci`, and uploads the Playwright HTML report.

## Legacy note

Older Flask/Python tooling has been removed. If you need it, check out a commit before December 2025.
