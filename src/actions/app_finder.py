"""
Busca aplicaciones instaladas automáticamente, indexando los accesos
directos del Menú Inicio de Windows. El resultado se guarda en una
caché local (generada por el propio programa) para no tener que
re-escanear en cada arranque.
"""

import difflib
import glob
import json
import os

import win32com.client

START_MENU_PATHS = [
    os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
    os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs"),
]

CACHE_PATH = "app_index_cache.json"


def _resolve_shortcut(lnk_path: str) -> str | None:
    """Devuelve la ruta del ejecutable al que apunta un acceso directo .lnk."""
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(lnk_path)
    return shortcut.Targetpath or None


def _scan_start_menu() -> dict[str, str]:
    """Escanea de verdad el Menú Inicio (lento la primera vez, ~1-2 segundos)."""
    index = {}

    for start_menu_path in START_MENU_PATHS:
        pattern = os.path.join(start_menu_path, "**", "*.lnk")
        for lnk_path in glob.glob(pattern, recursive=True):
            app_name = os.path.splitext(os.path.basename(lnk_path))[0]
            target = _resolve_shortcut(lnk_path)
            if target and target.lower().endswith(".exe"):
                index[app_name.lower()] = target

    return index


def build_app_index(force_refresh: bool = False) -> dict[str, str]:
    """
    Devuelve el índice de apps instaladas. Usa la caché guardada si
    existe y no se pide refrescar; si no, escanea de nuevo y actualiza
    la caché automáticamente.
    """
    if not force_refresh and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as cache_file:
            return json.load(cache_file)

    index = _scan_start_menu()

    with open(CACHE_PATH, "w", encoding="utf-8") as cache_file:
        json.dump(index, cache_file, ensure_ascii=False, indent=2)

    return index


def find_app_path(app_name: str, index: dict[str, str]) -> str | None:
    """Busca la app por coincidencia aproximada de nombre."""
    app_name = app_name.lower()

    if app_name in index:
        return index[app_name]

    matches = difflib.get_close_matches(app_name, index.keys(), n=1, cutoff=0.6)
    return index[matches[0]] if matches else None