"""Command line microphone streaming for real-time sentiment analysis."""

import sys

import speech_recognition as sr

from analysis import classify_sentiment, transcribe_audio_bytes


def _print_result(transcript: str, sentiment: dict | None) -> None:
    label = sentiment["label"] if sentiment else "UNKNOWN"
    score = sentiment["score"] if sentiment else None
    score_display = f"{score:.2f}" if isinstance(score, (int, float)) else "--"
    body = transcript or "<no speech>"
    print(f"\nText: {body}\nSentiment: {label} ({score_display})\n")


def _stream_loop(recognizer: sr.Recognizer, microphone: sr.Microphone, language: str) -> None:
    print("Calibrating microphone…")
    recognizer.adjust_for_ambient_noise(microphone)
    print("Ready. Speak now… (press Ctrl+C to stop)")

    while True:
        try:
            audio = recognizer.listen(microphone, timeout=1, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            continue

        try:
            transcript = transcribe_audio_bytes(audio.get_wav_data(), language=language)
        except RuntimeError as exc:
            print(f"Speech API error: {exc}")
            break

        if not transcript:
            _print_result("", None)
            continue

        sentiment = classify_sentiment(transcript)
        _print_result(transcript, sentiment)


def main(language: str = "en-US") -> None:
    recognizer = sr.Recognizer()
    with sr.Microphone() as microphone:
        _stream_loop(recognizer, microphone, language)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping stream.")
        sys.exit(0)
