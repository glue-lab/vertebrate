from vertebrate.data import Address
from vertebrate.plan import Plan
from vertebrate.testing import PlanContract


class DepthFirstPlan(Plan):
    """
    A reference plan: run each requirement, depth first, before its dependent.
    """

    def make(self, address: Address) -> None:
        done: set[Address] = set()

        def visit(address: Address) -> None:
            if address in done:
                return
            for requirement in self.orders[address].requirements:
                visit(requirement)
            self.orders[address]()
            done.add(address)

        visit(address)


class TestDepthFirstPlan(PlanContract):
    def make_plan(self, orders):
        return DepthFirstPlan(orders)
