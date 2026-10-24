import pytest

from vertebrate.testing._assertions import raises


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
