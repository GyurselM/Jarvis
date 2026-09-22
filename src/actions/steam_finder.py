"""
Busca juegos instalados en Steam, leyendo los manifiestos que Steam
guarda por cada juego (con su nombre y App ID), y los lanza usando
el protocolo steam:// — así no hace falta encontrar el .exe del
juego a mano, Steam se encarga de arrancarlo correctamente.
"""

import glob
import json
import os
import re
import winreg

CACHE_PATH = "steam_index_cache.json"


def _get_steam_install_path() -> str | None:
    """Localiza dónde está instalado Steam, vía el registro de Windows."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        path, _ = winreg.QueryValueEx(key, "SteamPath")
        return path
    except FileNotFoundError:
        return None


def _get_library_folders(steam_path: str) -> list[str]:
    """
    Steam puede repartir juegos en varias 'bibliotecas' (por ejemplo,
    una en cada disco duro). Este archivo lista todas las que tengas.
    """
    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    libraries = [steam_path]

    if not os.path.exists(vdf_path):
        return libraries

    with open(vdf_path, "r", encoding="utf-8") as file:
        content = file.read()

    for match in re.finditer(r'"path"\s+"([^"]+)"', content):
        path = match.group(1).replace("\\\\", "\\")
        if path not in libraries:
            libraries.append(path)

    return libraries


def _scan_steam_games() -> dict[str, str]:
    """Escanea de verdad los manifiestos de Steam (lento la primera vez)."""
    steam_path = _get_steam_install_path()
    if not steam_path:
        return {}

    index = {}

    for library in _get_library_folders(steam_path):
        pattern = os.path.join(library, "steamapps", "appmanifest_*.acf")
        for manifest_path in glob.glob(pattern):
            with open(manifest_path, "r", encoding="utf-8") as file:
                content = file.read()

            name_match = re.search(r'"name"\s+"([^"]+)"', content)
            appid_match = re.search(r'"appid"\s+"([^"]+)"', content)

            if name_match and appid_match:
                index[name_match.group(1).lower()] = appid_match.group(1)

    return index


def build_steam_index(force_refresh: bool = False) -> dict[str, str]:
    """
    Devuelve {nombre_del_juego: app_id}, usando caché local salvo que
    se pida refrescar explícitamente.
    """
    if not force_refresh and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as cache_file:
            return json.load(cache_file)

    index = _scan_steam_games()

    with open(CACHE_PATH, "w", encoding="utf-8") as cache_file:
        json.dump(index, cache_file, ensure_ascii=False, indent=2)

    return index


def launch_steam_game(app_id: str) -> None:
    """Lanza un juego de Steam por su App ID, sin necesitar su ruta."""
    os.startfile(f"steam://rungameid/{app_id}")