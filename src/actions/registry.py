"""
Registro de acciones disponibles. Traduce un Command (con su
action_name) en la Action concreta que debe ejecutarlo.

Añadir una acción nueva en el futuro (Spotify, correo, visión...)
solo requiere una línea nueva en ACTIONS, sin tocar nada más.
"""

from actions.base import Action
from actions.open_app import OpenAppAction
from core.command import Command, CommandResult

ACTIONS: dict[str, Action] = {
    "open_app": OpenAppAction(),
}


def execute_command(command: Command) -> CommandResult:
    """
    Busca la Action correspondiente al Command y la ejecuta.
    Si no existe ninguna acción registrada con ese nombre, devuelve
    un CommandResult de error controlado en vez de reventar.
    """
    action = ACTIONS.get(command.action_name)

    if action is None:
        return CommandResult(
            success=False,
            spoken_response=f"No sé cómo hacer '{command.action_name}' todavía."
        )

    return action.execute(command)