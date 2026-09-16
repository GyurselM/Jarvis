"""
Script de pruebas manuales, para verificar a ojo que las cosas
funcionan de verdad en tu sistema. No forma parte de la lógica
del asistente ni se importa desde ningún otro sitio.
"""

from brain.router import Router
from integrations.llm_client import GeminiClient

if __name__ == "__main__":
    router = Router(llm_client=GeminiClient())

    command = router.decide("ábreme el bloc de notas")
    print("Prueba 1 (debería dar open_app):", command)

    command = router.decide("qué tiempo hace hoy")
    print("Prueba 2 (debería dar None):", command)