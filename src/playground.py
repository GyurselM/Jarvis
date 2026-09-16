"""
Script de pruebas manuales, para verificar a ojo que las cosas
funcionan de verdad en tu sistema. No forma parte de la lógica
del asistente ni se importa desde ningún otro sitio.
"""

from actions.open_app import OpenAppAction
from core.command import Command

if __name__ == "__main__":
    action = OpenAppAction()
    result = action.execute(Command("open_app", {"app_name": "notepad"}))
    print(result)