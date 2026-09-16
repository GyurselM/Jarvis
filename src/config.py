"""
Configuración central del proyecto. Cualquier valor sensible o
configurable (claves API, settings) se lee aquí una sola vez.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "Falta GEMINI_API_KEY en el archivo .env. "
        "Copia .env.example a .env y añade tu clave."
    )