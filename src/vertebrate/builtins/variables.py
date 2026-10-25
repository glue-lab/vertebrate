"""
An implementation of a variable namespace.
"""

import builtins
from typing import Any
from uuid import uuid4

from vertebrate.data import (
    Address,
    Location,
    Namespace,
    Temporary,
    TemporaryLocation,
)


class Value(Location):
    def get(self) -> Any:
        return self.namespace.dict_[self.address]

    def set(self, val: Any) -> None:
        self.namespace.dict_[self.address] = val


class TemporaryValue(Value, TemporaryLocation):
    pass


class Dictionary(Namespace, Temporary):
    def __init__(self, dict_: dict[str, Any]):
        self.dict_ = dict_

    def type(self, address: Address) -> builtins.type | None:
        return type(self.dict_[address]) if address in self.dict_ else None

    @property
    def LocationType(self) -> builtins.type[Location]:
        return Value

    def __contains__(self, address: Address) -> bool:
        return address in self.dict_

    def __delitem__(self, address: Address) -> None:
        self.dict_.pop(address, None)

    def temp(self) -> TemporaryLocation:
        temp_key = f"tmp_{str(uuid4()).replace('-', '_')}"
        return TemporaryValue(self, temp_key)
