"""Simple cross-platform Tkinter overlay for audio sentiment analysis."""
import os
import queue
import threading
import time
import tkinter as tk
from tkinter import filedialog, ttk

import speech_recognition as sr

from analysis import analyze_audio_file, classify_sentiment, transcribe_audio_bytes


class SentimentOverlay:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Audio Sentiment Overlay")
        self.root.geometry("640x480")
        self.root.minsize(540, 420)
        self.root.configure(padx=16, pady=16)

        self.recognizer = sr.Recognizer()
        self.language_var = tk.StringVar(value="en-US")
        self.status_var = tk.StringVar(value="Ready")
        self.sentiment_var = tk.StringVar(value="Sentiment: --")

        self._mic_thread: threading.Thread | None = None
        self._mic_active = threading.Event()
        self._results = queue.Queue()

        self._build_layout()
        self._poll_results()

    def _build_layout(self) -> None:
        header = ttk.Label(self.root, text="Audio Sentiment Bot", font=("Helvetica", 18, "bold"))
        header.pack(anchor="w", pady=(0, 12))

        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(fill="x", pady=(0, 12))

        file_button = ttk.Button(controls_frame, text="Open Audio File", command=self._prompt_file)
        file_button.pack(side="left")

        mic_start = ttk.Button(controls_frame, text="Start Listening", command=lambda: self._toggle_microphone(True))
        mic_start.pack(side="left", padx=(12, 0))
        self._mic_start_button = mic_start

        mic_stop = ttk.Button(controls_frame, text="Stop Listening", command=lambda: self._toggle_microphone(False))
        mic_stop.pack(side="left", padx=(12, 0))
        self._mic_stop_button = mic_stop
        self._mic_stop_button.state(["disabled"])

        ttk.Label(controls_frame, text="Language:").pack(side="left", padx=(18, 6))
        languages = ["en-US", "en-GB", "es-ES", "de-DE", "fr-FR"]
        language_box = ttk.Combobox(controls_frame, textvariable=self.language_var, values=languages, width=8)
        language_box.pack(side="left")

        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", pady=(0, 8))
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(anchor="w")

        sentiment_label = ttk.Label(status_frame, textvariable=self.sentiment_var, font=("Helvetica", 12, "bold"))
        sentiment_label.pack(anchor="w", pady=(4, 0))

        self.transcript_box = tk.Text(self.root, wrap="word", height=14)
        self.transcript_box.pack(fill="both", expand=True)
        self.transcript_box.configure(state="disabled")
        self.transcript_box.tag_configure("POSITIVE", foreground="#0a7d3b")
        self.transcript_box.tag_configure("NEGATIVE", foreground="#c0392b")
        self.transcript_box.tag_configure("NEUTRAL", foreground="#2c3e50")
        self.transcript_box.tag_configure("INFO", foreground="#555555")

    def _prompt_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.flac *.aiff *.aif"),
                ("All Files", "*.*"),
            ],
        )
        if not path:
            return

        self.status_var.set(f"Analyzing {os.path.basename(path)}…")
        thread = threading.Thread(target=self._analyze_file_worker, args=(path,), daemon=True)
        thread.start()

    def _analyze_file_worker(self, path: str) -> None:
        try:
            transcript, sentiment = analyze_audio_file(path, language=self.language_var.get())
            self._results.put({
                "type": "file",
                "source": os.path.basename(path),
                "transcript": transcript,
                "sentiment": sentiment,
            })
        except Exception as exc:  # pragma: no cover - UI notify path
            self._results.put({
                "type": "error",
                "message": f"File analysis failed: {exc}",
            })

    def _toggle_microphone(self, enable: bool) -> None:
        if enable and self._mic_active.is_set():
            return
        if not enable and not self._mic_active.is_set():
            return

        if enable:
            self._mic_active.set()
            self._mic_start_button.state(["disabled"])
            self._mic_stop_button.state(["!disabled"])
            self.status_var.set("Listening…")
            self._mic_thread = threading.Thread(target=self._microphone_loop, daemon=True)
            self._mic_thread.start()
        else:
            self._mic_active.clear()
            self._mic_start_button.state(["!disabled"])
            self._mic_stop_button.state(["disabled"])
            self.status_var.set("Stopping microphone…")

    def _microphone_loop(self) -> None:
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                self._results.put({"type": "info", "message": "Microphone calibrated"})
                while self._mic_active.is_set():
                    try:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    except sr.WaitTimeoutError:
                        continue

                    language = self.language_var.get()
                    try:
                        text = transcribe_audio_bytes(audio.get_wav_data(), language=language)
                    except RuntimeError as exc:
                        self._results.put({"type": "error", "message": str(exc)})
                        self._mic_active.clear()
                        break

                    if not text:
                        self._results.put({"type": "info", "message": "Could not understand audio"})
                        continue

                    sentiment = classify_sentiment(text)
                    self._results.put({
                        "type": "microphone",
                        "transcript": text,
                        "sentiment": sentiment,
                        "timestamp": time.strftime("%H:%M:%S"),
                    })
        except Exception as exc:  # pragma: no cover - hardware failure path
            self._results.put({"type": "error", "message": f"Microphone error: {exc}"})
        finally:
            self._mic_active.clear()
            self._results.put({"type": "mic_stopped"})

    def _poll_results(self) -> None:
        while True:
            try:
                payload = self._results.get_nowait()
            except queue.Empty:
                break

            kind = payload.get("type")
            if kind == "file":
                self._display_transcript(payload.get("transcript"), payload.get("sentiment"), f"File · {payload.get('source')}")
                self.status_var.set("Ready")
            elif kind == "microphone":
                label = payload.get("timestamp", "Mic")
                self._display_transcript(payload.get("transcript"), payload.get("sentiment"), f"Mic · {label}")
                self.status_var.set("Listening…")
            elif kind == "mic_stopped":
                self.status_var.set("Ready")
                self._mic_start_button.state(["!disabled"])
                self._mic_stop_button.state(["disabled"])
            elif kind == "info":
                self._append_text(payload.get("message", ""), "INFO")
            elif kind == "error":
                self._append_text(payload.get("message", "Error"), "NEGATIVE")
                self.status_var.set("Ready")
        self.root.after(100, self._poll_results)

    def _display_transcript(self, transcript: str | None, sentiment: dict | None, source: str) -> None:
        text = transcript or "<no speech>"
        label = sentiment["label"] if sentiment else "UNKNOWN"
        score = sentiment["score"] if sentiment else None
        tag = label if label in {"POSITIVE", "NEGATIVE", "NEUTRAL"} else "INFO"
        score_label = f"{score:.2f}" if score is not None else "--"
        header = f"[{source}] {label} ({score_label})\n"
        self._append_text(header, tag)
        self._append_text(f"  {text}\n\n", tag)
        self.sentiment_var.set(f"Sentiment: {label} ({score_label})")

    def _append_text(self, content: str, tag: str) -> None:
        self.transcript_box.configure(state="normal")
        self.transcript_box.insert("end", content, (tag,))
        self.transcript_box.see("end")
        self.transcript_box.configure(state="disabled")


def main() -> None:
    root = tk.Tk()
    SentimentOverlay(root)
    root.mainloop()


if __name__ == "__main__":
    main()
