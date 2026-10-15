"""
Compara dos formas de enviar el audio a Gemini (subiéndolo como archivo
o dentro de la petición), midiendo el tiempo de cada una varias veces.
Es una herramienta de pruebas, no forma parte del asistente.
"""

import os
import tempfile
import time

from google import genai
from google.genai import types

from audio.microphone import record_audio
from config import GEMINI_API_KEY, TRANSCRIPTION_MODEL

PROMPT = (
    "Transcribe exactamente lo que se dice en este audio. "
    "Responde solo con el texto transcrito."
)
ROUNDS = 3


def via_upload(client, audio_path: str) -> str:
    uploaded = client.files.upload(file=audio_path)
    try:
        response = client.models.generate_content(
            model=TRANSCRIPTION_MODEL, contents=[PROMPT, uploaded]
        )
        return response.text.strip()
    finally:
        client.files.delete(name=uploaded.name)


def via_inline(client, audio_path: str) -> str:
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()

    response = client.models.generate_content(
        model=TRANSCRIPTION_MODEL,
        contents=[PROMPT, types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")],
    )
    return response.text.strip()


if __name__ == "__main__":
    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=20_000),
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        audio_path = tmp_file.name

    input("Pulsa Enter y, cuando salga 'habla ahora', di: 'abre el bloc de notas' ")
    record_audio(4, audio_path)

    print(f"Modelo: {TRANSCRIPTION_MODEL}\n")

    try:
        for label, method in (("subir archivo", via_upload), ("dentro de la petición", via_inline)):
            for round_number in range(1, ROUNDS + 1):
                start = time.time()
                try:
                    text = method(client, audio_path)
                    print(f"{label:24s} #{round_number}  {time.time() - start:5.1f}s  -> {text!r}")
                except Exception as error:
                    print(f"{label:24s} #{round_number}  {time.time() - start:5.1f}s  FALLA {type(error).__name__}")
    finally:
        os.remove(audio_path)