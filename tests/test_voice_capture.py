import numpy as np
from unittest.mock import patch, MagicMock
from audio.voice_capture import VoiceCapture
from audio.wake_word import WakeWordDetector

FRAME = 1280


class FakeDetector(WakeWordDetector):
    sample_rate = 16000
    frame_samples = FRAME

    def __init__(self, wake_on_call):
        self._calls = 0
        self._wake_on_call = wake_on_call
        self.reset_called = False

    def process_frame(self, frame):
        self._calls += 1
        return self._calls >= self._wake_on_call

    def reset(self):
        self.reset_called = True

    def close(self):
        pass


def _loud():
    return np.full(FRAME, 1000, dtype=np.int16)


def _silent():
    return np.zeros(FRAME, dtype=np.int16)


def _fake_stream_context(frames):
    iterator = iter(frames)
    fake_stream = MagicMock()
    fake_stream.read.side_effect = lambda n: (next(iterator).reshape(-1, 1), False)
    context = MagicMock()
    context.__enter__.return_value = fake_stream
    context.__exit__.return_value = False
    return context


def _make_capture(detector):
    # Con frames de 80 ms: silencio final = 2 frames, sin voz = 5 frames.
    return VoiceCapture(
        detector,
        speech_threshold=100,
        silence_seconds=0.16,
        max_command_seconds=2.0,
        no_speech_timeout=0.4,
    )


def test_records_command_until_silence_without_gap_after_wake_word():
    detector = FakeDetector(wake_on_call=1)
    # 1 trozo para activar, luego la orden (2 con voz + 2 de silencio),
    # y un trozo final que NO debe llegar a leerse.
    frames = [_silent(), _loud(), _loud(), _silent(), _silent(), _loud()]

    with patch("audio.voice_capture.sd.InputStream", return_value=_fake_stream_context(frames)), \
         patch("audio.voice_capture.sf.write") as mock_write:
        result = _make_capture(detector).wait_and_record("orden.wav")

    assert result is True
    assert detector.reset_called is True
    recorded = mock_write.call_args.args[1]
    assert recorded.shape == (4 * FRAME,)


def test_returns_false_when_nobody_speaks_after_wake_word():
    detector = FakeDetector(wake_on_call=1)
    frames = [_silent()] * 7

    with patch("audio.voice_capture.sd.InputStream", return_value=_fake_stream_context(frames)), \
         patch("audio.voice_capture.sf.write") as mock_write:
        result = _make_capture(detector).wait_and_record("orden.wav")

    assert result is False
    mock_write.assert_not_called()