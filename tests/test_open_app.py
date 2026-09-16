from unittest.mock import patch
from actions.open_app import OpenAppAction
from core.command import Command

def test_open_app_success():
    action = OpenAppAction()
    command = Command(action_name="open_app", parameters={"app_name": "notepad"})

    with patch("actions.open_app.subprocess.Popen") as mock_popen:
        result = action.execute(command)

    mock_popen.assert_called_once()
    assert result.success is True


def test_open_app_missing_name():
    action = OpenAppAction()
    command = Command(action_name="open_app", parameters={})

    result = action.execute(command)

    assert result.success is False