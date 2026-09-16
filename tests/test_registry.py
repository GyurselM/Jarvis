from actions.registry import execute_command, ACTIONS
from actions.base import Action
from core.command import Command, CommandResult


class FakeAction(Action):
    """Acción falsa para testear el registro sin efectos reales."""

    def execute(self, command: Command) -> CommandResult:
        return CommandResult(success=True, spoken_response="Ejecutada de mentira")


def test_execute_command_calls_correct_action():
    ACTIONS["fake_action"] = FakeAction()
    command = Command(action_name="fake_action")

    result = execute_command(command)

    assert result.success is True
    assert result.spoken_response == "Ejecutada de mentira"

    del ACTIONS["fake_action"]  # limpieza para no afectar a otros tests


def test_execute_command_handles_unknown_action():
    command = Command(action_name="algo_que_no_existe")

    result = execute_command(command)

    assert result.success is False