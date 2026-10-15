from unittest.mock import patch, MagicMock
from google.genai import errors
from audio.speech_to_text import GeminiTranscriber, TranscriptionError


def _make_transcriber(client):
    transcriber = GeminiTranscriber.__new__(GeminiTranscriber)
    transcriber._max_retries = 2
    transcriber._client = client
    return transcriber


def test_transcribe_uploads_file_and_returns_stripped_text():
    fake_client = MagicMock()
    fake_client.files.upload.return_value = MagicMock()
    fake_client.models.generate_content.return_value = MagicMock(text="  ábreme steam  ")

    result = _make_transcriber(fake_client).transcribe("fake.wav")

    assert result == "ábreme steam"
    fake_client.files.upload.assert_called_once_with(file="fake.wav")
    fake_client.files.delete.assert_called_once()


def test_transcribe_returns_empty_string_when_model_reports_silence():
    fake_client = MagicMock()
    fake_client.files.upload.return_value = MagicMock()
    fake_client.models.generate_content.return_value = MagicMock(text="[silencio]")

    result = _make_transcriber(fake_client).transcribe("fake.wav")

    assert result == ""


def test_transcribe_raises_after_all_retries_fail():
    fake_client = MagicMock()
    fake_client.files.upload.return_value = MagicMock()
    fake_client.models.generate_content.side_effect = errors.ServerError(
        504, {"error": {"message": "timeout"}}, MagicMock()
    )

    with patch("audio.speech_to_text.time.sleep"):
        try:
            _make_transcriber(fake_client).transcribe("fake.wav")
            assert False, "Debería haber lanzado TranscriptionError"
        except TranscriptionError:
            pass