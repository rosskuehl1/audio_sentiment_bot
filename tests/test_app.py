import io

from app import create_app


def _make_client(transcribe_fn, classify_fn):
    app = create_app(transcribe_fn=transcribe_fn, classify_fn=classify_fn)
    app.config.update(TESTING=True)
    return app.test_client()


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
