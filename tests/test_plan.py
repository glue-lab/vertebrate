from typing import Any

import pytest

from vertebrate.compute import Command, Environment
from vertebrate.data import Address
from vertebrate.plan import Order, Orders, Plan


class RecordingEnvironment(Environment):
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple]] = []

    def execute(self, executable: str, args: tuple, kwargs: dict[str, Any]) -> Any:
        self.calls.append((executable, args))

    def __contains__(self, item: str) -> bool:
        return True


class SpecOrder(Order):
    @property
    def command(self) -> Command:
        spec = self.namespace.spec[self.address]
        return Command(self.namespace.environment("env")[spec["exe"]], spec["args"])

    @property
    def requirements(self) -> list[Address]:
        return self.namespace.spec[self.address]["requirements"]


class SpecOrders(Orders):
    def __init__(self, spec: dict[str, dict[str, Any]]) -> None:
        self.spec = spec
        self.env = RecordingEnvironment()

    def type(self, address: Address) -> type | None:
        return Order if address in self.spec else None

    def __contains__(self, address: Address) -> bool:
        return address in self.spec

    def __delitem__(self, address: Address) -> None:
        del self.spec[address]

    @property
    def LocationType(self) -> type[Order]:
        return SpecOrder

    def environment(self, env: str) -> Environment:
        return self.env


SPEC = {
    "build": {"exe": "make", "args": ("all",), "requirements": ["fetch"]},
    "fetch": {"exe": "curl", "args": ("-O", "data.csv"), "requirements": []},
}


class TestOrder:
    def test_call_runs_its_command(self):
        orders = SpecOrders(SPEC)
        orders["build"]()
        assert orders.env.calls == [("make", ("all",))]

    def test_call_does_not_run_requirements(self):
        orders = SpecOrders(SPEC)
        orders["build"]()
        assert ("curl", ("-O", "data.csv")) not in orders.env.calls

    def test_exposes_requirements(self):
        assert SpecOrders(SPEC)["build"].requirements == ["fetch"]


class TestOrders:
    def test_requires_environment_resolution(self):
        class WithoutEnvironment(Orders):
            type = SpecOrders.type
            __contains__ = SpecOrders.__contains__
            __delitem__ = SpecOrders.__delitem__
            LocationType = SpecOrders.LocationType

        with pytest.raises(TypeError, match="environment"):
            WithoutEnvironment()

    def test_getitem_returns_order(self):
        order = SpecOrders(SPEC)["build"]
        assert isinstance(order, Order)
        assert order.address == "build"


class TestPlan:
    def test_requires_make(self):
        with pytest.raises(TypeError, match="abstract"):
            Plan(SpecOrders(SPEC))

    def test_exposes_its_orders(self):
        class NoopPlan(Plan):
            def make(self, address: Address) -> None:
                pass

        orders = SpecOrders(SPEC)
        assert NoopPlan(orders).orders is orders
