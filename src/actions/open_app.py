"""
Acción que abre una aplicación instalada en Windows por su nombre.
"""

import subprocess
from actions.base import Action
from core.command import Command, CommandResult


class OpenAppAction(Action):
    """
    Abre una aplicación usando el comando 'start' de Windows.

    Espera un Command con parameters={"app_name": "steam"}, donde
    app_name debe ser algo que Windows sepa reconocer (nombre del
    ejecutable, o un alias registrado en el sistema).
    """

    def execute(self, command: Command) -> CommandResult:
        app_name = command.parameters.get("app_name")

        if not app_name:
            return CommandResult(
                success=False,
                spoken_response="No me has dicho qué aplicación abrir."
            )

        try:
            subprocess.Popen(f"start {app_name}", shell=True)
            return CommandResult(
                success=True,
                spoken_response=f"Abriendo {app_name}."
            )
        except Exception as error:
            return CommandResult(
                success=False,
                spoken_response=f"No he podido abrir {app_name}.",
                data={"error": str(error)}
            )