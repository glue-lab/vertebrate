import pytest

from vertebrate.data import Address
from vertebrate.plan import Order, Orders, Plan
from vertebrate.testing import RecordingEnvironment, SpecOrders

SPEC = {
    "build": {
        "env": "shell",
        "exe": "make",
        "args": ("all",),
        "requirements": ["fetch"],
    },
    "fetch": {"env": "shell", "exe": "curl", "args": ("-O", "data.csv")},
}


def make_orders() -> tuple[SpecOrders, RecordingEnvironment]:
    shell = RecordingEnvironment({"make", "curl"})
    return SpecOrders(SPEC, {"shell": shell}), shell


class TestOrder:
    def test_requires_command_and_requirements(self):
        orders, _ = make_orders()
        with pytest.raises(TypeError, match="abstract"):
            Order(orders, "build")

    def test_call_runs_its_command(self):
        orders, shell = make_orders()
        orders["build"]()
        assert shell.calls == [("make", ("all",), {})]

    def test_call_does_not_run_requirements(self):
        orders, shell = make_orders()
        orders["build"]()
        assert [call[0] for call in shell.calls] == ["make"]

    def test_exposes_requirements(self):
        orders, _ = make_orders()
        assert orders["build"].requirements == ["fetch"]


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
        orders, _ = make_orders()
        order = orders["build"]
        assert isinstance(order, Order)
        assert order.address == "build"


class TestPlan:
    def test_requires_make(self):
        orders, _ = make_orders()
        with pytest.raises(TypeError, match="abstract"):
            Plan(orders)

    def test_exposes_its_orders(self):
        class NoopPlan(Plan):
            def make(self, address: Address) -> None:
                pass

        orders, _ = make_orders()
        assert NoopPlan(orders).orders is orders
