import io

import analysis
from app import create_app


def test_full_pipeline_integration(monkeypatch):
    def fake_transcribe(audio_bytes, language="en-US"):
        assert audio_bytes == b"audio"
        assert language == "en-US"
        return "What a wonderful day"

    class _Analyzer:
        def polarity_scores(self, text):
            assert text == "What a wonderful day"
            return {"compound": 0.32}

    monkeypatch.setattr(analysis, "_sentiment_analyzer", _Analyzer())

    app = create_app(transcribe_fn=fake_transcribe)
    app.config.update(TESTING=True)
    client = app.test_client()

    data = {"audio": (io.BytesIO(b"audio"), "clip.wav")}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["transcript"] == "What a wonderful day"
    assert payload["sentiment"] == {"label": "POSITIVE", "score": 0.32}
