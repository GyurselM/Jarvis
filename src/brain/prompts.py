"""
Prompt fijo del router. El usuario nunca escribe esto: es la
instrucción programada una única vez para que el LLM sepa cómo
comportarse como "cerebro" de decisión de Jarvis.
"""

SYSTEM_INSTRUCTIONS = (
    "Eres el módulo de decisión de un asistente de voz llamado Jarvis. "
    "Tu única función es interpretar la orden del usuario y llamar a la "
    "función correspondiente con los parámetros correctos. "
    "No respondas con texto libre: si la orden no coincide con ninguna "
    "función disponible, no llames a ninguna."
)


def build_prompt(user_text: str) -> str:
    return f'{SYSTEM_INSTRUCTIONS}\n\nOrden del usuario: "{user_text}"'