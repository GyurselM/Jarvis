from unittest.mock import patch
from audio.microphone import record_audio


def test_record_audio_calls_sounddevice_and_saves_file():
    with patch("audio.microphone.sd.rec") as mock_rec, \
         patch("audio.microphone.sd.wait") as mock_wait, \
         patch("audio.microphone.sf.write") as mock_write:
        mock_rec.return_value = "fake_recording_array"

        result = record_audio(duration_seconds=3, output_path="test.wav")

    mock_rec.assert_called_once()
    mock_wait.assert_called_once()
    mock_write.assert_called_once_with("test.wav", "fake_recording_array", 16000)
    assert result == "test.wav"