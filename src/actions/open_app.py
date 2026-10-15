"""
Acción que abre una aplicación o juego instalado, buscándolo
automáticamente en varias fuentes, de la más rápida/fiable a la más
exhaustiva. Nunca pasa texto al shell: solo ejecuta rutas encontradas.
"""

import ctypes
import shutil
import subprocess

from actions.base import Action
from actions.app_finder import build_app_index, find_app_path
from actions.steam_finder import build_steam_index, launch_steam_game
from actions.deep_scan_finder import build_deep_scan_index
from core.command import Command, CommandResult

ERROR_ELEVATION_REQUIRED = 740
PATH_CHARACTERS = ("\\", "/", ":")


def _launch_executable(path: str) -> None:
    """
    Lanza un ejecutable normalmente. Si Windows exige permisos de
    administrador para ese programa en concreto, lo relanza pidiendo
    elevación (esto sigue mostrando el aviso de Windows — no se
    puede ni se debe evitar esa confirmación).
    """
    try:
        subprocess.Popen([path])
    except OSError as error:
        if getattr(error, "winerror", None) == ERROR_ELEVATION_REQUIRED:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", path, None, None, 1)
        else:
            raise


class OpenAppAction(Action):
    """
    Abre una aplicación o juego. Orden de búsqueda:
    1. Índice de juegos de Steam (por App ID, vía protocolo steam://).
    2. Índice automático del Menú Inicio.
    3. Escaneo profundo multi-unidad.
    4. Programas del sistema que están en el PATH de Windows (notepad, calc...).
    Si no aparece en ninguna parte, devuelve un error controlado.
    """

    def __init__(
        self,
        app_index: dict[str, str] | None = None,
        steam_index: dict[str, str] | None = None,
        deep_scan_index: dict[str, str] | None = None,
    ):
        self._app_index = app_index if app_index is not None else build_app_index()
        self._steam_index = steam_index if steam_index is not None else build_steam_index()
        self._deep_scan_index = (
            deep_scan_index if deep_scan_index is not None else build_deep_scan_index()
        )

    def execute(self, command: Command) -> CommandResult:
        app_name = command.parameters.get("app_name")

        if not app_name:
            return CommandResult(
                success=False,
                spoken_response="No me has dicho qué aplicación abrir."
            )

        if any(character in app_name for character in PATH_CHARACTERS):
            return CommandResult(
                success=False,
                spoken_response="Solo puedo abrir aplicaciones por su nombre."
            )

        try:
            steam_appid = find_app_path(app_name, self._steam_index)
            if steam_appid:
                launch_steam_game(steam_appid)
                return CommandResult(success=True, spoken_response=f"Abriendo {app_name}.")

            found_path = find_app_path(app_name, self._app_index)
            if found_path:
                _launch_executable(found_path)
                return CommandResult(success=True, spoken_response=f"Abriendo {app_name}.")

            deep_path = find_app_path(app_name, self._deep_scan_index)
            if deep_path:
                _launch_executable(deep_path)
                return CommandResult(success=True, spoken_response=f"Abriendo {app_name}.")

            system_path = shutil.which(app_name)
            if system_path:
                _launch_executable(system_path)
                return CommandResult(success=True, spoken_response=f"Abriendo {app_name}.")

            return CommandResult(
                success=False,
                spoken_response=f"No encuentro ninguna aplicación llamada {app_name}."
            )

        except Exception as error:
            return CommandResult(
                success=False,
                spoken_response=f"No he podido abrir {app_name}.",
                data={"error": str(error)}
            )