from unittest.mock import patch, MagicMock
from google.genai import errors
from audio.speech_to_text import GeminiTranscriber, TranscriptionError


def test_transcribe_returns_stripped_response_text():
    transcriber = GeminiTranscriber.__new__(GeminiTranscriber)
    transcriber._max_retries = 2
    fake_client = MagicMock()
    fake_response = MagicMock(text="  ábreme steam  ")
    fake_client.models.generate_content.return_value = fake_response
    transcriber._client = fake_client

    with patch("audio.speech_to_text.open", create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = b"fake_audio"
        result = transcriber.transcribe("fake.wav")

    assert result == "ábreme steam"


def test_transcribe_raises_after_all_retries_fail():
    transcriber = GeminiTranscriber.__new__(GeminiTranscriber)
    transcriber._max_retries = 2
    fake_client = MagicMock()
    fake_client.models.generate_content.side_effect = errors.ServerError(
        504, {"error": {"message": "timeout"}}, MagicMock()
    )
    transcriber._client = fake_client

    with patch("audio.speech_to_text.open", create=True) as mock_open, \
         patch("audio.speech_to_text.time.sleep"):
        mock_open.return_value.__enter__.return_value.read.return_value = b"fake_audio"

        try:
            transcriber.transcribe("fake.wav")
            assert False, "Debería haber lanzado TranscriptionError"
        except TranscriptionError:
            pass