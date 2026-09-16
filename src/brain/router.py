"""
El router: recibe texto del usuario, se lo pasa al LLM junto con las
herramientas disponibles, y traduce la respuesta en un Command listo
para que una Action lo ejecute.
"""

from integrations.llm_client import LLMClient
from brain.prompts import build_prompt
from core.command import Command

OPEN_APP_TOOL = {
    "type": "function",
    "name": "open_app",
    "description": "Abre una aplicación instalada en el ordenador por su nombre.",
    "parameters": {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Nombre de la aplicación a abrir, ej. 'notepad', 'steam'.",
            },
        },
        "required": ["app_name"],
    },
}

AVAILABLE_TOOLS = [OPEN_APP_TOOL]


class Router:
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def decide(self, user_text: str) -> Command | None:
        prompt = build_prompt(user_text)
        function_call = self._llm_client.get_function_call(prompt, AVAILABLE_TOOLS)

        if function_call is None:
            return None

        return Command(
            action_name=function_call["name"],
            parameters=function_call["arguments"],
        )