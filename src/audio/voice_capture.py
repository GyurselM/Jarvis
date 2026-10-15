"""
Captura de voz continua: mantiene UN solo micrófono abierto, espera la
palabra de activación y, sin soltarlo, graba la orden hasta que el
usuario deja de hablar. Así no se pierde nada entre "Hey Jarvis" y la orden.
"""

import numpy as np
import sounddevice as sd
import soundfile as sf

from audio.wake_word import WakeWordDetector


class VoiceCapture:
    """
    speech_threshold: volumen medio a partir del cual un trozo cuenta como voz.
    silence_seconds: silencio que marca el final de la orden.
    max_command_seconds: duración máxima de una orden.
    no_speech_timeout: si tras activarse no se oye voz en este tiempo, se descarta.
    """

    def __init__(
        self,
        detector: WakeWordDetector,
        speech_threshold: float = 100,
        silence_seconds: float = 0.8,
        max_command_seconds: float = 8.0,
        no_speech_timeout: float = 3.0,
    ):
        frame_seconds = detector.frame_samples / detector.sample_rate

        self._detector = detector
        self._speech_threshold = speech_threshold
        self._silence_limit = round(silence_seconds / frame_seconds)
        self._max_frames = round(max_command_seconds / frame_seconds)
        self._no_speech_limit = round(no_speech_timeout / frame_seconds)

    def wait_and_record(self, output_path: str) -> bool:
        """
        Bloquea hasta oír la palabra de activación y graba la orden en
        output_path. Devuelve True si grabó una orden, o False si se
        activó pero no se oyó a nadie hablar después.
        """
        self._detector.reset()

        with sd.InputStream(
            samplerate=self._detector.sample_rate,
            blocksize=self._detector.frame_samples,
            channels=1,
            dtype="int16",
        ) as stream:
            self._wait_for_wake_word(stream)
            frames = self._record_command(stream)

        if frames is None:
            return False

        sf.write(
            output_path,
            np.concatenate(frames),
            self._detector.sample_rate,
            subtype="PCM_16",
        )
        return True

    def _read_frame(self, stream) -> np.ndarray:
        data, _overflowed = stream.read(self._detector.frame_samples)
        return data[:, 0]

    def _wait_for_wake_word(self, stream) -> None:
        while True:
            if self._detector.process_frame(self._read_frame(stream)):
                return

    def _is_speech(self, frame: np.ndarray) -> bool:
        # astype(int32) evita un desbordamiento al calcular el valor absoluto en int16.
        return np.abs(frame.astype(np.int32)).mean() >= self._speech_threshold

    def _record_command(self, stream) -> list[np.ndarray] | None:
        frames = []
        heard_speech = False
        silent_frames = 0

        while len(frames) < self._max_frames:
            frame = self._read_frame(stream)
            frames.append(frame)

            if self._is_speech(frame):
                heard_speech = True
                silent_frames = 0
            else:
                silent_frames += 1

            if heard_speech and silent_frames >= self._silence_limit:
                break

            if not heard_speech and len(frames) >= self._no_speech_limit:
                return None

        return frames