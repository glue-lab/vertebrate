from typing import Any

import pytest

from vertebrate.data import (
    Address,
    Location,
    LocationTypes,
    Namespace,
    Temporary,
    TemporaryLocation,
    Transfer,
    TransferImplementation,
    Transfers,
)


class Value(Location):
    def get(self) -> Any:
        return self.namespace.values[self.address]

    def set(self, value: Any) -> None:
        self.namespace.values[self.address] = value


class TemporaryValue(Value, TemporaryLocation):
    pass


class DictNamespace(Namespace, Temporary):
    def __init__(self, values: dict[str, Any] | None = None) -> None:
        self.values = {} if values is None else values

    def type(self, address: Address) -> type | None:
        return type(self.values[address]) if address in self.values else None

    def __contains__(self, address: Address) -> bool:
        return address in self.values

    def __delitem__(self, address: Address) -> None:
        del self.values[address]

    @property
    def LocationType(self) -> type[Location]:
        return Value

    def temp(self) -> TemporaryLocation:
        address = f"tmp{len(self.values)}"
        self.values[address] = None
        return TemporaryValue(self, address)


class DictTransfers(Transfers):
    def __init__(self, catalog: dict[LocationTypes, TransferImplementation]) -> None:
        self.catalog = catalog
        self.lookups: list[LocationTypes] = []

    def __getitem__(self, datatypes: LocationTypes) -> TransferImplementation | None:
        self.lookups.append(datatypes)
        return self.catalog.get(datatypes)

    def __contains__(self, datatypes: LocationTypes) -> bool:
        return datatypes in self.catalog


def copy(source: Value, target: Value) -> None:
    target.set(source.get())


def stringify(source: Value, target: Value) -> None:
    target.set(str(source.get()))


@pytest.fixture
def catalog(monkeypatch):
    catalog = DictTransfers({(int, int): copy, (int, str): stringify})
    monkeypatch.setattr(Transfer, "catalog", catalog)
    return catalog


class TestNamespace:
    def test_requires_abstract_methods(self):
        with pytest.raises(TypeError, match="abstract"):
            Namespace()

    def test_getitem_returns_location_bound_to_namespace(self):
        ns = DictNamespace({"a": 1})
        location = ns["a"]
        assert isinstance(location, Value)
        assert location.namespace is ns
        assert location.address == "a"

    def test_getitem_does_not_require_address_to_exist(self):
        assert DictNamespace()["missing"].address == "missing"


class TestLocation:
    def test_type_delegates_to_namespace(self):
        assert DictNamespace({"a": 1})["a"].type is int

    def test_rshift_builds_transfer_with_self_as_source(self):
        ns = DictNamespace({"a": 1, "b": 2})
        transfer = ns["a"] >> ns["b"]
        assert isinstance(transfer, Transfer)
        assert (transfer.source.address, transfer.target.address) == ("a", "b")

    def test_lshift_builds_transfer_with_self_as_target(self):
        ns = DictNamespace({"a": 1, "b": 2})
        transfer = ns["a"] << ns["b"]
        assert (transfer.source.address, transfer.target.address) == ("b", "a")

    def test_building_a_transfer_does_not_perform_it(self):
        ns = DictNamespace({"a": 1, "b": 2})
        ns["a"] >> ns["b"]
        assert ns.values == {"a": 1, "b": 2}


class TestTemporaryLocation:
    def test_enter_returns_the_location(self):
        location = DictNamespace().temp()
        with location as entered:
            assert entered is location

    def test_exit_deletes_the_location(self):
        ns = DictNamespace()
        with ns.temp() as location:
            assert location.address in ns
        assert location.address not in ns

    def test_exit_deletes_the_location_and_propagates_errors(self):
        ns = DictNamespace()
        with pytest.raises(RuntimeError), ns.temp() as location:
            raise RuntimeError
        assert location.address not in ns


class TestTemporary:
    def test_requires_temp(self):
        with pytest.raises(TypeError, match="abstract"):
            Temporary()


class TestTransfers:
    def test_requires_abstract_methods(self):
        with pytest.raises(TypeError, match="abstract"):
            Transfers()


class TestTransfer:
    def test_exposes_source_and_target(self):
        ns = DictNamespace({"a": 1, "b": 2})
        transfer = Transfer(source=ns["a"], target=ns["b"])
        assert (transfer.source.address, transfer.target.address) == ("a", "b")

    def test_call_dispatches_on_location_types(self, catalog):
        ns = DictNamespace({"a": 1, "b": "x"})
        (ns["a"] >> ns["b"])()
        assert catalog.lookups == [(int, str)]
        assert ns.values["b"] == "1"

    def test_call_with_source_type_overrides_inferred_type(self, catalog):
        ns = DictNamespace({"a": 1, "b": 2})
        (ns["a"] >> ns["b"])(source=int, target=str)
        assert catalog.lookups == [(int, str)]
        assert ns.values["b"] == "1"

    def test_call_with_target_type_overrides_inferred_type(self, catalog):
        ns = DictNamespace({"a": 1})
        (ns["a"] >> ns["b"])(target=int)
        assert catalog.lookups == [(int, int)]
        assert ns.values["b"] == 1

    def test_call_with_explicit_transfer_bypasses_catalog(self, catalog):
        ns = DictNamespace({"a": 1, "b": 2})
        (ns["a"] >> ns["b"])(transfer=stringify)
        assert catalog.lookups == []
        assert ns.values["b"] == "1"

    def test_call_raises_when_catalog_has_no_transfer(self, catalog):
        ns = DictNamespace({"a": "x", "b": 2})
        with pytest.raises(NotImplementedError, match="No transfer defined"):
            (ns["a"] >> ns["b"])()
