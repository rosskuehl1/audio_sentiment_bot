# Audio Sentiment Bot

Audio Sentiment Bot is now a zero-backend, browser-first experience. The app runs entirely on the client using WebAssembly-powered models to transcribe spoken English and predict sentiment—streamed live from your microphone or loaded from a file—without shipping audio to a server.

![Audio Sentiment Bot UI](docs/assets/ui-preview.png)

## Guitarist quick start

1. Plug an electric guitar (or any line-level source) into your USB interface and pick **Electric guitar / line-in** in the Input mode selector.
2. Tap **Start recording**. Instrument mode disables auto-gain/noise suppression so sustain, transients, and harmonic content stay intact.
3. Watch the live sentiment gauge, energy %, confidence, and trend sparkline react every few seconds. Stop whenever you're ready and click **Analyze latest recording** to capture the full transcription in history.

> Voice / acoustic sources still work great—just flip the selector to **Voice** to re-enable echo cancellation and noise suppression.

## What changed

- **All client-side** – Everything runs in your browser; no Flask server, Python runtime, or API key required.
- **Realtime streaming** – Watch the live sentiment gauge update every few seconds while you speak; recordings are optional.
- **Modern models** – Speech recognition uses Whisper Tiny (quantized) via `@xenova/transformers`. Sentiment scores come from DistilBERT, also loaded on-demand in the browser.
- **Same polished UI** – Waveform preview, accessible status messaging, and analysis history remain intact.
- **Sticky history** – Analyses persist locally between sessions so you can compare takes later, with a one-click clear control in the history panel.
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

## Development workflow

The repo now ships with a lightweight Node toolchain for local preview + Playwright smoke tests.

```bash
npm install           # installs Playwright + serve
npm run dev           # serves docs/ at http://127.0.0.1:3000 by default
npm run test          # runs Playwright smoke spec against the served docs/
```

`npm run test` automatically spins up `npx serve docs` (via Playwright's `webServer` config) so you can keep iterating inside `docs/` without extra steps.

## Live streaming tips

- Grant microphone access when prompted, then watch the live sentiment meter while you speak.
- The realtime transcript accumulates in short snippets; click **Stop** to preserve the clip for a full transcription review.
- Use **Analyze latest recording** after stopping to run full transcription on the captured audio, including a stored history entry.

> Note: The first transcription may take a minute while the WebAssembly bundles download and compile. Keep the tab open—progress is shown in the status banner.

## Deploying to GitHub Pages

The project ships ready for Pages. Point your repository settings to the `docs/` folder or copy the folder into your Pages repo (`rosskuehl1.github.io`). GitHub will deploy automatically on push—no build step necessary.

Recommended checklist before publishing:

1. `npm run dev` (or standalone `npx serve docs`) and open the served URL.
2. Run one or two analyses—ideally both **Voice** and **Electric guitar** modes—to warm the model cache and validate latency.
3. `npm run test` to execute the Playwright smoke suite locally.
4. Commit changes and push to `main`. GitHub Actions runs the same Playwright tests (`.github/workflows/ci.yml`) and must stay green before deploying to Pages.

## Project structure

- `docs/index.html` – Static HTML shell (instrument selector, live insight chips, CI badge, waveform card, history list).
- `docs/assets/styles.css` – Responsive layout, live sentiment visuals, instrument quick-start styling, and component tokens.
- `docs/assets/app.js` – Client-side waveform rendering, live stream analysis, audio resampling, speech transcription, sentiment scoring, instrument-mode tuning, energy/trend analytics, and CI status fetch via GitHub API.
- `package.json`, `playwright.config.ts`, `tests/` – Tooling + smoke tests to keep the Pages-ready bundle healthy.
- `docs/assets/ui-preview.png` – Screenshot used in docs.
- `positive.wav` – Sample clip for manual testing.

## Testing & CI

- **Local** – `npm run test` executes `tests/smoke.spec.ts`, which asserts the plug-and-play guitar workflow UI, CI badge, and instrument selector behaviors.
- **CI** – `.github/workflows/ci.yml` installs dependencies, provisions Chromium via `npx playwright install --with-deps chromium`, runs the smoke suite, and uploads the HTML report artifact on every push & PR.
- **Pages sync** – After CI passes, copy `docs/` into `rosskuehl1.github.io/` (or keep it symlinked) and push. The UI also surfaces CI health in the Live sentiment card, so regressions are visible to end users.

## Browser requirements

- Chromium 115+, Firefox 116+, or any browser with WebAssembly SIMD + Multi-Threading support.
- Microphones are optional but required for realtime streaming; the app also works with recorded files (`.wav`, `.mp3`, `.m4a`, `.aac`, etc.).
- Expect a one-time download of roughly 80 MB for the model pair. Assets are cached by the browser after the first run.

## Legacy tooling

The previous Flask API, desktop overlay, and Python streaming helpers were removed from the main branch. If you still need them, check the git history prior to December 2025.

## License

This project remains open source for personal or educational use.
