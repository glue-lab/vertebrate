"""
An implementation of a variable namespace.
"""

from typing import Any, Type
from uuid import uuid4

from vertebrate.data import (
    Namespace,
    Location,
    Address,
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

    def type(self, address: Address) -> type:
        return type(self.dict_[address])

    @property
    def LocationType(self) -> Type[Location]:
        return Value

    def __contains__(self, address: Address) -> bool:
        return address in self.dict_

    def __delitem__(self, address: Address) -> None:
        del self.dict_[address]

    def temp(self) -> TemporaryLocation:
        temp_key = f"tmp_{str(uuid4()).replace('-', '_')}"
        return TemporaryValue(self, temp_key)
