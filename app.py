# app.py
import io
import os
from flask import Flask, request, jsonify
import speech_recognition as sr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# 1. Load the sentiment analysis model once (heavy operation)
sentiment_analyzer = SentimentIntensityAnalyzer()

# 2. Helper: transcribe audio bytes (WAV or MP3)
def transcribe_audio(audio_bytes, language="en-US"):
    recognizer = sr.Recognizer()
    # Use a temporary in‑memory file
    # sr.AudioFile accepts a filename or any file-like object; BytesIO keeps it in memory
    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
        audio_data = recognizer.record(source)
    try:
        # Google Web Speech API (free quota ~ 60 sec per request)
        text = recognizer.recognize_google(audio_data, language=language)
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError as e:
        raise RuntimeError(f"Speech API error: {e}")
    return text

# 3. Endpoint: POST /analyze
@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Expects multipart/form-data with a file field named 'audio'.
    Returns JSON: { "transcript": "...", "sentiment": {"label":"POSITIVE","score":0.99} }
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Read raw bytes
    audio_bytes = audio_file.read()

    try:
        transcript = transcribe_audio(audio_bytes)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    if not transcript:
        return jsonify({"transcript": "", "sentiment": None, "error":"Could not transcribe audio"}), 200

    # Run sentiment analysis with VADER's compound score
    scores = sentiment_analyzer.polarity_scores(transcript)
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

    sentiment = {"label": label, "score": round(confidence, 4)}

    return jsonify({
        "transcript": transcript,
        "sentiment": sentiment
    })

# 4. Simple home page for quick test
@app.route("/")
def index():
    return """
    <h1>Audio Sentiment Bot</h1>
    <p>Send a POST request to /analyze with an audio file (WAV/MP3).</p>
    """

# 5. Run
if __name__ == "__main__":
    # For local dev; set host=0.0.0.0 to expose
    app.run(host="0.0.0.0", port=6142, debug=True)
