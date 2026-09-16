from core.command import Command, CommandResult


def test_command_default_parameters_is_empty_dict():
    command = Command(action_name="open_app")
    assert command.parameters == {}


def test_command_result_stores_success_and_response():
    result = CommandResult(success=True, spoken_response="Hecho")
    assert result.success is True
    assert result.spoken_response == "Hecho"