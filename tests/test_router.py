from brain.router import Router
from integrations.llm_client import LLMClient


class FakeLLMClient(LLMClient):
    """Doble de prueba: siempre devuelve la misma función, sin llamar a ninguna API."""

    def get_function_call(self, prompt, tools):
        return {"name": "open_app", "arguments": {"app_name": "steam"}}


class FakeLLMClientNoMatch(LLMClient):
    def get_function_call(self, prompt, tools):
        return None


def test_router_builds_command_from_function_call():
    router = Router(llm_client=FakeLLMClient())
    command = router.decide("ábreme steam")

    assert command.action_name == "open_app"
    assert command.parameters == {"app_name": "steam"}


def test_router_returns_none_when_no_function_matches():
    router = Router(llm_client=FakeLLMClientNoMatch())
    command = router.decide("cuéntame un chiste")

    assert command is None