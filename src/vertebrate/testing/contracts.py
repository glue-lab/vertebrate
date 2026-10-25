"""
Implementation-agnostic test suites for Vertebrate's ABCs.

Each contract is a plain class of `test_*` methods. To check an implementation,
subclass the contract in a test suite and implement its hook methods; any test
framework that collects `test_*` methods can run it. For unittest, also mix in
`unittest.TestCase`. Assertions are plain `assert` statements, so don't run
contracts under `python -O`.
"""

import unittest

from vertebrate.compute import Action, Command, Environment
from vertebrate.data import (
    Address,
    Location,
    LocationTypes,
    Namespace,
    Temporary,
    TemporaryLocation,
    Transfers,
)
from vertebrate.plan import Order
from vertebrate.testing._assertions import raises


def _unimplemented(contract: str, hook: str) -> NotImplementedError:
    return NotImplementedError(f"Implement {hook}() to run {contract}")


def _delete_or_skip(namespace: Namespace, address: Address) -> None:
    # unittest.SkipTest is honored by unittest and pytest alike
    try:
        del namespace[address]
    except NotImplementedError as error:
        reason = f"deletion not supported ({type(error).__name__}: {error})"
        raise unittest.SkipTest(reason) from error


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


class NamespaceContract:
    """
    Promises every Namespace keeps.

    An absent address is a normal state, not an error: the namespace hands out a
    location for it (through which it may be created), may report the type it
    would hold, and deleting it does nothing.

    A namespace may be read-only: if deletion raises NotImplementedError, the
    deletion tests are skipped, with the error's message as the reason.

    Hooks: `make_namespace()` returns a fresh namespace; `present_address()`
    names an address in it; `absent_address()` names one that isn't.
    """

    def make_namespace(self) -> Namespace:
        raise _unimplemented("NamespaceContract", "make_namespace")

    def present_address(self) -> Address:
        raise _unimplemented("NamespaceContract", "present_address")

    def absent_address(self) -> Address:
        raise _unimplemented("NamespaceContract", "absent_address")

    def test_contains_present_address(self):
        namespace, address = self.make_namespace(), self.present_address()
        assert address in namespace, f"{address!r} should be in {namespace!r}"

    def test_does_not_contain_absent_address(self):
        namespace, address = self.make_namespace(), self.absent_address()
        assert address not in namespace, f"{address!r} should not be in {namespace!r}"

    def test_getitem_returns_location_bound_to_namespace(self):
        namespace = self.make_namespace()
        for address in (self.present_address(), self.absent_address()):
            location = namespace[address]
            assert isinstance(location, namespace.LocationType), (
                f"{location!r} should be a {namespace.LocationType!r}"
            )
            assert location.namespace is namespace, "Location should be bound to it"
            assert location.address == address, f"{location.address!r} != {address!r}"

    def test_location_type_matches_namespace_type(self):
        namespace, address = self.make_namespace(), self.present_address()
        location_type, namespace_type = namespace[address].type, namespace.type(address)
        assert location_type == namespace_type, (
            f"{location_type!r} != {namespace_type!r}"
        )

    def test_type_of_absent_address_is_a_type_or_none(self):
        namespace, address = self.make_namespace(), self.absent_address()
        datatype = namespace.type(address)
        assert datatype is None or isinstance(datatype, type), (
            f"type({address!r}) should be a type or None, not {datatype!r}"
        )

    def test_delete_removes_present_address(self):
        namespace, address = self.make_namespace(), self.present_address()
        _delete_or_skip(namespace, address)
        assert address not in namespace, f"{address!r} should have been deleted"

    def test_delete_absent_address_does_nothing(self):
        namespace, address = self.make_namespace(), self.absent_address()
        _delete_or_skip(namespace, address)
        assert address not in namespace, f"{address!r} should still be absent"


class _BlockError(Exception):
    pass


