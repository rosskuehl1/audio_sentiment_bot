import analysis
import pytest


class _DummyAudioFile:
    def __init__(self, _buffer):
        self._entered = False

    def __enter__(self):
        self._entered = True
        return "source"

    def __exit__(self, _exc_type, _exc, _tb):
        return False


class _DummyRecognizer:
    def __init__(self, exception):
        self._exception = exception
        self.recorded = False

    def record(self, source):
        assert source == "source"
        self.recorded = True
        return "audio-chunk"

    def recognize_google(self, _audio_data, language="en-US"):
        assert language == "en-US"
        raise self._exception


def test_transcribe_returns_empty_on_unknown(monkeypatch):
    recognizer = _DummyRecognizer(analysis.sr.UnknownValueError())
    monkeypatch.setattr(analysis.sr, "Recognizer", lambda: recognizer)
    monkeypatch.setattr(analysis.sr, "AudioFile", lambda _buffer: _DummyAudioFile(_buffer))

    result = analysis.transcribe_audio_bytes(b"data", language="en-US")

    assert result == ""
    assert recognizer.recorded is True


def test_transcribe_wraps_request_errors(monkeypatch):
    recognizer = _DummyRecognizer(analysis.sr.RequestError("no network"))
    monkeypatch.setattr(analysis.sr, "Recognizer", lambda: recognizer)
    monkeypatch.setattr(analysis.sr, "AudioFile", lambda _buffer: _DummyAudioFile(_buffer))

    with pytest.raises(RuntimeError) as excinfo:
        analysis.transcribe_audio_bytes(b"data", language="en-US")

    assert "Speech API error: no network" in str(excinfo.value)
    assert recognizer.recorded is True


@pytest.mark.parametrize(
    "compound,label,score",
    [
        (0.9, "POSITIVE", 0.9),
        (-0.42, "NEGATIVE", 0.42),
        (0.0, "NEUTRAL", 1.0),
        (0.04, "NEUTRAL", 0.96),
    ],
)
def test_classify_sentiment_branches(monkeypatch, compound, label, score):
    class _FakeAnalyzer:
        def polarity_scores(self, _text):
            return {"compound": compound}

    monkeypatch.setattr(analysis, "_sentiment_analyzer", _FakeAnalyzer())

    result = analysis.classify_sentiment("text")

    assert result == {"label": label, "score": pytest.approx(score, abs=1e-4)}


def test_classify_sentiment_returns_none_for_empty():
    assert analysis.classify_sentiment("") is None
    assert analysis.classify_sentiment(None) is None


def test_analyze_audio_bytes_uses_injected_functions():
    calls = {"transcribe": None, "classify": None}

    def fake_transcribe(data, language="en-US"):
        calls["transcribe"] = (data, language)
        return "bonjour"

    def fake_classify(text):
        calls["classify"] = text
        return {"label": "NEUTRAL", "score": 0.8}

    transcript, sentiment = analysis.analyze_audio_bytes(
        b"bytes",
        language="fr-FR",
        transcribe_fn=fake_transcribe,
        classify_fn=fake_classify,
    )

    assert transcript == "bonjour"
    assert sentiment == {"label": "NEUTRAL", "score": 0.8}
    assert calls["transcribe"] == (b"bytes", "fr-FR")
    assert calls["classify"] == "bonjour"


def test_analyze_audio_file_delegates(tmp_path, monkeypatch):
    audio_path = tmp_path / "clip.wav"
    audio_path.write_bytes(b"binary")

    def fake_transcribe(audio_bytes, language="en-US"):
        assert audio_bytes == b"binary"
        assert language == "fr-FR"
        return "bonjour"

    def fake_classify(transcript):
        assert transcript == "bonjour"
        return {"label": "NEUTRAL", "score": 0.77}

    monkeypatch.setattr(analysis, "transcribe_audio_bytes", fake_transcribe)
    monkeypatch.setattr(analysis, "classify_sentiment", fake_classify)

    transcript, sentiment = analysis.analyze_audio_file(str(audio_path), language="fr-FR")

    assert transcript == "bonjour"
    assert sentiment == {"label": "NEUTRAL", "score": 0.77}
