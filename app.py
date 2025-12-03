"""Flask application exposing the audio sentiment analysis API and UI."""

import os

from flask import Flask, current_app, jsonify, render_template, request
from flask.typing import ResponseReturnValue

from analysis import analyze_audio_bytes, classify_sentiment, transcribe_audio_bytes


TRANSCRIBE_KEY = "TRANSCRIBE_AUDIO_FN"
CLASSIFY_KEY = "CLASSIFY_SENTIMENT_FN"
DEFAULT_LANGUAGE = "en-US"
LANGUAGE_CHOICES = (
    ("en-US", "English (United States)"),
    ("en-GB", "English (United Kingdom)"),
    ("es-ES", "Spanish (Spain)"),
    ("fr-FR", "French (France)"),
    ("de-DE", "German"),
)
_LANGUAGE_CODES = {code for code, _ in LANGUAGE_CHOICES}


def _normalize_language(raw_value: str | None) -> str:
    cleaned = (raw_value or "").strip() or DEFAULT_LANGUAGE
    return cleaned if cleaned in _LANGUAGE_CODES else DEFAULT_LANGUAGE


ALLOWED_HEADERS = "Content-Type, Accept"
ALLOWED_METHODS = "POST, OPTIONS"


def _set_vary_header(response, header_value: str) -> None:
    """Ensure the Vary header includes the provided value."""

    existing = response.headers.get("Vary")
    if existing:
        if header_value not in {part.strip() for part in existing.split(",")}:
            response.headers["Vary"] = f"{existing}, {header_value}"
    else:
        response.headers["Vary"] = header_value


def create_app(
    transcribe_fn=transcribe_audio_bytes,
    classify_fn=classify_sentiment,
) -> Flask:
    """App factory that supports dependency injection for easier testing."""

    app = Flask(__name__)
    app.config[TRANSCRIBE_KEY] = transcribe_fn
    app.config[CLASSIFY_KEY] = classify_fn
    app.config.setdefault(
        "CORS_ORIGIN",
        os.environ.get("AUDIO_SENTIMENT_BOT_CORS_ORIGIN", "*"),
    )

    @app.after_request
    def _apply_cors_headers(response):
        origin = current_app.config.get("CORS_ORIGIN")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = ALLOWED_HEADERS
            response.headers["Access-Control-Allow-Methods"] = ALLOWED_METHODS
            if origin != "*":
                _set_vary_header(response, "Origin")
        return response

    @app.route("/analyze", methods=["POST", "OPTIONS"])
    def analyze() -> ResponseReturnValue:
        """Accept multipart audio uploads and return transcript plus sentiment."""

        if request.method == "OPTIONS":
            return ("", 204)

        transcribe = current_app.config[TRANSCRIBE_KEY]
        classify = current_app.config[CLASSIFY_KEY]

        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        if audio_file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        language = _normalize_language(request.form.get("language"))
        file_name = audio_file.filename
        audio_bytes = audio_file.read()

        try:
            transcript, sentiment = analyze_audio_bytes(
                audio_bytes,
                language=language,
                transcribe_fn=transcribe,
                classify_fn=classify,
            )
        except RuntimeError as exc:
            payload = {
                "error": str(exc),
                "transcript": "",
                "sentiment": None,
                "language": language,
                "fileName": file_name,
            }
            return jsonify(payload), 500

        if not transcript:
            payload = {
                "transcript": "",
                "sentiment": None,
                "error": "Could not transcribe audio",
                "language": language,
                "fileName": file_name,
            }
            return jsonify(payload), 200

        return jsonify(
            {
                "transcript": transcript,
                "sentiment": sentiment,
                "language": language,
                "fileName": file_name,
            }
        )

    @app.route("/")
    def index():
        return render_template("index.html", languages=LANGUAGE_CHOICES)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6142, debug=True)
