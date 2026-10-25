"""
Implementation-agnostic test suites for Vertebrate's ABCs.

Each contract is a plain class of `test_*` methods. To check an implementation,
subclass the contract in a test suite and implement its hook methods; any test
framework that collects `test_*` methods can run it. For unittest, also mix in
`unittest.TestCase`. Assertions are plain `assert` statements, so don't run
contracts under `python -O`.
"""

from vertebrate.compute import Action, Environment
from vertebrate.testing._assertions import raises


def _unimplemented(contract: str, hook: str) -> NotImplementedError:
    return NotImplementedError(f"Implement {hook}() to run {contract}")


class EnvironmentContract:
    """
    Promises every Environment keeps.

    Hooks: `make_environment()` returns a fresh environment;
    `present_executable()` names an executable in it; `absent_executable()`
    names one that isn't.
    """

    def make_environment(self) -> Environment:
        raise _unimplemented("EnvironmentContract", "make_environment")

    def present_executable(self) -> str:
        raise _unimplemented("EnvironmentContract", "present_executable")

    def absent_executable(self) -> str:
        raise _unimplemented("EnvironmentContract", "absent_executable")

    def test_contains_present_executable(self):
        environment, name = self.make_environment(), self.present_executable()
        assert name in environment, f"{name!r} should be in {environment!r}"

    def test_does_not_contain_absent_executable(self):
        environment, name = self.make_environment(), self.absent_executable()
        assert name not in environment, f"{name!r} should not be in {environment!r}"

    def test_getitem_returns_action_bound_to_environment(self):
        environment, name = self.make_environment(), self.present_executable()
        action = environment[name]
        assert isinstance(action, Action), f"{action!r} should be an Action"
        assert action.environment is environment, "Action should be bound to it"
        assert action.executable == name, f"{action.executable!r} != {name!r}"

    def test_calling_absent_executable_raises_key_error(self):
        environment, name = self.make_environment(), self.absent_executable()
        with raises(KeyError):
            environment[name]()
