"""Compatibility shim for Python 3.13+ where the stdlib aifc module was removed.

This provides the minimal surface that SpeechRecognition expects, without
implementing full AIFF parsing. Attempting to open an AIFF file will raise an
error that clearly states the limitation.
"""

class Error(NotImplementedError):
    """Raised when AIFF functionality is requested but not available."""


def open(*_args, **_kwargs):  # noqa: D401 (simple wrapper)
    """Raise an informative error because AIFF support is unavailable."""
    raise Error(
        "AIFF decoding is not supported on this Python build. Convert audio to WAV instead."
    )
