import io

from app import create_app


def _make_client(transcribe_fn, classify_fn):
    app = create_app(transcribe_fn=transcribe_fn, classify_fn=classify_fn)
    app.config.update(TESTING=True)
    return app.test_client()


def test_options_preflight_respects_configured_origin():
    def fake_transcribe(_audio_bytes, language="en-US"):
        return ""

    app = create_app(transcribe_fn=fake_transcribe, classify_fn=lambda *_a, **_k: None)
    app.config.update(TESTING=True, CORS_ORIGIN="https://example.com")
    client = app.test_client()

    response = client.options("/analyze", headers={"Origin": "https://irrelevant"})

    assert response.status_code == 204
    assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
    assert "POST" in response.headers["Access-Control-Allow-Methods"]
    assert "Content-Type" in response.headers["Access-Control-Allow-Headers"]
    assert "Origin" in response.headers.get("Vary", "")


def test_missing_audio_returns_400():
    client = _make_client(lambda *_args, **_kwargs: "", lambda *_args, **_kwargs: None)
    response = client.post("/analyze")
    assert response.status_code == 400
    assert response.get_json()["error"] == "No audio file provided"


def test_empty_filename_returns_400():
    client = _make_client(lambda *_args, **_kwargs: "", lambda *_args, **_kwargs: None)
    data = {"audio": (io.BytesIO(b"test"), "")}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Empty filename"


def test_transcription_empty_returns_warning_without_classification():
    classify_calls = []

    def fake_transcribe(_audio_bytes, language="en-US"):
        assert language == "en-US"
        return ""

    def fake_classify(transcript):
        classify_calls.append(transcript)
        return {"label": "POSITIVE", "score": 0.9}

    client = _make_client(fake_transcribe, fake_classify)
    data = {"audio": (io.BytesIO(b"fake"), "clip.wav")}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["transcript"] == ""
    assert payload["sentiment"] is None
    assert payload["error"] == "Could not transcribe audio"
    assert payload["fileName"] == "clip.wav"
    assert not classify_calls


def test_successful_analysis_uses_injected_fns():
    def fake_transcribe(audio_bytes, language="en-US"):
        assert audio_bytes == b"abc"
        assert language == "en-GB"
        return "I love testing"

    def fake_classify(transcript):
        assert transcript == "I love testing"
        return {"label": "POSITIVE", "score": 0.88}

    client = _make_client(fake_transcribe, fake_classify)
    data = {"audio": (io.BytesIO(b"abc"), "clip.wav"), "language": "en-GB"}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["language"] == "en-GB"
    assert payload["sentiment"] == {"label": "POSITIVE", "score": 0.88}
    assert payload["fileName"] == "clip.wav"


def test_blank_language_defaults_to_en_us():
    def fake_transcribe(_audio_bytes, language="en-US"):
        assert language == "en-US"
        return "Hooray"

    def fake_classify(transcript):
        assert transcript == "Hooray"
        return {"label": "NEUTRAL", "score": 0.5}

    client = _make_client(fake_transcribe, fake_classify)
    data = {"audio": (io.BytesIO(b"abc"), "clip.wav"), "language": "   "}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["language"] == "en-US"
    assert payload["transcript"] == "Hooray"
    assert payload["sentiment"] == {"label": "NEUTRAL", "score": 0.5}
    assert payload["fileName"] == "clip.wav"


def test_invalid_language_defaults_to_en_us():
    def fake_transcribe(_audio_bytes, language="en-US"):
        assert language == "en-US"
        return "Testing"

    def fake_classify(transcript):
        assert transcript == "Testing"
        return {"label": "NEUTRAL", "score": 0.51}

    client = _make_client(fake_transcribe, fake_classify)
    data = {"audio": (io.BytesIO(b"abc"), "clip.wav"), "language": "zz-ZZ"}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["language"] == "en-US"
    assert payload["fileName"] == "clip.wav"
    assert payload["sentiment"] == {"label": "NEUTRAL", "score": 0.51}


def test_transcription_failure_is_returned_as_500():
    def fake_transcribe(_audio_bytes, language="en-US"):
        raise RuntimeError("Boom")

    client = _make_client(fake_transcribe, lambda *_args, **_kwargs: None)
    data = {"audio": (io.BytesIO(b"abc"), "clip.wav")}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    payload = response.get_json()

    assert response.status_code == 500
    assert payload["error"] == "Boom"
    assert payload["sentiment"] is None
    assert payload["fileName"] == "clip.wav"
