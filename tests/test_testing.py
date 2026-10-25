import pytest

from vertebrate.testing import EnvironmentContract
from vertebrate.testing._assertions import raises


@pytest.mark.parametrize(
    "hook", ["make_environment", "present_executable", "absent_executable"]
)
def test_unimplemented_hook_names_itself_and_its_contract(hook):
    with pytest.raises(NotImplementedError, match=f"{hook}.*EnvironmentContract"):
        getattr(EnvironmentContract(), hook)()


class TestRaises:
    def test_passes_when_expected_error_is_raised(self):
        with raises(KeyError):
            raise KeyError("missing")

    def test_accepts_a_subclass_of_the_expected_error(self):
        with raises(LookupError):
            raise KeyError("missing")

    def test_fails_when_nothing_is_raised(self):
        with pytest.raises(AssertionError, match="Did not raise"), raises(KeyError):
            pass

    def test_does_not_catch_a_different_error(self):
        with pytest.raises(ValueError), raises(KeyError):
            raise ValueError

    def test_checks_message_against_match(self):
        with raises(KeyError, match="miss"):
            raise KeyError("missing")

    def test_fails_when_message_does_not_match(self):
        with pytest.raises(AssertionError, match="does not match"):
            with raises(KeyError, match="absent"):
                raise KeyError("missing")
