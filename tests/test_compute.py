import pytest

from vertebrate.compute import Action, Command, Environment
from vertebrate.testing import RecordingEnvironment


class TestEnvironment:
    def test_requires_execute_and_contains(self):
        with pytest.raises(TypeError, match="abstract"):
            Environment()

    def test_getitem_returns_action_bound_to_environment(self):
        env = RecordingEnvironment({"ls"})
        action = env["ls"]
        assert isinstance(action, Action)
        assert action.environment is env
        assert action.executable == "ls"

    def test_getitem_defers_execution(self):
        env = RecordingEnvironment({"ls"})
        env["ls"]
        assert env.calls == []


class TestAction:
    def test_call_forwards_args_and_kwargs_to_execute(self):
        env = RecordingEnvironment({"ls"})
        env["ls"]("-l", ".", color="never")
        assert env.calls == [("ls", ("-l", "."), {"color": "never"})]

    def test_call_without_arguments_forwards_empty_args_and_kwargs(self):
        env = RecordingEnvironment({"ls"})
        env["ls"]()
        assert env.calls == [("ls", (), {})]

    def test_call_returns_execute_result(self):
        assert RecordingEnvironment({"ls"})["ls"]() == "result of ls"


class TestCommand:
    def test_exposes_bound_action_args_and_kwargs(self):
        action = RecordingEnvironment({"ls"})["ls"]
        command = Command(action, args=("-l",), kwargs={"color": "never"})
        assert command.action is action
        assert command.args == ("-l",)
        assert command.kwargs == {"color": "never"}

    def test_defaults_to_no_args_or_kwargs(self):
        command = Command(RecordingEnvironment({"ls"})["ls"])
        assert command.args == ()
        assert command.kwargs == {}

    def test_call_invokes_action_with_bound_arguments(self):
        env = RecordingEnvironment({"ls"})
        Command(env["ls"], args=("-l",), kwargs={"color": "never"})()
        assert env.calls == [("ls", ("-l",), {"color": "never"})]

    def test_call_returns_action_result(self):
        assert Command(RecordingEnvironment({"ls"})["ls"])() == "result of ls"

    def test_can_be_called_repeatedly(self):
        env = RecordingEnvironment({"ls"})
        command = Command(env["ls"], args=("-l",))
        command()
        command()
        assert env.calls == [("ls", ("-l",), {})] * 2

    def test_default_kwargs_are_not_shared_between_commands(self):
        first = Command(RecordingEnvironment({"ls"})["ls"])
        first.kwargs["color"] = "never"
        assert Command(RecordingEnvironment({"ls"})["ls"]).kwargs == {}
