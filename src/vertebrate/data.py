"""
ABCs for data transfer.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from types import TracebackType
from typing import Any, Type


type Address = str


class Namespace(ABC):
    """
    A typed collection of locations where data resides.
    """

    @abstractmethod
    def type(self, address: Address) -> type | None:
        pass

    @abstractmethod
    def __contains__(self, address: Address) -> bool:
        pass

    @abstractmethod
    def __delitem__(self, address: Address) -> None:
        pass

    @property
    @abstractmethod
    def LocationType(self) -> Type["Location"]:
        pass

    def __getitem__(self, address: Address) -> "Location":
        return self.LocationType(self, address)


class Temporary(ABC):
    """
    Mix-in for namespaces that implement temporary locations.
    """

    @abstractmethod
    def temp(self) -> "TemporaryLocation":
        pass


class Location(object):
    """
    A location that data can be read from and written to.
    The exact semantics of its read and write operations differ
    by implementation (ex. a simple file, a message queue, etc.).
    """

    def __init__(self, namespace: Namespace, address: Address) -> None:
        self._namespace = namespace
        self._address = address

    @property
    def namespace(self) -> Namespace:
        return self._namespace

    @property
    def address(self) -> Address:
        return self._address

    @property
    def type(self) -> type:
        return self.namespace.type(self.address)

    def __rshift__(self, loc: "Location") -> "Transfer":
        """
        A data transfer where this location is the source.
        """
        return Transfer(source=self, target=loc)

    def __lshift__(self, loc: "Location") -> "Transfer":
        """
        A data transfer where this location is the target.
        """
        return Transfer(source=loc, target=self)


class TemporaryLocation(Location):
    """
    A temporary location. Adds a context manager for location clean-up.
    """

    def __enter__(self) -> "TemporaryLocation":
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        del self.namespace[self.address]


type LocationTypes = tuple[type, type]
type TransferImplementation = Callable[[Location, Location], None]


class Transfers(ABC):
    """
    A collection of known transfers between datatypes
    (ex. dict to JSON, JSON to dict, database table to Parquet file, etc.).
    """

    @abstractmethod
    def __getitem__(self, datatypes: LocationTypes) -> TransferImplementation | None:
        pass

    @abstractmethod
    def __contains__(self, datatypes: LocationTypes) -> bool:
        pass


class Transfer(object):
    """
    A transfer of data from one location to another.
    """

    catalog: Transfers | None = None

    def __init__(self, source: Location, target: Location) -> None:
        self._source = source
        self._target = target

    @property
    def source(self) -> Location:
        return self._source

    @property
    def target(self) -> Location:
        return self._target

    def __call__(
        self,
        source: type | None = None,
        target: type | None = None,
        transfer: TransferImplementation | None = None,
    ) -> None:
        source_type = source if source else self.source.type
        target_type = target if target else self.target.type
        if not transfer:
            transfer = self.catalog[source_type, target_type]
        if not transfer:
            msg = f"No transfer defined from {source_type} to {target_type}."
            raise NotImplementedError(msg)
        transfer(self.source, self.target)
