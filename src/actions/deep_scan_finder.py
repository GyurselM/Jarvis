"""
Escaneo profundo de discos: busca ejecutables en las carpetas de
cada unidad, sin depender de nombres concretos de launcher — funciona
igual en cualquier PC, sea cual sea su estructura de carpetas.
"""

import difflib
import json
import os
import string

CACHE_PATH = "deep_scan_cache.json"

# Carpetas de sistema que se ignoran siempre en cualquier Windows.
IGNORED_FOLDERS = {
    "windows", "$recycle.bin", "system volume information",
    "programdata", "recovery", "perflogs", "recycler",
}


def _get_local_drives() -> list[str]:
    return [
        f"{letter}:\\"
        for letter in string.ascii_uppercase
        if os.path.exists(f"{letter}:\\")
    ]


def _find_best_exe(folder: str, folder_name: str, max_depth: int = 4) -> str | None:
    """
    Busca el ejecutable más probable dentro de una carpeta: prioriza
    el que más se parece por nombre a la propia carpeta (patrón
    habitual: 'Rematch' suele contener 'Rematch.exe'), y si no hay
    ninguno parecido, se queda con el más grande (suele ser el
    programa real, no un instalador o utilidad auxiliar).
    """
    base_depth = folder.rstrip(os.sep).count(os.sep)
    candidates = []

    for root, dirs, files in os.walk(folder):
        current_depth = root.count(os.sep) - base_depth
        if current_depth >= max_depth:
            dirs[:] = []
            continue
        for filename in files:
            if filename.lower().endswith(".exe"):
                candidates.append(os.path.join(root, filename))

    if not candidates:
        return None

    candidate_names = [os.path.splitext(os.path.basename(c))[0].lower() for c in candidates]
    name_matches = difflib.get_close_matches(folder_name.lower(), candidate_names, n=1, cutoff=0.4)

    if name_matches:
        for candidate in candidates:
            if os.path.splitext(os.path.basename(candidate))[0].lower() == name_matches[0]:
                return candidate

    return max(candidates, key=os.path.getsize)


def _scan_drives() -> dict[str, str]:
    index = {}

    for drive in _get_local_drives():
        try:
            top_level_folders = os.listdir(drive)
        except PermissionError:
            continue

        for folder_name in top_level_folders:
            if folder_name.lower() in IGNORED_FOLDERS:
                continue

            full_path = os.path.join(drive, folder_name)
            if not os.path.isdir(full_path):
                continue

            # Caso 1: la propia carpeta es una app/juego individual.
            exe_path = _find_best_exe(full_path, folder_name)
            if exe_path:
                index[folder_name.lower()] = exe_path

            # Caso 2: la carpeta es un contenedor de varias apps/juegos
            # (Program Files, Epic Games, o cualquier carpeta rara que
            # alguien haya creado — no importa el nombre).
            try:
                sub_folders = os.listdir(full_path)
            except PermissionError:
                continue

            for sub_name in sub_folders:
                sub_path = os.path.join(full_path, sub_name)
                if os.path.isdir(sub_path):
                    sub_exe_path = _find_best_exe(sub_path, sub_name)
                    if sub_exe_path:
                        index[sub_name.lower()] = sub_exe_path

    return index


def build_deep_scan_index(force_refresh: bool = False) -> dict[str, str]:
    if not force_refresh and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as cache_file:
            return json.load(cache_file)

    index = _scan_drives()

    with open(CACHE_PATH, "w", encoding="utf-8") as cache_file:
        json.dump(index, cache_file, ensure_ascii=False, indent=2)

    return index