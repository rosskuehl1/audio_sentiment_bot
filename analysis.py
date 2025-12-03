"""Shared transcription and sentiment helpers."""
import io
from typing import Optional, Tuple

import speech_recognition as sr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_sentiment_analyzer = SentimentIntensityAnalyzer()


def transcribe_audio_bytes(audio_bytes: bytes, language: str = "en-US") -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data, language=language)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as exc:  # pragma: no cover - network failure path
        raise RuntimeError(f"Speech API error: {exc}") from exc


def classify_sentiment(transcript: str) -> Optional[dict]:
    if not transcript:
        return None

    scores = _sentiment_analyzer.polarity_scores(transcript)
    compound = scores["compound"]
    if compound >= 0.05:
        label = "POSITIVE"
        confidence = compound
    elif compound <= -0.05:
        label = "NEGATIVE"
        confidence = abs(compound)
    else:
        label = "NEUTRAL"
        confidence = 1 - abs(compound)

    return {"label": label, "score": round(confidence, 4)}


def analyze_audio_file(file_path: str, language: str = "en-US") -> Tuple[str, Optional[dict]]:
    with open(file_path, "rb") as audio_stream:
        audio_bytes = audio_stream.read()

    transcript = transcribe_audio_bytes(audio_bytes, language=language)
    sentiment = classify_sentiment(transcript)
    return transcript, sentiment
