"""
Implementation of a Plan that uses the Luigi framework for orchestration.
"""

import luigi

from vertebrate.builtins.dag import DAGPlan
from vertebrate.builtins.utils import ObjectByAddress, format_address
from vertebrate.data import Address

tasks = ObjectByAddress(globals())


class LuigiPlan(DAGPlan):
    def _define_tasks(self, address: Address) -> None:

        orders = self.orders

        for order_name in self._plan(address):

            def run(self):
                orders[self.name]()
                with self.output().open("w") as file_out:
                    file_out.write("DONE")

            def requires(self):
                return [tasks[req]() for req in orders[self.name].requirements]

            def output(self):
                # A good place to save receipts if/when implemented
                return luigi.LocalTarget(f"{format_address(self.name)}")

            namespace = {
                "__module__": __name__,
                "name": order_name,
                "run": run,
                "requires": requires,
                "output": output,
            }

            Task = type(format_address(order_name), (luigi.Task,), namespace)
            tasks[order_name] = Task

    def make(self, address: Address) -> None:
        self._define_tasks(address)
        luigi.build([tasks[address]()], local_scheduler=True)
