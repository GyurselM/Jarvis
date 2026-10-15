"""
Detección de la palabra de activación ("Hey Jarvis"). Esta pieza solo
analiza trozos de audio que le pasan: no abre el micrófono (de eso se
encarga VoiceCapture), así es fácil de probar y de sustituir.
"""

import numpy as np
from openwakeword.model import Model


class WakeWordDetector:
    """Interfaz que cualquier detector de palabra de activación debe cumplir."""

    sample_rate: int
    frame_samples: int

    def process_frame(self, frame: np.ndarray) -> bool:
        """Analiza un trozo de audio y devuelve True si contiene la palabra."""
        raise NotImplementedError

    def reset(self) -> None:
        """Olvida el audio anterior, para no activarse con restos de la orden previa."""
        raise NotImplementedError

    def close(self) -> None:
        """Libera los recursos del detector."""
        raise NotImplementedError


class OpenWakeWordDetector(WakeWordDetector):
    """
    Implementación con openWakeWord (en Windows se usa ONNX). Solo reacciona
    a los modelos cuyo nombre contenga 'wake_word', por defecto 'jarvis'.

    threshold: de 0 a 1. Más bajo = se activa con más facilidad (y puede
    activarse de más); más alto = más estricto.
    """

    sample_rate = 16000
    frame_samples = 1280  # 80 ms de audio a 16 kHz: el tamaño que espera openWakeWord

    def __init__(self, wake_word: str = "jarvis", threshold: float = 0.25):
        self._wake_word = wake_word
        self._threshold = threshold
        self._model = Model(inference_framework="onnx")

    def process_frame(self, frame: np.ndarray) -> bool:
        predictions = self._model.predict(frame)

        return any(
            score >= self._threshold
            for model_name, score in predictions.items()
            if self._wake_word in model_name.lower()
        )

    def reset(self) -> None:
        self._model.reset()

    def close(self) -> None:
        # openWakeWord no necesita liberar nada explícitamente.
        pass