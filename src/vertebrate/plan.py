"""
ABCs for planning/orchestration.
"""

from abc import ABC, abstractmethod

from vertebrate.compute import Command, Environment
from vertebrate.data import Address, Location, Namespace


class Order(Location, ABC):
    @property
    @abstractmethod
    def command(self) -> Command:
        pass

    def __call__(self) -> None:
        # Enforce returning a receipt?
        self.command()

    @property
    @abstractmethod
    def requirements(self) -> list[Address]:
        pass


class Orders(Namespace):
    @property
    @abstractmethod
    def LocationType(self) -> type[Order]:
        pass

    @abstractmethod
    def environment(self, env: str) -> Environment:
        # Order namespaces are responsible for Environment resolution
        pass


# Should Plans be proper Environments? They are collections of executable Orders
class Plan(ABC):
    def __init__(self, orders: Orders) -> None:
        self._orders = orders

    @property
    def orders(self) -> Orders:
        return self._orders

    @abstractmethod
    def make(self, address: Address) -> None:
        pass
