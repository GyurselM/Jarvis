"""
Script de pruebas manuales, para verificar a ojo que las cosas
funcionan de verdad en tu sistema. No forma parte de la lógica
del asistente ni se importa desde ningún otro sitio.
"""

from brain.router import Router
from integrations.llm_client import GeminiClient
from actions.registry import execute_command

if __name__ == "__main__":
    router = Router(llm_client=GeminiClient())

    command = router.decide("ábreme el bloc de notas")
    print("Command decidido:", command)

    if command is not None:
        result = execute_command(command)
        print("Resultado de ejecutarlo:", result)
    else:
        print("El router no encontró ninguna acción para esa frase.")