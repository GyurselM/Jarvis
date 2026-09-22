from unittest.mock import patch, mock_open
from actions.steam_finder import build_steam_index, launch_steam_game


def test_build_steam_index_scans_when_no_cache():
    acf_content = '"appid"\t\t"123456"\n"name"\t\t"Rematch"\n'

    with patch("actions.steam_finder.os.path.exists", return_value=False), \
         patch("actions.steam_finder.winreg.OpenKey"), \
         patch("actions.steam_finder.winreg.QueryValueEx", return_value=("C:\\Steam", None)), \
         patch("actions.steam_finder.glob.glob", return_value=["C:\\Steam\\steamapps\\appmanifest_123456.acf"]), \
         patch("actions.steam_finder.open", mock_open(read_data=acf_content)):
        index = build_steam_index()

    assert index.get("rematch") == "123456"


def test_launch_steam_game_uses_protocol_url():
    with patch("actions.steam_finder.os.startfile") as mock_startfile:
        launch_steam_game("123456")

    mock_startfile.assert_called_once_with("steam://rungameid/123456")