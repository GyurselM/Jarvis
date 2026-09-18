"""
Voz a texto: transcribe un archivo de audio usando Gemini,
sin necesitar ningún modelo local descargado.
"""

import time

from google import genai
from google.genai import types, errors
from config import GEMINI_API_KEY


class Transcriber:
    """Interfaz que cualquier motor de voz a texto debe cumplir."""

    def transcribe(self, audio_path: str) -> str:
        raise NotImplementedError


class TranscriptionError(Exception):
    """Se lanza cuando la transcripción falla tras los reintentos."""


class GeminiTranscriber(Transcriber):
    def __init__(self, max_retries: int = 2):
        self._client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=30_000),  # 30 segundos
        )
        self._max_retries = max_retries

    def transcribe(self, audio_path: str) -> str:
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        last_error = None

        for attempt in range(1, self._max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=[
                        "Transcribe exactamente lo que se dice en este audio. "
                        "Responde solo con el texto transcrito, sin comentarios "
                        "adicionales ni puntuación extra.",
                        types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                    ],
                )
                return response.text.strip()

            except errors.ServerError as error:
                last_error = error
                print(f"Intento {attempt} falló (error del servidor), reintentando...")
                time.sleep(2)

        raise TranscriptionError(
            f"No se pudo transcribir tras {self._max_retries} intentos: {last_error}"
        )