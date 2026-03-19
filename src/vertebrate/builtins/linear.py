"""
Implementation of a Plan that executes orders linearly.
"""

from collections.abc import Iterator
import logging

from vertebrate.builtins.dag import DAGPlan
from vertebrate.data import Address


logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class LinearPlan(DAGPlan):

    def make(self, address: Address) -> None:
        for order_name in self._plan(address):
            logging.info(f"Satisfying {order_name}")
            self.orders[order_name]()
