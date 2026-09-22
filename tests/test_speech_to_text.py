from unittest.mock import patch, MagicMock
from google.genai import errors
from audio.speech_to_text import GeminiTranscriber, TranscriptionError


def test_transcribe_uploads_file_and_returns_stripped_text():
    transcriber = GeminiTranscriber.__new__(GeminiTranscriber)
    transcriber._max_retries = 2

    fake_client = MagicMock()
    fake_uploaded_file = MagicMock()
    fake_client.files.upload.return_value = fake_uploaded_file
    fake_response = MagicMock(text="  ábreme steam  ")
    fake_client.models.generate_content.return_value = fake_response
    transcriber._client = fake_client

    result = transcriber.transcribe("fake.wav")

    assert result == "ábreme steam"
    fake_client.files.upload.assert_called_once_with(file="fake.wav")
    fake_client.files.delete.assert_called_once()


def test_transcribe_raises_after_all_retries_fail():
    transcriber = GeminiTranscriber.__new__(GeminiTranscriber)
    transcriber._max_retries = 2

    fake_client = MagicMock()
    fake_client.files.upload.return_value = MagicMock()
    fake_client.models.generate_content.side_effect = errors.ServerError(
        504, {"error": {"message": "timeout"}}, MagicMock()
    )
    transcriber._client = fake_client

    with patch("audio.speech_to_text.time.sleep"):
        try:
            transcriber.transcribe("fake.wav")
            assert False, "Debería haber lanzado TranscriptionError"
        except TranscriptionError:
            pass