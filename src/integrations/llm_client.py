"""
Cliente de bajo nivel para hablar con un LLM. No sabe nada de Command
ni de Action — solo entiende "te mando este texto y estas herramientas,
te devuelvo qué función decidió llamar el modelo, si alguna".
"""

from google import genai
from config import GEMINI_API_KEY


class LLMClient:
    """Interfaz que cualquier proveedor de LLM debe cumplir."""

    def get_function_call(self, prompt: str, tools: list[dict]) -> dict | None:
        raise NotImplementedError


class GeminiClient(LLMClient):
    """Implementación concreta usando la API de Gemini."""

    def __init__(self):
        self._client = genai.Client(api_key=GEMINI_API_KEY)

    def get_function_call(self, prompt: str, tools: list[dict]) -> dict | None:
        interaction = self._client.interactions.create(
            model="gemini-flash-latest",
            input=prompt,
            tools=tools,
        )

        for step in (interaction.steps or []):
            if step.type == "function_call":
                return {"name": step.name, "arguments": step.arguments}

        return None