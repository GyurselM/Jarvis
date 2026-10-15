"""
Voz a texto: transcribe un archivo de audio usando Gemini,
sin necesitar ningún modelo local descargado.
"""

import time

from google import genai
from google.genai import types, errors
from config import GEMINI_API_KEY, TRANSCRIPTION_MODEL

NO_SPEECH_MARKER = "[silencio]"

TRANSCRIPTION_PROMPT = (
    "Transcribe exactamente lo que se dice en este audio. "
    "Escribe los números con cifras (por ejemplo 6, no seis). "
    f"Si en el audio no se oye a nadie hablar, responde exactamente: {NO_SPEECH_MARKER} "
    "Responde solo con el texto transcrito, sin comentarios adicionales."
)


class Transcriber:
    """Interfaz que cualquier motor de voz a texto debe cumplir."""

    def transcribe(self, audio_path: str) -> str:
        """Devuelve el texto dicho, o una cadena vacía si no se oyó a nadie."""
        raise NotImplementedError


class TranscriptionError(Exception):
    """Se lanza cuando la transcripción falla tras los reintentos."""


class GeminiTranscriber(Transcriber):
    def __init__(self, max_retries: int = 3):
        self._client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=10_000),
        )
        self._max_retries = max_retries

    def transcribe(self, audio_path: str) -> str:
        last_error = None

        for attempt in range(1, self._max_retries + 1):
            uploaded_file = None
            try:
                uploaded_file = self._client.files.upload(file=audio_path)

                response = self._client.models.generate_content(
                    model=TRANSCRIPTION_MODEL,
                    contents=[TRANSCRIPTION_PROMPT, uploaded_file],
                )

                text = response.text.strip()
                return "" if NO_SPEECH_MARKER in text.lower() else text

            except errors.ServerError as error:
                last_error = error
                print(f"Intento {attempt} de {self._max_retries} falló (error del servidor).")
                if attempt < self._max_retries:
                    time.sleep(2 ** attempt)  # espera progresiva: 2 s, 4 s...

            finally:
                if uploaded_file is not None:
                    self._client.files.delete(name=uploaded_file.name)

        raise TranscriptionError(
            f"No se pudo transcribir tras {self._max_retries} intentos: {last_error}"
        )