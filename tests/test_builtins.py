import os
import subprocess

import pytest

import vertebrate.examples.orders as examples
from vertebrate.builtins.files import FileSystem
from vertebrate.builtins.orders import SimpleOrders
from vertebrate.builtins.os import OSEnvironment
from vertebrate.builtins.python import PythonEnvironment
from vertebrate.builtins.variables import Dictionary
from vertebrate.testing import (
    EnvironmentContract,
    NamespaceContract,
    OrdersContract,
    TemporaryContract,
)


class TestDictionary(NamespaceContract, TemporaryContract):
    def make_namespace(self):
        return Dictionary({"a": 1})

    def present_address(self):
        return "a"

    def absent_address(self):
        return "missing"

    def populate(self, location):
        location.set(1)


class TestFileSystem(NamespaceContract):
    @pytest.fixture(autouse=True)
    def present_file(self, tmp_path):
        (tmp_path / "present.json").write_text("{}")
        self.directory = tmp_path

    def make_namespace(self):
        return FileSystem()

    def present_address(self):
        return str(self.directory / "present.json")

    def absent_address(self):
        return str(self.directory / "absent.csv")


class TestSimpleOrders(OrdersContract):
    def make_namespace(self):
        return SimpleOrders(examples.specs, PythonEnvironment(examples))

    def present_address(self):
        return "file2"

    def absent_address(self):
        return "missing"

    def environment_name(self):
        return "PythonEnvironment"


class TestOSEnvironment(EnvironmentContract):
    def make_environment(self):
        return OSEnvironment()

    def present_executable(self):
        return "sh"

    def absent_executable(self):
        return "not-a-program-vertebrate"

    def test_returns_stdout(self):
        assert OSEnvironment()["sh"]("-c", "printf ok") == b"ok"

    def test_preserves_argument_boundaries(self):
        output = OSEnvironment()["printf"]("[%s]", "a b", "c")
        assert output == b"[a b][c]"

    def test_inherits_process_environment(self, monkeypatch):
        monkeypatch.setenv("VERTEBRATE_TEST", "inherited")
        output = OSEnvironment()["sh"]("-c", 'printf %s "$VERTEBRATE_TEST"')
        assert output == b"inherited"

    def test_kwargs_add_to_and_override_process_environment(self, monkeypatch):
        monkeypatch.setenv("VERTEBRATE_TEST", "inherited")
        command = 'printf "%s %s" "$VERTEBRATE_TEST" "$VERTEBRATE_ADDED"'
        output = OSEnvironment()["sh"](
            "-c", command, VERTEBRATE_TEST="override", VERTEBRATE_ADDED="added"
        )
        assert output == b"override added"

    def test_kwargs_do_not_leak_into_process_environment(self):
        OSEnvironment()["sh"]("-c", "true", VERTEBRATE_LEAK="leaked")
        assert "VERTEBRATE_LEAK" not in os.environ

    def test_raises_on_non_zero_exit_with_stderr_as_note(self):
        with pytest.raises(subprocess.CalledProcessError) as error:
            OSEnvironment()["sh"]("-c", "echo out; echo err >&2; exit 3")
        assert error.value.returncode == 3
        assert error.value.stdout == b"out\n"
        assert "err" in error.value.__notes__[0]

    def test_raises_without_note_when_stderr_is_empty(self):
        with pytest.raises(subprocess.CalledProcessError) as error:
            OSEnvironment()["sh"]("-c", "exit 3")
        assert not getattr(error.value, "__notes__", None)

    def test_check_false_returns_stdout_despite_non_zero_exit(self):
        output = OSEnvironment(check=False)["sh"]("-c", "echo out; exit 3")
        assert output == b"out\n"
