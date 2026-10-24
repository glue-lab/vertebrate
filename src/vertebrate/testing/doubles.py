"""
Minimal implementations of Vertebrate's ABCs, to stand in for real ones in tests.
"""

import builtins
import itertools
from collections.abc import Iterable
from typing import Any

from vertebrate.compute import Command, Environment
from vertebrate.data import (
    Address,
    Location,
    LocationTypes,
    Namespace,
    Temporary,
    TemporaryLocation,
    TransferImplementation,
    Transfers,
)
from vertebrate.plan import Order, Orders


class RecordingEnvironment(Environment):
    """
    An environment that records each execution and returns a placeholder result.
    """

    def __init__(self, executables: Iterable[str] = ()) -> None:
        self.executables = set(executables)
        self.calls: list[tuple[str, tuple, dict[str, Any]]] = []

    def execute(self, executable: str, args: tuple, kwargs: dict[str, Any]) -> Any:
        if executable not in self:
            raise KeyError(f"Executable not found: {executable}")
        self.calls.append((executable, tuple(args), dict(kwargs)))
        return f"result of {executable}"

    def __contains__(self, item: str) -> bool:
        return item in self.executables


class Value(Location):
    def get(self) -> Any:
        return self.namespace.values[self.address]

    def set(self, value: Any) -> None:
        self.namespace.values[self.address] = value


class TemporaryValue(Value, TemporaryLocation):
    pass


class DictNamespace(Namespace, Temporary):
    """
    A namespace of values held in a dict, with temporary locations.
    """

    def __init__(self, values: dict[str, Any] | None = None) -> None:
        self.values = {} if values is None else values
        self._counter = itertools.count()

    def type(self, address: Address) -> builtins.type | None:
        return type(self.values[address]) if address in self.values else None

    def __contains__(self, address: Address) -> bool:
        return address in self.values

    def __delitem__(self, address: Address) -> None:
        self.values.pop(address, None)

    @property
    def LocationType(self) -> builtins.type[Location]:
        return Value

    def temp(self) -> TemporaryLocation:
        while (address := f"tmp_{next(self._counter)}") in self.values:
            pass
        return TemporaryValue(self, address)


class DictTransfers(Transfers):
    """
    A catalog of transfers held in a dict, recording each lookup.
    """

    def __init__(self, catalog: dict[LocationTypes, TransferImplementation]) -> None:
        self.catalog = catalog
        self.lookups: list[LocationTypes] = []

    def __getitem__(self, datatypes: LocationTypes) -> TransferImplementation | None:
        self.lookups.append(datatypes)
        return self.catalog.get(datatypes)

    def __contains__(self, datatypes: LocationTypes) -> bool:
        return datatypes in self.catalog


class SpecOrder(Order):
    @property
    def command(self) -> Command:
        spec = self.namespace.spec[self.address]
        environment = self.namespace.environment(spec["env"])
        args = tuple(spec.get("args", ()))
        kwargs = dict(spec.get("kwargs", {}))
        return Command(environment[spec["exe"]], args, kwargs)

    @property
    def requirements(self) -> list[Address]:
        return list(self.namespace.spec[self.address].get("requirements", []))


class SpecOrders(Orders):
    """
    Orders defined by specs in a dict, each run in one of the named environments.

    A spec has an "env" and an "exe", and optionally "args", "kwargs" and
    "requirements".
    """

    def __init__(
        self,
        spec: dict[str, dict[str, Any]],
        environments: dict[str, Environment],
    ) -> None:
        self.spec = spec
        self.environments = environments

    def type(self, address: Address) -> builtins.type | None:
        return None

    def __contains__(self, address: Address) -> bool:
        return address in self.spec

    def __delitem__(self, address: Address) -> None:
        self.spec.pop(address, None)

    @property
    def LocationType(self) -> builtins.type[Order]:
        return SpecOrder

    def environment(self, env: str) -> Environment:
        return self.environments[env]
