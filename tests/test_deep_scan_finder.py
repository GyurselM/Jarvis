from unittest.mock import patch, mock_open
from actions.deep_scan_finder import build_deep_scan_index


def test_build_deep_scan_index_works_with_any_folder_name():
    """
    Usamos un nombre de carpeta inventado ('MisJuegos') que no está
    en ninguna lista predefinida, para confirmar que el escaneo
    generaliza a cualquier estructura de disco, no solo a la nuestra.
    También comprobamos que elige el .exe correcto (por nombre)
    aunque haya otro de por medio (un crash handler, por ejemplo).
    """
    def fake_exists(path):
        return path == "C:\\"

    def fake_listdir(path):
        if path == "C:\\":
            return ["MisJuegos", "Windows"]
        if path == "C:\\MisJuegos":
            return ["Rematch"]
        return []

    def fake_walk(path):
        if path == "C:\\MisJuegos":
            yield ("C:\\MisJuegos", ["Rematch"], [])
        elif path == "C:\\MisJuegos\\Rematch":
            yield ("C:\\MisJuegos\\Rematch", [], ["Rematch.exe", "UnityCrashHandler64.exe"])

    def fake_getsize(path):
        return 500_000_000 if "Rematch.exe" in path else 1_000_000

    with patch("actions.deep_scan_finder.os.path.exists", side_effect=fake_exists), \
         patch("actions.deep_scan_finder.os.listdir", side_effect=fake_listdir), \
         patch("actions.deep_scan_finder.os.path.isdir", return_value=True), \
         patch("actions.deep_scan_finder.os.walk", side_effect=fake_walk), \
         patch("actions.deep_scan_finder.os.path.getsize", side_effect=fake_getsize), \
         patch("actions.deep_scan_finder.open", mock_open()):
        index = build_deep_scan_index(force_refresh=True)

    assert index.get("rematch") == "C:\\MisJuegos\\Rematch\\Rematch.exe"