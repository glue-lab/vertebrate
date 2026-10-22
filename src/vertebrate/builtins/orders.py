"""
A simple implementation of an order namespace.
"""

from typing import Any, Type

from vertebrate.builtins.os import OSEnvironment
from vertebrate.builtins.python import PythonEnvironment
from vertebrate.compute import Command, Environment
from vertebrate.data import Address
from vertebrate.plan import Order, Orders


class SimpleOrder(Order):
    @property
    def info(self) -> dict[str, Any]:
        return self.namespace.spec[self.address]

    @property
    def requirements(self):
        return self.info["requirements"]

    @property
    def command(self) -> Command:
        env = self.namespace.environment(self.info["env"])
        action = env[self.info["exe"]]
        return Command(action, args=self.info["args"])


class SimpleOrders(Orders):
    def __init__(self, spec: dict[str, Any], pyenv: PythonEnvironment) -> None:
        self.spec = spec
        self.pyenv = pyenv
        self.osenv = OSEnvironment()

    def type(self, address: Address) -> type | None:
        # No meaningful notion of order type for now
        if address in self:
            return Order

    def __contains__(self, address: Address) -> bool:
        return address in self.spec

    def __delitem__(self, address: Address) -> None:
        raise NotImplementedError("Deletion not implemented for SimpleOrders")

    @property
    def LocationType(self) -> Type[Order]:
        return SimpleOrder

    def PythonEnvironment(self) -> PythonEnvironment:
        return self.pyenv

    def OSEnvironment(self) -> OSEnvironment:
        return self.osenv

    def environment(self, env: str) -> Environment:
        return getattr(self, env)()
