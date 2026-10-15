"""
Configuración central del proyecto. Cualquier valor sensible o
configurable (claves API, modelos, settings) se lee aquí una sola vez.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Modelos de Gemini. Cambiar de modelo es editar solo estas dos líneas.
# Alternativa estable (más lenta): "gemini-flash-lite-latest".
TRANSCRIPTION_MODEL = "gemini-3.1-flash-lite-preview"
ROUTER_MODEL = "gemini-3.1-flash-lite-preview"

if not GEMINI_API_KEY:
    raise RuntimeError(
        "Falta GEMINI_API_KEY en el archivo .env. "
        "Copia .env.example a .env y añade tu clave."
    )