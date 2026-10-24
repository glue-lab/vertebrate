from typing import Any

import pytest

from vertebrate.compute import Action, Command, Environment


class RecordingEnvironment(Environment):
    def __init__(self, executables: set[str] = frozenset()) -> None:
        self.executables = executables
        self.calls: list[tuple[str, tuple, dict]] = []

    def execute(self, executable: str, args: tuple, kwargs: dict[str, Any]) -> Any:
        self.calls.append((executable, args, kwargs))
        return f"result of {executable}"

    def __contains__(self, item: str) -> bool:
        return item in self.executables


class TestEnvironment:
    def test_requires_execute_and_contains(self):
        with pytest.raises(TypeError, match="abstract"):
            Environment()

    def test_getitem_returns_action_bound_to_environment(self):
        env = RecordingEnvironment()
        action = env["ls"]
        assert isinstance(action, Action)
        assert action.environment is env
        assert action.executable == "ls"

    def test_getitem_defers_execution(self):
        env = RecordingEnvironment()
        env["ls"]
        assert env.calls == []


class TestAction:
    def test_call_forwards_args_and_kwargs_to_execute(self):
        env = RecordingEnvironment()
        env["ls"]("-l", ".", color="never")
        assert env.calls == [("ls", ("-l", "."), {"color": "never"})]

    def test_call_without_arguments_forwards_empty_args_and_kwargs(self):
        env = RecordingEnvironment()
        env["ls"]()
        assert env.calls == [("ls", (), {})]

    def test_call_returns_execute_result(self):
        assert RecordingEnvironment()["ls"]() == "result of ls"


class TestCommand:
    def test_exposes_bound_action_args_and_kwargs(self):
        action = RecordingEnvironment()["ls"]
        command = Command(action, args=("-l",), kwargs={"color": "never"})
        assert command.action is action
        assert command.args == ("-l",)
        assert command.kwargs == {"color": "never"}

    def test_defaults_to_no_args_or_kwargs(self):
        command = Command(RecordingEnvironment()["ls"])
        assert command.args == ()
        assert command.kwargs == {}

    def test_call_invokes_action_with_bound_arguments(self):
        env = RecordingEnvironment()
        Command(env["ls"], args=("-l",), kwargs={"color": "never"})()
        assert env.calls == [("ls", ("-l",), {"color": "never"})]

    def test_call_returns_action_result(self):
        assert Command(RecordingEnvironment()["ls"])() == "result of ls"

    def test_can_be_called_repeatedly(self):
        env = RecordingEnvironment()
        command = Command(env["ls"], args=("-l",))
        command()
        command()
        assert env.calls == [("ls", ("-l",), {})] * 2
