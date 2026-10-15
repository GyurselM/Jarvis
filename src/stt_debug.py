"""
Diagnóstico de transcripción: graba una orden y la prueba con varios
modelos de Gemini, midiendo tiempo y resultado de cada uno. Es una
herramienta de pruebas, no forma parte del asistente.
"""

import os
import tempfile
import time

from google import genai
from google.genai import types

from audio.microphone import record_audio
from config import GEMINI_API_KEY

PROMPT = (
    "Transcribe exactamente lo que se dice en este audio. "
    "Responde solo con el texto transcrito."
)
EXCLUDED_WORDS = ("image", "tts", "live", "audio", "embedding")
MAX_MODELS = 6


def candidate_models(client) -> list[str]:
    names = ["gemini-flash-latest"]

    for model in client.models.list():
        name = model.name.removeprefix("models/")
        actions = getattr(model, "supported_actions", None) or []

        if (
            "flash" in name
            and (not actions or "generateContent" in actions)
            and not any(word in name for word in EXCLUDED_WORDS)
            and name not in names
        ):
            names.append(name)

    return names[:MAX_MODELS]


if __name__ == "__main__":
    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=20_000),
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        audio_path = tmp_file.name

    input("Pulsa Enter y, cuando salga 'habla ahora', di: 'abre el bloc de notas' ")
    record_audio(4, audio_path)

    uploaded = client.files.upload(file=audio_path)

    try:
        for name in candidate_models(client):
            start = time.time()
            try:
                response = client.models.generate_content(
                    model=name, contents=[PROMPT, uploaded]
                )
                seconds = time.time() - start
                print(f"OK    {name:38s} {seconds:5.1f}s -> {response.text.strip()!r}")
            except Exception as error:
                seconds = time.time() - start
                print(f"FALLA {name:38s} {seconds:5.1f}s -> {type(error).__name__}: {str(error)[:70]}")
    finally:
        client.files.delete(name=uploaded.name)
        os.remove(audio_path)