from unittest.mock import patch, mock_open, MagicMock
from actions.app_finder import build_app_index, find_app_path


def test_build_app_index_scans_when_no_cache_exists():
    fake_shortcut = MagicMock()
    fake_shortcut.Targetpath = "C:\\Program Files (x86)\\Steam\\steam.exe"
    fake_shell = MagicMock()
    fake_shell.CreateShortcut.return_value = fake_shortcut

    with patch("actions.app_finder.os.path.exists", return_value=False), \
         patch("actions.app_finder.glob.glob", return_value=["C:\\StartMenu\\Steam.lnk"]), \
         patch("actions.app_finder.win32com.client.Dispatch", return_value=fake_shell), \
         patch("actions.app_finder.open", mock_open()):
        index = build_app_index()

    assert index.get("steam") == "C:\\Program Files (x86)\\Steam\\steam.exe"


def test_build_app_index_uses_cache_when_available():
    fake_cache_content = '{"steam": "C:\\\\Steam\\\\steam.exe"}'

    with patch("actions.app_finder.os.path.exists", return_value=True), \
         patch("actions.app_finder.open", mock_open(read_data=fake_cache_content)):
        index = build_app_index()

    assert index == {"steam": "C:\\Steam\\steam.exe"}


def test_find_app_path_exact_match():
    index = {"steam": "C:\\Steam\\steam.exe"}
    assert find_app_path("steam", index) == "C:\\Steam\\steam.exe"


def test_find_app_path_fuzzy_match():
    index = {"counter-strike 2": "C:\\Steam\\steamapps\\common\\cs2\\cs2.exe"}
    assert find_app_path("counter strike 2", index) == "C:\\Steam\\steamapps\\common\\cs2\\cs2.exe"


def test_find_app_path_no_match_returns_none():
    index = {"steam": "C:\\Steam\\steam.exe"}
    assert find_app_path("app_que_no_existe_xyz", index) is None