import numpy as np
from unittest.mock import patch, MagicMock
from audio.wake_word import OpenWakeWordDetector


def _make_detector(predictions, **kwargs):
    fake_model = MagicMock()
    fake_model.predict.side_effect = predictions

    with patch("audio.wake_word.Model", return_value=fake_model):
        detector = OpenWakeWordDetector(**kwargs)

    return detector, fake_model


def _frame():
    return np.zeros(OpenWakeWordDetector.frame_samples, dtype=np.int16)


def test_process_frame_true_when_score_above_threshold():
    detector, _ = _make_detector([{"hey_jarvis": 0.90}])
    assert detector.process_frame(_frame()) is True


def test_process_frame_false_when_score_below_threshold():
    detector, _ = _make_detector([{"hey_jarvis": 0.10}])
    assert detector.process_frame(_frame()) is False


def test_process_frame_ignores_other_wake_words():
    detector, _ = _make_detector([{"alexa": 0.99, "hey_jarvis": 0.10}])
    assert detector.process_frame(_frame()) is False


def test_reset_resets_the_model():
    detector, fake_model = _make_detector([])
    detector.reset()
    fake_model.reset.assert_called_once()