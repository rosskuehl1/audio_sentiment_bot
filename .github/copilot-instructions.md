# Audio Sentiment Bot – AI Agent Guide

## Mission Priorities
- Deliver a natural plug-and-play experience: a guitarist should connect, play, and instantly get meaningful, visually engaging sentiment feedback powered by lively visualizations and clever computations.
- Modernize the audio analyzer UI first: responsive layout, realtime sentiment feedback, and recording UX live in `docs/index.html`, `docs/assets/styles.css`, and `docs/assets/app.js`.
- Keep `docs/` deployment-ready; every commit should be safe to push straight to `rosskuehl1.github.io` for Pages + Playwright smoke tests, with CI/CD fully integrated end-to-end.
- Treat `https://rosskuehl1.github.io/` as the canonical production host—optimize iteration speed around that URL.

## Architecture (browser-only)
- Zero-backend: all logic sits in `docs/assets/app.js`, using `@xenova/transformers` via jsDelivr to run Whisper Tiny + DistilBERT fully in the browser.
- `docs/index.html` defines the shell: upload form, recording controls, live meter, waveform canvas, and history list. Keep IDs/data attributes stable so JS hooks remain valid.
- `docs/assets/styles.css` contains design tokens (panels, badges, tone colors). Update here to rebrand; JS only toggles `data-tone` attributes.
- State lives in a single `state` object (buffers, recording stream, live analysis metadata). Reuse helpers instead of introducing globals to avoid race conditions.

## Core Workflows
- **Local preview**: `cd audio_sentiment_bot && npx serve docs` then visit the printed URL. Chrome/Edge/Firefox with WebAssembly SIMD is required.
- **Live recording**: `startRecording()` wires `MediaStream`, `AnalyserNode`, and ScriptProcessor to collect Float32 chunks. Keep chunk size + `LIVE_ANALYSIS_*` constants aligned when tweaking latency.
- **Waveform + metadata**: `drawWaveform` and `drawLiveWaveform` are the only places touching `<canvas>`. When changing layout, adjust both static preview and live mic renderer.
- **Model bootstrap**: `ensurePipelines()` emits status updates while loading models. Any UX changes must preserve these status messages so users know why the UI is idle.

## Integration & Deployment
- Pages deploys directly from `docs/`. Avoid build steps; if you add tooling, ensure the generated assets still land inside `docs/` before commit.
- GitHub Pages + Playwright CI hits `https://rosskuehl1.github.io/`. Keep selectors stable (data attributes) to avoid breaking tests.
- When iterating, mirror changes into `rosskuehl1.github.io` (sibling repo) or symlink the `docs/` folder to keep deployments in sync.

## Testing & Diagnostics
- Manual smoke: `npx serve docs`, drop `positive.wav`, then run mic streaming; confirm history cards populate and the live gauge updates every ~3s.
- Browser console is the primary log surface; `setStatus`/`setRecordingStatus` should always reflect actionable errors (decode failure, mic denial, etc.).
- If live sentiment stalls, inspect `state.liveAnalysis` (`pendingPromise`, `lastProcessedSamples`). Don’t add new async loops—extend `queueLiveAnalysis()` instead.

## Coding Conventions
- Keep everything ES modules compliant; no bundler transforms are assumed.
- Reuse helpers (`mixToMono`, `resample`, `analyzeAudioInput`) rather than inlining new logic—this keeps waveform preview, file analysis, and recording analysis behavior identical.
- Data attributes (`data-form`, `data-live-card`, etc.) double as Playwright selectors. If UI changes require new markup, update tests accordingly in `rosskuehl1.github.io`.
- Limit clip length to `MAX_DURATION_SECONDS` (90s). When changing, adjust UI copy in `index.html` and validation logic in `analyzeAudioInput` simultaneously.

## External Dependencies
- `@xenova/transformers@2.8.0` is loaded straight from CDN. Upgrades must be tested offline to ensure caching + WASM threading still work.
- No server APIs remain; removing or breaking client-only behaviors regresses the live site immediately.

## When In Doubt
- Optimize for the GitHub Pages experience first; legacy Flask/Python files exist only in history.
- Ask for UX feedback if a change could affect Playwright flows (record start/stop, analyze latest recording, history prepend).
