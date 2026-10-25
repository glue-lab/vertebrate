import unittest

import pytest

from vertebrate.testing import (
    DictNamespace,
    EnvironmentContract,
    NamespaceContract,
    OrdersContract,
    TemporaryContract,
    TransfersContract,
)
from vertebrate.testing._assertions import raises

HOOKS = [
    (EnvironmentContract, "make_environment", ()),
    (EnvironmentContract, "present_executable", ()),
    (EnvironmentContract, "absent_executable", ()),
    (NamespaceContract, "make_namespace", ()),
    (NamespaceContract, "present_address", ()),
    (NamespaceContract, "absent_address", ()),
    (TemporaryContract, "make_namespace", ()),
    (TemporaryContract, "populate", (None,)),
    (TransfersContract, "make_transfers", ()),
    (TransfersContract, "supported_datatypes", ()),
    (TransfersContract, "unsupported_datatypes", ()),
    (OrdersContract, "environment_name", ()),
]


@pytest.mark.parametrize(("contract", "hook", "args"), HOOKS)
def test_unimplemented_hook_names_itself_and_its_contract(contract, hook, args):
    with pytest.raises(NotImplementedError, match=f"{hook}.*{contract.__name__}"):
        getattr(contract(), hook)(*args)


class ReadOnlyNamespace(DictNamespace):
    def __delitem__(self, address):
        raise NotImplementedError("read-only")


class ReadOnlyContract(NamespaceContract):
    def make_namespace(self):
        return ReadOnlyNamespace({"a": 1})

    def present_address(self):
        return "a"

    def absent_address(self):
        return "missing"


@pytest.mark.parametrize(
    "test",
    ["test_delete_removes_present_address", "test_delete_absent_address_does_nothing"],
)
def test_read_only_namespace_skips_deletion_tests_with_reason(test):
    reason = r"deletion not supported \(NotImplementedError: read-only\)"
    with pytest.raises(unittest.SkipTest, match=reason):
        getattr(ReadOnlyContract(), test)()


def test_forgotten_hook_is_not_mistaken_for_read_only():
    class MissingAbsentAddress(NamespaceContract):
        def make_namespace(self):
            return DictNamespace({"a": 1})

    with pytest.raises(NotImplementedError, match="absent_address"):
        MissingAbsentAddress().test_delete_absent_address_does_nothing()


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