class TemporaryContract:
    """
    Promises every Temporary namespace keeps.

    Hooks: `make_namespace()` returns a fresh namespace; `populate(location)`
    writes something to a location so that its address exists.
    """

    def make_namespace(self) -> Temporary:
        raise _unimplemented("TemporaryContract", "make_namespace")

    def populate(self, location: Location) -> None:
        raise _unimplemented("TemporaryContract", "populate")

    def test_temp_returns_temporary_location_in_namespace(self):
        namespace = self.make_namespace()
        location = namespace.temp()
        assert isinstance(location, TemporaryLocation), (
            f"{location!r} should be a TemporaryLocation"
        )
        assert location.namespace is namespace, "Location should be bound to it"

    def test_temp_address_is_unused(self):
        namespace = self.make_namespace()
        address = namespace.temp().address
        assert address not in namespace, f"{address!r} should not exist yet"

    def test_temp_addresses_are_distinct(self):
        namespace = self.make_namespace()
        first = namespace.temp()
        self.populate(first)
        second = namespace.temp()
        assert first.address != second.address, f"{first.address!r} was reused"

    def test_exit_removes_populated_location(self):
        namespace = self.make_namespace()
        with namespace.temp() as location:
            self.populate(location)
            assert location.address in namespace, "populate() should create it"
        assert location.address not in namespace, f"{location.address!r} remains"

    def test_exit_tolerates_unpopulated_location(self):
        namespace = self.make_namespace()
        with namespace.temp() as location:
            pass
        assert location.address not in namespace, f"{location.address!r} remains"

    def test_exit_removes_location_when_block_raises(self):
        namespace = self.make_namespace()
        with raises(_BlockError), namespace.temp() as location:
            self.populate(location)
            raise _BlockError
        assert location.address not in namespace, f"{location.address!r} remains"


class TransfersContract:
    """
    Promises every Transfers catalog keeps.

    Hooks: `make_transfers()` returns a fresh catalog; `supported_datatypes()`
    names a (source, target) pair of types it can transfer between;
    `unsupported_datatypes()` names a pair it can't.
    """

    def make_transfers(self) -> Transfers:
        raise _unimplemented("TransfersContract", "make_transfers")

    def supported_datatypes(self) -> LocationTypes:
        raise _unimplemented("TransfersContract", "supported_datatypes")

    def unsupported_datatypes(self) -> LocationTypes:
        raise _unimplemented("TransfersContract", "unsupported_datatypes")

    def test_contains_supported_datatypes(self):
        transfers, datatypes = self.make_transfers(), self.supported_datatypes()
        assert datatypes in transfers, f"{datatypes!r} should be in {transfers!r}"

    def test_does_not_contain_unsupported_datatypes(self):
        transfers, datatypes = self.make_transfers(), self.unsupported_datatypes()
        assert datatypes not in transfers, f"{datatypes!r} should not be in it"

    def test_getitem_returns_transfer_for_supported_datatypes(self):
        transfers, datatypes = self.make_transfers(), self.supported_datatypes()
        transfer = transfers[datatypes]
        assert callable(transfer), f"transfers[{datatypes!r}] is {transfer!r}"

    def test_getitem_returns_none_for_unsupported_datatypes(self):
        transfers, datatypes = self.make_transfers(), self.unsupported_datatypes()
        transfer = transfers[datatypes]
        assert transfer is None, f"transfers[{datatypes!r}] is {transfer!r}"


class OrdersContract(NamespaceContract):
    """
    Promises every Orders namespace keeps, in addition to NamespaceContract's.

    Hooks: those of NamespaceContract, where `present_address()` should name an
    order with requirements; `environment_name()` names an environment the
    orders can resolve.
    """

    def environment_name(self) -> str:
        raise _unimplemented("OrdersContract", "environment_name")

    def test_getitem_returns_order(self):
        orders, address = self.make_namespace(), self.present_address()
        order = orders[address]
        assert isinstance(order, Order), f"{order!r} should be an Order"

    def test_order_command_is_command(self):
        orders, address = self.make_namespace(), self.present_address()
        command = orders[address].command
        assert isinstance(command, Command), f"{command!r} should be a Command"

    def test_order_requirements_are_orders(self):
        orders, address = self.make_namespace(), self.present_address()
        for requirement in orders[address].requirements:
            assert requirement in orders, (
                f"{address!r} requires {requirement!r}, which is not in {orders!r}"
            )

    def test_environment_resolves_to_environment(self):
        orders, name = self.make_namespace(), self.environment_name()
        environment = orders.environment(name)
        assert isinstance(environment, Environment), (
            f"environment({name!r}) should be an Environment, not {environment!r}"
        )
