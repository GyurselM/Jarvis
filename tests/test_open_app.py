from unittest.mock import patch
from actions.open_app import OpenAppAction
from core.command import Command


def _make_action(**overrides):
    defaults = {"app_index": {}, "steam_index": {}, "deep_scan_index": {}}
    defaults.update(overrides)
    return OpenAppAction(**defaults)


def test_open_app_success():
    action = _make_action()
    command = Command(action_name="open_app", parameters={"app_name": "notepad"})

    with patch("actions.open_app.subprocess.Popen") as mock_popen:
        result = action.execute(command)

    mock_popen.assert_called_once()
    assert result.success is True


def test_open_app_missing_name():
    action = _make_action()
    command = Command(action_name="open_app", parameters={})

    result = action.execute(command)

    assert result.success is False


def test_open_app_launches_steam_game_when_matched():
    action = _make_action(steam_index={"rematch": "123456"})
    command = Command(action_name="open_app", parameters={"app_name": "rematch"})

    with patch("actions.open_app.launch_steam_game") as mock_launch:
        result = action.execute(command)

    mock_launch.assert_called_once_with("123456")
    assert result.success is True


def test_open_app_falls_back_to_deep_scan_index():
    action = _make_action(deep_scan_index={"rematch": "C:\\Epic Games\\Rematch\\Rematch.exe"})
    command = Command(action_name="open_app", parameters={"app_name": "rematch"})

    with patch("actions.open_app.subprocess.Popen") as mock_popen:
        result = action.execute(command)

    mock_popen.assert_called_once_with(["C:\\Epic Games\\Rematch\\Rematch.exe"])
    assert result.success is True


def test_open_app_requests_elevation_when_needed():
    action = _make_action(deep_scan_index={"baba is you": "D:\\Baba Is You\\Baba Is You.exe"})
    command = Command(action_name="open_app", parameters={"app_name": "baba is you"})

    elevation_error = OSError("elevación requerida")
    elevation_error.winerror = 740

    with patch("actions.open_app.subprocess.Popen", side_effect=elevation_error), \
         patch("actions.open_app.ctypes.windll.shell32.ShellExecuteW") as mock_shell_execute:
        result = action.execute(command)

    mock_shell_execute.assert_called_once_with(
        None, "runas", "D:\\Baba Is You\\Baba Is You.exe", None, None, 1
    )
    assert result.success is True