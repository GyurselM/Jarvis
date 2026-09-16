"""
Modelos de datos centrales del sistema.

Un Command representa una acción que el LLM ha decidido ejecutar,
tras interpretar lo que el usuario dijo por voz.

Un CommandResult representa el resultado de haber ejecutado esa acción.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Command:
    """
    Instrucción estructurada que el 'cerebro' (brain/router.py) genera
    a partir del texto transcrito del usuario.

    Ejemplo: el usuario dice "súbeme el volumen al 50 por ciento"
    y esto se convierte en:
        Command(action_name="spotify_volume", parameters={"level": 50})
    """
    action_name: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandResult:
    """
    Resultado de ejecutar un Command. Toda acción, sin excepción,
    debe devolver uno de estos — así el sistema siempre sabe si algo
    salió bien o mal, y qué decir en voz alta como respuesta.
    """
    success: bool
    spoken_response: str
    data: dict[str, Any] = field(default_factory=dict)